# Terraform 완전 정복 — 5일 커리큘럼

> 목표: AWS + LocalStack 기반 IaC 실습 → PF-IaC 포트폴리오 완성  
> 기간: 6/23(D1) ~ 6/27(D5)

---

## 목차

1. [Terraform이란?](#1-terraform이란)
2. [핵심 개념 5개](#2-핵심-개념-5개)
3. [HCL 문법 완전 정리](#3-hcl-문법-완전-정리)
4. [Terraform 워크플로우 명령어](#4-terraform-워크플로우-명령어)
5. [LocalStack 환경 설정](#5-localstack-환경-설정-d1)
6. [Variables · Outputs · Locals](#6-variables--outputs--locals-d2)
7. [Data Sources](#7-data-sources)
8. [Modules](#8-modules-d2)
9. [State 관리](#9-state-관리-d3)
10. [Workspace](#10-workspace-d3)
11. [AWS Provider 심화 패턴](#11-aws-provider-심화-패턴-d4)
12. [면접 Q&A](#12-면접-qa)

---

## 1. Terraform이란?

HashiCorp가 만든 오픈소스 IaC(Infrastructure as Code) 도구.  
AWS, Azure, GCP, Kubernetes 등 200개 이상의 Provider를 지원한다.

### AWS 콘솔 클릭 vs Terraform

```
AWS 콘솔 클릭        Terraform
────────────────     ─────────────────────────────
재현 불가능          코드 그대로 재실행
협업 어려움          git으로 코드 리뷰 + 이력 추적
실수 즉시 반영       plan으로 사전 확인
환경별 일일이 반복   workspace/tfvars로 분리
```

### 선언형(Declarative) vs 명령형(Imperative)

```
명령형 (Bash 스크립트)
  "EC2 API 호출해 → 완료 기다려 → 보안그룹 연결해 → 에러면 재시도해"

선언형 (Terraform)
  "EC2 + 보안그룹이 이런 상태여야 해"
  → Terraform이 현재 상태 분석 후 필요한 작업만 알아서 실행
```

---

## 2. 핵심 개념 5개

### ① Provider

Terraform과 클라우드 API 사이의 플러그인.  
`terraform init` 실행 시 `.terraform/` 폴더에 다운로드된다.

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"   # 5.x 최신 버전 사용 (5.0 이상 6.0 미만)
    }
  }
}

provider "aws" {
  region = "ap-northeast-2"  # 서울 리전
}
```

### ② Resource

실제로 만들 인프라 단위. `resource "타입" "이름"` 형식.

```hcl
resource "aws_s3_bucket" "logs" {    # → aws_s3_bucket.logs 로 다른 곳에서 참조
  bucket = "my-logs-bucket"
}
```

- 첫 번째 인자 `"aws_s3_bucket"` = Provider가 정의한 리소스 타입
- 두 번째 인자 `"logs"` = Terraform 코드 내부 식별자 (실제 AWS 이름과 무관)

### ③ State

Terraform의 기억장치. `terraform.tfstate` 파일에 JSON으로 저장.

```
┌──────────────┐          ┌──────────────┐
│  코드(원함)  │  apply   │  실제 AWS   │
│  main.tf     │ ──────▶  │  리소스들   │
└──────────────┘          └──────────────┘
       ↑                         ↑
       │   terraform.tfstate     │
       └─────── (둘을 매핑) ─────┘

plan 실행 = 코드 vs tfstate 비교 → 차이만 변경
```

### ④ Plan / Apply 사이클

```
코드 작성
    ↓
terraform plan    ← 변경사항 미리보기. 이걸 꼭 읽는 습관!
    ↓
terraform apply   ← 실제 적용
    ↓
terraform destroy ← 삭제 (실습 후 비용 방지)
```

### ⑤ Dependency Graph (의존관계 자동 해결)

리소스 간 참조가 있으면 Terraform이 생성 순서를 자동으로 결정한다.

```hcl
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "pub" {
  vpc_id     = aws_vpc.main.id   # vpc.main이 먼저 생성됨을 Terraform이 파악
  cidr_block = "10.0.1.0/24"
}
```

---

## 3. HCL 문법 완전 정리

### 3.1 기본 타입

```hcl
# string
name = "my-resource"

# number
port = 8080

# bool
enabled = true

# list(string)
azs = ["ap-northeast-2a", "ap-northeast-2b", "ap-northeast-2c"]

# map(string)
tags = {
  Env   = "dev"
  Owner = "jsy"
}

# object (혼합 타입)
config = {
  size    = "t3.micro"
  enabled = true
}
```

### 3.2 문자열 보간(Interpolation)

```hcl
# ${} 안에 표현식
bucket = "logs-${var.env}-${var.project}"
name   = "web-${count.index}"

# 멀티라인 (heredoc)
policy = <<-EOT
  {
    "Version": "2012-10-17",
    "Statement": []
  }
EOT
```

### 3.3 조건식과 for

```hcl
# 삼항 연산자
instance_type = var.env == "prod" ? "t3.large" : "t3.micro"

# for 표현식 → list 생성
cidr_blocks = [for i in range(3) : "10.0.${i}.0/24"]
# 결과: ["10.0.0.0/24", "10.0.1.0/24", "10.0.2.0/24"]

# for 표현식 → map 생성
upper_tags = { for k, v in var.tags : k => upper(v) }

# count: 같은 리소스 여러 개
resource "aws_s3_bucket" "buckets" {
  count  = 3
  bucket = "bucket-${count.index}"   # bucket-0, bucket-1, bucket-2
}

# for_each: map/set 기반 (이름으로 참조 가능 → count보다 권장)
resource "aws_s3_bucket" "env_buckets" {
  for_each = toset(["dev", "stg", "prod"])
  bucket   = "myapp-${each.key}"
}
```

### 3.4 참조 문법

```hcl
# 다른 resource 속성 참조
vpc_id    = aws_vpc.main.id
subnet_id = aws_subnet.public[0].id              # count 사용 시 인덱스
bucket    = aws_s3_bucket.env_buckets["dev"].id  # for_each 사용 시 키

# variable 참조
instance_type = var.instance_type

# local 참조
name = local.name_prefix

# data source 참조
ami = data.aws_ami.amazon_linux.id

# module output 참조
subnet_id = module.vpc.public_subnet_ids[0]
```

### 3.5 자주 쓰는 내장 함수

```hcl
# 문자열
lower("HELLO")              # "hello"
upper("hello")              # "HELLO"
format("%s-%s", "a", "b")  # "a-b"
join("-", ["a","b","c"])    # "a-b-c"
split(",", "a,b,c")         # ["a","b","c"]
replace("foo-bar","bar","baz") # "foo-baz"
trimspace("  hello  ")      # "hello"

# 컬렉션
length(["a","b","c"])       # 3
toset(["a","b","a"])        # {"a","b"} (중복 제거)
merge({a=1},{b=2})          # {a=1, b=2}
flatten([["a"],["b","c"]])  # ["a","b","c"]
concat(["a"],["b"])         # ["a","b"]
keys({a=1,b=2})             # ["a","b"]
values({a=1,b=2})           # [1,2]

# CIDR
cidrsubnet("10.0.0.0/16", 8, 0)  # "10.0.0.0/24"
cidrsubnet("10.0.0.0/16", 8, 1)  # "10.0.1.0/24"

# 인코딩
jsonencode({key = "val"})   # '{"key":"val"}'
base64encode("hello")
```

---

## 4. Terraform 워크플로우 명령어

```bash
# 초기화 (provider 플러그인 다운로드)
terraform init

# 코드 자동 포맷팅 (커밋 전 항상 실행)
terraform fmt

# 문법 검사
terraform validate

# 변경사항 미리보기 (반드시 읽기!)
terraform plan

# 실제 적용
terraform apply
terraform apply -auto-approve    # 확인 프롬프트 생략

# 전체 삭제
terraform destroy
terraform destroy -auto-approve

# output 값 출력
terraform output
terraform output vpc_id

# state 관련
terraform show                               # state 전체 보기
terraform state list                         # 리소스 목록
terraform state show aws_s3_bucket.practice  # 특정 리소스 상세
terraform state mv old_name new_name         # 리소스 이름 변경 (코드 리팩토링 시)
terraform state rm aws_s3_bucket.old         # state에서만 제거 (실제 삭제 X)
terraform import aws_s3_bucket.b bucket-name # 기존 리소스를 state로 끌어오기
```

### plan 출력 읽는 법

```
+ 생성될 리소스
~ 수정될 리소스
- 삭제될 리소스
-/+ 삭제 후 재생성 (forces replacement ← 주의! 운영 중이면 다운타임)

예시:
# aws_s3_bucket.practice will be created
+ resource "aws_s3_bucket" "practice" {
    + bucket = "terraform-practice-bucket"
    + id     = (known after apply)          ← apply 후에 알 수 있는 값
  }

Plan: 1 to add, 0 to change, 0 to destroy.  ← 요약 줄 꼭 확인
```

---

## 5. LocalStack 환경 설정 (D1)

### LocalStack 실행

```bash
# Docker로 실행 (포트폴리오에서는 이미 사용 경험 있음)
docker run --rm -d \
  -p 4566:4566 \
  --name localstack \
  localstack/localstack

# 실행 확인
curl http://localhost:4566/_localstack/health | python3 -m json.tool
```

### Provider 설정 — LocalStack용 핵심 설정

```hcl
# main.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region                      = "us-east-1"
  access_key                  = "test"
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  endpoints {
    s3      = "http://localhost:4566"
    ec2     = "http://localhost:4566"
    iam     = "http://localhost:4566"
    sts     = "http://localhost:4566"
    vpc     = "http://localhost:4566"
    dynamodb = "http://localhost:4566"
  }
}
```

### D1 실습: 첫 S3 버킷

```hcl
resource "aws_s3_bucket" "practice" {
  bucket = "terraform-practice-bucket"

  tags = {
    Name = "practice"
    Env  = "local"
  }
}

output "bucket_name" {
  description = "생성된 버킷 이름"
  value       = aws_s3_bucket.practice.bucket
}
```

```bash
terraform init      # 초기화
terraform fmt       # 포맷
terraform validate  # 검사
terraform plan      # 미리보기 (출력 읽기!)
terraform apply     # 적용

# 생성 확인
aws --endpoint-url=http://localhost:4566 s3 ls

terraform destroy   # 삭제 (사이클 완성)
```

---

## 6. Variables · Outputs · Locals (D2)

### 6.1 Input Variables

```hcl
# variables.tf
variable "env" {
  description = "배포 환경 (dev / stg / prod)"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "stg", "prod"], var.env)
    error_message = "env는 dev, stg, prod 중 하나여야 합니다."
  }
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "subnet_count" {
  type    = number
  default = 2
}

variable "enable_nat" {
  type    = bool
  default = false
}

variable "allowed_cidrs" {
  type    = list(string)
  default = ["0.0.0.0/0"]
}
```

**값 입력 우선순위 (높을수록 우선)**

```
1. -var 플래그:          terraform apply -var="env=prod"
2. -var-file 지정:       terraform apply -var-file="prod.tfvars"
3. terraform.tfvars:     (자동 로드)
4. 환경변수:             TF_VAR_env=prod terraform apply
5. default 값:           variable 블록의 default
```

```hcl
# terraform.tfvars (자동 로드)
env          = "dev"
vpc_cidr     = "10.0.0.0/16"
subnet_count = 2

# prod.tfvars (수동 지정)
env          = "prod"
vpc_cidr     = "10.1.0.0/16"
subnet_count = 3
```

### 6.2 Output Values

```hcl
# outputs.tf
output "vpc_id" {
  description = "생성된 VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "퍼블릭 서브넷 ID 목록"
  value       = aws_subnet.public[*].id
}

output "db_password" {
  value     = var.db_password
  sensitive = true   # terraform output에서 ***로 가려짐
}
```

### 6.3 Local Values

반복되는 표현식을 변수처럼 묶을 때. 코드 중복 제거 용도.

```hcl
# locals.tf
locals {
  name_prefix = "${var.project}-${var.env}"

  common_tags = {
    Project   = var.project
    Env       = var.env
    ManagedBy = "terraform"
  }
}

# 사용 예
resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr
  tags       = merge(local.common_tags, { Name = "${local.name_prefix}-vpc" })
}
```

---

## 7. Data Sources

이미 존재하는 리소스를 **조회**할 때 (생성 X). `data "타입" "이름"` 형식.

```hcl
# 최신 Amazon Linux 2 AMI 자동 조회
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

# 사용 가능한 AZ 목록 조회
data "aws_availability_zones" "available" {
  state = "available"
}

# 기존 VPC 가져오기 (이미 만들어진 VPC를 코드에서 참조)
data "aws_vpc" "existing" {
  id = "vpc-0123456789abcdef0"
}

# 사용 예
resource "aws_instance" "web" {
  ami               = data.aws_ami.amazon_linux.id
  instance_type     = "t3.micro"
  availability_zone = data.aws_availability_zones.available.names[0]
}
```

---

## 8. Modules (D2)

### 모듈이란?

`.tf` 파일들이 들어있는 폴더 하나 = 모듈 하나.  
재사용 가능한 인프라 블록. "VPC 모듈", "EC2 모듈" 처럼 나눈다.

```
terraform/
├── main.tf          ← root module (호출하는 쪽)
├── variables.tf
├── outputs.tf
├── locals.tf
└── modules/
    ├── vpc/         ← VPC 모듈
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    └── ec2/         ← EC2 모듈
        ├── main.tf
        ├── variables.tf
        └── outputs.tf
```

### 모듈 작성 (modules/vpc/)

```hcl
# modules/vpc/variables.tf
variable "cidr_block"    { type = string }
variable "env"           { type = string }
variable "subnet_count"  { type = number; default = 2 }

# modules/vpc/main.tf
data "aws_availability_zones" "az" { state = "available" }

resource "aws_vpc" "this" {
  cidr_block           = var.cidr_block
  enable_dns_hostnames = true
  tags = { Name = "${var.env}-vpc" }
}

resource "aws_subnet" "public" {
  count                   = var.subnet_count
  vpc_id                  = aws_vpc.this.id
  cidr_block              = cidrsubnet(var.cidr_block, 8, count.index)
  availability_zone       = data.aws_availability_zones.az.names[count.index]
  map_public_ip_on_launch = true
  tags = { Name = "${var.env}-public-${count.index}" }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.this.id
  tags   = { Name = "${var.env}-igw" }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.this.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
}

resource "aws_route_table_association" "public" {
  count          = var.subnet_count
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

# modules/vpc/outputs.tf
output "vpc_id"            { value = aws_vpc.this.id }
output "public_subnet_ids" { value = aws_subnet.public[*].id }
```

### 모듈 호출 (root main.tf)

```hcl
module "vpc" {
  source       = "./modules/vpc"
  cidr_block   = var.vpc_cidr
  env          = var.env
  subnet_count = var.subnet_count
}

# 모듈 output 참조: module.<모듈이름>.<output이름>
resource "aws_instance" "web" {
  subnet_id = module.vpc.public_subnet_ids[0]
}

output "vpc_id" {
  value = module.vpc.vpc_id
}
```

---

## 9. State 관리 (D3)

### 9.1 State 파일 구조

```
terraform.tfstate 파일 내용 (JSON):
{
  "version": 4,
  "resources": [
    {
      "type": "aws_s3_bucket",
      "name": "practice",
      "instances": [
        {
          "attributes": {
            "id": "terraform-practice-bucket",
            "bucket": "terraform-practice-bucket",
            ...
          }
        }
      ]
    }
  ]
}
```

### 9.2 Remote State — S3 Backend

팀 협업 시 로컬 tfstate 파일은 충돌 위험. S3에 저장.

```hcl
terraform {
  backend "s3" {
    bucket         = "my-terraform-state-bucket"
    key            = "dev/vpc/terraform.tfstate"   # 환경/서비스/파일명
    region         = "ap-northeast-2"
    dynamodb_table = "terraform-state-lock"         # 동시 apply 방지 락
    encrypt        = true
  }
}
```

**LocalStack으로 Remote State 테스트:**

```hcl
terraform {
  backend "s3" {
    bucket                      = "tf-state-local"
    key                         = "dev/terraform.tfstate"
    region                      = "us-east-1"
    access_key                  = "test"
    secret_key                  = "test"
    skip_credentials_validation = true
    skip_metadata_api_check     = true
    force_path_style            = true
    endpoint                    = "http://localhost:4566"
  }
}
```

```bash
# S3 버킷 먼저 생성 후 backend 설정
aws --endpoint-url=http://localhost:4566 s3 mb s3://tf-state-local
terraform init -reconfigure
```

### 9.3 State 명령어

```bash
terraform state list                                # 리소스 목록
terraform state show aws_vpc.main                   # 특정 리소스 상세 보기
terraform state mv aws_s3_bucket.old aws_s3_bucket.new  # 이름 변경 (코드 리팩토링 시)
terraform state rm aws_s3_bucket.practice           # state에서만 제거 (실제 리소스는 남음)
terraform import aws_s3_bucket.practice my-bucket  # 기존 리소스 → state 편입
```

### 9.4 State 충돌 시나리오

```
팀원 A: terraform apply 실행 중...
팀원 B: 동시에 terraform apply 실행 → state 파일 덮어써 버림 → 인프라 불일치

해결: DynamoDB 락 (dynamodb_table 설정)
  → apply 시작 시 DynamoDB에 락 기록
  → 다른 사람이 apply하면 락 감지 → 대기
  → 완료 후 락 해제
```

---

## 10. Workspace (D3)

같은 코드로 dev / stg / prod 환경을 분리하는 방법.  
각 workspace는 독립된 tfstate를 가진다.

```bash
terraform workspace new dev      # 생성
terraform workspace new stg
terraform workspace new prod
terraform workspace list         # 목록 (현재 workspace에 * 표시)
terraform workspace select prod  # 전환
terraform workspace show         # 현재 workspace 확인
```

**코드에서 workspace 이름 참조:**

```hcl
locals {
  env = terraform.workspace   # "dev", "stg", "prod" 등

  instance_type = {
    dev  = "t3.micro"
    stg  = "t3.small"
    prod = "t3.large"
  }
}

resource "aws_s3_bucket" "app" {
  bucket = "myapp-${local.env}-data"
}

resource "aws_instance" "web" {
  instance_type = local.instance_type[local.env]
}
```

**State 파일 위치:**

```
로컬: terraform.tfstate.d/dev/terraform.tfstate
      terraform.tfstate.d/prod/terraform.tfstate
S3:   s3://bucket/dev/terraform.tfstate
      s3://bucket/prod/terraform.tfstate   (key 경로에 workspace 이름 포함)
```

---

## 11. AWS Provider 심화 패턴 (D4)

### 11.1 전체 네트워크 (VPC + Subnet + IGW + Route Table)

```hcl
data "aws_availability_zones" "az" { state = "available" }

# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true
  tags = { Name = "${local.name_prefix}-vpc" }
}

# 퍼블릭 서브넷 (2개)
resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.${count.index}.0/24"
  availability_zone       = data.aws_availability_zones.az.names[count.index]
  map_public_ip_on_launch = true
  tags = { Name = "${local.name_prefix}-public-${count.index}" }
}

# 프라이빗 서브넷 (2개)
resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.${count.index + 10}.0/24"
  availability_zone = data.aws_availability_zones.az.names[count.index]
  tags = { Name = "${local.name_prefix}-private-${count.index}" }
}

# Internet Gateway
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "${local.name_prefix}-igw" }
}

# Route Table (퍼블릭용)
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
  tags = { Name = "${local.name_prefix}-rt-public" }
}

