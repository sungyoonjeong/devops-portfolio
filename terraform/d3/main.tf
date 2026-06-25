# =============================================================================
# d3/main.tf  —  Workspace 에 따라 사양이 달라지는 EC2 프로비저닝
# 같은 코드인데 workspace 를 prod 로 바꾸면 instance_type 이 t3.large 로,
# state 도 prod 전용으로 분리된다 → "코드 1벌, 환경 여러 개"를 직접 체감.
# =============================================================================

resource "aws_instance" "web" {
  ami           = var.ami_id                     # 변수로 받은 AMI
  instance_type = local.instance_type[local.env] # ★ 현재 workspace 에 맞는 타입 선택

  tags = merge( # 공통 태그 + 이 리소스 고유 태그 병합
    local.common_tags,
    { Name = "${local.name_prefix}-web" } # 예) portfolio-dev-web
  )
}
