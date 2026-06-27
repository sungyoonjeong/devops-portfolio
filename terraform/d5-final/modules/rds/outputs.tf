# =============================================================================
# d5-final/modules/rds/outputs.tf
# endpoint 는 앱(EC2)이 DB 에 접속할 주소 — 루트 output 으로 끌어올린다.
# =============================================================================

output "db_endpoint" {
  description = "RDS 접속 엔드포인트 (host:port)"
  value       = aws_db_instance.this.endpoint
}

output "db_subnet_group" {
  description = "RDS 가 사용하는 DB 서브넷 그룹 이름"
  value       = aws_db_subnet_group.this.name
}
