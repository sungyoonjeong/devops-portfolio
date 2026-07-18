# CI/CD 개념 정리

7/17 CI/CD D1 학습 — 브랜치 전략, GitHub Actions 구조, 파이프라인 각 단계의 목적.

---

## 1. 브랜치 전략: Git Flow vs GitHub Flow

### Git Flow
`main`(배포용) · `develop`(통합) · `feature/*` · `release/*` · `hotfix/*` 다섯 종류 브랜치를 역할별로 나눠 쓰는 모델. 정식 릴리스 주기가 있는 제품(버전 태그를 자주 찍고, 여러 버전을 동시에 유지보수해야 하는 경우)에 맞는다. 브랜치 종류가 많은 만큼 규칙도 복잡하고, 머지 경로가 길어서 릴리스 준비에 오버헤드가 든다.

### GitHub Flow
`main` 하나 + 짧게 사는 `feature/*` 브랜치만 쓰는 단순한 모델. 흐름은:

1. `main`에서 `feature/작업명` 브랜치를 판다
2. 그 브랜치에서 커밋을 쌓는다
3. PR을 열고, CI(lint·test·build)를 통과시킨다
4. `main`에 머지하면 그게 곧 배포 대상이 된다

release 브랜치가 따로 없다는 게 핵심 차이 — `main`이 항상 배포 가능한 상태를 유지해야 한다는 전제가 깔린다. 그래서 CI가 `main` 앞을 반드시 지켜야 한다(머지 전에 test job이 막아주는 구조).

### 이 포트폴리오에 적용한 이유
PF1~PF3, 캡스톤 전부 버전을 여러 개 동시 유지보수할 일이 없고(계속 최신 하나만 굴러가는 개인 프로젝트), 릴리스 주기 관리보다는 "PR 열면 CI가 자동으로 검증"이라는 실무 감각을 보여주는 게 포트폴리오 목적에 맞는다. 그래서 **GitHub Flow**로 확정. `feature/ci-pipeline`처럼 작업 단위로 브랜치를 짧게 파고, PR 머지 시점에 CI 5개 job이 전부 통과해야 `main`에 들어가는 구조를 목표로 한다.

---

## 2. GitHub Actions 기본 구조

```yaml
on:              # 트리거 — 언제 실행할지
jobs:
  job이름:
    runs-on:     # 어떤 러너(가상머신)에서 실행할지
    needs:       # 이 job이 실행되려면 먼저 끝나야 하는 job (의존성 = 순서 강제)
    steps:       # 실제로 실행할 명령들 (순서대로)
```

- **workflow**: `.github/workflows/*.yml` 파일 하나가 workflow 하나. 레포 루트의 `.github/workflows/`만 GitHub이 인식한다 — 서브폴더에 넣으면 인식 안 됨. 그래서 모노레포(PF2가 `PortFolio/PF2/` 서브폴더에 있는 구조)에서도 workflow 파일 자체는 항상 레포 루트에 둬야 한다.
- **job**: 독립된 가상머신 하나에서 도는 작업 단위. `needs`로 명시하지 않으면 여러 job이 기본적으로 **병렬**로 뜬다 — lint/test/build를 굳이 `needs`로 안 엮으면 test가 lint 실패와 무관하게 같이 돌아버려서, 실패한 코드로 이미지까지 빌드하는 낭비가 생긴다. 그래서 `needs: lint`처럼 체인을 걸어 **fail fast**(앞 단계 실패하면 뒤는 아예 안 돎)를 강제한다.
- **step**: job 안에서 순차 실행되는 최소 단위. `uses`(마켓플레이스에 있는 재사용 액션 호출, 예: `actions/checkout@v4`)와 `run`(쉘 명령 직접 실행) 두 종류가 있다.
- **모노레포 경로 필터**: `on.push.paths: ["PortFolio/PF2/**"]`를 안 걸면 레포의 다른 폴더(k8s, terraform 등) 문서만 고쳐도 PF2 CI가 매번 돈다. `paths` 필터로 실제 PF2 코드가 바뀔 때만 트리거되게 제한했다.

---

## 3. 파이프라인 5단계와 각각의 존재 이유

