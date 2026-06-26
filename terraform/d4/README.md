# Terraform D4 실습 — AWS Provider 심화(SG·IAM) + 전체 인프라 모듈화

D2(vpc 모듈)·D3(원격 state·workspace)에서 한 단계 더. **보안그룹·IAM·EC2를 각각
모듈로 만들고, 루트에서 "모듈 출력 → 다음 모듈 입력"으로 엮어** 전체 인프라를
모듈만으로 조립한다. 개념서 11장(AWS Provider 심화)의 코드를 모듈 구조로 재구성한 것.

> 개념은 `../TERRAFORM_STUDY.md` 11장(VPC·SG·IAM·EC2) 참고. 끝나면 D4 자가점검 Q1~Q4.

## 학습 포인트
- **모듈 합성(composition)**: vpc → security_groups → iam → ec2 를 루트에서 데이터로 연결
  - `module.vpc.vpc_id` 를 `security_groups` 입력으로, `module.security_groups.web_sg_id` 를 `ec2` 입력으로
- **Security Group**: web(80/443 공개) + rds(web SG 출처만 5432) — CIDR 대신 **SG 참조**가 더 안전
- **IAM 3종 세트**: Role(역할) → Policy(권한, 최소권한 원칙) → Instance Profile(EC2 부착 고리)
  - EC2에 액세스키를 박지 않고 S3 읽기 → **키리스(keyless)** 패턴
- **EC2 조립**: subnet + security group + instance profile + user_data + 암호화 디스크 + lifecycle

## 폴더 구조
```
d4/
├── main.tf            # provider + S3 버킷 + 4개 모듈 조립(핵심)
├── variables.tf       # 루트 입력 변수
├── locals.tf          # name_prefix · 환경별 instance_type · common_tags
├── outputs.tf         # 각 모듈 출력을 최종 노출
├── terraform.tfvars   # dev 기본값
└── modules/
    ├── vpc/               # VPC+서브넷+IGW+RT (D2 재사용)
    ├── security_groups/   # web SG + rds SG (D4 신규)
    ├── iam/               # Role+Policy+Instance Profile (D4 신규)
    └── ec2/               # 위 셋을 연결한 인스턴스 (D4 신규)
```

## 실행 순서 (LocalStack 필요)
```bash
localstack start -d              # LocalStack 기동 (별도 터미널)

cd terraform/d4
terraform init                   # 모듈·프로바이더 초기화
terraform validate               # 문법·참조 검증
terraform plan                   # 무엇이 생기는지 미리보기 (VPC·SG·IAM·EC2)
terraform apply -auto-approve    # 실제 생성

terraform output                 # summary 한 줄로 전체 구성 확인
terraform destroy -auto-approve  # 정리
```

## 직접 확인해볼 것 (배움 포인트)
- `terraform graph` 또는 plan 순서로 **모듈 간 의존성**(vpc → sg → ec2) 이 자동 추론되는지
- rds SG 인바운드가 CIDR 가 아니라 `security_groups = [web]` 로 잡히는지 (`awslocal ec2 describe-security-groups`)
- EC2 에 `iam_instance_profile` 이 붙었는지 (`awslocal ec2 describe-instances`)
- `environment = "prod"` 로 바꾸면 instance_type 이 t3.large 로 달라지는지

## AMI 주의 (D3 에서 배운 것)
LocalStack 은 **자체 내장 AMI(`ami-760aaa0f` = Amazon Linux)만** 받는다. 임의 AMI 는
`InvalidAMIID.NotFound` 가 난다. 실제 AWS 라면 `ec2` 모듈에서 아래처럼 동적 조회가 정석:
```hcl
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]
  filter { name = "name", values = ["amzn2-ami-hvm-*-x86_64-gp2"] }
}
# ami = data.aws_ami.amazon_linux.id
```

## D1~D4 흐름
- D1: 단일 리소스, 하드코딩, local state
- D2: 변수·로컬·**vpc 모듈**·for_each (추상화)
- D3: **원격 state(S3+락) + Workspace**(환경 분리)
- **D4: SG·IAM·EC2 까지 전부 모듈화 + 모듈 합성** ← 실무 IaC 폴더 구조의 뼈대
