# =============================================================================
# main.tf (루트 모듈)
# Provider(LocalStack) 설정 + VPC 모듈 호출. 실제 리소스는 모듈 안에 있고,
# 여기서는 "어떤 모듈을 어떤 값으로 부를지"만 조립한다.
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

# ---- Provider: LocalStack 로 향하게 설정 (D1 과 동일 패턴) ------------------
provider "aws" {
  region                      = var.aws_region # 리전 (변수로 주입)
  access_key                  = "test"         # LocalStack 은 아무 값이나 통과
  secret_key                  = "test"         # 실제 AWS 라면 절대 하드코딩 금지
  skip_credentials_validation = true           # 자격증명 실제 검증 건너뜀 (로컬용)
  skip_metadata_api_check     = true           # EC2 메타데이터 조회 건너뜀
  skip_requesting_account_id  = true           # 계정 ID 조회 건너뜀
  s3_use_path_style           = true           # LocalStack 호환 S3 경로 방식

  endpoints {                          # 각 서비스 API 를 LocalStack 으로 리다이렉트
    ec2      = var.localstack_endpoint # VPC/서브넷/IGW 는 EC2 API 로 처리됨
    s3       = var.localstack_endpoint
    iam      = var.localstack_endpoint
    sts      = var.localstack_endpoint
    dynamodb = var.localstack_endpoint
  }
}

# ---- VPC 모듈 호출 ---------------------------------------------------------
module "vpc" {             # "vpc" = 이 모듈 인스턴스 이름
  source = "./modules/vpc" # 로컬 경로의 모듈 사용

  name_prefix     = local.name_prefix   # locals 에서 만든 접두사 전달
  vpc_cidr        = var.vpc_cidr        # VPC 대역 전달
  public_subnets  = var.public_subnets  # 퍼블릭 서브넷 정의 전달
  private_subnets = var.private_subnets # 프라이빗 서브넷 정의 전달
  common_tags     = local.common_tags   # 공통 태그 전달
}
