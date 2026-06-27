# =============================================================================
# d5-final/modules/vpc/outputs.tf  —  vpc 모듈이 밖으로 돌려주는 값
# 다른 모듈(security_groups·ec2)이 vpc_id·서브넷 ID 를 입력으로 받아 쓴다.
# =============================================================================

output "vpc_id" {
  description = "생성된 VPC ID"
  value       = aws_vpc.this.id
}

output "vpc_cidr" {
  description = "VPC CIDR 블록"
  value       = aws_vpc.this.cidr_block
}

output "public_subnet_ids" {
  description = "퍼블릭 서브넷 ID 리스트"
  value       = [for s in aws_subnet.public : s.id] # 맵 → ID 리스트
}

output "private_subnet_ids" {
  description = "프라이빗 서브넷 ID 리스트"
  value       = [for s in aws_subnet.private : s.id]
}

output "internet_gateway_id" {
  description = "인터넷 게이트웨이 ID"
  value       = aws_internet_gateway.this.id
}
