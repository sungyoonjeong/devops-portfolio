# =============================================================================
# d3/outputs.tf  —  apply 후 확인용 출력값
# workspace 를 바꿔가며 apply 하면 이 출력들이 어떻게 달라지는지 관찰하는 게 학습 포인트.
# =============================================================================

output "current_workspace" {
  description = "현재 활성 workspace (default/dev/stg/prod)"
  value       = terraform.workspace
}

output "instance_id" {
  description = "생성된 EC2 인스턴스 ID"
  value       = aws_instance.web.id
}

output "instance_type" {
  description = "workspace 에 따라 선택된 인스턴스 타입"
  value       = aws_instance.web.instance_type
}

output "state_location" {
  description = "이 환경의 state 가 S3 에 저장되는 경로 (workspace 별로 분리됨)"
  # s3 backend + workspace 면 key 앞에 'env:/<workspace>/' 접두사가 자동으로 붙는다.
  # default workspace 만 접두사 없이 key 그대로 저장된다.
  value = "s3://tf-state-local/env:/${terraform.workspace}/d3/terraform.tfstate"
}
