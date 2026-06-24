# =============================================================================
# modules/vpc/main.tf
# VPC 한 세트(VPC + 퍼블릭/프라이빗 서브넷 + IGW + 라우트 테이블)를 만드는 모듈.
# for_each 로 서브넷을 동적으로 여러 개 생성하는 패턴을 보여준다.
# =============================================================================

# ---- VPC 본체 -------------------------------------------------------------
resource "aws_vpc" "this" {                       # "this" = 모듈 안 대표 리소스 관용 이름
  cidr_block           = var.vpc_cidr             # VPC가 차지할 전체 IP 대역
  enable_dns_hostnames = var.enable_dns_hostnames # 인스턴스 DNS 호스트네임 부여 여부
  enable_dns_support   = true                     # VPC 내부 DNS 해석 활성화 (기본 켬)

  tags = merge(var.common_tags, {   # 공통 태그 + 이 리소스 전용 태그를 병합
    Name = "${var.name_prefix}-vpc" # 콘솔에서 식별할 이름 태그
  })
}

# ---- 인터넷 게이트웨이 (VPC 의 외부 출입구) --------------------------------
resource "aws_internet_gateway" "this" { # 퍼블릭 서브넷이 인터넷과 통신하려면 필수
  vpc_id = aws_vpc.this.id               # 위에서 만든 VPC 에 부착 (암묵적 의존성 생성)

  tags = merge(var.common_tags, {
    Name = "${var.name_prefix}-igw"
  })
}

# ---- 퍼블릭 서브넷 (for_each 로 N개 생성) ----------------------------------
resource "aws_subnet" "public" { # 키 개수만큼 서브넷이 생긴다
  for_each = var.public_subnets  # 맵을 순회 — each.key=이름, each.value={cidr,az}

  vpc_id                  = aws_vpc.this.id # 어느 VPC 소속인지
  cidr_block              = each.value.cidr # 이 서브넷의 IP 대역
  availability_zone       = each.value.az   # 이 서브넷이 위치할 AZ
  map_public_ip_on_launch = true            # 여기 뜨는 인스턴스에 공인 IP 자동 부여 → 퍼블릭

  tags = merge(var.common_tags, {
    Name = "${var.name_prefix}-${each.key}" # 예: portfolio-dev-public-a
    Tier = "public"                         # 계층 구분용 커스텀 태그
  })
}

# ---- 프라이빗 서브넷 (for_each 로 N개 생성) --------------------------------
resource "aws_subnet" "private" {
  for_each = var.private_subnets

  vpc_id            = aws_vpc.this.id
  cidr_block        = each.value.cidr
  availability_zone = each.value.az
  # map_public_ip_on_launch 미지정 → 기본 false → 공인 IP 없음 → 프라이빗

  tags = merge(var.common_tags, {
    Name = "${var.name_prefix}-${each.key}"
    Tier = "private"
  })
}

# ---- 퍼블릭 라우트 테이블 (인터넷으로 나가는 길) ---------------------------
resource "aws_route_table" "public" { # 퍼블릭 서브넷들이 공유할 라우팅 규칙
  vpc_id = aws_vpc.this.id

  route {                                     # 라우트 규칙 한 줄
    cidr_block = "0.0.0.0/0"                  # 목적지 = 모든 외부 IP (디폴트 라우트)
    gateway_id = aws_internet_gateway.this.id # 그 트래픽을 IGW 로 보냄 → 인터넷 연결
  }

  tags = merge(var.common_tags, {
    Name = "${var.name_prefix}-public-rt"
  })
}

# ---- 퍼블릭 서브넷 ↔ 퍼블릭 라우트 테이블 연결 -----------------------------
resource "aws_route_table_association" "public" { # 라우트 테이블은 서브넷에 "연결"해야 적용됨
  for_each = aws_subnet.public                    # 만든 퍼블릭 서브넷 수만큼 연결 생성

  subnet_id      = each.value.id             # 각 퍼블릭 서브넷
  route_table_id = aws_route_table.public.id # 위 퍼블릭 라우트 테이블에 묶음
}

# 참고: 프라이빗 서브넷은 별도 라우트 테이블을 만들지 않으면 VPC 의 메인 라우트
# 테이블(로컬 통신만 가능, 외부 차단)을 자동으로 따른다 → 의도한 "프라이빗" 동작.
