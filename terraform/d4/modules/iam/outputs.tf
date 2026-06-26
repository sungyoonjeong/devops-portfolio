# =============================================================================
# d4/modules/iam/outputs.tf
# instance_profile_name 을 ec2 모듈이 받아 인스턴스에 부착한다.
# =============================================================================

output "instance_profile_name" {
  description = "EC2 에 붙일 인스턴스 프로파일 이름"
  value       = aws_iam_instance_profile.ec2_profile.name
}

output "role_arn" {
  description = "EC2 IAM 역할 ARN"
  value       = aws_iam_role.ec2_role.arn
}
