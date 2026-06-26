# =============================================================================
# d4/modules/security_groups/variables.tf
# =============================================================================

variable "name_prefix" {
  description = "리소스 이름 접두사"
  type        = string
}

variable "vpc_id" {
  description = "보안그룹을 만들 VPC ID (루트가 vpc 모듈 출력에서 전달)"
  type        = string
}

variable "common_tags" {
  description = "공통 태그"
  type        = map(string)
  default     = {}
}
