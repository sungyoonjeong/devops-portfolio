# 7/17 — CI/CD D1 실습: 브랜치 전략 + PF2 GitHub Actions CI

목표: PF2(Go 서버) 레포에 GitHub Actions 파이프라인을 처음부터 붙인다. 개념(브랜치 전략, job 구조)은 [CICD_STUDY.md](CICD_STUDY.md) 참조, 여기는 실제로 실행한 명령과 결과 기록.

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

## 4. ECR 레포지토리 + 최소권한 IAM 사용자 생성

7/17에는 워크플로 파일만 작성해두고 실제 Secrets 등록·그린 실행 검증은 미완이었다. 여기서부터 이어서, `ecr-push` job이 실제로 동작하도록 AWS 쪽 자원을 준비한다.

**원칙: 이 WSL에 이미 연결된 AWS CLI 계정(`admin-sy`)은 관리자 권한이라 CI에 그대로 못 쓴다.** GitHub Secrets는 레포 관리자면 누구나 값을 재등록(덮어쓰기)할 수 있고, 워크플로 로그에 실수로라도 노출되면 그 즉시 계정 전체가 뚫린다. 그래서 **ECR push 한 가지 동작만 가능한 전용 IAM 사용자**를 새로 만들어 그 키만 등록한다 — 최소 권한 원칙(Principle of Least Privilege).

### 4-1. ECR 레포지토리 생성 + 프리티어 보호용 lifecycle policy

```bash
$ aws ecr create-repository --repository-name pf2 --region ap-northeast-2 \
    --image-scanning-configuration scanOnPush=true --output table
--------------------------------------------------------------------------
|                             CreateRepository                            |
+--------------------------------------------------------------------------+
||                              repository                                ||
|+---------------------------------------+--------------------------------+|
||  repositoryArn   |  arn:aws:ecr:ap-northeast-2:759869090525:repository/pf2  ||
||  repositoryName  |  pf2                                                 ||
||  repositoryUri   |  759869090525.dkr.ecr.ap-northeast-2.amazonaws.com/pf2 ||
```

`--image-scanning-configuration scanOnPush=true`: 이미지가 push될 때마다 ECR이 자체적으로 취약점 스캔을 한 번 더 돌린다(Basic scanning은 무료) — Trivy(CI 단계)와 별개로 레지스트리 쪽에서도 상시 스캔되는 이중 방어.

![ECR 레포 생성](images/ecr-01-repo-create.png)

이미지를 계속 쌓아두면 무료 한도를 넘길 수 있어, **최신 5개만 남기고 자동 만료**시키는 lifecycle policy를 바로 걸었다:

```bash
$ aws ecr put-lifecycle-policy --repository-name pf2 --region ap-northeast-2 \
    --lifecycle-policy-text '{"rules":[{"rulePriority":1,
      "description":"free tier storage guard - keep last 5 images only",
      "selection":{"tagStatus":"any","countType":"imageCountMoreThan","countNumber":5},
      "action":{"type":"expire"}}]}'
```

![lifecycle policy 등록](images/ecr-02-lifecycle-policy.png)

### 4-2. IAM 사용자 생성 — ECR push 전용, admin 키 사용 안 함

```bash
$ aws iam create-user --user-name pf2-ci-ecr-push --output table
```

![IAM 사용자 생성](images/iam-01-user-create.png)

