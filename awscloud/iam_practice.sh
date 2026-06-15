#!/bin/bash
# ============================================================
# iam_practice.sh
# 목적: AWS LocalStack IAM 실습 스크립트
# 실행: bash iam_practice.sh
# 전제: localstack이 실행 중이어야 함
# ============================================================

echo "========================================"
echo "  IAM 실습 시작"
echo "========================================"

# ── 사용자 생성 ──────────────────────────────────────────
echo ""
echo "[1] 사용자 생성"
awslocal iam create-user --user-name devops-user
# IAM 사용자 = AWS를 사용하는 사람 또는 프로그램
# --user-name: 사용자 이름 지정

# ── 사용자 목록 확인 ─────────────────────────────────────
echo ""
echo "[2] 사용자 목록 확인"
awslocal iam list-users

# ── 그룹 생성 ────────────────────────────────────────────
echo ""
echo "[3] 그룹 생성"
awslocal iam create-group --group-name devops-team
# 그룹 = 여러 사용자를 묶어 한 번에 권한 관리

# ── 그룹에 사용자 추가 ───────────────────────────────────
echo ""
echo "[4] 그룹에 사용자 추가"
awslocal iam add-user-to-group \
  --user-name devops-user \
  --group-name devops-team

# ── 그룹 목록 확인 ───────────────────────────────────────
echo ""
echo "[5] 그룹 목록 확인"
awslocal iam list-groups

# ── 사용자에 정책 연결 ───────────────────────────────────
echo ""
echo "[6] S3 전체 권한 정책 연결"
awslocal iam attach-user-policy \
  --user-name devops-user \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
# policy-arn: 정책의 고유 주소 (ARN)
# AmazonS3FullAccess: AWS 관리형 정책 (S3 전체 권한)
# 최소 권한 원칙: 실무에서는 필요한 것만 부여

# ── 연결된 정책 확인 ─────────────────────────────────────
echo ""
echo "[7] 연결된 정책 확인"
awslocal iam list-attached-user-policies \
  --user-name devops-user

# ── 그룹에 읽기 전용 정책 연결 ──────────────────────────
echo ""
echo "[8] 그룹에 S3 읽기 전용 정책 연결"
awslocal iam attach-group-policy \
  --group-name devops-team \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
# ReadOnlyAccess: 읽기만 가능 (업로드 불가)

# ── 그룹 정책 확인 ───────────────────────────────────────
echo ""
echo "[9] 그룹 연결 정책 확인"
awslocal iam list-attached-group-policies \
  --group-name devops-team

# ── Access Key 생성 ──────────────────────────────────────
echo ""
echo "[10] Access Key 생성"
awslocal iam create-access-key \
  --user-name devops-user
# 프로그래밍 방식 AWS 접근용 키 발급
# Access Key ID + Secret Access Key 출력

# ── 정리 ─────────────────────────────────────────────────
echo ""
echo "[정리] 리소스 삭제"
awslocal iam detach-user-policy \
  --user-name devops-user \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess
# 사용자 삭제 전 정책 먼저 분리 필수

awslocal iam detach-group-policy \
  --group-name devops-team \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

awslocal iam remove-user-from-group \
  --user-name devops-user \
  --group-name devops-team

awslocal iam delete-group --group-name devops-team

awslocal iam delete-user --user-name devops-user

echo ""
echo "========================================"
echo "  IAM 실습 완료"
echo "========================================"