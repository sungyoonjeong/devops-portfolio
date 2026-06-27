# Terraform 학습·실습 (D1~D5)

AWS 인프라를 코드(IaC)로 관리하는 Terraform을 5일에 걸쳐 단계적으로 쌓고,
마지막에 **하나의 통합 스택(`d5-final/`)** 으로 합친 기록이다.
LocalStack으로 로컬에서 검증하므로 실제 AWS 비용 없이 전 과정을 돌릴 수 있다.

> 개념 정리: [`TERRAFORM_STUDY.md`](./TERRAFORM_STUDY.md) (0~16장 + D1~D5 자가점검 정답·해설)

## 학습 여정 한눈에

```
d1/         단일 리소스 · 하드코딩 · local state          (HCL·provider·S3 기초)
  ↓
d2/         변수·locals·VPC 모듈·for_each                 (추상화·재사용)
  ↓
d3/         원격 state(S3 backend) + DynamoDB 락 + Workspace  (팀 협업·환경 분리)
  ↓ + bootstrap/ : state 저장소(S3·DynamoDB)를 먼저 만드는 부트스트랩
d4/         SG·IAM·EC2 모듈화 + 모듈 합성                 (실무 폴더 구조의 뼈대)
  ↓
d5-final/   ★ 통합 최종본: d2~d4 모듈 + d3 원격 backend + RDS 추가
            vpc → security_groups → iam → ec2 / rds 를 루트에서 전부 합성
```

## 각 단계 핵심

- **d1** — `main.tf` 하나로 S3 버킷 생성. `init → plan → apply → destroy` 생애주기와
  provider(LocalStack 대상) 설정, `s3_use_path_style` 같은 LocalStack 호환 옵션을 익힘.
- **d2** — 값을 `variables.tf`/`terraform.tfvars`로 빼고 `locals`로 계산값을 모음.
  VPC 한 세트를 `modules/vpc`로 모듈화하고 `for_each`로 서브넷을 N개 생성.
- **d3** — local state를 S3 backend로 전환. 닭-달걀 문제(state 저장소도 코드로 만들고 싶다)를
  `bootstrap/`을 먼저 apply해 푼다. DynamoDB 락으로 동시 apply 충돌 방지, Workspace로 환경 분리.
- **d4** — `security_groups`(rds는 CIDR 대신 **SG 참조**), `iam`(Role→Policy→Instance Profile
  **키리스** 패턴), `ec2`를 각각 모듈로. 루트에서 **"모듈 출력 → 다음 모듈 입력"** 으로 합성.
- **d5-final** — 위 모듈들을 한 스택으로 합치고 **RDS(PostgreSQL)** 모듈을 더해
  EC2(퍼블릭)·RDS(프라이빗) 2계층 구조를 완성. d3의 원격 backend까지 얹어 실무형 골격을 갖춤.

## 공통 실행법 (LocalStack 필요)

```bash
localstack start -d          # LocalStack 기동 (별도 터미널)

cd terraform/<단계>          # 예: d5-final
terraform init              # 모듈·프로바이더 초기화 (원격 backend 단계는 bootstrap 먼저)
terraform validate          # 문법·참조 검증
terraform plan              # 생성될 리소스 미리보기
terraform apply -auto-approve
terraform output            # summary 한 줄로 구성 확인
terraform destroy -auto-approve
```

> 오프라인에서 문법만 볼 때는 `terraform init -backend=false && terraform validate`.

## 버전관리 규칙 (.gitignore)

`.terraform/`(프로바이더 캐시)·`*.tfstate`(상태·비밀 포함 가능)는 커밋하지 않는다.
**`.terraform.lock.hcl`(프로바이더 잠금)만 커밋**해 팀원이 같은 버전을 쓰게 한다.

## 다음 단계 (PF-IaC, 8월)

`d5-final/`이 포트폴리오 **PF-IaC의 씨앗**이다. 여기에 Ansible(서버 설정)·Vault(DB 비밀번호
암호화)·checkov/tflint(IaC 정적 스캔 CI 연동)·ALB를 더해 실제 AWS에 1회 배포하는 게 목표.
