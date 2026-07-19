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

### `needs`는 실행 순서만 강제하지 않는다 — output 접근 범위도 결정한다

이번에 `ecr-push` job에서 직접 겪은 함정: `needs: trivy-scan`만 걸어두면 실행 순서는 `docker-build → trivy-scan → ecr-push`로 정확히 지켜지지만, `ecr-push` 안에서 `${{ needs.docker-build.outputs.tag }}`를 쓰면 **빈 문자열**이 된다. GitHub Actions는 `needs` 그래프를 전이적으로(transitively) 따라가며 output을 보여주지 않는다 — **오직 그 job의 `needs` 목록에 "직접" 이름이 올라간 job의 output만** 참조 가능하다. `trivy-scan → docker-build`처럼 사이에 다른 job이 껴 있어도, `ecr-push`가 `docker-build`의 값을 쓰려면 `needs: [docker-build, trivy-scan]`처럼 **본인이 직접** 나열해야 한다. "A가 B를 필요로 하고 B가 C를 필요로 하면 A도 C를 볼 수 있다"는 직관이 여기선 틀린다 — 순서(scheduling)와 데이터 접근 범위(scoping)는 별개의 규칙이라는 게 핵심.

### `defaults.run.working-directory`의 적용 범위 — workflow 레벨 vs job 레벨

`defaults`를 workflow 최상단에 걸면 **그 워크플로의 모든 job, 모든 step**에 상속된다. 이게 안전한 전제는 "모든 job이 공통으로 소스를 체크아웃한다"는 것인데, 실제로는 job마다 체크아웃 여부가 다를 수 있다(예: 아티팩트만 받아 쓰는 job은 체크아웃이 필요 없음). 이런 워크플로에서 workflow-level `defaults`를 쓰면, 체크아웃 안 한 job의 러너에는 그 디렉토리 자체가 없어서 셸이 뜨지도 못하고 죽는다. **`defaults`는 그 값이 실제로 유효한 범위(job)에만 걸어야 한다** — 범위를 넓게 잡을수록 "왜 이 job만 이상하게 실패하지" 디버깅이 어려워진다.

---

## 5. AWS IAM — CI 전용 최소권한 사용자 설계

### 왜 관리자 키를 CI에 그대로 못 쓰는가
CI 파이프라인의 자격증명은 두 가지 이유로 개인 관리자 키보다 훨씬 좁게 잡아야 한다:
1. **저장 위치가 다르다**: GitHub Secrets는 레포 관리자 권한이 있는 누구나 재등록(덮어쓰기)할 수 있고, 워크플로 로그·서드파티 액션의 실수로 유출될 가능성이 개인 키보다 구조적으로 높다.
2. **필요한 권한이 좁다**: CI가 실제로 하는 일은 "이 레포에 이미지 하나 올리기"뿐이다. 계정 전체를 조작할 수 있는 관리자 키를 여기에 쓰면, 키가 유출됐을 때의 피해 범위(blast radius)가 계정 전체로 커진다.

### 최소권한 IAM 정책 설계 — 리소스를 ARN으로 좁히기
`ecr:GetAuthorizationToken`은 ECR API 특성상 리소스를 특정 레포로 좁힐 수 없어 `Resource: "*"`가 강제되지만(이 액션 자체는 "로그인 토큰 발급"이라 레포 단위 개념이 없음), 실제 이미지 업로드 액션들(`PutImage`, `InitiateLayerUpload` 등)은 `Resource`를 특정 레포의 ARN(`arn:aws:ecr:REGION:ACCOUNT:repository/pf2`)으로 명시해 **그 레포 하나에만** 쓸 수 있게 좁혔다. 이렇게 하면 이 IAM 사용자의 키가 유출돼도, 공격자가 할 수 있는 일은 `pf2` 레포에 이미지를 올리는 것뿐이고, 다른 레포를 건드리거나 이미지를 내려받거나(`pull`) ECR 밖의 다른 AWS 서비스를 조작하는 건 전부 불가능하다.

### 시크릿 값을 다루는 원칙
- **화면·로그에 절대 echo하지 않는다**: `SecretAccessKey`처럼 한 번 유출되면 재발급 전까지 계속 위험한 값은, 셸 변수에 담아 다음 명령으로 바로 넘기되 그 변수 자체를 출력하는 코드는 절대 실행하지 않는다.
- **로컬 파일은 최소 권한 + 즉시 삭제**: 부득이하게 파일로 거쳐야 한다면 `chmod 600`(소유자만 읽기)으로 좁히고, 목적(GitHub Secrets 등록)을 마치는 즉시 `shred -u`(단순 삭제가 아니라 디스크 내용까지 덮어써 지움)로 없앤다.
- **GitHub 쪽도 write-only**: `gh secret set`으로 등록한 값은 이후 `gh secret list`로도 값 자체는 절대 조회되지 않는다(이름·등록일만). 이 구조 자체가 "등록 후엔 값을 다시 꺼내볼 필요가 없게" 설계돼 있다 — CI 쪽 자격증명 관리의 일반적인 원칙이다.

---

## 6. ECR 운영 — 이미지 자동 정리(lifecycle policy)

컨테이너 레지스트리는 push할 때마다 새 이미지가 쌓이기만 하고 자동으로 안 지워진다. 커밋 해시 태깅 전략(매 배포마다 새 태그)과 만나면 이미지가 무한히 늘어나 저장 비용이 계속 증가한다. `aws ecr put-lifecycle-policy`로 **"태그 개수가 5개를 넘으면 오래된 것부터 자동 만료"** 규칙을 걸어두면, 별도 운영 작업 없이도 최근 배포 이력만 유지된다. 실무에서는 보통 "최근 N개 유지" + "N일 이상 지난 미사용 태그 삭제"를 함께 걸어 스토리지 비용과 롤백 가능 범위(최근 몇 개까지 되돌릴 수 있는지)의 균형을 잡는다.

---

## 7. GitHub Actions 로그를 읽고 원인을 좁히는 절차

이번에 실제로 3개 버그를 순서대로 만나면서 정착한 디버깅 순서:

1. **`gh run list --workflow <파일명> --limit N`**으로 최근 실행과 상태(✓/X/*)를 먼저 확인
2. **`gh run view <run-id> --json jobs --jq '.jobs[] | {name, conclusion}'`**로 어느 job이 실패했는지 한눈에 파악 — 성공한 job은 더 볼 필요가 없으므로 조사 범위를 즉시 좁힌다
3. **`gh run view --job <job-id>`**로 그 job의 step별 성공/실패 목록 확인 — 어느 step에서 멈췄는지 특정
4. **`gh api /repos/OWNER/REPO/actions/jobs/<job-id>/logs`**로 그 job의 raw 로그 전체를 받아 직접 `grep` — `gh run view --log-failed`가 간혹 캐시·타이밍 문제로 빈 결과를 줄 때가 있어서, 이 API 직접 호출이 더 안정적이었다
5. 로그에서 찾은 에러 메시지를 **그대로 재현할 수 있는 최소 단위**로 로컬에서 재현(예: `docker run golang:1.22-alpine gofmt -l .`) 후 수정 → 재푸시 → 처음부터 다시 확인

이 순서의 핵심은 "전체 로그를 처음부터 끝까지 읽지 않는다"는 것 — job 단위로 먼저 좁히고, 그 안에서 실패한 step 하나만 정확히 짚어서 원인을 찾는 게 훨씬 빠르다.
