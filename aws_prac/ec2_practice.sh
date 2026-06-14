#!/bin/bash
# ============================================================
# ec2_practice.sh
# 목적: AWS LocalStack EC2 실습 스크립트
# 실행: bash ec2_practice.sh
# 전제: localstack이 실행 중이어야 함
# ============================================================

echo "========================================"
echo "  EC2 실습 시작"
echo "========================================"

# ── 사용 가능한 AMI 목록 확인 ────────────────────────────
echo ""
echo "[1] 사용 가능한 AMI 목록"
awslocal ec2 describe-images \
  --query 'Images[*].[ImageId,Name]' \
  --output table
# AMI = Amazon Machine Image (OS 이미지 템플릿)
# 인스턴스 생성 시 어떤 OS를 쓸지 결정

# ── 키 페어 생성 ──────────────────────────────────────────
echo ""
echo "[2] 키 페어 생성"
awslocal ec2 create-key-pair \
  --key-name devops-key \
  --query 'KeyMaterial' \
  --output text > devops-key.pem
# 키 페어 = SSH 접속 시 사용하는 공개키/개인키
# --query 'KeyMaterial': 개인키 내용만 추출
# > devops-key.pem: 파일로 저장

chmod 400 devops-key.pem
# SSH 접속 시 개인키 권한이 넓으면 거부당함
# 400 = 소유자만 읽기 가능
echo "키 파일 생성 완료: devops-key.pem"

# ── 인스턴스 실행 ─────────────────────────────────────────
echo ""
echo "[3] EC2 인스턴스 실행"
INSTANCE_ID=$(awslocal ec2 run-instances \
  --image-id ami-785db401 \
  --instance-type t2.micro \
  --key-name devops-key \
  --count 1 \
  --query 'Instances[0].InstanceId' \
  --output text)
# ami-785db401: Ubuntu 16.04 (LocalStack 내장 AMI)
# t2.micro: 1vCPU, 1GB RAM (프리티어 해당)
# --count 1: 1개 생성
# InstanceId 변수에 저장
echo "생성된 인스턴스 ID: $INSTANCE_ID"

# ── 인스턴스 목록 확인 ────────────────────────────────────
echo ""
echo "[4] 인스턴스 목록 확인"
awslocal ec2 describe-instances \
  --query 'Reservations[*].Instances[*].[InstanceId,State.Name,InstanceType]' \
  --output table
# State.Name: pending / running / stopped / terminated

# ── 인스턴스 중지 ─────────────────────────────────────────
echo ""
echo "[5] 인스턴스 중지"
awslocal ec2 stop-instances \
  --instance-ids $INSTANCE_ID
# running → stopping → stopped
# 중지해도 EBS 스토리지 비용은 계속 발생 (실제 AWS)

echo ""
echo "[6] 상태 재확인"
awslocal ec2 describe-instances \
  --query 'Reservations[*].Instances[*].[InstanceId,State.Name]' \
  --output table

# ── 인스턴스 시작 ─────────────────────────────────────────
echo ""
echo "[7] 인스턴스 다시 시작"
awslocal ec2 start-instances \
  --instance-ids $INSTANCE_ID
# stopped → pending → running

# ── 인스턴스 종료 (삭제) ──────────────────────────────────
echo ""
echo "[8] 인스턴스 종료 (삭제)"
awslocal ec2 terminate-instances \
  --instance-ids $INSTANCE_ID
# running → shutting-down → terminated
# 완전 삭제, 복구 불가
# 종료 후 과금 없음

echo ""
echo "[9] 최종 상태 확인"
awslocal ec2 describe-instances \
  --query 'Reservations[*].Instances[*].[InstanceId,State.Name]' \
  --output table

# ── 정리 ─────────────────────────────────────────────────
rm -f devops-key.pem
echo ""
echo "========================================"
echo "  EC2 실습 완료"
echo "========================================"