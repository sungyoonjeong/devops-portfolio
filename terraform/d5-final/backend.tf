# =============================================================================
# d5-final/backend.tf  —  Terraform 요구사항 + 원격 State backend(S3 + DynamoDB 락)
# D3 에서 배운 원격 backend 를 통합본에 그대로 적용한다. state 를 로컬이 아니라 S3 에
# 두고, apply 시 DynamoDB 로 락을 걸어 동시 수정 충돌을 막는다(팀 협업 표준).
#
# ※ 전제: 이 backend 가 가리키는 버킷/락 테이블이 "먼저" 있어야 한다.
#   → d3/bootstrap/ 을 한 번 apply 해 두면 같은 버킷(tf-state-local)을 공유한다.
#     (state 저장소 자체를 별도 부트스트랩하는 건 현업에서도 정석)
# ※ backend 블록 안에서는 var.* 보간이 불가능 → 전부 리터럴로 적는다.
# =============================================================================

terraform {
  required_version = ">= 1.6" # endpoints{} backend 문법은 Terraform 1.6+ 필요
  required_providers {
    aws = {
      source  = "hashicorp/aws" # AWS 프로바이더
      version = "~> 5.0"        # 5.x 대 고정 (d1~d4 와 동일)
    }
  }

  backend "s3" {
    bucket = "tf-state-local"             # d3/bootstrap 이 만든 공유 state 버킷
    key    = "d5-final/terraform.tfstate" # 버킷 안 이 스택만의 경로 (d3 와 분리)
    region = "us-east-1"

    # ↓ LocalStack 을 backend 로 쓰기 위한 설정 (실제 AWS 면 이 6줄 불필요)
    access_key                  = "test"
    secret_key                  = "test"
    skip_credentials_validation = true
    skip_metadata_api_check     = true
    skip_requesting_account_id  = true
    use_path_style              = true # path-style (LocalStack 호환)

    endpoints = {
      s3       = "http://localhost:4566" # state 읽기/쓰기용 S3
      dynamodb = "http://localhost:4566" # 락 기록용 DynamoDB
    }

    dynamodb_table = "terraform-state-lock" # bootstrap 이 만든 락 테이블
    encrypt        = true                   # 저장되는 state 서버측 암호화
  }
}
