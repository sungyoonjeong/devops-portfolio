# =============================================================================
# d5-final/modules/vpc/main.tf
# VPC 한 세트(VPC + 퍼블릭/프라이빗 서브넷 + IGW + 라우트 테이블)를 만드는 모듈.
# D2 에서 만든 모듈과 동일 — D4 에서는 이 위에 SG·IAM·EC2 모듈을 얹는다.
# =============================================================================

# ---- VPC 본체 -------------------------------------------------------------
resource "aws_vpc" "this" {
  cidr_block           = var.vpc_cidr             # VPC 전체 IP 대역
  enable_dns_hostnames = var.enable_dns_hostnames # 인스턴스 DNS 호스트네임 부여
  enable_dns_support   = true                     # VPC 내부 DNS 해석 활성화

  tags = merge(var.common_tags, {
    Name = "${var.name_prefix}-vpc"
  })
}

# ---- 인터넷 게이트웨이 (외부 출입구) ---------------------------------------
resource "aws_internet_gateway" "this" {
  vpc_id = aws_vpc.this.id # 위 VPC 에 부착

  tags = merge(var.common_tags, {
    Name = "${var.name_prefix}-igw"
  })
}

# ---- 퍼블릭 서브넷 (for_each 로 N개) ---------------------------------------
resource "aws_subnet" "public" {
  for_each = var.public_subnets # 맵 순회: each.key=이름, each.value={cidr,az}

  vpc_id                  = aws_vpc.this.id
  cidr_block              = each.value.cidr
  availability_zone       = each.value.az
  map_public_ip_on_launch = true # 공인 IP 자동 부여 → 퍼블릭

  tags = merge(var.common_tags, {
    Name = "${var.name_prefix}-${each.key}"
    Tier = "public"
  })
}

# ---- 프라이빗 서브넷 (for_each 로 N개) -------------------------------------
resource "aws_subnet" "private" {
  for_each = var.private_subnets

  vpc_id            = aws_vpc.this.id
  cidr_block        = each.value.cidr
  availability_zone = each.value.az
  # map_public_ip_on_launch 미지정 → false → 공인 IP 없음 → 프라이빗

  tags = merge(var.common_tags, {
    Name = "${var.name_prefix}-${each.key}"
    Tier = "private"
  })
}

# ---- 퍼블릭 라우트 테이블 (인터넷으로 나가는 길) ---------------------------
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.this.id

  route {
    cidr_block = "0.0.0.0/0"                  # 모든 외부 IP (디폴트 라우트)
    gateway_id = aws_internet_gateway.this.id # IGW 로 보냄 → 인터넷 연결
  }

  tags = merge(var.common_tags, {
    Name = "${var.name_prefix}-public-rt"
  })
}

# ---- 퍼블릭 서브넷 ↔ 라우트 테이블 연결 ------------------------------------
resource "aws_route_table_association" "public" {
  for_each = aws_subnet.public # 퍼블릭 서브넷 수만큼 연결

  subnet_id      = each.value.id
  route_table_id = aws_route_table.public.id
}
