# =============================================================================
# d3/providers.tf  —  AWS Provider 설정 (LocalStack 대상)
# backend.tf 가 "state 를 어디에 둘지"라면, 여기는 "실제 리소스를 어디에 만들지"다.
# d1/d2 와 동일한 LocalStack 패턴. 다만 D3 는 EC2 를 만들므로 ec2 엔드포인트가 핵심.
# =============================================================================

provider "aws" {
  region                      = var.aws_region # 변수로 받은 리전 (기본 us-east-1)
  access_key                  = "test"         # LocalStack 자격증명(아무 값)
  secret_key                  = "test"
  skip_credentials_validation = true # 자격증명 검증 건너뜀
  skip_metadata_api_check     = true # 메타데이터 조회 건너뜀
  skip_requesting_account_id  = true # 계정 ID 조회 건너뜀
  s3_use_path_style           = true # path-style (LocalStack 호환)

  endpoints {                          # 서비스별 호출을 LocalStack 으로 돌림
    ec2      = "http://localhost:4566" # ★ D3 에서 만드는 EC2 인스턴스용
    s3       = "http://localhost:4566" # S3
    iam      = "http://localhost:4566" # IAM
    sts      = "http://localhost:4566" # STS
    dynamodb = "http://localhost:4566" # DynamoDB
  }
}
