# =============================================================================
# variables.tf (루트 모듈)
# 이 실습 전체의 입력 변수. 실제 값은 terraform.tfvars 에서 주입한다.
# =============================================================================

variable "aws_region" { # LocalStack/AWS 리전
  description = "AWS 리전"
  type        = string
  default     = "us-east-1" # LocalStack 기본 리전
}

variable "localstack_endpoint" { # LocalStack 게이트웨이 주소
  description = "LocalStack 엔드포인트 URL"
  type        = string
  default     = "http://localhost:4566" # 모든 AWS API 를 받는 단일 포트
}

variable "project" { # 프로젝트 이름 (이름 접두사에 사용)
  description = "프로젝트 이름"
  type        = string
  default     = "portfolio"
}

variable "environment" { # 환경 구분 (dev/stg/prod 등)
  description = "배포 환경"
  type        = string
  default     = "dev"

  validation {                                                        # 입력값 검증 규칙 (D2 심화 문법)
    condition     = contains(["dev", "stg", "prod"], var.environment) # 허용 목록 안에 있는지
    error_message = "environment 는 dev, stg, prod 중 하나여야 합니다."        # 위반 시 표시 메시지
  }
}

variable "vpc_cidr" { # VPC 전체 IP 대역
  description = "VPC CIDR 블록"
  type        = string
  default     = "10.0.0.0/16" # 65,536개 IP — /24 서브넷 256개 분할 가능
}

variable "public_subnets" { # 퍼블릭 서브넷 정의 (모듈로 그대로 전달)
  description = "퍼블릭 서브넷 맵"
  type = map(object({
    cidr = string
    az   = string
  }))
}

variable "private_subnets" { # 프라이빗 서브넷 정의
  description = "프라이빗 서브넷 맵"
  type = map(object({
    cidr = string
    az   = string
  }))
}
