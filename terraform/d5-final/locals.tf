# =============================================================================
# d5-final/locals.tf  (루트 모듈)  —  반복 계산값 한 곳에 모으기
# =============================================================================

locals {
  name_prefix = "${var.project}-${var.environment}" # 예: portfolio-dev

  # 환경별 EC2 인스턴스 타입: prod 면 크게, 나머지는 작게 (삼항식 패턴)
  instance_type = var.environment == "prod" ? "t3.large" : "t3.micro"

  # 환경별 RDS 스펙: prod 면 크게, 나머지는 작게 (통합본에서 추가)
  db_instance_class = var.environment == "prod" ? "db.t3.medium" : "db.t3.micro"

  common_tags = {                 # 모든 리소스 공통 태그
    Project     = var.project     # 프로젝트
    Environment = var.environment # 환경
    ManagedBy   = "terraform"     # IaC 관리 자원 표식
    Day         = "D5"            # 학습 일차 (통합 최종본)
  }
}
