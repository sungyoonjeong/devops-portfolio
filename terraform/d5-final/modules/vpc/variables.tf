# =============================================================================
# d5-final/modules/vpc/variables.tf  —  vpc 모듈이 루트로부터 받는 입력
# =============================================================================

variable "name_prefix" {
  description = "리소스 이름 접두사 (project-environment)"
  type        = string
}

variable "vpc_cidr" {
  description = "VPC CIDR 블록 (예: 10.0.0.0/16)"
  type        = string
}

variable "enable_dns_hostnames" {
  description = "VPC DNS 호스트네임 활성화 여부"
  type        = bool
  default     = true
}

variable "public_subnets" {
  description = "퍼블릭 서브넷 맵 {이름 = {cidr, az}}"
  type = map(object({
    cidr = string
    az   = string
  }))
}

variable "private_subnets" {
  description = "프라이빗 서브넷 맵 {이름 = {cidr, az}}"
  type = map(object({
    cidr = string
    az   = string
  }))
}

variable "common_tags" {
  description = "모든 리소스에 적용할 공통 태그"
  type        = map(string)
  default     = {}
}
