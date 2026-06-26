# =============================================================================
# d4/locals.tf  (루트 모듈)  —  반복 계산값 한 곳에 모으기
# =============================================================================

locals {
  name_prefix = "${var.project}-${var.environment}" # 예: portfolio-dev

  # 환경별 인스턴스 타입: prod 면 크게, 나머지는 작게 (개념서 11.4 의 삼항식 패턴)
  instance_type = var.environment == "prod" ? "t3.large" : "t3.micro"

  common_tags = {                 # 모든 리소스 공통 태그
    Project     = var.project     # 프로젝트
    Environment = var.environment # 환경
    ManagedBy   = "terraform"     # IaC 관리 자원 표식
    Day         = "D4"            # 학습 일차
  }
}
