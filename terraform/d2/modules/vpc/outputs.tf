# =============================================================================
# modules/vpc/outputs.tf
# 모듈이 외부(루트 모듈)로 "돌려주는" 값. 모듈 내부 리소스는 밖에서 직접
# 참조할 수 없으므로, 필요한 값은 반드시 output 으로 노출해야 한다.
# =============================================================================

output "vpc_id" { # 생성된 VPC 의 ID
  description = "생성된 VPC ID"
  value       = aws_vpc.this.id # 다른 모듈/리소스가 이 ID 를 참조 가능
}

output "vpc_cidr" { # VPC 의 CIDR (참고용)
  description = "VPC CIDR 블록"
  value       = aws_vpc.this.cidr_block
}

output "public_subnet_ids" { # 퍼블릭 서브넷 ID 목록
  description = "퍼블릭 서브넷 ID 리스트"
  value       = [for s in aws_subnet.public : s.id] # for 표현식으로 맵 → ID 리스트 변환
}

output "private_subnet_ids" { # 프라이빗 서브넷 ID 목록
  description = "프라이빗 서브넷 ID 리스트"
  value       = [for s in aws_subnet.private : s.id]
}

output "internet_gateway_id" { # IGW ID
  description = "인터넷 게이트웨이 ID"
  value       = aws_internet_gateway.this.id
}
