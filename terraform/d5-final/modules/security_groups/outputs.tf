# =============================================================================
# d5-final/modules/security_groups/outputs.tf
# web_sg_id 는 ec2 모듈이 인스턴스에 붙일 때 입력으로 받는다.
# =============================================================================

output "web_sg_id" {
  description = "웹 서버 보안그룹 ID"
  value       = aws_security_group.web.id
}

output "rds_sg_id" {
  description = "RDS 보안그룹 ID"
  value       = aws_security_group.rds.id
}
