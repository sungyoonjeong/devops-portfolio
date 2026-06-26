# =============================================================================
# d4/terraform.tfvars  —  변수 실제 값 (terraform 이 자동 로드)
# =============================================================================

project     = "portfolio"   # 이름 접두사용
environment = "dev"         # dev → 인스턴스 t3.micro (prod 면 t3.large)
vpc_cidr    = "10.0.0.0/16" # VPC 전체 대역

# 퍼블릭 서브넷 2개 — 서로 다른 AZ (고가용성 패턴)
public_subnets = {
  public-a = { cidr = "10.0.1.0/24", az = "us-east-1a" }
  public-b = { cidr = "10.0.2.0/24", az = "us-east-1b" }
}

# 프라이빗 서브넷 2개
private_subnets = {
  private-a = { cidr = "10.0.11.0/24", az = "us-east-1a" }
  private-b = { cidr = "10.0.12.0/24", az = "us-east-1b" }
}

# ami_id 는 variables.tf 기본값(ami-760aaa0f, LocalStack 내장 AMI) 사용
