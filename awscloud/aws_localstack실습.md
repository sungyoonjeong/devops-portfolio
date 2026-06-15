# ☁️ AWS LocalStack 실습 
> IAM · S3 · EC2 · VPC — 개념 + 실습 완전 정리

---

## 목차
1. [LocalStack이란](#1-localstack이란)
2. [설치 및 실행](#2-설치-및-실행)
3. [AWS CLI 설정](#3-aws-cli-설정)
4. [IAM 실습](#4-iam-실습)
5. [S3 실습](#5-s3-실습)
6. [EC2 실습](#6-ec2-실습)
7. [VPC 실습](#7-vpc-실습)
8. [핵심 개념 정리](#8-핵심-개념-정리)
9. [자주 하는 실수](#9-자주-하는-실수)
10. [명령어 치트시트](#10-명령어-치트시트)

---

## 1. LocalStack이란

```
LocalStack = AWS 서비스를 로컬 PC에서 에뮬레이션하는 도구

왜 쓰나:
  실제 AWS = 신용카드 등록 필요 + 비용 발생 가능
  LocalStack = 무료, 로컬에서 실제와 동일한 명령어 실습 가능

동작 원리:
  Docker 컨테이너로 실행
  localhost:4566 포트에서 AWS API 에뮬레이션
  awslocal = aws --endpoint-url=http://localhost:4566 와 동일

지원 서비스 (무료):
  S3, IAM, EC2, VPC, Lambda, SQS, SNS 등 핵심 서비스
```

---

## 2. 설치 및 실행

### 설치

```bash
pip install localstack
pip install awscli-local
```

```
localstack:      AWS 에뮬레이터 본체
awscli-local:    LocalStack 전용 AWS CLI (awslocal 명령어)
```

### 실행

```bash
# Auth Token과 함께 실행 (무료 계정 토큰)
LOCALSTACK_AUTH_TOKEN=ls-xxxxx localstack start -d

# -d: 백그라운드(detached) 실행
# Docker 컨테이너로 자동 실행됨
```

### 상태 확인

```bash
localstack status services
# 각 서비스가 "running" 상태인지 확인

docker ps
# LocalStack 컨테이너 실행 중인지 확인
# STATUS: Up ... (healthy) 면 정상
```

---

## 3. AWS CLI 설정

```bash
aws configure
# AWS Access Key ID:     test
# AWS Secret Access Key: test
# Default region name:   us-east-1
# Default output format: json
```

```
실제 AWS: 진짜 Access Key 필요
LocalStack: 아무 값이나 가능 (test/test)

region us-east-1:
  AWS 버지니아 북부 데이터센터
  LocalStack은 실제로 로컬이지만 설정 필요

output json:
  CLI 결과를 JSON 형식으로 출력
  table: 테이블 형식 / text: 텍스트 형식
```

---

## 4. IAM 실습

### IAM이란

```
IAM = Identity and Access Management
  AWS 리소스에 대한 접근 권한을 관리하는 서비스

핵심 구성요소:
  User(사용자): AWS를 사용하는 사람 또는 프로그램
  Group(그룹): 여러 사용자를 묶어 한 번에 권한 관리
  Policy(정책): "무엇을 할 수 있다"는 권한 규칙 (JSON 문서)
  Role(역할): 사람이 아닌 AWS 서비스(EC2 등)에 부여하는 임시 권한

황금 원칙: 최소 권한 (Least Privilege)
  → 필요한 권한만 딱 그만큼만 부여
  → 과도한 권한 = 보안 위협

실생활 비유:
  IAM = 회사 출입증 시스템
  User = 직원
  Group = 팀 (개발팀, 운영팀)
  Policy = 출입 가능 구역 규칙
  Role = 특정 업무 수행 시 임시 배지
```

### IAM 실습 명령어

```bash
# ── 사용자 생성 ──────────────────────────────────
awslocal iam create-user --user-name devops-user
# devops-user 라는 IAM 사용자 생성
# --user-name: 사용자 이름 지정

# 사용자 목록 확인
awslocal iam list-users
# 현재 계정의 모든 IAM 사용자 출력

# ── 그룹 생성 ────────────────────────────────────
awslocal iam create-group --group-name devops-team
# devops-team 그룹 생성
# 여러 사용자를 묶어 한 번에 권한 관리 가능

# 그룹에 사용자 추가
awslocal iam add-user-to-group \
  --user-name devops-user \
  --group-name devops-team
# devops-user를 devops-team 그룹에 소속

# 그룹 목록 확인
awslocal iam list-groups

# ── 정책 연결 ────────────────────────────────────
awslocal iam attach-user-policy \
  --user-name devops-user \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
# policy-arn: 정책의 고유 주소 (ARN = Amazon Resource Name)
# AmazonS3FullAccess: AWS가 미리 만들어둔 S3 전체 권한 정책

# 연결된 정책 확인
awslocal iam list-attached-user-policies \
  --user-name devops-user

# 그룹에 정책 연결
awslocal iam attach-group-policy \
  --group-name devops-team \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
# ReadOnlyAccess: S3 읽기만 가능 (업로드 불가)

# ── Access Key 생성 ──────────────────────────────
awslocal iam create-access-key \
  --user-name devops-user
# 프로그래밍 방식으로 AWS 접근할 때 쓰는 키 발급
# → Access Key ID + Secret Access Key 출력

# ── 정리 ─────────────────────────────────────────
awslocal iam detach-user-policy \
  --user-name devops-user \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
# 정책 분리 (삭제 전 필수)

awslocal iam delete-user --user-name devops-user
# 사용자 삭제
```

---

## 5. S3 실습

### S3란

```
S3 = Simple Storage Service
  파일(객체)을 저장하는 클라우드 스토리지

핵심 개념:
  버킷(Bucket): 최상위 컨테이너 (폴더 개념)
  객체(Object): 버킷 안에 저장되는 실제 파일
  키(Key):      객체의 경로+이름 (예: logs/2026/app.log)

특징:
  파일 크기 5TB까지 저장 가능
  99.999999999% 내구성 (11 nine)
  버킷 이름은 전 세계에서 고유해야 함 (실제 AWS)

DevOps 활용:
  CI/CD 빌드 산출물 저장
  로그 파일 장기 보관
  K8s etcd 백업 저장
  정적 웹사이트 호스팅

실생활 비유:
  S3 = 구글 드라이브
  버킷 = 구글 드라이브의 폴더
  객체 = 폴더 안의 파일
```

### S3 실습 명령어

```bash
# ── 버킷 생성 ────────────────────────────────────
awslocal s3 mb s3://devops-bucket-jsy
# mb = make bucket
# s3:// 로 시작하는 것이 S3 주소 형식

# 버킷 목록 확인
awslocal s3 ls

# ── 파일 업로드 ──────────────────────────────────
echo "Hello DevOps!" > hello.txt
awslocal s3 cp hello.txt s3://devops-bucket-jsy/
# cp = copy (로컬 → S3 업로드)
# upload: ./hello.txt to s3://devops-bucket-jsy/hello.txt

# 폴더 경로 지정해서 업로드
awslocal s3 cp hello.txt s3://devops-bucket-jsy/logs/hello.txt
# logs/ 라는 경로(키)에 저장
# S3에는 실제 폴더가 없고 키(경로) 이름으로 구분

# ── 버킷 내 목록 확인 ───────────────────────────
awslocal s3 ls s3://devops-bucket-jsy/
awslocal s3 ls s3://devops-bucket-jsy/logs/

# 전체 목록 재귀 확인
awslocal s3 ls s3://devops-bucket-jsy/ --recursive

# ── 파일 다운로드 ────────────────────────────────
awslocal s3 cp s3://devops-bucket-jsy/hello.txt ./downloaded.txt
# download: s3://... to ./downloaded.txt
cat downloaded.txt
# → Hello DevOps! 출력되면 성공

# ── 폴더 동기화 (sync) ──────────────────────────
mkdir -p ./myfiles
echo "file1" > ./myfiles/file1.txt
echo "file2" > ./myfiles/file2.txt
awslocal s3 sync ./myfiles s3://devops-bucket-jsy/myfiles/
# sync: 변경된 파일만 업로드 (전체 cp보다 효율적)
# CI/CD에서 빌드 결과물 배포 시 자주 사용

# ── 파일·버킷 삭제 ──────────────────────────────
awslocal s3 rm s3://devops-bucket-jsy/hello.txt
# 단일 파일 삭제

awslocal s3 rm s3://devops-bucket-jsy/ --recursive
# 버킷 안 전체 파일 삭제

awslocal s3 rb s3://devops-bucket-jsy
# rb = remove bucket (버킷 삭제, 비어있어야 가능)

awslocal s3 rb s3://devops-bucket-jsy --force
# --force: 내용물 있어도 강제 삭제
```

---

## 6. EC2 실습

### EC2란

```
EC2 = Elastic Compute Cloud
  클라우드에서 실행하는 가상 서버 (VM과 동일한 개념)

핵심 개념:
  인스턴스(Instance): 실행 중인 가상 서버 1대
  AMI(Amazon Machine Image): 인스턴스 생성 시 쓰는 OS 이미지 (틀)
  인스턴스 타입: 서버 사양 (t2.micro = 1vCPU, 1GB RAM)
  키 페어(Key Pair): SSH 접속 시 사용하는 공개키/개인키 쌍
  보안 그룹(Security Group): 인바운드/아웃바운드 트래픽 방화벽

인스턴스 상태:
  pending → running → stopping → stopped → terminated
  terminated = 완전 삭제 (복구 불가)

DevOps 활용:
  애플리케이션 서버
  CI/CD 빌드 서버
  K8s 워커 노드
  배스천 호스트 (보안 접속 경유 서버)

실생활 비유:
  EC2 = 클라우드에서 빌려 쓰는 컴퓨터
  AMI = 컴퓨터에 깔린 OS (Ubuntu, Windows 등)
  키 페어 = 집 열쇠 (개인키로만 접속 가능)
```

### EC2 실습 명령어

```bash
# ── AMI 목록 확인 ────────────────────────────────
awslocal ec2 describe-images \
  --query 'Images[*].[ImageId,Name]' \
  --output table
# 사용 가능한 AMI 목록 테이블 형식으로 출력
# LocalStack에 내장된 AMI 목록

# ── 키 페어 생성 ─────────────────────────────────
awslocal ec2 create-key-pair \
  --key-name devops-key \
  --query 'KeyMaterial' \
  --output text > devops-key.pem
# --key-name: 키 페어 이름
# --query 'KeyMaterial': 개인키 내용만 추출
# > devops-key.pem: 파일로 저장

chmod 400 devops-key.pem
# 개인키 파일 권한을 소유자 읽기 전용으로 변경
# SSH 접속 시 권한이 너무 넓으면 거부당함

# ── 인스턴스 실행 ────────────────────────────────
awslocal ec2 run-instances \
  --image-id ami-785db401 \
  --instance-type t2.micro \
  --key-name devops-key \
  --count 1
# --image-id: 사용할 AMI ID (Ubuntu 16.04)
# --instance-type: 서버 사양
# --key-name: SSH 접속용 키 페어
# --count: 생성할 인스턴스 수

# ── 인스턴스 목록 확인 ──────────────────────────
awslocal ec2 describe-instances \
  --query 'Reservations[*].Instances[*].[InstanceId,State.Name]' \
  --output table
# InstanceId: i-xxxxxxxx 형식
# State.Name: pending / running / stopped / terminated

# ── 인스턴스 중지 ────────────────────────────────
awslocal ec2 stop-instances \
  --instance-ids i-xxxxxxxx
# running → stopping → stopped
# 중지해도 과금은 계속 (EBS 스토리지 비용)

# ── 인스턴스 시작 ────────────────────────────────
awslocal ec2 start-instances \
  --instance-ids i-xxxxxxxx
# stopped → pending → running

# ── 인스턴스 종료(삭제) ─────────────────────────
awslocal ec2 terminate-instances \
  --instance-ids i-xxxxxxxx
# running → shutting-down → terminated
# 완전 삭제 (복구 불가!)
# 종료 후 과금 없음
```

---

## 7. VPC 실습

### VPC란

```
VPC = Virtual Private Cloud
  AWS 안의 나만의 격리된 가상 네트워크

핵심 개념:
  VPC: 가상 네트워크 전체 (CIDR 블록으로 IP 범위 정의)
  서브넷(Subnet): VPC를 더 작게 나눈 네트워크 단위
    퍼블릭 서브넷: 인터넷 직접 접근 가능
    프라이빗 서브넷: 인터넷 직접 접근 불가 (DB 서버 등)
  인터넷 게이트웨이: VPC ↔ 인터넷 연결 통로
  라우팅 테이블: 네트워크 트래픽 경로 규칙
  보안 그룹: 인스턴스 단위 방화벽 (포트 제어)

CIDR 표기:
  10.0.0.0/16 = 10.0.0.0 ~ 10.0.255.255 (65,536개 IP)
  10.0.1.0/24 = 10.0.1.0 ~ 10.0.1.255 (256개 IP)

CCNP 지식 연결:
  VPC = 온프레미스의 VLAN 개념
  서브넷 = IP 서브네팅
  보안 그룹 = ACL (Access Control List)
  → CCNP 지식이 클라우드 네트워크 이해에 직결

DevOps 활용:
  퍼블릭 서브넷: 웹 서버, 로드밸런서
  프라이빗 서브넷: DB 서버, 캐시 서버
  K8s 클러스터를 VPC 내 프라이빗 서브넷에 배치
```

```bash
# ── VPC 생성 ─────────────────────────────────────
awslocal ec2 create-vpc --cidr-block 10.0.0.0/16
# CIDR 10.0.0.0/16 = 사용 가능한 IP 범위

# VPC 목록 확인
awslocal ec2 describe-vpcs \
  --query 'Vpcs[*].[VpcId,CidrBlock,State]' \
  --output table

# ── 서브넷 생성 ──────────────────────────────────
awslocal ec2 create-subnet \
  --vpc-id vpc-xxxxxxxx \
  --cidr-block 10.0.1.0/24
# VPC 안에 /24 서브넷 생성
# 실제 사용 가능 IP: 256 - 5(예약) = 251개

# 서브넷 확인
awslocal ec2 describe-subnets \
  --query 'Subnets[*].[SubnetId,CidrBlock,VpcId]' \
  --output table

# ── 인터넷 게이트웨이 생성 ──────────────────────
awslocal ec2 create-internet-gateway
# VPC ↔ 인터넷 연결 통로 생성

# VPC에 연결
awslocal ec2 attach-internet-gateway \
  --internet-gateway-id igw-xxxxxxxx \
  --vpc-id vpc-xxxxxxxx
```

---

## 8. 핵심 개념 정리

| 서비스 | 한줄 요약 |
|--------|---------|
| **IAM User** | AWS 접근하는 사람/프로그램 |
| **IAM Group** | 여러 사용자 묶음 → 한 번에 권한 관리 |
| **IAM Policy** | 권한 규칙 (뭘 할 수 있는지 정의) |
| **IAM Role** | EC2 등 서비스에 부여하는 임시 권한 |
| **S3 Bucket** | 파일 저장 컨테이너 (폴더 개념) |
| **S3 Object** | 버킷 안의 실제 파일 |
| **S3 Key** | 객체의 경로+이름 |
| **EC2 Instance** | 클라우드 가상 서버 1대 |
| **AMI** | EC2 생성 시 사용하는 OS 이미지 |
| **키 페어** | SSH 접속용 공개키/개인키 |
| **VPC** | AWS 안의 격리된 가상 네트워크 |
| **서브넷** | VPC를 나눈 더 작은 네트워크 |
| **보안 그룹** | 인스턴스 단위 방화벽 |

---

## 9. 자주 하는 실수

```bash
# 1. AMI ID 형식 오류
--image-id abcd1234    # ❌ ami- 로 시작해야 함
--image-id ami-785db401 # ✅

# 2. S3 다운로드 경로 오류
# 업로드를 logs/hello.txt로 했는데
awslocal s3 cp s3://bucket/hello.txt ./file   # ❌ 404 에러
awslocal s3 cp s3://bucket/logs/hello.txt ./file # ✅

# 3. 버킷 삭제 시 비어있지 않음
awslocal s3 rb s3://bucket    # ❌ 파일 있으면 에러
awslocal s3 rb s3://bucket --force # ✅ 강제 삭제

# 4. 개인키 파일 권한
ssh -i devops-key.pem ...  # ❌ 권한 넓으면 거부
chmod 400 devops-key.pem   # ✅ 먼저 권한 설정

# 5. 쿼리 오타
--query 'Instances[*].[InstanceID,State.Name]'  # ❌ ID 대문자
--query 'Instances[*].[InstanceId,State.Name]'  # ✅ Id 소문자

# 6. LocalStack 안 띄우고 명령어 실행
# Error: could not connect to LocalStack
LOCALSTACK_AUTH_TOKEN=ls-xxx localstack start -d  # 먼저 실행
```

---

## 10. 명령어 치트시트

### IAM
```bash
awslocal iam create-user --user-name [이름]
awslocal iam list-users
awslocal iam create-group --group-name [이름]
awslocal iam add-user-to-group --user-name [u] --group-name [g]
awslocal iam attach-user-policy --user-name [u] --policy-arn [arn]
awslocal iam list-attached-user-policies --user-name [u]
awslocal iam create-access-key --user-name [u]
awslocal iam delete-user --user-name [u]
```

### S3
```bash
awslocal s3 mb s3://[버킷명]
awslocal s3 ls
awslocal s3 ls s3://[버킷명]/ --recursive
awslocal s3 cp [파일] s3://[버킷]/
awslocal s3 cp s3://[버킷]/[파일] ./[로컬파일]
awslocal s3 sync ./[폴더] s3://[버킷]/[경로]/
awslocal s3 rm s3://[버킷]/[파일]
awslocal s3 rb s3://[버킷] --force
```

### EC2
```bash
awslocal ec2 describe-images --query 'Images[*].[ImageId,Name]' --output table
awslocal ec2 create-key-pair --key-name [이름] --query 'KeyMaterial' --output text > key.pem
awslocal ec2 run-instances --image-id [ami] --instance-type t2.micro --key-name [키] --count 1
awslocal ec2 describe-instances --query 'Reservations[*].Instances[*].[InstanceId,State.Name]' --output table
awslocal ec2 stop-instances --instance-ids [id]
awslocal ec2 start-instances --instance-ids [id]
awslocal ec2 terminate-instances --instance-ids [id]
```

### VPC
```bash
awslocal ec2 create-vpc --cidr-block 10.0.0.0/16
awslocal ec2 describe-vpcs --query 'Vpcs[*].[VpcId,CidrBlock,State]' --output table
awslocal ec2 create-subnet --vpc-id [vpc-id] --cidr-block 10.0.1.0/24
awslocal ec2 create-internet-gateway
awslocal ec2 attach-internet-gateway --internet-gateway-id [igw-id] --vpc-id [vpc-id]
```

---

## LocalStack 종료

```bash
localstack stop
# 실습 완료 후 컨테이너 종료
```

---

