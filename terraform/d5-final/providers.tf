# =============================================================================
# d5-final/providers.tf  —  AWS Provider 설정 (LocalStack 대상)
# backend.tf 가 "state 를 어디 둘지"라면, 여기는 "실제 리소스를 어디 만들지"다.
# d1~d4 와 동일한 LocalStack 패턴 — 통합본은 RDS 까지 만들므로 rds 엔드포인트를 추가.
# =============================================================================

provider "aws" {
  region                      = var.aws_region # 변수로 받은 리전 (기본 us-east-1)
  access_key                  = "test"         # LocalStack 자격증명(아무 값)
  secret_key                  = "test"         # ★ 실제 AWS 라면 절대 하드코딩 금지
  skip_credentials_validation = true           # 자격증명 검증 건너뜀
  skip_metadata_api_check     = true           # 메타데이터 조회 건너뜀
  skip_requesting_account_id  = true           # 계정 ID 조회 건너뜀
  s3_use_path_style           = true           # path-style (LocalStack 호환)

  endpoints {                          # 서비스별 호출을 LocalStack 으로 리다이렉트
    ec2      = var.localstack_endpoint # VPC/서브넷/IGW/SG/EC2
    s3       = var.localstack_endpoint # 앱 데이터 버킷
    iam      = var.localstack_endpoint # IAM Role/Policy/Instance Profile
    sts      = var.localstack_endpoint # AssumeRole 등
    dynamodb = var.localstack_endpoint # (backend 락과 동일 게이트웨이)
    rds      = var.localstack_endpoint # ★ 통합본에서 추가 — RDS API
  }
}
