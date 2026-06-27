# =============================================================================
# d5-final/variables.tf  (루트 모듈)  —  입력 변수 선언
# d4 변수에 RDS(DB) 관련 변수를 더했다. 실제 값은 terraform.tfvars 에서 주입.
# =============================================================================

variable "aws_region" {
  description = "AWS 리전"
  type        = string
  default     = "us-east-1" # LocalStack 기본 리전
}

variable "localstack_endpoint" {
  description = "LocalStack 엔드포인트 URL"
  type        = string
  default     = "http://localhost:4566" # 모든 AWS API 를 받는 단일 포트
}

variable "project" {
  description = "프로젝트 이름 (이름 접두사에 사용)"
  type        = string
  default     = "portfolio"
}

variable "environment" {
  description = "배포 환경 (dev/stg/prod) — 인스턴스 타입·Multi-AZ 분기에 사용"
  type        = string
  default     = "dev"

  validation {
    condition     = contains(["dev", "stg", "prod"], var.environment) # 허용 목록 검증
    error_message = "environment 는 dev, stg, prod 중 하나여야 합니다."
  }
}

variable "vpc_cidr" {
  description = "VPC CIDR 블록"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnets" {
  description = "퍼블릭 서브넷 맵 {이름 = {cidr, az}} (EC2 배치)"
  type = map(object({
    cidr = string
    az   = string
  }))
}

variable "private_subnets" {
  description = "프라이빗 서브넷 맵 {이름 = {cidr, az}} (RDS 배치)"
  type = map(object({
    cidr = string
    az   = string
  }))
}

variable "ami_id" {
  description = "EC2 AMI ID"
  type        = string
  # ★ LocalStack 은 자체 내장 AMI 만 받는다. ami-760aaa0f = 기본 Amazon Linux.
  # 실제 AWS 면 ec2 모듈 안에서 data.aws_ami 로 최신 AMI 동적 조회가 정석(README 참고).
  default = "ami-760aaa0f"
}

# ---- RDS(DB) 관련 변수 (통합본에서 추가) -----------------------------------
variable "db_engine_version" {
  description = "PostgreSQL 엔진 버전"
  type        = string
  default     = "15.4"
}

variable "db_username" {
  description = "RDS 마스터 사용자 이름"
  type        = string
  default     = "appuser"
}

variable "db_password" {
  description = "RDS 마스터 비밀번호 (★ 데모용 기본값 — 실무는 Vault/Secrets Manager 주입)"
  type        = string
  sensitive   = true # 출력 마스킹
  default     = "ChangeMe-In-Vault-123!"
}
