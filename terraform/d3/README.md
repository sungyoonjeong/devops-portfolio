# Terraform D3 실습 — 원격 State(S3 backend) · DynamoDB Lock · Workspace

D2(변수·모듈·VPC)에서 한 단계 더. state 를 **로컬 파일에서 S3 원격 backend 로
전환**하고, **DynamoDB 락**으로 동시 apply 충돌을 막고, **Workspace** 로 같은
코드를 dev/stg/prod 로 분기한다. 마지막으로 workspace 사양에 맞는 **EC2** 를 올린다.

> 개념은 `../TERRAFORM_STUDY.md` 9장(State)·10장(Workspace) 참고. 끝나면 D3 자가점검 Q4·Q5.

## 학습 포인트
- **닭-달걀 문제**: 원격 state 의 그릇(S3 버킷+DynamoDB)을 `bootstrap/` 으로 먼저 만든다
- `backend "s3"` 블록 — local → 원격 전환, 블록 안에선 변수 보간 불가(전부 리터럴)
- **State Lock** — DynamoDB 테이블(파티션 키 이름은 반드시 `LockID`)
- **Workspace** — `terraform.workspace` 로 환경별 사양·state 분리
- 신버전 backend 문법: `endpoints {}` + `use_path_style` (구버전 `endpoint`/`force_path_style` 아님)

## 폴더 구조
```
d3/
├── bootstrap/main.tf   # [1단계] local backend로 state용 S3 버킷 + 락 DynamoDB 생성
├── backend.tf          # [2단계] s3 backend 선언 (bootstrap 결과물을 가리킴)
├── providers.tf        # AWS provider (LocalStack, ec2 엔드포인트)
├── variables.tf        # 입력 변수
├── locals.tf           # terraform.workspace 기반 동적 값
├── main.tf             # workspace 사양에 맞는 EC2 인스턴스
├── outputs.tf          # workspace·인스턴스·state 경로 출력
└── terraform.tfvars    # 변수 값
```

## 실행 순서 (LocalStack 필요)
```bash
localstack start -d            # LocalStack 기동 (별도 터미널)

# ── 1단계: 원격 state 의 그릇 만들기 (local backend) ──
cd terraform/d3/bootstrap
terraform init
terraform apply -auto-approve  # tf-state-local 버킷 + terraform-state-lock 테이블 생성
awslocal s3 ls                 # 버킷 생겼는지 확인
awslocal dynamodb list-tables  # 락 테이블 생겼는지 확인

# ── 2단계: 상위 d3 를 원격 backend 로 초기화 ──
cd ..
terraform init                 # backend "s3" 로 state 를 S3 에 둠 (락 테이블 연결)

# ── 3단계: Workspace 로 환경 분기 ──
terraform workspace new dev    # dev 슬롯 생성·전환
terraform apply -auto-approve  # t3.micro EC2 생성, state 는 S3 의 dev 경로에
terraform workspace new prod   # prod 슬롯 생성·전환
terraform apply -auto-approve  # 같은 코드인데 t3.large 로 생성, state 는 prod 경로에

terraform output               # current_workspace, instance_type, state_location 확인
terraform workspace list       # default/dev/prod 목록 (현재 * 표시)

# ── 정리 (workspace 별로 각각) ──
terraform workspace select dev  && terraform destroy -auto-approve
terraform workspace select prod && terraform destroy -auto-approve
```

## 직접 확인해볼 것 (배움 포인트)
- `terraform init` 후 로컬에 `terraform.tfstate` 가 **안 생기는지** 확인 → S3 로 갔다는 증거
- `awslocal s3 ls s3://tf-state-local --recursive` 로 workspace 별 state 경로가 갈리는지 확인
- 터미널 2개에서 동시에 `apply` 시도 → 한쪽이 "Error acquiring the state lock" 나는지 (DynamoDB 락 작동)
- `dev` 와 `prod` 의 `terraform output instance_type` 이 t3.micro vs t3.large 로 다른지

## D1·D2 와의 차이
- D1: 단일 리소스, 하드코딩, local state
- D2: 변수·로컬·모듈·for_each (추상화), local state
- **D3: state 를 원격으로(S3+락) + 같은 코드로 여러 환경(Workspace)** ← 팀 협업의 기반
