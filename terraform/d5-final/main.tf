# =============================================================================
# d5-final/main.tf  (루트 모듈)  —  D1~D5 통합 최종본: 전체 인프라를 모듈로 조립
# D5 의 목표(개념서 11.5 + study 13장): D2~D4 에서 쌓은 모듈들을 하나의 스택으로
# 합치고, D3 의 원격 backend 까지 얹어 "실무 IaC 폴더 구조의 뼈대"를 완성한다.
#
# 데이터 흐름(루트가 모듈 출력 → 다음 모듈 입력으로 엮음):
#   vpc → security_groups → iam → ec2 / rds
#   (의존성은 terraform 이 참조 관계로 자동 추론 → 순서대로 생성)
#
# 구성: S3(앱데이터) + VPC(네트워크) + SG(방화벽) + IAM(키리스) + EC2(웹) + RDS(DB)
# =============================================================================
# ※ terraform{}/provider{} 블록은 backend.tf · providers.tf 로 분리 (관심사 분리)

# ---- 앱 데이터용 S3 버킷 (IAM 정책이 가리킬 대상) ---------------------------
resource "aws_s3_bucket" "app" {
  bucket = "${local.name_prefix}-app-data" # 예: portfolio-dev-app-data
  tags   = merge(local.common_tags, { Name = "${local.name_prefix}-app-data" })
}

# ---- ① VPC 모듈 (네트워크 토대 — 퍼블릭/프라이빗 서브넷 + IGW + RT) ---------
module "vpc" {
  source = "./modules/vpc"

  name_prefix     = local.name_prefix   # 이름 접두사
  vpc_cidr        = var.vpc_cidr        # VPC 대역
  public_subnets  = var.public_subnets  # 퍼블릭 서브넷 (EC2 배치)
  private_subnets = var.private_subnets # 프라이빗 서브넷 (RDS 배치)
  common_tags     = local.common_tags
}

# ---- ② 보안그룹 모듈 (web/rds SG) ------------------------------------------
module "security_groups" {
  source = "./modules/security_groups"

  name_prefix = local.name_prefix # 이름 접두사
  vpc_id      = module.vpc.vpc_id # ★ vpc 출력 → 입력
  common_tags = local.common_tags
}

# ---- ③ IAM 모듈 (EC2 가 S3 를 읽을 Role/Policy/Instance Profile, 키리스) ----
module "iam" {
  source = "./modules/iam"

  name_prefix    = local.name_prefix     # 이름 접두사
  app_bucket_arn = aws_s3_bucket.app.arn # ★ 위 버킷 ARN 을 정책 대상으로
  common_tags    = local.common_tags
}

# ---- ④ EC2 모듈 (퍼블릭 서브넷 + web SG + IAM 프로파일 연결한 웹 서버) ------
module "ec2" {
  source = "./modules/ec2"

  name_prefix      = local.name_prefix                # 이름 접두사
  ami_id           = var.ami_id                       # AMI (LocalStack 내장)
  instance_type    = local.instance_type              # 환경별 타입 (locals 계산)
  subnet_id        = module.vpc.public_subnet_ids[0]  # ★ 첫 퍼블릭 서브넷
  web_sg_id        = module.security_groups.web_sg_id # ★ web SG
  instance_profile = module.iam.instance_profile_name # ★ IAM 인스턴스 프로파일
  common_tags      = local.common_tags
}

# ---- ⑤ RDS 모듈 (프라이빗 서브넷 + rds SG 에 연결한 PostgreSQL) ------------
module "rds" {
  source = "./modules/rds"

  name_prefix       = local.name_prefix                # 이름 접두사
  db_subnet_ids     = module.vpc.private_subnet_ids    # ★ 프라이빗 서브넷에 배치
  rds_sg_id         = module.security_groups.rds_sg_id # ★ web 에서만 접근하는 rds SG
  db_instance_class = local.db_instance_class          # 환경별 DB 스펙 (locals 계산)
  engine_version    = var.db_engine_version            # 엔진 버전
  db_username       = var.db_username                  # 마스터 사용자
  db_password       = var.db_password                  # 마스터 비밀번호 (sensitive)
  multi_az          = var.environment == "prod"        # ★ prod 만 다중 AZ
  common_tags       = local.common_tags
}
