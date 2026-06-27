# =============================================================================
# d5-final/modules/rds/variables.tf  —  rds 모듈이 루트로부터 받는 입력
# =============================================================================

variable "name_prefix" {
  description = "리소스 이름 접두사 (project-environment)"
  type        = string
}

variable "db_subnet_ids" {
  description = "DB 를 배치할 프라이빗 서브넷 ID 리스트 (vpc 모듈 출력)"
  type        = list(string)
}

variable "rds_sg_id" {
  description = "RDS 에 붙일 보안그룹 ID (security_groups 모듈 출력)"
  type        = string
}

variable "engine_version" {
  description = "PostgreSQL 엔진 버전"
  type        = string
  default     = "15.4"
}

variable "db_instance_class" {
  description = "RDS 인스턴스 스펙 (환경별, 루트에서 계산해 전달)"
  type        = string
}

variable "allocated_storage" {
  description = "스토리지 크기(GB)"
  type        = number
  default     = 20
}

variable "db_name" {
  description = "초기 생성할 데이터베이스 이름"
  type        = string
  default     = "appdb"
}

variable "db_username" {
  description = "DB 마스터 사용자 이름"
  type        = string
}

variable "db_password" {
  description = "DB 마스터 비밀번호 (★ 평문 tfvars 금지 — 실무는 Vault/Secrets Manager)"
  type        = string
  sensitive   = true # plan/apply 출력에 값이 노출되지 않게 마스킹
}

variable "multi_az" {
  description = "다중 AZ 배치 여부 (prod 고가용성)"
  type        = bool
  default     = false
}

variable "common_tags" {
  description = "공통 태그"
  type        = map(string)
  default     = {}
}
