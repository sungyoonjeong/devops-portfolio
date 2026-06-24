# =============================================================================
# d1/main.tf  —  Terraform D1: HCL 기초 + LocalStack S3 실습
# 목표: provider 설정 → 리소스 1개 생성 → 다른 리소스에서 참조(암묵적 의존성)
#       → output 으로 값 노출, 이라는 Terraform 의 가장 기본 흐름을 익힌다.
# D1 은 일부러 변수/모듈을 쓰지 않고 값을 하드코딩한다(그건 D2 에서 배운다).
# =============================================================================

terraform {                   # Terraform 자체 + 프로바이더 요구사항 선언 블록
  required_version = ">= 1.5" # 이 버전 이상의 terraform CLI 필요
  required_providers {
    aws = {                     # AWS 프로바이더를 쓰겠다고 선언
      source  = "hashicorp/aws" # 프로바이더 출처(레지스트리 경로)
      version = "~> 5.0"        # 5.x 최신(6.0 미만) 허용 — init 시 잠금
    }
  }
}

# ---- Provider: 실제 AWS 가 아니라 LocalStack 으로 향하게 설정 ----------------
provider "aws" {
  region                      = "us-east-1" # 사용할 리전 (LocalStack 기본값)
  access_key                  = "test"      # LocalStack 은 자격증명을 검사 안 함 → 아무 값
  secret_key                  = "test"      # 실제 AWS 라면 절대 코드에 하드코딩 금지
  skip_credentials_validation = true        # 자격증명 실제 검증 단계 건너뜀(로컬용)
  skip_metadata_api_check     = true        # EC2 메타데이터 서버 조회 건너뜀
  skip_requesting_account_id  = true        # AWS 계정 ID 조회 건너뜀
  s3_use_path_style           = true        # path-style(http://host:4566/버킷) 사용 — LocalStack 호환

  endpoints {                          # 각 AWS 서비스 호출을 LocalStack 주소로 돌림
    s3       = "http://localhost:4566" # S3 API → LocalStack 단일 게이트웨이 포트
    ec2      = "http://localhost:4566" # (D2 이후 사용) EC2/VPC API
    iam      = "http://localhost:4566" # IAM API
    sts      = "http://localhost:4566" # STS(임시 자격증명) API
    dynamodb = "http://localhost:4566" # DynamoDB API
  }
}

# ---- 리소스 1: S3 버킷 -----------------------------------------------------
resource "aws_s3_bucket" "practice" {  # 타입=aws_s3_bucket, 로컬이름=practice
  bucket = "terraform-practice-bucket" # 실제 생성될 버킷 이름(전역 고유해야 함)

  tags = {            # 리소스에 붙는 키-값 메타데이터
    Name = "practice" # 식별용 이름 태그
    Env  = "local"    # 로컬 실습 환경 표시
    Day  = "D1"       # 학습 일차 표식
  }
}

# ---- 리소스 2: 위 버킷의 버전 관리 활성화 (리소스 간 참조 예시) -------------
resource "aws_s3_bucket_versioning" "practice" { # 버킷의 "버전관리" 설정을 담당하는 별도 리소스
  bucket = aws_s3_bucket.practice.id             # 위 버킷의 id 참조 → 암묵적 의존성(버킷 먼저 생성)

  versioning_configuration { # 버전관리 세부 설정 블록
    status = "Enabled"       # 버전관리 켬 — 같은 키 덮어써도 이전 버전 보존
  }
}

# ---- 출력: apply 후 터미널에 보여줄 값 -------------------------------------
output "bucket_name" {                        # 출력 이름
  description = "생성된 S3 버킷 이름"                # 설명
  value       = aws_s3_bucket.practice.bucket # 버킷의 실제 이름 값을 노출
}

output "versioning_status" { # 버전관리 상태도 함께 확인용으로 출력
  description = "버킷 버전관리 상태"
  value       = aws_s3_bucket_versioning.practice.versioning_configuration[0].status # 중첩 블록 첫 요소의 status
}
