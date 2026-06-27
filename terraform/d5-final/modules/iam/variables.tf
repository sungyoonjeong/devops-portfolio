# =============================================================================
# d5-final/modules/iam/variables.tf
# =============================================================================

variable "name_prefix" {
  description = "리소스 이름 접두사"
  type        = string
}

variable "app_bucket_arn" {
  description = "정책이 읽기 권한을 줄 S3 버킷 ARN (루트에서 전달)"
  type        = string
}

variable "common_tags" {
  description = "공통 태그"
  type        = map(string)
  default     = {}
}
