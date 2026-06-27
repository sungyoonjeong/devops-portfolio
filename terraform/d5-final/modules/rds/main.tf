# =============================================================================
# d5-final/modules/rds/main.tf  —  RDS(PostgreSQL) 모듈 (D5 신규, 통합본에서 추가)
# D1~D4 에는 없던 데이터베이스 계층. 앞 모듈들의 산출물에 연결된다:
#   db_subnet_group(vpc 프라이빗 서브넷) + vpc_security_group_ids(security_groups 의 rds SG)
# ★ 프라이빗 서브넷에만 두고, rds SG 로 "web 에서 온 5432" 만 받게 해 외부 직접 노출을 막는다.
# =============================================================================

# ---- DB 서브넷 그룹: RDS 를 어느 서브넷들에 둘지 (프라이빗 2개 이상, 다른 AZ) ----
# RDS 는 Multi-AZ 대비로 최소 2개 AZ 의 서브넷이 필요하다 → vpc 모듈의 프라이빗 서브넷 사용.
resource "aws_db_subnet_group" "this" {
  name       = "${var.name_prefix}-db-subnet-group"
  subnet_ids = var.db_subnet_ids # ★ 루트가 vpc 모듈의 private_subnet_ids 를 넘겨줌

  tags = merge(var.common_tags, { Name = "${var.name_prefix}-db-subnet-group" })
}

# ---- RDS 인스턴스 (PostgreSQL) --------------------------------------------
resource "aws_db_instance" "this" {
  identifier     = "${var.name_prefix}-db" # 인스턴스 식별자
  engine         = "postgres"              # 엔진
  engine_version = var.engine_version      # 버전 (변수)
  instance_class = var.db_instance_class   # 스펙 (환경별, 루트에서 계산해 전달)

  allocated_storage = var.allocated_storage # 스토리지 크기(GB)
  storage_encrypted = true                  # ★ 저장 데이터 암호화 (보안 베스트프랙티스)

  db_name  = var.db_name     # 초기 생성할 DB 이름
  username = var.db_username # 마스터 사용자 (★ 실무는 Vault/Secrets Manager 로 관리)
  password = var.db_password # 마스터 비밀번호 (★ tfvars 평문 금지 — PF-IaC 에서 Vault 연동)

  db_subnet_group_name   = aws_db_subnet_group.this.name # 위에서 만든 서브넷 그룹
  vpc_security_group_ids = [var.rds_sg_id]               # ★ security_groups 모듈의 rds SG
  multi_az               = var.multi_az                  # prod 면 다중 AZ (고가용성, 루트에서 분기)
  publicly_accessible    = false                         # ★ 퍼블릭 IP 미부여 — 외부 직접 접근 차단

  skip_final_snapshot = true # 실습/파괴 편의 (실무 prod 는 false 로 최종 스냅샷 보존)
  apply_immediately   = true # 변경 즉시 적용 (실습용)

  tags = merge(var.common_tags, { Name = "${var.name_prefix}-db" })
}