이 사용자에게 붙일 정책은 **딱 두 가지 권한만** 준다: 인증 토큰 발급(`GetAuthorizationToken`, 이 액션은 리소스를 특정 레포로 못 좁히는 AWS 구조상 제약이라 `Resource: "*"`가 불가피)과, **`pf2` 레포 ARN 하나에만 스코프**된 이미지 업로드 4종:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ECRAuthToken",
      "Effect": "Allow",
      "Action": "ecr:GetAuthorizationToken",
      "Resource": "*"
    },
    {
      "Sid": "ECRPushPF2Only",
      "Effect": "Allow",
      "Action": [
        "ecr:BatchCheckLayerAvailability",
        "ecr:PutImage",
        "ecr:InitiateLayerUpload",
        "ecr:UploadLayerPart",
        "ecr:CompleteLayerUpload"
      ],
      "Resource": "arn:aws:ecr:ap-northeast-2:759869090525:repository/pf2"
    }
  ]
}
```

![IAM 정책 JSON 작성](images/iam-02-policy-json.png)

```bash
$ aws iam put-user-policy --user-name pf2-ci-ecr-push \
    --policy-name pf2-ecr-push-only --policy-document file:///tmp/pf2-ecr-push-policy.json
$ aws iam list-user-policies --user-name pf2-ci-ecr-push --output table
```

![정책 연결 확인](images/iam-03-policy-attached.png)

이 사용자는 **읽기(pull)도, 다른 레포 접근도, ECR 외 다른 서비스도 전부 불가능** — 이 키가 통째로 유출돼도 공격자가 할 수 있는 일은 `pf2` 레포에 이미지 하나 올리는 것뿐이다. GitHub Actions 로그가 공개(public repo)라는 걸 감안하면 이 정도 격리가 최소 기준이라고 판단했다.

### 4-3. 액세스 키 발급 — 시크릿 값은 화면에 절대 노출하지 않는다

```bash
$ aws iam create-access-key --user-name pf2-ci-ecr-push --output json > /tmp/pf2-ci-key.json
$ chmod 600 /tmp/pf2-ci-key.json
$ python3 -c "
import json
d = json.load(open('/tmp/pf2-ci-key.json'))['AccessKey']
print('AccessKeyId  :', d['AccessKeyId'])
print('SecretAccessKey: [REDACTED - /tmp/pf2-ci-key.json, chmod 600, GitHub Secrets 등록 후 즉시 삭제 예정]')
"
AccessKeyId  : AKIA3B252FLOUUTPE6RX
SecretAccessKey: [REDACTED - /tmp/pf2-ci-key.json, chmod 600, GitHub Secrets 등록 후 즉시 삭제 예정]
```

![액세스 키 발급 (시크릿 값 redacted)](images/iam-04-accesskey-redacted.png)

`AccessKeyId`는 그 자체로는 민감정보가 아니라(짝인 `SecretAccessKey`가 없으면 아무 것도 못 함) 화면에 남겨도 되지만, `SecretAccessKey`는 절대 터미널에 echo하거나 스크린샷에 남기지 않았다 — 파일에 `chmod 600`으로 저장해두고 다음 단계에서 바로 GitHub Secrets로 옮긴 뒤 로컬에서 완전히 삭제(`shred -u`)했다.

---

## 5. GitHub Secrets 등록

```bash
$ AWS_ACCESS_KEY_ID=$(python3 -c "import json;print(json.load(open('/tmp/pf2-ci-key.json'))['AccessKey']['AccessKeyId'])")
$ AWS_SECRET_ACCESS_KEY=$(python3 -c "import json;print(json.load(open('/tmp/pf2-ci-key.json'))['AccessKey']['SecretAccessKey'])")
$ gh secret set AWS_ACCESS_KEY_ID --repo sungyoonjeong/devops-portfolio --body "$AWS_ACCESS_KEY_ID"
$ gh secret set AWS_SECRET_ACCESS_KEY --repo sungyoonjeong/devops-portfolio --body "$AWS_SECRET_ACCESS_KEY"
$ gh secret set ECR_REGISTRY --repo sungyoonjeong/devops-portfolio --body "759869090525.dkr.ecr.ap-northeast-2.amazonaws.com"
$ unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY
$ shred -u /tmp/pf2-ci-key.json
$ gh secret list --repo sungyoonjeong/devops-portfolio
AWS_ACCESS_KEY_ID      2026-07-19T...
AWS_SECRET_ACCESS_KEY  2026-07-19T...
ECR_REGISTRY            2026-07-19T...
```

![GitHub Secrets 등록 확인](images/secrets-01-registered.png)

**값을 화면에 노출하지 않는 방법**: `gh secret set`은 값을 표준입력이 아니라 `--body` 인자로 받는데, 셸 변수(`"$AWS_ACCESS_KEY_ID"`)로 넘기면 그 변수 자체를 별도로 `echo`하지 않는 한 터미널 화면·스크린샷 어디에도 실제 값이 찍히지 않는다. `gh secret list`도 이름·등록일만 보여줄 뿐 값은 절대 되돌려주지 않는다(GitHub API 자체가 write-only로 설계됨) — 그래서 이 커밋된 스크린샷 어디에도 실제 키 값은 없다.

---

## 6. workflow_dispatch 수동 트리거 추가

Secrets 등록 후 재검증할 때마다 코드를 억지로 바꿔 push하지 않아도 되도록, 워크플로에 수동 실행 트리거를 추가했다:

```yaml
on:
  push:
    branches: [main]
    paths: ["PortFolio/PF2/**", ".github/workflows/pf2-ci.yml"]
  pull_request:
    branches: [main]
    paths: ["PortFolio/PF2/**"]
  workflow_dispatch:  # 수동 트리거 - Secrets 등록 후 재검증 편의용
