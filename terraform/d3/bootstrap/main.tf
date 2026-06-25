# =============================================================================
# d3/bootstrap/main.tf  —  원격 state의 "그릇"을 먼저 만드는 단계
# 닭-달걀 문제: state를 S3에 두려면(원격 backend) 그 S3 버킷과 잠금용
# DynamoDB 테이블이 "이미" 있어야 한다. 그런데 그것들도 Terraform 으로 만들고 싶다.
# → 해법: 이 bootstrap 만 local backend(로컬 tfstate)로 먼저 apply 해서
#   버킷·테이블을 만들어 두고, 그 다음 상위 d3/ 가 그것을 backend 로 쓴다.
# (현업에서도 "state 저장소 자체는 별도로 부트스트랩"하는 게 정석)
# =============================================================================

terraform {                   # 이 bootstrap 은 일부러 backend 선언이 없다 → local 기본값
  required_version = ">= 1.6" # 상위 d3 와 버전 맞춤
  required_providers {
    aws = {
      source  = "hashicorp/aws" # AWS 프로바이더
      version = "~> 5.0"        # 5.x (d1/d2/d3 와 동일하게 고정)
    }
  }
}

# ---- Provider: LocalStack 으로 향하게 설정 (d1/d2 와 동일 패턴) --------------
provider "aws" {
  region                      = "us-east-1" # 리전 (LocalStack 기본)
  access_key                  = "test"      # LocalStack 은 자격증명 미검사
  secret_key                  = "test"      # 실제 AWS 라면 코드 하드코딩 금지
  skip_credentials_validation = true        # 자격증명 검증 건너뜀
  skip_metadata_api_check     = true        # 메타데이터 API 조회 건너뜀
  skip_requesting_account_id  = true        # 계정 ID 조회 건너뜀
  s3_use_path_style           = true        # path-style 접근 (LocalStack 호환)

  endpoints {                          # 각 서비스 호출을 LocalStack 으로
    s3       = "http://localhost:4566" # S3 API
    dynamodb = "http://localhost:4566" # DynamoDB API
  }
}

# ---- state 를 담을 S3 버킷 -------------------------------------------------
resource "aws_s3_bucket" "tf_state" {
  bucket = "tf-state-local" # 상위 d3/backend.tf 의 bucket 값과 반드시 일치

  tags = {
    Name = "tf-state-local"
    Day  = "D3"
    Role = "remote-state-store"
  }
}

# state 버킷은 버전관리를 켜는 게 정석 — 실수로 덮어써도 이전 state 복구 가능
resource "aws_s3_bucket_versioning" "tf_state" {
  bucket = aws_s3_bucket.tf_state.id # 위 버킷 참조 (암묵적 의존성)
  versioning_configuration {
    status = "Enabled" # 버전관리 켬
  }
}

# ---- 동시 apply 를 막는 잠금(lock)용 DynamoDB 테이블 -----------------------
resource "aws_dynamodb_table" "tf_lock" {
  name         = "terraform-state-lock" # 상위 d3/backend.tf 의 dynamodb_table 값과 일치
  billing_mode = "PAY_PER_REQUEST"      # 용량 미리 안 잡고 쓴 만큼 (락 테이블에 적합)
  hash_key     = "LockID"               # ★ Terraform 규약상 파티션 키 이름은 반드시 "LockID"

  attribute {       # hash_key 로 쓰는 속성의 타입 정의
    name = "LockID" # 키 이름
    type = "S"      # S = String
  }

  tags = {
    Name = "terraform-state-lock"
    Day  = "D3"
    Role = "state-lock"
  }
}

# ---- 만든 그릇 정보를 출력 (상위 d3 backend 설정에 그대로 넣으면 됨) --------
output "state_bucket" {
  description = "원격 state 를 저장할 S3 버킷 이름"
  value       = aws_s3_bucket.tf_state.bucket
}

output "lock_table" {
  description = "state 잠금용 DynamoDB 테이블 이름"
  value       = aws_dynamodb_table.tf_lock.name
}
