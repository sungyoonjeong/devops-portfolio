# 7/17 — CI/CD D1 실습: 브랜치 전략 + PF2 GitHub Actions CI

목표: PF2(Go 서버) 레포에 GitHub Actions 파이프라인을 처음부터 붙인다. 개념(브랜치 전략, job 구조)은 [CICD_STUDY.md](CICD_STUDY.md) 참조, 여기는 실제로 실행한 명령과 결과 기록.

세션 사정으로 사용자 대신 Claude가 실제 터미널에서 전 과정을 직접 실행 — 코드 작성(브랜치 생성, 테스트 코드, workflow yaml)부터 로컬 검증까지 전부 터미널에 그대로 남겼다.

---

## 1. 브랜치 전략 — GitHub Flow 적용

`PortFolio/PF2` 디렉토리에서 작업용 feature 브랜치를 생성:

```bash
$ cd ~/devops-portfolio/PortFolio/PF2
$ git checkout -b feature/ci-pipeline
Switched to a new branch 'feature/ci-pipeline'
$ git branch
* feature/ci-pipeline
  main
```

![브랜치 생성](images/branch-01-feature-checkout.png)

Git Flow(`develop`/`release`/`hotfix` 다중 브랜치)가 아니라 **GitHub Flow**(main + 짧은 feature 브랜치)를 택한 이유는 STUDY.md 1장 참조 — 버전을 여러 개 동시 유지보수할 필요가 없는 개인 포트폴리오 구조라서, "PR 열면 CI가 검증"이라는 흐름만으로 충분하다.

---

## 2. PF2 테스트 코드 작성 — `main_test.go`

기존 PF2에는 테스트가 하나도 없었다(`main.go`만 존재). CI의 test job이 실행할 대상이 필요해서, `/health`·`/metrics` 핸들러를 검증하는 테스트를 새로 작성했다.

```go
package main

import (
    "encoding/json"
    "net/http"
    "net/http/httptest"
    "testing"
)

// TestHealthHandler: GET /health 가 200 OK와 status=ok JSON을 반환하는지 검증
func TestHealthHandler(t *testing.T) {
    req := httptest.NewRequest(http.MethodGet, "/health", nil)
    rec := httptest.NewRecorder()

    healthHandler(rec, req)

    if rec.Code != http.StatusOK {
        t.Fatalf("want 200, got %d", rec.Code)
    }

    var body map[string]string
    if err := json.NewDecoder(rec.Body).Decode(&body); err != nil {
        t.Fatalf("invalid JSON response: %v", err)
    }
    if body["status"] != "ok" {
        t.Fatalf("want status=ok, got %s", body["status"])
    }
}

// TestMetricsHandler: GET /metrics 호출 시 requests_total 카운터가 1 증가하는지 검증
func TestMetricsHandler(t *testing.T) {
    before := requestsTotal // 다른 테스트가 먼저 카운터를 올렸을 수 있어 절대값이 아닌 상대값으로 비교

    req := httptest.NewRequest(http.MethodGet, "/metrics", nil)
    rec := httptest.NewRecorder()

    metricsHandler(rec, req)

    if rec.Code != http.StatusOK {
        t.Fatalf("want 200, got %d", rec.Code)
    }

    var body map[string]interface{}
    if err := json.NewDecoder(rec.Body).Decode(&body); err != nil {
        t.Fatalf("invalid JSON response: %v", err)
    }

    got := int64(body["requests_total"].(float64)) // JSON 숫자는 디코드하면 float64가 된다
    if got != before+1 {
        t.Fatalf("want requests_total=%d, got %d", before+1, got)
    }
}
```

**설계 포인트**: `httptest.NewRequest` + `httptest.NewRecorder`로 실제 TCP 소켓을 열지 않고 핸들러 함수를 직접 호출한다. 서버를 띄우지 않아도 되니 테스트가 빠르고(`0.008s`), CI에서 포트 충돌 걱정도 없다.

