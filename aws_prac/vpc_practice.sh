#!/bin/bash
# ============================================================
# vpc_practice.sh
# 목적: AWS LocalStack VPC 실습 스크립트
# 실행: bash vpc_practice.sh
# 전제: localstack이 실행 중이어야 함
# ============================================================

echo "========================================"
echo "  VPC 실습 시작"
echo "========================================"

# ── VPC 생성 ──────────────────────────────────────────────
echo ""
echo "[1] VPC 생성"
VPC_ID=$(awslocal ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --query 'Vpc.VpcId' \
  --output text)
# CIDR 10.0.0.0/16 = 사용 가능한 IP: 10.0.0.0 ~ 10.0.255.255
# /16 = 65,536개 IP 주소
# CCNP 지식 연결: 온프레미스의 VLAN 개념과 동일
echo "생성된 VPC ID: $VPC_ID"

# ── VPC 목록 확인 ─────────────────────────────────────────
echo ""
echo "[2] VPC 목록 확인"
awslocal ec2 describe-vpcs \
  --query 'Vpcs[*].[VpcId,CidrBlock,State]' \
  --output table

# ── 퍼블릭 서브넷 생성 ────────────────────────────────────
echo ""
echo "[3] 퍼블릭 서브넷 생성"
PUBLIC_SUBNET=$(awslocal ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.1.0/24 \
  --query 'Subnet.SubnetId' \
  --output text)
# /24 = 256개 IP (실제 사용 251개, 5개 AWS 예약)
# 퍼블릭 서브넷 = 인터넷 직접 접근 가능 (웹 서버)
echo "퍼블릭 서브넷 ID: $PUBLIC_SUBNET"

# ── 프라이빗 서브넷 생성 ──────────────────────────────────
echo ""
echo "[4] 프라이빗 서브넷 생성"
PRIVATE_SUBNET=$(awslocal ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.2.0/24 \
  --query 'Subnet.SubnetId' \
  --output text)
# 프라이빗 서브넷 = 인터넷 직접 접근 불가 (DB 서버)
echo "프라이빗 서브넷 ID: $PRIVATE_SUBNET"

# ── 서브넷 목록 확인 ──────────────────────────────────────
echo ""
echo "[5] 서브넷 목록 확인"
awslocal ec2 describe-subnets \
  --query 'Subnets[*].[SubnetId,CidrBlock,VpcId]' \
  --output table

# ── 인터넷 게이트웨이 생성 ────────────────────────────────
echo ""
echo "[6] 인터넷 게이트웨이 생성"
IGW_ID=$(awslocal ec2 create-internet-gateway \
  --query 'InternetGateway.InternetGatewayId' \
  --output text)
# 인터넷 게이트웨이 = VPC ↔ 인터넷 연결 통로
echo "IGW ID: $IGW_ID"

# ── VPC에 IGW 연결 ────────────────────────────────────────
echo ""
echo "[7] IGW를 VPC에 연결"
awslocal ec2 attach-internet-gateway \
  --internet-gateway-id $IGW_ID \
  --vpc-id $VPC_ID
# IGW 연결해야 퍼블릭 서브넷이 인터넷과 통신 가능

echo ""
echo "========================================"
echo "  VPC 구성 완료"
echo ""
echo "  구성 요약:"
echo "  VPC:             $VPC_ID (10.0.0.0/16)"
echo "  퍼블릭 서브넷:   $PUBLIC_SUBNET (10.0.1.0/24)"
echo "  프라이빗 서브넷: $PRIVATE_SUBNET (10.0.2.0/24)"
echo "  IGW:             $IGW_ID"
echo "========================================"