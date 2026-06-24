# =============================================================================
# terraform.tfvars
# 변수의 실제 값. 이 파일은 terraform 이 자동으로 읽어 variables.tf 를 채운다.
# (실 운영에서 민감값은 tfvars 에 두지 말 것 — 여기선 로컬 실습이라 무방)
# =============================================================================

project     = "portfolio"   # 이름 접두사용 프로젝트명
environment = "dev"         # 환경 (validation 통과 위해 dev/stg/prod)
vpc_cidr    = "10.0.0.0/16" # VPC 전체 대역

# 퍼블릭 서브넷 2개 — 서로 다른 AZ 에 배치(고가용성 패턴)
public_subnets = {
  public-a = { cidr = "10.0.1.0/24", az = "us-east-1a" } # AZ a 의 퍼블릭 서브넷
  public-b = { cidr = "10.0.2.0/24", az = "us-east-1b" } # AZ b 의 퍼블릭 서브넷
}

# 프라이빗 서브넷 2개 — 퍼블릭과 동일하게 AZ 분산
private_subnets = {
  private-a = { cidr = "10.0.11.0/24", az = "us-east-1a" } # AZ a 의 프라이빗 서브넷
  private-b = { cidr = "10.0.12.0/24", az = "us-east-1b" } # AZ b 의 프라이빗 서브넷
}
