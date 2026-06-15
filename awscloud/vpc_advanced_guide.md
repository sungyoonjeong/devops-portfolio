# 🌐 AWS VPC 심화 가이드
> 보안그룹 · NACL · 라우팅테이블 · NAT 게이트웨이

---

## 목차
1. [VPC 전체 구조](#1-vpc-전체-구조)
2. [퍼블릭 vs 프라이빗 서브넷](#2-퍼블릭-vs-프라이빗-서브넷)
3. [인터넷 게이트웨이 (IGW)](#3-인터넷-게이트웨이-igw)
4. [라우팅 테이블](#4-라우팅-테이블)
5. [보안 그룹 (Security Group)](#5-보안-그룹-security-group)
6. [NACL (Network ACL)](#6-nacl-network-acl)
7. [NAT 게이트웨이](#7-nat-게이트웨이)
8. [보안 그룹 vs NACL 비교](#8-보안-그룹-vs-nacl-비교)
9. [LocalStack 전체 실습](#9-localstack-전체-실습)
10. [면접 핵심 Q&A](#10-면접-핵심-qa)
11. [핵심 개념 치트시트](#11-핵심-개념-치트시트)

---

## 1. VPC 전체 구조

```
인터넷
  ↓
인터넷 게이트웨이 (IGW)
  ↓
라우팅 테이블 (퍼블릭용)
  ↓
NACL (서브넷 방화벽)
  ↓
┌─────────────────────────────────────────┐
│              VPC (10.0.0.0/16)          │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │       퍼블릭 서브넷              │    │
│  │       10.0.1.0/24              │    │
│  │  EC2 (웹서버) · ALB            │    │
│  │  보안그룹 (인스턴스 방화벽)     │    │
│  └─────────────────────────────────┘    │
│                   ↕ (VPC 내부 통신)     │
│  ┌─────────────────────────────────┐    │
│  │       프라이빗 서브넷            │    │
│  │       10.0.2.0/24              │    │
│  │  RDS (DB서버) · ElastiCache    │    │
│  │  보안그룹 (인스턴스 방화벽)     │    │
│  └─────────────────────────────────┘    │
│                   ↓ (외부 접근 필요시)  │
│            NAT 게이트웨이              │
└─────────────────────────────────────────┘
```

### 데이터 흐름

```
[외부 → 웹서버]
인터넷 → IGW → 라우팅테이블 → NACL → 보안그룹 → EC2

[웹서버 → DB서버]
EC2(웹) → 보안그룹 → NACL → 보안그룹 → RDS(DB)

[프라이빗 서버 → 인터넷]
RDS → NAT 게이트웨이 → IGW → 인터넷
(역방향 불가 = 인터넷에서 RDS 직접 접근 불가)
```

---

## 2. 퍼블릭 vs 프라이빗 서브넷

### 퍼블릭 서브넷

```
정의:
  인터넷과 직접 통신 가능한 서브넷
  라우팅 테이블에 IGW 경로(0.0.0.0/0 → IGW) 있음

주로 배치되는 것:
  웹 서버 (EC2)
  로드 밸런서 (ALB)
  배스천 호스트 (SSH 접속 경유)
  NAT 게이트웨이

특징:
  퍼블릭 IP 또는 Elastic IP 할당 가능
  외부에서 직접 접근 가능
```

### 프라이빗 서브넷

```
정의:
  인터넷과 직접 통신 불가한 서브넷
  라우팅 테이블에 IGW 경로 없음

주로 배치되는 것:
  DB 서버 (RDS)
  캐시 서버 (ElastiCache)
  애플리케이션 서버 (내부 API)
  K8s 워커 노드

특징:
  퍼블릭 IP 없음
  외부에서 직접 접근 불가
  NAT 통해서만 인터넷 아웃바운드 가능
```

### CCNP 연결

```
퍼블릭 서브넷 = DMZ (비무장지대)
프라이빗 서브넷 = 내부망 (Inside Network)
IGW = 인터넷 라우터
NACL = 라우터의 ACL
보안 그룹 = 호스트 기반 방화벽
NAT GW = NAT 장비
```

---

## 3. 인터넷 게이트웨이 (IGW)

```
정의:
  VPC ↔ 인터넷을 연결하는 통로
  VPC 당 하나만 연결 가능
  고가용성(HA) 자동 지원 (AWS가 관리)
  수평 확장 자동 (트래픽 폭발해도 문제 없음)

조건:
  IGW를 VPC에 연결해도
  라우팅 테이블에 IGW 경로(0.0.0.0/0)를 추가해야
  실제로 인터넷 통신 가능

비용:
  IGW 자체는 무료
  데이터 전송 비용만 발생
```

```bash
# IGW 생성
awslocal ec2 create-internet-gateway

# VPC에 연결
awslocal ec2 attach-internet-gateway \
  --internet-gateway-id igw-xxx \
  --vpc-id vpc-xxx

# IGW 목록 확인
awslocal ec2 describe-internet-gateways \
  --query 'InternetGateways[*].[InternetGatewayId,Attachments]'
```

---

## 4. 라우팅 테이블

```
정의:
  네트워크 트래픽이 어디로 가야하는지 결정하는 규칙표
  서브넷마다 하나의 라우팅 테이블 연결

CCNP 연결:
  라우터의 Routing Table과 완전히 동일 개념
```

### 퍼블릭 서브넷 라우팅 테이블

```
목적지          대상
10.0.0.0/16    local    ← VPC 내부 통신
0.0.0.0/0      igw-xxx  ← 인터넷 (IGW로)
```

### 프라이빗 서브넷 라우팅 테이블

```
목적지          대상
10.0.0.0/16    local     ← VPC 내부 통신
0.0.0.0/0      nat-xxx   ← NAT 게이트웨이로 (인터넷 아웃바운드)
```

### 라우팅 우선순위

```
더 구체적인 경로가 우선
10.0.1.0/24 > 10.0.0.0/16 > 0.0.0.0/0
(가장 구체적인 것 먼저 매칭)
```

```bash
# 라우팅 테이블 생성
RTB_ID=$(awslocal ec2 create-route-table \
  --vpc-id $VPC_ID \
  --query 'RouteTable.RouteTableId' \
  --output text)

# 인터넷 경로 추가
awslocal ec2 create-route \
  --route-table-id $RTB_ID \
  --destination-cidr-block 0.0.0.0/0 \
  --gateway-id $IGW_ID

# 서브넷에 연결
awslocal ec2 associate-route-table \
  --subnet-id $PUBLIC_SUBNET \
  --route-table-id $RTB_ID

# 라우팅 테이블 확인
awslocal ec2 describe-route-tables \
  --route-table-ids $RTB_ID \
  --query 'RouteTables[*].Routes' \
  --output table
```

---

## 5. 보안 그룹 (Security Group)

### 개념

```
정의:
  인스턴스(EC2·RDS 등) 단위의 가상 방화벽
  인바운드·아웃바운드 트래픽 제어

특성:
  Stateful:
    인바운드 허용 시 응답 트래픽 자동 허용
    (별도 아웃바운드 규칙 불필요)

  허용 규칙만 존재:
    기본적으로 모든 인바운드 거부
    명시적으로 허용한 것만 통과
    거부 규칙 추가 불가 (NACL과 차이)

  여러 인스턴스에 적용 가능:
    하나의 보안 그룹을 여러 EC2에 연결 가능
```

### 실전 예시

```
웹 서버 보안 그룹 (web-sg):
  인바운드:
    TCP 80  (HTTP)  0.0.0.0/0  허용
    TCP 443 (HTTPS) 0.0.0.0/0  허용
    TCP 22  (SSH)   내 IP만    허용
  아웃바운드:
    전체 허용 (기본값)

DB 서버 보안 그룹 (db-sg):
  인바운드:
    TCP 3306 (MySQL) web-sg에서만 허용  ← 보안그룹 참조!
  아웃바운드:
    전체 허용

★ DB는 인터넷(0.0.0.0/0)이 아닌
  웹서버 보안그룹(web-sg)으로만 접근 허용
  → 가장 안전한 구성
```

```bash
# 보안 그룹 생성
SG_ID=$(awslocal ec2 create-security-group \
  --group-name web-sg \
  --description "Web server security group" \
  --vpc-id $VPC_ID \
  --query 'GroupId' \
  --output text)

# HTTP 허용 (80)
awslocal ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

# HTTPS 허용 (443)
awslocal ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# SSH 허용 (22)
awslocal ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0

# 보안 그룹 규칙 확인
awslocal ec2 describe-security-groups \
  --group-ids $SG_ID \
  --query 'SecurityGroups[*].[GroupName,IpPermissions]' \
  --output table

# 규칙 삭제
awslocal ec2 revoke-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 22 \
  --cidr 0.0.0.0/0
```

---

## 6. NACL (Network ACL)

### 개념

```
정의:
  서브넷 단위의 방화벽
  모든 서브넷에는 기본 NACL이 자동 연결됨

특성:
  Stateless:
    인바운드 허용해도 아웃바운드 별도 설정 필요
    응답 트래픽도 명시적으로 허용해야 함

  허용·거부 규칙 모두 존재:
    규칙 번호 낮은 것이 우선 적용
    마지막에 * (전체 거부) 규칙 존재

  서브넷에 연결:
    하나의 서브넷에 하나의 NACL
    하나의 NACL은 여러 서브넷에 적용 가능

기본 NACL:
  모든 인바운드·아웃바운드 허용
  (보안 취약 → 커스텀 NACL 사용 권장)
```

### 규칙 번호 동작 방식

```
인바운드 규칙 예시:
  규칙 100: TCP 80  허용
  규칙 200: TCP 443 허용
  규칙 *:   전체   거부  ← 항상 마지막

→ 80포트 요청: 규칙 100 매칭 → 허용
→ 22포트 요청: 100·200 불일치 → * 매칭 → 거부
```

### Stateless 주의사항

```
HTTP 요청·응답 과정:
  클라이언트 → EC2: 80포트 요청
  EC2 → 클라이언트: 임시포트(1024~65535)로 응답

NACL 설정 시:
  인바운드: TCP 80 허용
  아웃바운드: TCP 1024-65535 허용 ← 반드시 필요!
  (Stateless이므로 응답도 명시적 허용)
```

```bash
# NACL 생성
NACL_ID=$(awslocal ec2 create-network-acl \
  --vpc-id $VPC_ID \
  --query 'NetworkAcl.NetworkAclId' \
  --output text)

# 인바운드: HTTP 허용 (규칙 100)
awslocal ec2 create-network-acl-entry \
  --network-acl-id $NACL_ID \
  --rule-number 100 \
  --protocol tcp \
  --port-range From=80,To=80 \
  --cidr-block 0.0.0.0/0 \
  --rule-action allow \
  --ingress

# 인바운드: HTTPS 허용 (규칙 200)
awslocal ec2 create-network-acl-entry \
  --network-acl-id $NACL_ID \
  --rule-number 200 \
  --protocol tcp \
  --port-range From=443,To=443 \
  --cidr-block 0.0.0.0/0 \
  --rule-action allow \
  --ingress

# 아웃바운드: 임시포트 허용 (응답 트래픽)
awslocal ec2 create-network-acl-entry \
  --network-acl-id $NACL_ID \
  --rule-number 100 \
  --protocol tcp \
  --port-range From=1024,To=65535 \
  --cidr-block 0.0.0.0/0 \
  --rule-action allow \
  --egress

# 서브넷에 NACL 연결
awslocal ec2 replace-network-acl-association \
  --network-acl-id $NACL_ID \
  --association-id [기존 연결 ID]

# NACL 확인
awslocal ec2 describe-network-acls \
  --network-acl-ids $NACL_ID \
  --query 'NetworkAcls[*].Entries' \
  --output table
```

---

## 7. NAT 게이트웨이

```
정의:
  프라이빗 서브넷 → 인터넷 단방향 통신 제공
  인터넷 → 프라이빗 서브넷 직접 접근 불가

배치 위치:
  퍼블릭 서브넷에 배치 (Elastic IP 필요)
  프라이빗 서브넷의 라우팅 테이블에서 참조

사용 예시:
  프라이빗 서브넷의 EC2가 apt update 할 때
  프라이빗 서브넷의 Lambda가 외부 API 호출할 때

CCNP 연결:
  NAT (Network Address Translation)과 동일
  사설IP → 공인IP 변환

비용 주의:
  NAT 게이트웨이 = 시간당 요금 + 데이터 전송 요금
  실제 AWS에서는 비용 발생 (프리티어 미포함)
  → LocalStack에서는 무료로 실습

NAT 게이트웨이 vs NAT 인스턴스:
  NAT 게이트웨이: AWS 관리형, 고가용성 자동, 비쌈
  NAT 인스턴스:  EC2 직접 운영, 관리 필요, 저렴
```

```bash
# Elastic IP 할당 (NAT GW에 필요)
EIP=$(awslocal ec2 allocate-address \
  --query 'AllocationId' \
  --output text)
echo "Elastic IP: $EIP"

# NAT 게이트웨이 생성 (퍼블릭 서브넷에)
NAT_ID=$(awslocal ec2 create-nat-gateway \
  --subnet-id $PUBLIC_SUBNET \
  --allocation-id $EIP \
  --query 'NatGateway.NatGatewayId' \
  --output text)
echo "NAT GW: $NAT_ID"

# 프라이빗 서브넷 라우팅 테이블 생성
PRIVATE_RTB=$(awslocal ec2 create-route-table \
  --vpc-id $VPC_ID \
  --query 'RouteTable.RouteTableId' \
  --output text)

# 프라이빗 라우팅 테이블에 NAT 경로 추가
awslocal ec2 create-route \
  --route-table-id $PRIVATE_RTB \
  --destination-cidr-block 0.0.0.0/0 \
  --nat-gateway-id $NAT_ID

# 프라이빗 서브넷에 연결
awslocal ec2 associate-route-table \
  --subnet-id $PRIVATE_SUBNET \
  --route-table-id $PRIVATE_RTB

# NAT GW 상태 확인
awslocal ec2 describe-nat-gateways \
  --query 'NatGateways[*].[NatGatewayId,State]' \
  --output table
```

---

## 8. 보안 그룹 vs NACL 비교

| 항목 | 보안 그룹 | NACL |
|------|---------|------|
| 적용 단위 | 인스턴스 (EC2 등) | 서브넷 |
| Stateful/Stateless | **Stateful** (응답 자동) | **Stateless** (응답 별도 설정) |
| 규칙 종류 | 허용만 | 허용 + 거부 |
| 규칙 우선순위 | 모든 규칙 평가 후 결정 | 번호 낮은 것 우선 |
| 기본 동작 | 인바운드 전체 거부 | 전체 허용 |
| 체이닝 | 여러 SG 적용 가능 | 서브넷당 1개 |

```
★ SAA 시험 단골 문제:
  "보안 그룹은 Stateful, NACL은 Stateless"
  반드시 암기
```

---

## 9. LocalStack 전체 실습

아래 스크립트를 저장 후 실행:

```bash
#!/bin/bash
# vpc_advanced_practice.sh

echo "=== VPC 심화 실습 시작 ==="

# 1. VPC 생성
VPC_ID=$(awslocal ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --query 'Vpc.VpcId' --output text)
echo "[1] VPC: $VPC_ID"

# 2. 서브넷 생성
PUBLIC_SUBNET=$(awslocal ec2 create-subnet \
  --vpc-id $VPC_ID --cidr-block 10.0.1.0/24 \
  --query 'Subnet.SubnetId' --output text)
PRIVATE_SUBNET=$(awslocal ec2 create-subnet \
  --vpc-id $VPC_ID --cidr-block 10.0.2.0/24 \
  --query 'Subnet.SubnetId' --output text)
echo "[2] 퍼블릭: $PUBLIC_SUBNET / 프라이빗: $PRIVATE_SUBNET"

# 3. IGW 생성 및 연결
IGW_ID=$(awslocal ec2 create-internet-gateway \
  --query 'InternetGateway.InternetGatewayId' --output text)
awslocal ec2 attach-internet-gateway \
  --internet-gateway-id $IGW_ID --vpc-id $VPC_ID
echo "[3] IGW: $IGW_ID (VPC에 연결 완료)"

# 4. 퍼블릭 라우팅 테이블
RTB_PUBLIC=$(awslocal ec2 create-route-table \
  --vpc-id $VPC_ID --query 'RouteTable.RouteTableId' --output text)
awslocal ec2 create-route \
  --route-table-id $RTB_PUBLIC \
  --destination-cidr-block 0.0.0.0/0 \
  --gateway-id $IGW_ID
awslocal ec2 associate-route-table \
  --subnet-id $PUBLIC_SUBNET --route-table-id $RTB_PUBLIC
echo "[4] 퍼블릭 라우팅 테이블: $RTB_PUBLIC"

# 5. 보안 그룹
SG_WEB=$(awslocal ec2 create-security-group \
  --group-name web-sg --description "Web SG" \
  --vpc-id $VPC_ID --query 'GroupId' --output text)
awslocal ec2 authorize-security-group-ingress \
  --group-id $SG_WEB --protocol tcp --port 80 --cidr 0.0.0.0/0
awslocal ec2 authorize-security-group-ingress \
  --group-id $SG_WEB --protocol tcp --port 443 --cidr 0.0.0.0/0
awslocal ec2 authorize-security-group-ingress \
  --group-id $SG_WEB --protocol tcp --port 22 --cidr 0.0.0.0/0
echo "[5] 보안그룹: $SG_WEB (HTTP·HTTPS·SSH 허용)"

# 6. NAT 게이트웨이
EIP=$(awslocal ec2 allocate-address \
  --query 'AllocationId' --output text)
NAT_ID=$(awslocal ec2 create-nat-gateway \
  --subnet-id $PUBLIC_SUBNET --allocation-id $EIP \
  --query 'NatGateway.NatGatewayId' --output text)
echo "[6] NAT GW: $NAT_ID"

# 7. 프라이빗 라우팅 테이블
RTB_PRIVATE=$(awslocal ec2 create-route-table \
  --vpc-id $VPC_ID --query 'RouteTable.RouteTableId' --output text)
awslocal ec2 create-route \
  --route-table-id $RTB_PRIVATE \
  --destination-cidr-block 0.0.0.0/0 \
  --nat-gateway-id $NAT_ID
awslocal ec2 associate-route-table \
  --subnet-id $PRIVATE_SUBNET --route-table-id $RTB_PRIVATE
echo "[7] 프라이빗 라우팅 테이블: $RTB_PRIVATE"

echo ""
echo "=== 전체 구성 완료 ==="
echo "VPC:             $VPC_ID  (10.0.0.0/16)"
echo "퍼블릭 서브넷:   $PUBLIC_SUBNET (10.0.1.0/24)"
echo "프라이빗 서브넷: $PRIVATE_SUBNET (10.0.2.0/24)"
echo "IGW:             $IGW_ID"
echo "NAT GW:          $NAT_ID"
echo "웹 보안그룹:     $SG_WEB"
```

---

## 10. 면접 핵심 Q&A

**Q. 퍼블릭과 프라이빗 서브넷 차이는?**
```
라우팅 테이블에 IGW 경로(0.0.0.0/0 → IGW)가
있으면 퍼블릭, 없으면 프라이빗 서브넷입니다.
```

**Q. 보안 그룹과 NACL 차이는?**
```
보안 그룹은 인스턴스 단위의 Stateful 방화벽으로
허용 규칙만 존재합니다.
NACL은 서브넷 단위의 Stateless 방화벽으로
허용·거부 규칙이 모두 존재합니다.
NACL은 응답 트래픽도 별도로 허용해야 합니다.
```

**Q. NAT 게이트웨이가 왜 필요한가?**
```
프라이빗 서브넷의 서버가 보안상 인터넷에
직접 노출되면 안 되지만, 패키지 업데이트 등
아웃바운드 인터넷 통신은 필요합니다.
NAT 게이트웨이는 프라이빗→인터넷 단방향 통신만 허용해
보안을 유지하면서 아웃바운드를 가능하게 합니다.
```

**Q. CCNP 경험이 VPC 이해에 어떻게 도움됐나?**
```
CCNP에서 배운 서브네팅, ACL, NAT, 라우팅 테이블
개념이 VPC와 1:1로 매핑됩니다.
VPC = 가상 네트워크, NACL = 라우터 ACL,
보안그룹 = 호스트 방화벽, NAT GW = NAT 장비로
이해해서 학습 속도가 빨랐습니다.
```

---

## 11. 핵심 개념 치트시트

| 개념 | 한줄 요약 | CCNP 연결 |
|------|---------|---------|
| VPC | AWS 안의 격리된 가상 네트워크 | VLAN |
| 서브넷 | VPC를 나눈 단위 (퍼블릭/프라이빗) | IP 서브네팅 |
| IGW | VPC ↔ 인터넷 연결 통로 | 인터넷 라우터 |
| 라우팅 테이블 | 트래픽 경로 결정 규칙 | Routing Table |
| 보안 그룹 | 인스턴스 방화벽, Stateful, 허용만 | 호스트 방화벽 |
| NACL | 서브넷 방화벽, Stateless, 허용+거부 | 라우터 ACL |
| NAT GW | 프라이빗→인터넷 단방향 | NAT 장비 |
| Elastic IP | 고정 공인 IP | Static Public IP |

---