resource "aws_route_table_association" "public" {
  count          = 2
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}
```

### 11.2 Security Group

```hcl
resource "aws_security_group" "web" {
  name        = "${local.name_prefix}-web-sg"
  description = "Web server security group"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP"
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"   # 모든 프로토콜
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "${local.name_prefix}-web-sg" }
}

# 서비스 간 SG 참조 (CIDR 대신 SG ID 사용 → 더 안전)
resource "aws_security_group" "rds" {
  name   = "${local.name_prefix}-rds-sg"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id]   # web SG에서만 허용
  }
}
```

### 11.3 IAM Role + Policy

```hcl
# EC2가 S3에 읽기 권한
resource "aws_iam_role" "ec2_role" {
  name = "${local.name_prefix}-ec2-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "s3_read" {
  name = "s3-read-policy"
  role = aws_iam_role.ec2_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "s3:GetObject",
        "s3:ListBucket"
      ]
      Resource = [
        "arn:aws:s3:::${aws_s3_bucket.app.bucket}",
        "arn:aws:s3:::${aws_s3_bucket.app.bucket}/*"
      ]
    }]
  })
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "${local.name_prefix}-ec2-profile"
  role = aws_iam_role.ec2_role.name
}
```

### 11.4 EC2 (완전한 예시)

```hcl
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

