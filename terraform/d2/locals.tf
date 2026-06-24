# =============================================================================
# locals.tf (루트 모듈)
# locals = 모듈 안에서만 쓰는 "이름 붙인 계산값". 변수와 달리 외부에서 못 바꾸고,
# 반복되는 식을 한 곳에 모아 재사용한다.
# =============================================================================

locals {
  name_prefix = "${var.project}-${var.environment}" # 예: "portfolio-dev" — 모든 리소스 이름 앞에 붙임

  common_tags = {                 # 모든 리소스에 일괄 적용할 태그 묶음
    Project     = var.project     # 어떤 프로젝트인지
    Environment = var.environment # 어떤 환경인지
    ManagedBy   = "terraform"     # 수동이 아닌 IaC 관리 자원임을 표시
    Day         = "D2"            # 학습 일차 표식 (실습용)
  }
}