```

![workflow_dispatch 추가](images/ci-03-workflow-dispatch-added.png)

이 브랜치도 GitHub Flow대로 `feature/ci-manual-trigger` → PR 없이 바로 `--no-ff` 머지(1인 프로젝트라 리뷰어가 없어 PR을 안 거침, 리뷰어가 있다면 여기서 PR을 열어야 한다) → `main` push로 반영했다.

```bash
$ gh workflow run pf2-ci.yml --repo sungyoonjeong/devops-portfolio --ref main
$ gh run watch <run-id> --repo sungyoonjeong/devops-portfolio --exit-status
```

---

## 7. 실전 디버깅 — 그린 뜨기까지 만난 버그 3개

"작성한 워크플로가 처음부터 한 번에 통과"하는 경우는 거의 없다. 실제로 이 파이프라인도 3번 실패하고서야 전부 통과했다 — 각각 원인이 달라서 그대로 기록해둔다. GitHub Actions 로그를 실제로 읽고 원인을 좁혀나가는 과정 자체가 CI/CD 실무의 핵심이라, 결과만 보여주지 않고 디버깅 흐름을 그대로 남긴다.

### 버그 1 — `gofmt` 미적용 (lint 실패)

**증상**: `workflow_dispatch`로 처음 실행하자 `lint` job이 바로 실패.

```bash
$ gh run view <run-id> --repo sungyoonjeong/devops-portfolio
X lint in ...
  X gofmt 검사 (포맷 안 맞는 파일이 있으면 실패)
```

**원인**: 어제(7/17) 로컬 검증 때 `gofmt -l .`(목록만 출력, 종료코드는 항상 0)만 썼고 `-w`(실제로 파일을 고치는 옵션)는 안 걸었다. 그래서 `main_test.go`는 스페이스 들여쓰기 그대로 커밋됐는데, CI의 lint job은 `test -z "$(gofmt -l .)"`로 **"포맷 안 맞는 파일이 하나라도 나오면 실패"**하게 짜여 있어서 정직하게 걸러졌다. 로컬 검증 스크립트와 CI 검증 스크립트가 미묘하게 다르면 이렇게 "로컬은 됐는데 CI는 실패"하는 흔한 사고가 난다.

**수정**:

```bash
$ docker run --rm -v "$PWD/PortFolio/PF2":/app -w /app golang:1.22-alpine gofmt -w .
$ docker run --rm -v "$PWD/PortFolio/PF2":/app -w /app golang:1.22-alpine gofmt -l .
# (출력 없음 = 통과)
```

![gofmt 버그 발견·수정](images/debug-01-gofmt-bug-found-fixed.png)

`fix(pf2): main_test.go gofmt 재포맷` 커밋으로 반영.

### 버그 2 — `defaults.working-directory`가 워크플로 전체에 걸려 있던 문제 (trivy-scan·ecr-push 실행 불가)

**증상**: 재실행하자 `lint`·`test`·`docker-build`는 통과했는데 `trivy-scan`이 바로 죽었다.

```
X An error occurred trying to start process '/usr/bin/bash' with working directory
  '/home/runner/work/devops-portfolio/devops-portfolio/PortFolio/PF2'. No such file or directory