resource "aws_instance" "web" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = var.env == "prod" ? "t3.large" : "t3.micro"
  subnet_id              = aws_subnet.public[0].id
  vpc_security_group_ids = [aws_security_group.web.id]
  iam_instance_profile   = aws_iam_instance_profile.ec2_profile.name

  user_data = <<-EOF
    #!/bin/bash
    yum update -y
    yum install -y docker
    systemctl start docker
    systemctl enable docker
  EOF

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
    encrypted   = true
  }

  tags = merge(local.common_tags, { Name = "${local.name_prefix}-web" })

  lifecycle {
    create_before_destroy = true   # 교체 시 새 것 먼저 만들고 삭제
  }
}
```

### 11.5 PF-IaC 최종 폴더 구조 (D5 목표)

```
terraform/
├── main.tf              # provider + module 호출
├── variables.tf         # 모든 변수 선언
├── outputs.tf           # 최종 output
├── locals.tf            # 공통 태그·이름 prefix
├── terraform.tfvars     # dev 기본값
├── prod.tfvars          # prod 값
├── versions.tf          # required_providers (별도 파일로 분리하는 컨벤션)
└── modules/
    ├── vpc/
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    ├── ec2/
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    └── security_groups/
        ├── main.tf
        ├── variables.tf
        └── outputs.tf
