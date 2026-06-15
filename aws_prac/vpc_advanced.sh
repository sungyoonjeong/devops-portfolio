#!/bin/bash
# ============================================================
# vpc_advanced_practice.sh
# 목적: AWS LocalStack VPC 심화 실습
#       퍼블릭·프라이빗 서브넷 + 보안그룹 + NACL + NAT GW
# 실행: bash vpc_advanced_practice.sh
# 전제: localstack이 실행 중이어야 함
# ============================================================

echo "========================================"
echo "  AWS VPC 심화 실습 시작"
echo "========================================"

# ── STEP 1. VPC 생성 ─────────────────────────────────────
echo ""
echo "[STEP 1] VPC 생성 (10.0.0.0/16)"
VPC_ID=$(awslocal ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --query 'Vpc.VpcId' \
  --output text)
# CIDR 10.0.0.0/16 = 10.0.0.0 ~ 10.0.255.255 (65,536개 IP)
echo "  → VPC ID: $VPC_ID"

# ── STEP 2. 서브넷 생성 ──────────────────────────────────
echo ""
echo "[STEP 2] 퍼블릭·프라이빗 서브넷 생성"

PUBLIC_SUBNET=$(awslocal ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.1.0/24 \
  --query 'Subnet.SubnetId' \
  --output text)
# 퍼블릭 서브넷: 인터넷 직접 접근 가능 (웹서버·ALB 배치)
echo "  → 퍼블릭 서브넷: $PUBLIC_SUBNET (10.0.1.0/24)"

PRIVATE_SUBNET=$(awslocal ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.2.0/24 \
  --query 'Subnet.SubnetId' \
  --output text)
# 프라이빗 서브넷: 인터넷 직접 접근 불가 (DB·캐시 배치)
echo "  → 프라이빗 서브넷: $PRIVATE_SUBNET (10.0.2.0/24)"

# ── STEP 3. 인터넷 게이트웨이 ────────────────────────────
echo ""
echo "[STEP 3] 인터넷 게이트웨이 생성 및 VPC 연결"

IGW_ID=$(awslocal ec2 create-internet-gateway \
  --query 'InternetGateway.InternetGatewayId' \
  --output text)
# IGW = VPC ↔ 인터넷 연결 통로
echo "  → IGW ID: $IGW_ID"

awslocal ec2 attach-internet-gateway \
  --internet-gateway-id $IGW_ID \
  --vpc-id $VPC_ID
# IGW를 VPC에 연결해야 인터넷 통신 가능
echo "  → VPC에 IGW 연결 완료"

# ── STEP 4. 퍼블릭 라우팅 테이블 ────────────────────────
echo ""
echo "[STEP 4] 퍼블릭 서브넷 라우팅 테이블 설정"

RTB_PUBLIC=$(awslocal ec2 create-route-table \
  --vpc-id $VPC_ID \
  --query 'RouteTable.RouteTableId' \
  --output text)
# 라우팅 테이블 = 트래픽 경로 결정 규칙 (CCNP: routing table)
echo "  → 라우팅 테이블: $RTB_PUBLIC"

awslocal ec2 create-route \
  --route-table-id $RTB_PUBLIC \
  --destination-cidr-block 0.0.0.0/0 \
  --gateway-id $IGW_ID
# 0.0.0.0/0 → IGW = 모든 인터넷 트래픽을 IGW로
echo "  → 인터넷 경로 추가 (0.0.0.0/0 → IGW)"

awslocal ec2 associate-route-table \
  --subnet-id $PUBLIC_SUBNET \
  --route-table-id $RTB_PUBLIC
# 퍼블릭 서브넷에 이 라우팅 테이블 연결
echo "  → 퍼블릭 서브넷에 라우팅 테이블 연결 완료"

# ── STEP 5. 보안 그룹 (Security Group) ──────────────────
echo ""
echo "[STEP 5] 보안 그룹 생성 (웹 서버용)"

SG_WEB=$(awslocal ec2 create-security-group \
  --group-name web-sg \
  --description "Web server security group" \
  --vpc-id $VPC_ID \
  --query 'GroupId' \
  --output text)
# 보안 그룹 = 인스턴스 단위 방화벽
# Stateful = 인바운드 허용 시 응답 자동 허용
# 허용 규칙만 존재 (거부 규칙 없음)
echo "  → 웹 보안그룹: $SG_WEB"

awslocal ec2 authorize-security-group-ingress \
  --group-id $SG_WEB \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0
# HTTP 80 포트 전체 허용
echo "  → HTTP(80) 허용"

awslocal ec2 authorize-security-group-ingress \
  --group-id $SG_WEB \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0
# HTTPS 443 포트 전체 허용
echo "  → HTTPS(443) 허용"

awslocal ec2 authorize-security-group-ingress \
  --group-id $SG_WEB \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0
# SSH 22 포트 허용 (실제 운영 시 특정 IP만 허용)
echo "  → SSH(22) 허용"

# DB 서버용 보안 그룹 (MySQL)
SG_DB=$(awslocal ec2 create-security-group \
  --group-name db-sg \
  --description "DB server security group" \
  --vpc-id $VPC_ID \
  --query 'GroupId' \
  --output text)
echo "  → DB 보안그룹: $SG_DB"

awslocal ec2 authorize-security-group-ingress \
  --group-id $SG_DB \
  --protocol tcp \
  --port 3306 \
  --source-group $SG_WEB
# MySQL 3306: 웹서버 보안그룹(SG_WEB)에서만 허용
# 인터넷(0.0.0.0/0)이 아닌 보안그룹 참조 = 더 안전
echo "  → MySQL(3306): 웹서버SG에서만 허용"