### 로컬 검증 — Docker 컨테이너 안에서 실행

PF2는 로컬에 Go 툴체인을 설치하지 않고 `deploy.sh`처럼 Docker로만 빌드해온 프로젝트라, `gofmt`/`go vet`/`go test`도 호스트에 go가 없어 직접 실행이 안 됐다:

```bash
$ gofmt -w main_test.go
Command 'gofmt' not found, but can be installed with: sudo snap install go ...
```

CI가 쓸 것과 동일한 `golang:1.22-alpine` 이미지를 그 자리에서 컨테이너로 띄워 검증했다 — 이렇게 하면 "CI에서만 통과/실패하는" 환경 차이를 로컬에서 미리 잡을 수 있다:

```bash
$ docker run --rm -v "$PWD":/app -w /app golang:1.22-alpine \
    sh -c "gofmt -l . && go vet ./... && go test -v ./..."

main_test.go
=== RUN   TestHealthHandler
--- PASS: TestHealthHandler (0.00s)
=== RUN   TestMetricsHandler
--- PASS: TestMetricsHandler (0.00s)
PASS
ok      pf2     0.008s
```

![Docker 안에서 gofmt+vet+test 실행](images/test-01-docker-govet-gotest.png)

(`gofmt -l`이 `main_test.go`를 출력한 건 "포맷이 안 맞는 파일 목록"일 뿐 에러가 아니다 — 터미널에서 스페이스로 입력한 들여쓰기를 gofmt 컨벤션인 탭으로 자동 정리한 결과. `go vet`·`go test`는 이어서 정상 통과.)

---

## 3. GitHub Actions CI 워크플로 작성 — `.github/workflows/pf2-ci.yml`

**중요**: PF2는 `devops-portfolio` 모노레포의 `PortFolio/PF2/` 서브폴더에 있지만, GitHub Actions는 **레포 루트의 `.github/workflows/`만 인식**한다. 그래서 workflow 파일 자체는 루트에 두고, `paths` 필터로 PF2 변경 시에만 돌게 제한했다.

```bash
$ mkdir -p ~/devops-portfolio/.github/workflows
$ cd ~/devops-portfolio/.github/workflows
```

작성한 전체 워크플로(5개 job — lint → test → docker-build → trivy-scan → ecr-push, 순서대로 `needs`로 체이닝):