```

**원인**: 워크플로 최상단에 걸어둔 `defaults: run: working-directory: PortFolio/PF2`는 **워크플로 안의 모든 job, 모든 step에 상속**된다. 그런데 `trivy-scan`·`ecr-push` job은 소스 체크아웃을 아예 안 한다 — `docker-build`가 만든 이미지 tar만 아티팩트로 받아서 쓰기 때문이다. 그래서 이 두 job의 러너에는 `PortFolio/PF2`라는 디렉토리 자체가 존재하지 않고, 셸이 그 경로로 `cd`하려다 못 열어서 아예 뜨지도 못하고 죽었다.

**교훈**: workflow-level `defaults`는 "이 워크플로의 모든 job이 공통으로 체크아웃한 소스를 다룬다"는 전제가 있을 때만 안전하다. job마다 체크아웃 여부가 다르면 job-level로 내려야 한다.

**수정**: workflow-level `defaults` 제거 → `lint`/`test`/`docker-build`(checkout 있는 job) 3개에만 각각 job-level `defaults`를 걸었다.

```yaml
  lint:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: PortFolio/PF2   # 이 job에만 적용
    steps:
      - uses: actions/checkout@v4
      ...

  # trivy-scan, ecr-push는 checkout이 없으므로 working-directory 자체를 설정하지 않음
