# =============================================================================
# d3/locals.tf  —  Workspace 기반 동적 값 계산
# D3 의 또 다른 핵심: terraform.workspace 로 같은 코드를 dev/stg/prod 로 분기.
# =============================================================================

locals {
  # 현재 활성 workspace 이름. workspace 를 따로 안 만들면 "default" 가 된다.
  env = terraform.workspace

  # 이름 접두사: 예) portfolio-dev, portfolio-prod
  name_prefix = "${var.project}-${local.env}"

  # workspace 별로 다른 인스턴스 타입 (세이브 슬롯마다 사양을 다르게)
  # ★ "default" 키를 꼭 둔다 — workspace 를 안 만든 상태(default)에서 apply 해도
  #   map 조회가 실패하지 않도록. (없으면 key 없음 에러)
  instance_type = {
    default = "t3.micro" # workspace 미생성 시
    dev     = "t3.micro" # 개발: 작게
    stg     = "t3.small" # 스테이징: 중간
    prod    = "t3.large" # 운영: 크게
  }

  # 모든 리소스에 공통으로 붙일 태그
  common_tags = {
    Project   = var.project
    Env       = local.env
    Day       = "D3"
    ManagedBy = "Terraform"
  }
}