```

---

## 12. 면접 Q&A

**Q. Terraform State란 무엇인가요?**

Terraform이 실제 인프라와 코드 사이를 매핑하는 파일입니다. `terraform plan` 시 코드(원하는 상태)와 state(현재 상태)를 비교해 변경이 필요한 부분만 계산합니다. 팀 환경에서는 S3 backend + DynamoDB 락으로 동시 apply 충돌을 방지합니다.

**Q. IaC를 써야 하는 이유는?**

인프라를 코드로 관리하면 git을 통한 변경 이력 추적, 코드 리뷰로 실수 사전 방지, 동일 환경 반복 재현이 가능합니다. 특히 dev/stg/prod 환경을 동일하게 유지하거나 장애 시 인프라를 빠르게 재구성할 때 효과적입니다.

**Q. terraform plan에서 무엇을 확인하나요?**

생성(+) / 수정(~) / 삭제(-) 대상 리소스와 변경 속성을 확인합니다. 특히 `forces replacement` 표시가 있으면 삭제 후 재생성이므로 운영 환경에서는 다운타임 영향을 검토해야 합니다. "Plan: X to add, Y to change, Z to destroy" 요약도 반드시 확인합니다.

**Q. Module을 왜 사용하나요?**

반복되는 인프라 패턴(VPC+서브넷+IGW 조합 등)을 재사용 가능한 단위로 캡슐화합니다. dev/stg/prod 환경에서 같은 모듈을 다른 변수로 호출해 일관성을 유지하고, 변경 시 모듈만 수정하면 모든 환경에 반영됩니다.

**Q. Terraform과 CloudFormation 차이는?**

CloudFormation은 AWS 전용이고 YAML/JSON으로 작성합니다. Terraform은 HCL이 더 직관적이고, 단일 코드베이스로 AWS + Kubernetes + 모니터링 인프라까지 함께 관리할 수 있습니다. 단, CloudFormation은 AWS 서비스와 더 깊이 통합되어 있고 State 관리가 AWS에서 자동으로 처리됩니다.

**Q. count vs for_each 언제 각각 사용하나요?**

`count`는 순서가 있는 리스트에 적합하지만, 중간 요소가 삭제되면 인덱스가 밀려 이후 리소스가 재생성됩니다. `for_each`는 map/set 기반으로 각 리소스가 고유한 키로 식별돼 중간 삭제 시에도 다른 리소스에 영향이 없습니다. 실무에서는 `for_each` 권장.

---

## 일차별 실습 체크포인트

```
D1 (6/23): provider + S3 버킷 → init/plan/apply/destroy 사이클 완성
D2 (6/24): variables.tf + outputs.tf + modules/vpc/ → VPC+Subnet IaC
D3 (6/25): S3 Remote State + DynamoDB Lock + Workspace → EC2 프로비저닝
D4 (6/26): IAM Role + Security Group + EC2 → 전체 인프라 모듈화
D5 (6/27): 위 모두 통합 + terraform/ 폴더 최종 정리 + README + 커밋
```