```

![defaults 범위를 job 단위로 이동](images/debug-02-workdir-scope-fix.png)

`fix(pf2-ci): defaults.working-directory를 job 단위로 이동` 커밋으로 반영.

실제 `push` 이벤트로 `ecr-push` job까지 검증하려면 `PortFolio/PF2/**` 경로에 진짜 변경이 있어야 해서, `main.go`에 검증 완료 주석 한 줄을 추가하고 다시 push했다.

### 버그 3 — `needs` 전이(transitive) 접근 불가로 ECR 태그가 빈 문자열이 됨

**증상**: `lint`~`trivy-scan`까지 전부 성공했는데 `ecr-push`만 실패.

```
Error parsing reference: "pf2:" is not a valid repository/tag: invalid reference format
```

이미지 이름이 `pf2:14e1f58`가 아니라 `pf2:`(태그가 빈 문자열)로 해석됐다.

**원인**: `ecr-push` job은 `needs: trivy-scan`만 선언돼 있었다. `${{ needs.docker-build.outputs.tag }}`로 커밋 해시 태그를 참조하는 코드가 있었지만, **GitHub Actions는 `needs`가 직접 나열된 job의 output만 볼 수 있다 — 전이적으로(trivy-scan이 docker-build를 needs하니까 ecr-push도 자동으로 볼 수 있겠지, 라는) 접근은 지원하지 않는다.** `trivy-scan`은 `needs: docker-build`라 `needs.docker-build.outputs.tag`를 볼 수 있었지만(그래서 trivy-scan은 통과했다), `ecr-push`는 `docker-build`를 직접 `needs`하지 않았으므로 그 값이 애초에 정의되지 않은 컨텍스트였고, 빈 문자열로 평가됐다.

**수정**: `ecr-push`의 `needs`에 `docker-build`를 추가(실행 순서 자체는 `trivy-scan`이 이미 `docker-build` 뒤에 오므로 안 바뀐다 — 순전히 output 접근 권한을 위한 추가):

```yaml
  ecr-push:
    runs-on: ubuntu-latest
    needs: [docker-build, trivy-scan]   # trivy-scan만으론 docker-build.outputs 접근 불가
```

```python
# 인코딩 사고를 반복하지 않기 위해 readlines() + chr(10) 방식으로 안전하게 패치
path = ".github/workflows/pf2-ci.yml"
with open(path, encoding="utf-8") as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if line.strip() == "needs: trivy-scan":
        lines[i] = "    needs: [docker-build, trivy-scan]" + chr(10)
with open(path, "w", encoding="utf-8") as f:
    f.writelines(lines)
```

![needs 전이 접근 불가 발견](images/debug-03-needs-transitive-bug.png)
![수정 적용 확인](images/debug-03b-needs-fix-applied.png)

`fix(pf2-ci): ecr-push job이 needs.docker-build.outputs.tag에 접근 못하던 버그 수정` 커밋으로 반영.

---

## 8. 최종 검증 — 5-job 전부 그린 + 실제 ECR 이미지 확인

버그 3개를 전부 고친 뒤, `main.go` 주석 커밋(push 이벤트 유발용)을 다시 push해 **실제 `push` 이벤트로** 파이프라인을 처음부터 끝까지 돌렸다(주의: `workflow_dispatch`로 돌리면 `ecr-push`의 `if: github.event_name == 'push'` 조건에 안 걸려 스킵되므로, 이 job까지 검증하려면 반드시 진짜 push가 필요하다).

```bash
$ gh run watch 29677091005 --repo sungyoonjeong/devops-portfolio --exit-status
✓ lint in ...
✓ test in ...
✓ docker-build in 23s
✓ trivy-scan in 21s
✓ ecr-push in 19s
  ✓ AWS 자격증명 설정 (Secrets 방식)
  ✓ ECR 로그인
  ✓ 태그 후 ECR로 푸시
✓ Run PF2 CI (29677091005) completed with 'success'
```

![5개 job 전부 그린](images/final-01-5jobs-green.png)

ECR에 이미지가 실제로 올라갔는지 AWS 쪽에서 직접 확인:

```bash
$ aws ecr list-images --repository-name pf2 --region ap-northeast-2 --output table
-----------------------------------------------------------------------------------
|                                   ListImages                                    |
+-----------------------------------------------------------------------------------+
|  imageDigest: sha256:c6bb5d52b5f60f556281f4be61952a208f8ba0dc61cd5ca7e9cb2083f8519eba9  |  imageTag: 14e1f58  |
```

![ECR 이미지 실제 확인](images/final-02-ecr-image-verified.png)

`imageTag: 14e1f58`가 그 push를 만든 머지 커밋의 짧은 해시와 정확히 일치 — `deploy.sh`(로컬 배포)와 `pf2-ci.yml`(CI 배포) 양쪽에서 동일한 "커밋 해시 = 이미지 태그" 규칙이 실제로 지켜지는 것까지 확인됐다.

---

## 9. 다음 단계

- CI/CD D2: 이 파이프라인 뒤에 ArgoCD를 붙여 GitOps로 전환 — `PortFolio/PF-K8s/k8s/*.yaml`이 그 대상이라 배포물 구조를 먼저 복습
- PF1 단계에서 `ecr-push` job을 Secrets(장기 액세스키) → OIDC 키리스 인증으로 교체 (지금의 `pf2-ci-ecr-push` IAM 사용자도 그때 삭제하고, GitHub OIDC 신뢰관계를 신뢰하는 IAM 역할(Role)로 대체)
- ECR lifecycle policy(최근 5개 유지)가 실제로 오래된 이미지를 정리하는지, push를 몇 번 더 하면서 확인