# 보안 그룹 확인
echo ""
echo "  [보안그룹 인바운드 규칙 확인]"
awslocal ec2 describe-security-groups \
  --group-ids $SG_WEB \
  --query 'SecurityGroups[*].[GroupName,IpPermissions[*].[IpProtocol,FromPort,ToPort]]' \
  --output table

# ── STEP 6. NACL (Network ACL) ───────────────────────────
echo ""
echo "[STEP 6] NACL 생성 (서브넷 방화벽)"

NACL_ID=$(awslocal ec2 create-network-acl \
  --vpc-id $VPC_ID \
  --query 'NetworkAcl.NetworkAclId' \
  --output text)
# NACL = 서브넷 단위 방화벽
# Stateless = 인바운드·아웃바운드 각각 설정 필요
# 허용·거부 규칙 모두 존재
# 규칙 번호 낮은 것 우선 적용
echo "  → NACL: $NACL_ID"

# 인바운드: HTTP 허용 (규칙 100)
awslocal ec2 create-network-acl-entry \
  --network-acl-id $NACL_ID \
  --rule-number 100 \
  --protocol tcp \
  --port-range From=80,To=80 \
  --cidr-block 0.0.0.0/0 \
  --rule-action allow \
  --ingress
echo "  → 인바운드 규칙 100: HTTP(80) 허용"

# 인바운드: HTTPS 허용 (규칙 200)
awslocal ec2 create-network-acl-entry \
  --network-acl-id $NACL_ID \
  --rule-number 200 \
  --protocol tcp \
  --port-range From=443,To=443 \
  --cidr-block 0.0.0.0/0 \
  --rule-action allow \
  --ingress
echo "  → 인바운드 규칙 200: HTTPS(443) 허용"

# 아웃바운드: 임시포트 허용 (응답 트래픽)
awslocal ec2 create-network-acl-entry \
  --network-acl-id $NACL_ID \
  --rule-number 100 \
  --protocol tcp \
  --port-range From=1024,To=65535 \
  --cidr-block 0.0.0.0/0 \
  --rule-action allow \
  --egress
# Stateless이므로 응답 트래픽도 별도 허용 필요
# 임시포트(1024~65535) = 응답이 나가는 포트
echo "  → 아웃바운드 규칙 100: 임시포트(1024-65535) 허용"

# ── STEP 7. NAT 게이트웨이 ───────────────────────────────
echo ""
echo "[STEP 7] NAT 게이트웨이 생성 (프라이빗→인터넷 단방향)"

EIP=$(awslocal ec2 allocate-address \
  --query 'AllocationId' \
  --output text)
# Elastic IP = NAT GW에 필요한 고정 공인 IP
echo "  → Elastic IP: $EIP"

NAT_ID=$(awslocal ec2 create-nat-gateway \
  --subnet-id $PUBLIC_SUBNET \
  --allocation-id $EIP \
  --query 'NatGateway.NatGatewayId' \
  --output text)
# NAT GW는 퍼블릭 서브넷에 배치
# 프라이빗 서브넷 → 인터넷 단방향 통신
# 인터넷 → 프라이빗 서브넷 직접 접근 불가
echo "  → NAT GW: $NAT_ID (퍼블릭 서브넷에 배치)"

# ── STEP 8. 프라이빗 라우팅 테이블 ──────────────────────
echo ""
echo "[STEP 8] 프라이빗 서브넷 라우팅 테이블 설정"

RTB_PRIVATE=$(awslocal ec2 create-route-table \
  --vpc-id $VPC_ID \
  --query 'RouteTable.RouteTableId' \
  --output text)
echo "  → 라우팅 테이블: $RTB_PRIVATE"

awslocal ec2 create-route \
  --route-table-id $RTB_PRIVATE \
  --destination-cidr-block 0.0.0.0/0 \
  --nat-gateway-id $NAT_ID
# 0.0.0.0/0 → NAT GW = 인터넷 트래픽을 NAT GW로
# (IGW가 아닌 NAT GW = 아웃바운드만 가능)
echo "  → 인터넷 경로 추가 (0.0.0.0/0 → NAT GW)"

awslocal ec2 associate-route-table \
  --subnet-id $PRIVATE_SUBNET \
  --route-table-id $RTB_PRIVATE
echo "  → 프라이빗 서브넷에 라우팅 테이블 연결 완료"

# ── 최종 구성 확인 ────────────────────────────────────────
echo ""
echo "========================================"
echo "  VPC 전체 구성 완료 ✅"
echo "========================================"
echo ""
echo "  구성 요약:"
echo "  ┌─────────────────────────────────────┐"
echo "  │  VPC: $VPC_ID"
echo "  │  CIDR: 10.0.0.0/16"
echo "  │"
echo "  │  퍼블릭 서브넷: $PUBLIC_SUBNET"
echo "  │  → 10.0.1.0/24, IGW 연결"
echo "  │  → 웹서버 보안그룹: $SG_WEB"
echo "  │"
echo "  │  프라이빗 서브넷: $PRIVATE_SUBNET"
echo "  │  → 10.0.2.0/24, NAT GW 경유"
echo "  │  → DB 보안그룹: $SG_DB"
echo "  │"
echo "  │  IGW: $IGW_ID"
echo "  │  NAT GW: $NAT_ID"
echo "  │  NACL: $NACL_ID"
echo "  └─────────────────────────────────────┘"
echo ""
echo "  트래픽 흐름:"
echo "  인터넷 → IGW → 퍼블릭서브넷(웹서버) → 프라이빗서브넷(DB)"
echo "  프라이빗서브넷 → NAT GW → IGW → 인터넷 (아웃바운드만)"
echo "========================================"