### ① lint — `gofmt -l` + `go vet`
- `gofmt -l .`: 파일 목록만 출력(자동 수정 안 함) — 포맷이 안 맞는 파일이 하나라도 있으면 `test -z "$(gofmt -l .)"`가 실패해서 job이 죽는다. "코드 스타일이 안 맞으면 그 자리에서 걸러낸다"는 게 목적.
- `go vet`: 컴파일은 되지만 의심스러운 패턴(예: `Printf` 포맷 문자열과 인자 개수 불일치, 도달 불가능한 코드)을 정적으로 잡아낸다. 컴파일러보다 한 단계 더 깐깐한 검사.
- 왜 제일 먼저? — 제일 싸고 빠른 검사이기 때문. 문법·스타일 문제가 있는 코드로 테스트→빌드→스캔까지 돌리는 건 CI 시간 낭비다.

### ② test — `go test -v ./...`
- `main_test.go`에 작성한 `TestHealthHandler`, `TestMetricsHandler`가 여기서 실행된다.
- `httptest.NewRequest` + `httptest.NewRecorder`: 실제 소켓을 열지 않고, HTTP 핸들러 함수를 메모리 안에서 직접 호출해 요청/응답을 흉내낸다 — 서버를 띄우지 않고도 핸들러 로직만 빠르게 검증하는 Go 표준 패턴.
- lint 뒤에 두는 이유: 문법이 이상한 코드는 애초에 컴파일이 안 되니 테스트 자체가 무의미 — lint가 먼저 걸러줘야 test 단계가 의미 있다.

### ③ docker-build — 커밋 해시 태그로 이미지 빌드
- `deploy.sh`(로컬 배포 스크립트)와 **동일한 태깅 전략**을 그대로 이식: `TAG=$(git rev-parse --short HEAD)`. 로컬 배포든 CI 배포든 "어떤 커밋이 어떤 이미지가 됐는지"를 한 가지 규칙으로 추적할 수 있게 통일한 것.
- `docker save` → `actions/upload-artifact`: GitHub Actions의 각 job은 서로 다른 가상머신이라 파일시스템이 공유되지 않는다. 그래서 docker-build에서 만든 이미지를 trivy-scan·ecr-push job이 쓰려면, 이미지를 tar 파일로 압축해 artifact로 업로드하고 다음 job에서 다시 다운로드해야 한다.

### ④ trivy-scan — 이미지 취약점 스캔
- `deploy.sh`의 `trivy image --exit-code 0 --severity HIGH,CRITICAL` 로직을 그대로 Actions job으로 이식(`aquasecurity/trivy-action`).
- `exit-code: "0"`: 지금은 취약점이 나와도 파이프라인을 막지 않고 경고만 한다. 실제 프로덕션 전환 시 `"1"`로 바꾸면 HIGH/CRITICAL 발견 시 그 자리에서 배포가 차단된다 — 지금 단계에서 그렇게 안 한 이유는, 아직 알려진 베이스 이미지 취약점만으로 매번 파이프라인이 막히면 학습 흐름이 끊기기 때문(실무 전환 시점의 스위치로 문서에 명시해둠).

### ⑤ ecr-push — main 브랜치에만, Secrets 기반
- `if: github.event_name == 'push'`: PR(pull_request 이벤트)에서는 이미지를 푸시하지 않는다. PR은 "검증"이 목적이고, `main`에 실제로 병합된 커밋만 레지스트리에 올라가야 하기 때문 — GitHub Flow의 "main = 배포 가능 상태" 원칙과 맞물린다.
- **지금은 Secrets 방식**: `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`를 GitHub Secrets에 저장해 쓰는 장기 액세스키 인증. 구현이 단순해서 1차로 채택.
- **OIDC 키리스 인증은 PF1에서 정식 적용 예정**: OIDC는 GitHub Actions가 매 실행마다 AWS에 단기 토큰을 발급받아 쓰는 방식으로, 레포에 장기 액세스키를 저장할 필요가 없어 유출 위험이 원천적으로 낮다(보안 베스트 프랙티스). PF2는 CI 파이프라인 구조 자체를 익히는 게 목적이라 Secrets로 먼저 동작시키고, PF1에서 OIDC로 업그레이드하는 게 이번 학습 순서.

---

## 4. 배운 것 — job 간 데이터 전달 패턴

같은 workflow 안에서도 job은 서로 다른 VM이라는 걸 이번에 명확히 체감했다. `outputs`(job이 다음 job에 값 하나를 넘길 때, 예: 커밋 해시 태그)와 `upload-artifact`/`download-artifact`(파일 자체를 넘길 때, 예: 빌드된 이미지)는 쓰임이 다르다 — 작은 값은 outputs, 큰 파일은 artifact. 이 구분이 헷갈리면 "다음 job에서 왜 이미지가 안 보이지?" 하는 흔한 삽질을 하게 된다.
