# =============================================================================
# d4/modules/ec2/outputs.tf
# =============================================================================

output "instance_id" {
  description = "생성된 EC2 인스턴스 ID"
  value       = aws_instance.web.id
}

output "private_ip" {
  description = "인스턴스 사설 IP"
  value       = aws_instance.web.private_ip
}
