# =============================================================================
# d4/outputs.tf  (루트 모듈)  —  각 모듈 출력을 최종 노출
# 모듈 안 리소스는 밖에서 직접 못 보므로, 필요한 값은 모듈 output → 루트 output 으로 끌어올린다.
# =============================================================================

output "vpc_id" {
  description = "생성된 VPC ID"
  value       = module.vpc.vpc_id
}

output "public_subnet_ids" {
  description = "퍼블릭 서브넷 ID 리스트"
  value       = module.vpc.public_subnet_ids
}

output "web_sg_id" {
  description = "웹 서버 보안그룹 ID"
  value       = module.security_groups.web_sg_id
}

output "rds_sg_id" {
  description = "RDS 보안그룹 ID (web SG 에서만 인바운드 허용)"
  value       = module.security_groups.rds_sg_id
}

output "instance_profile_name" {
  description = "EC2 에 붙은 IAM 인스턴스 프로파일 이름"
  value       = module.iam.instance_profile_name
}

output "app_bucket" {
  description = "IAM 정책이 읽기 권한을 준 앱 데이터 버킷"
  value       = aws_s3_bucket.app.bucket
}

output "instance_id" {
  description = "생성된 EC2 인스턴스 ID"
  value       = module.ec2.instance_id
}

output "summary" { # 사람이 읽기 좋은 한 줄 요약
  description = "구성 요약"
  value       = "VPC ${module.vpc.vpc_id} / web-SG ${module.security_groups.web_sg_id} / EC2 ${module.ec2.instance_id} (${local.instance_type}) — IAM 프로파일 ${module.iam.instance_profile_name}"
}
