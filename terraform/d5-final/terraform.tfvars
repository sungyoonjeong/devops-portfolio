# =============================================================================
# d5-final/terraform.tfvars  —  변수 실제 값 (terraform 이 자동 로드)
# ※ db_password 는 데모용 기본값을 variables.tf 에 둔다. 실무라면 이 파일에 비밀번호를
#   평문으로 적지 말고 Vault/Secrets Manager 또는 TF_VAR_db_password 환경변수로 주입한다.
# =============================================================================

project     = "portfolio"   # 이름 접두사용
environment = "dev"         # dev → EC2 t3.micro / RDS db.t3.micro / Single-AZ
vpc_cidr    = "10.0.0.0/16" # VPC 전체 대역

# 퍼블릭 서브넷 2개 — 서로 다른 AZ (EC2·고가용성 패턴)
public_subnets = {
  public-a = { cidr = "10.0.1.0/24", az = "us-east-1a" }
  public-b = { cidr = "10.0.2.0/24", az = "us-east-1b" }
}

# 프라이빗 서브넷 2개 — RDS 배치 (Multi-AZ 대비 최소 2개 AZ 필요)
private_subnets = {
  private-a = { cidr = "10.0.11.0/24", az = "us-east-1a" }
  private-b = { cidr = "10.0.12.0/24", az = "us-east-1b" }
}

# ami_id 는 variables.tf 기본값(ami-760aaa0f, LocalStack 내장 AMI) 사용
# db_* 는 variables.tf 기본값 사용 (engine 15.4 / appuser / 데모 비밀번호)
