# =============================================================================
# d4/modules/security_groups/main.tf  —  보안그룹(방화벽) 모듈 (D4 신규)
# web SG: 외부에서 80/443 허용. rds SG: web SG 에서 온 5432 만 허용.
# ★ 핵심 패턴: rds 인바운드를 CIDR("0.0.0.0/0") 대신 security_groups=[web]로 →
#   "특정 서버에서 온 트래픽만" 허용하는 게 더 안전하다(개념서 11.2).
# =============================================================================

# ---- 웹 서버 보안그룹 (외부 공개용) ----------------------------------------
resource "aws_security_group" "web" {
  name        = "${var.name_prefix}-web-sg"
  description = "Web server security group"
  vpc_id      = var.vpc_id # 루트가 vpc 모듈에서 받아 넘겨준 VPC ID

  ingress { # 인바운드 규칙: HTTP
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # 어디서든 접속 허용 (웹 공개)
    description = "HTTP"
  }

  ingress { # 인바운드 규칙: HTTPS
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTPS"
  }

  egress { # 아웃바운드: 전부 허용 (서버가 외부로 나가는 건 열어둠)
    from_port   = 0
    to_port     = 0
    protocol    = "-1" # -1 = 모든 프로토콜
    cidr_blocks = ["0.0.0.0/0"]
    description = "all outbound"
  }

  tags = merge(var.common_tags, { Name = "${var.name_prefix}-web-sg" })
}

# ---- RDS 보안그룹 (web SG 에서만 접근) -------------------------------------
resource "aws_security_group" "rds" {
  name        = "${var.name_prefix}-rds-sg"
  description = "RDS security group - only from web SG"
  vpc_id      = var.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.web.id] # ★ CIDR 아님 — web SG 출처만 허용
    description     = "PostgreSQL from web SG only"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = merge(var.common_tags, { Name = "${var.name_prefix}-rds-sg" })
}
