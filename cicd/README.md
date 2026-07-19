# CI/CD 실습

GitHub Actions로 PF2(Go 서버)에 5-job 파이프라인을 붙이는 연습. 브랜치 전략(GitHub Flow)부터 lint→test→docker-build→trivy-scan→ecr-push까지, 실제로 그린 뜨는 것까지 확인했다.

이론 정리는 `CICD_STUDY.md`, 실습 기록(명령·출력·스크린샷)은 `CICD_PRACTICE.md`.

## 구성

- `CICD_STUDY.md` — 0장(PR·CI·CD·모노레포·워크플로/잡/스텝 등 처음부터)부터 브랜치 전략, Actions 구조, IAM 최소권한, ECR lifecycle, 디버깅 절차까지 개념 정리
- `CICD_PRACTICE.md` — 실습 기록: 브랜치 생성, 테스트 코드 작성, 워크플로 작성, AWS 자원 준비, 실전 버그 3건과 수정 과정, 최종 검증(스크린샷 포함)
- `images/` — 각 단계 스크린샷
- 실제 워크플로 파일은 여기가 아니라 레포 루트 `.github/workflows/pf2-ci.yml`에 있다 — GitHub Actions가 레포 루트의 `.github/workflows/`만 인식하기 때문(모노레포라 `paths` 필터로 PF2 변경 시에만 트리거)

## 대상 앱

- `PortFolio/PF2/main.go` + `main_test.go` — 파이프라인이 빌드·테스트·스캔·배포하는 대상
- AWS 쪽: ECR 레포 `pf2` + IAM 사용자 `pf2-ci-ecr-push`(해당 레포 push 전용, 최소권한)

## 메모

- CI 실패는 대부분 "로컬 검증과 CI 검증이 미묘하게 다름"에서 나온다 — `gofmt -l`(목록만)과 `test -z "$(gofmt -l .)"`(실패시 종료)의 차이가 실제로 한 번 걸렸다.
- `needs`는 실행 순서만 강제하고 output 접근 범위는 별개다 — 전이적으로 안 열린다.
- `defaults.run.working-directory`는 workflow-level에 걸면 checkout 안 하는 job까지 깨진다.

## 다음 — 이 시리즈의 순서

이 레포의 DevOps 파이프라인 실습은 3부작이다: **CI/CD(여기, 빌드까지)** → [`../argocd/`](../argocd/)(그 이미지를 클러스터에 자동 배포, GitOps) → [`../observability/`](../observability/)(배포된 서비스를 지표·대시보드·알람으로 관측). 순서대로 읽으면 "코드 push 한 번이 검증→배포→모니터링까지 전부 자동으로 이어지는" 전체 그림이 잡힌다.

같은 PF2 파이프라인을 다른 도구로도 만들어본 게 [`../jenkins/`](../jenkins/) — GitHub Actions(관리형)와 Jenkins(직접 호스팅)를 나란히 비교하는 곁가지 실습.
