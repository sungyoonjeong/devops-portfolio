# =============================================================================
# d4/modules/ec2/variables.tf
# 이 모듈은 다른 모듈들의 출력을 입력으로 받아 한 인스턴스에 조립한다.
# =============================================================================

variable "name_prefix" {
  description = "리소스 이름 접두사"
  type        = string
}

variable "ami_id" {
  description = "EC2 AMI ID"
  type        = string
}

variable "instance_type" {
  description = "인스턴스 타입 (환경별, 루트에서 계산해 전달)"
  type        = string
}

variable "subnet_id" {
  description = "인스턴스를 띄울 서브넷 ID (vpc 모듈 출력)"
  type        = string
}

variable "web_sg_id" {
  description = "인스턴스에 붙일 웹 보안그룹 ID (security_groups 모듈 출력)"
  type        = string
}

variable "instance_profile" {
  description = "인스턴스에 붙일 IAM 인스턴스 프로파일 이름 (iam 모듈 출력)"
  type        = string
}

variable "common_tags" {
  description = "공통 태그"
  type        = map(string)
  default     = {}
}