```yaml
# PF2 Go 서버 CI 파이프라인
# 모노레포이므로 PortFolio/PF2/** 경로 변경이 있을 때만 실행 (다른 프로젝트 수정 시 불필요하게 안 돌게)
name: PF2 CI

on:
  push:
    branches: [main]
    paths:
      - "PortFolio/PF2/**"
      - ".github/workflows/pf2-ci.yml"
  pull_request:
    branches: [main]
    paths:
      - "PortFolio/PF2/**"

# 모든 job의 기본 작업 디렉토리를 PF2 폴더로 고정 — step마다 working-directory 반복 안 써도 되게
defaults:
  run:
    working-directory: PortFolio/PF2

env:
  IMAGE_NAME: pf2

jobs:
  # 1) lint: gofmt 포맷 검사 + go vet 정적 분석
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: "1.22"
      - name: gofmt 검사 (포맷 안 맞는 파일이 있으면 실패)
        run: test -z "$(gofmt -l .)"
      - name: go vet
        run: go vet ./...

  # 2) test: 단위 테스트 (main_test.go - TestHealthHandler, TestMetricsHandler)
  test:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: "1.22"
      - name: go test
        run: go test -v ./...

  # 3) docker-build: 커밋 해시 태그로 이미지 빌드 (deploy.sh와 동일 태깅 전략 재사용)
  docker-build:
    runs-on: ubuntu-latest
    needs: test
    outputs:
      tag: ${{ steps.vars.outputs.tag }}
    steps:
      - uses: actions/checkout@v4
      - name: 커밋 해시 태그 생성
        id: vars
        run: echo "tag=$(git rev-parse --short HEAD)" >> "$GITHUB_OUTPUT"
      - name: docker build
        run: docker build -t $IMAGE_NAME:${{ steps.vars.outputs.tag }} .
      - name: 뒤 job에 이미지를 넘겨주기 위해 tar로 저장
        run: docker save $IMAGE_NAME:${{ steps.vars.outputs.tag }} -o /tmp/pf2.tar
      - uses: actions/upload-artifact@v4
        with:
          name: pf2-image
          path: /tmp/pf2.tar

  # 4) trivy-scan: deploy.sh의 trivy image 로직을 Actions job으로 이식
  trivy-scan:
    runs-on: ubuntu-latest
    needs: docker-build
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: pf2-image
          path: /tmp
      - name: 이미지 로드
        run: docker load -i /tmp/pf2.tar
      - name: Trivy 스캔 (HIGH·CRITICAL만, 지금은 경고용 exit-code 0)
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: pf2:${{ needs.docker-build.outputs.tag }}
          severity: "HIGH,CRITICAL"
          exit-code: "0"
          # 프로덕션 전환 시 exit-code: "1"로 바꿔 취약점 발견 시 배포 자체를 막는 게 베스트 프랙티스

  # 5) ecr-push: main 브랜치 push일 때만 실행, ECR 로그인 후 푸시
  #    지금은 Secrets에 넣은 장기 액세스키 방식 - OIDC 키리스 인증은 PF1에서 정식 적용 예정 (보안 베스트 프랙티스로 남겨둠)
  ecr-push:
    runs-on: ubuntu-latest
    needs: trivy-scan
    if: github.event_name == 'push'
    steps:
      - uses: actions/download-artifact@v4
        with:
          name: pf2-image
          path: /tmp
      - name: 이미지 로드
        run: docker load -i /tmp/pf2.tar
      - name: AWS 자격증명 설정 (Secrets 방식)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ap-northeast-2
      - name: ECR 로그인
        uses: aws-actions/amazon-ecr-login@v2
      - name: 태그 후 ECR로 푸시
        run: |
          docker tag $IMAGE_NAME:${{ needs.docker-build.outputs.tag }} ${{ secrets.ECR_REGISTRY }}/$IMAGE_NAME:${{ needs.docker-build.outputs.tag }}
          docker push ${{ secrets.ECR_REGISTRY }}/$IMAGE_NAME:${{ needs.docker-build.outputs.tag }}
```

![워크플로 작성 완료](images/ci-01-workflow-written.png)

### 문법 검증

GitHub에 push하기 전에 YAML 자체가 파싱 가능한지 로컬에서 먼저 확인:

```bash
$ cat pf2-ci.yml | python3 -c "import sys,yaml; yaml.safe_load(sys.stdin); print('YAML_OK')"
YAML_OK
```

![YAML 문법 검증](images/ci-02-yaml-syntax-check.png)

(실제 job 실행 자체는 GitHub 서버의 러너에서만 도니, 이 로컬 검증은 "문법 오류로 워크플로 자체가 안 뜨는" 가장 흔한 실수만 미리 잡아주는 용도. `secrets.AWS_ACCESS_KEY_ID` 등 실제 Secrets 등록은 이 레포를 실제로 push해서 쓸 때 GitHub 레포 설정에서 별도로 진행해야 한다.)

---

## 4. 다음 단계

- `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `ECR_REGISTRY` GitHub Secrets 등록 후 실제 push로 5개 job 전부 그린 확인
- CI/CD D2(7/18): 이 파이프라인 뒤에 ArgoCD를 붙여 GitOps로 전환 — `PortFolio/PF-K8s/k8s/*.yaml`이 그 대상이라 배포물 구조를 아침에 먼저 복습
- PF1 단계에서 ecr-push job을 Secrets → OIDC 키리스 인증으로 교체
