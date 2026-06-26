# =============================================================================
# d4/main.tf  (루트 모듈)  —  Provider(LocalStack) + 4개 모듈 조립
# D4 의 핵심: D2 에서 만든 vpc 모듈에 더해 security_groups·iam·ec2 모듈을 추가하고,
# 루트에서 "모듈 출력 → 다음 모듈 입력"으로 엮어 전체 인프라를 모듈만으로 구성한다.
# (개념서 11장: VPC+SG+IAM+EC2 / 11.5 모듈 폴더 구조 목표)
# =============================================================================

terraform {                   # Terraform 자체/프로바이더 요구사항 선언
  required_version = ">= 1.5" # 이 버전 이상의 terraform CLI 필요
  required_providers {
    aws = {                     # AWS 프로바이더 사용
      source  = "hashicorp/aws" # 레지스트리 출처
      version = "~> 5.0"        # 5.x 대 최신 (6.0 미만) 허용
    }
  }
}

# ---- Provider: LocalStack 로 향하게 설정 (d1~d3 와 동일 패턴) ----------------
provider "aws" {
  region                      = var.aws_region # 리전 (변수로 주입)
  access_key                  = "test"         # LocalStack 은 아무 값이나 통과
  secret_key                  = "test"         # 실제 AWS 라면 절대 하드코딩 금지
  skip_credentials_validation = true           # 자격증명 실제 검증 건너뜀 (로컬용)
  skip_metadata_api_check     = true           # EC2 메타데이터 조회 건너뜀
  skip_requesting_account_id  = true           # 계정 ID 조회 건너뜀
  s3_use_path_style           = true           # LocalStack 호환 S3 경로 방식

  endpoints {                          # 각 서비스 API 를 LocalStack 으로 리다이렉트
    ec2      = var.localstack_endpoint # EC2/VPC/서브넷/IGW/SG 모두 EC2 API 로 처리
    s3       = var.localstack_endpoint # 앱 데이터 버킷
    iam      = var.localstack_endpoint # IAM Role/Policy/Instance Profile
    sts      = var.localstack_endpoint # AssumeRole 등
    dynamodb = var.localstack_endpoint
  }
}

# ---- 앱 데이터용 S3 버킷 (IAM 정책이 가리킬 대상) ---------------------------
# IAM 모듈의 정책이 "이 버킷을 읽을 수 있다"고 권한을 줄 대상. 루트에서 만들어
# 그 ARN 을 iam 모듈로 넘겨 모듈 간 데이터 흐름(루트 → 모듈)을 보여준다.
resource "aws_s3_bucket" "app" {
  bucket = "${local.name_prefix}-app-data" # 예: portfolio-dev-app-data
  tags   = merge(local.common_tags, { Name = "${local.name_prefix}-app-data" })
}

# ---- ① VPC 모듈 (D2 와 동일 — 네트워크 토대) -------------------------------
module "vpc" {
  source = "./modules/vpc" # 로컬 경로 모듈

  name_prefix     = local.name_prefix   # 이름 접두사 전달
  vpc_cidr        = var.vpc_cidr        # VPC 대역
  public_subnets  = var.public_subnets  # 퍼블릭 서브넷 정의
  private_subnets = var.private_subnets # 프라이빗 서브넷 정의
  common_tags     = local.common_tags   # 공통 태그
}

# ---- ② 보안그룹 모듈 (vpc_id 를 받아 web/rds SG 생성) -----------------------
module "security_groups" {
  source = "./modules/security_groups"

  name_prefix = local.name_prefix # 이름 접두사
  vpc_id      = module.vpc.vpc_id # ★ vpc 모듈 출력을 입력으로 — 모듈 간 연결
  common_tags = local.common_tags
}

# ---- ③ IAM 모듈 (EC2 가 S3 를 읽을 Role/Policy/Instance Profile) ------------
module "iam" {
  source = "./modules/iam"

  name_prefix    = local.name_prefix     # 이름 접두사
  app_bucket_arn = aws_s3_bucket.app.arn # ★ 위에서 만든 버킷 ARN 을 정책 대상으로
  common_tags    = local.common_tags
}

# ---- ④ EC2 모듈 (SG·IAM·서브넷을 모두 연결한 인스턴스) ----------------------
module "ec2" {
  source = "./modules/ec2"

  name_prefix      = local.name_prefix                # 이름 접두사
  ami_id           = var.ami_id                       # AMI (LocalStack 내장 AMI)
  instance_type    = local.instance_type              # 환경별 인스턴스 타입(locals 계산)
  subnet_id        = module.vpc.public_subnet_ids[0]  # ★ vpc 의 첫 퍼블릭 서브넷에 배치
  web_sg_id        = module.security_groups.web_sg_id # ★ security_groups 의 web SG 연결
  instance_profile = module.iam.instance_profile_name # ★ iam 의 인스턴스 프로파일 연결
  common_tags      = local.common_tags
}
