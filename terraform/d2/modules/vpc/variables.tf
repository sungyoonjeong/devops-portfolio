# =============================================================================
# modules/vpc/variables.tf
# VPC 모듈이 외부(루트 모듈)로부터 받는 입력 변수 정의.
# 모듈은 자기 안에서 값을 하드코딩하지 않고 전부 변수로 받아야 재사용 가능하다.
# =============================================================================

variable "name_prefix" {                              # 모든 리소스 이름 앞에 붙일 접두사 (예: "portfolio-dev")
  description = "리소스 이름 접두사 (project-environment 형태)" # terraform 문서/plan에 표시되는 설명
  type        = string                                # 문자열 타입으로 제약 — 숫자/리스트 들어오면 에러
}

variable "vpc_cidr" { # VPC 전체가 사용할 사설 IP 대역
  description = "VPC의 CIDR 블록 (예: 10.0.0.0/16)"
  type        = string
}

variable "enable_dns_hostnames" { # VPC 안 인스턴스에 DNS 호스트네임 부여 여부
  description = "VPC DNS 호스트네임 활성화 여부"
  type        = bool # 참/거짓만 허용
  default     = true # 호출 시 생략하면 true 사용 (기본값)
}

variable "public_subnets" { # 퍼블릭 서브넷 정의 묶음 (key = 서브넷 이름)
  description = "퍼블릭 서브넷 맵 {이름 = {cidr, az}}"
  type = map(object({ # "맵 of 오브젝트" — 키마다 cidr/az 두 필드를 강제
    cidr = string     # 각 서브넷의 IP 대역
    az   = string     # 각 서브넷이 속할 가용영역(AZ)
  }))
}

variable "private_subnets" { # 프라이빗 서브넷 정의 묶음 (구조는 퍼블릭과 동일)
  description = "프라이빗 서브넷 맵 {이름 = {cidr, az}}"
  type = map(object({
    cidr = string
    az   = string
  }))
}

variable "common_tags" { # 모든 리소스에 공통으로 붙일 태그
  description = "모든 리소스에 적용할 공통 태그"
  type        = map(string) # 키도 값도 문자열인 맵
  default     = {}          # 호출 시 생략하면 빈 맵 (태그 없음)
}
