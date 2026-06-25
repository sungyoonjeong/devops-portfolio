# =============================================================================
# d3/backend.tf  —  원격 State backend(S3 + DynamoDB 락) 설정
# D3 의 핵심: local backend(로컬 terraform.tfstate) → s3 backend 전환.
# 이 블록이 있으면 terraform 은 state 를 로컬 파일이 아니라 S3 에 두고,
# apply 시 DynamoDB 에 락을 걸어 동시 수정 충돌을 막는다.
#
# ※ 전제: 이 backend 가 가리키는 버킷/테이블이 "먼저" 존재해야 한다.
#   → 그래서 bootstrap/ 을 먼저 apply 한 뒤, 여기서 `terraform init` 한다.
# ※ backend 블록 안에서는 변수(var.*) 보간이 불가능 → 전부 리터럴로 적는다.
# =============================================================================

terraform {
  required_version = ">= 1.6" # endpoints{} backend 문법은 Terraform 1.6+ 부터
  required_providers {
    aws = {
      source  = "hashicorp/aws" # AWS 프로바이더
      version = "~> 5.0"        # 5.x 고정
    }
  }

  backend "s3" {
    bucket = "tf-state-local"       # bootstrap 이 만든 state 버킷 (이름 일치 필수)
    key    = "d3/terraform.tfstate" # 버킷 안에서 이 state 의 경로/파일명
    region = "us-east-1"            # 리전

    # ↓ LocalStack 을 backend 로 쓰기 위한 설정 (실제 AWS 면 이 6줄은 불필요)
    access_key                  = "test" # LocalStack 자격증명(아무 값)
    secret_key                  = "test"
    skip_credentials_validation = true # 자격증명 검증 건너뜀
    skip_metadata_api_check     = true # 메타데이터 조회 건너뜀
    skip_requesting_account_id  = true # 계정 ID 조회 건너뜀
    use_path_style              = true # path-style (LocalStack 호환)

    # ★ 신버전 문법: 서비스별 엔드포인트를 endpoints 맵으로 지정
    #   (study 9.2 의 endpoint="..."/force_path_style 은 구버전 — 5.x 에선 아래 형태)
    endpoints = {
      s3       = "http://localhost:4566" # state 읽기/쓰기용 S3
      dynamodb = "http://localhost:4566" # 락 기록용 DynamoDB
    }

    dynamodb_table = "terraform-state-lock" # 락 테이블 (bootstrap 이 만든 것)
    encrypt        = true                   # S3 에 저장되는 state 를 서버측 암호화
  }
}
