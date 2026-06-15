#!/bin/bash
# ============================================================
# s3_practice.sh
# 목적: AWS LocalStack S3 실습 스크립트
# 실행: bash s3_practice.sh
# 전제: localstack이 실행 중이어야 함
# ============================================================

echo "========================================"
echo "  S3 실습 시작"
echo "========================================"

# ── 버킷 생성 ─────────────────────────────────────────────
echo ""
echo "[1] 버킷 생성"
awslocal s3 mb s3://devops-bucket-jsy
# mb = make bucket
# s3:// 로 시작하는 것이 S3 주소 형식

# ── 버킷 목록 확인 ─────────────────────────────────────────
echo ""
echo "[2] 버킷 목록 확인"
awslocal s3 ls

# ── 파일 생성 및 업로드 ────────────────────────────────────
echo ""
echo "[3] 파일 업로드"
echo "Hello DevOps!" > hello.txt
awslocal s3 cp hello.txt s3://devops-bucket-jsy/
# cp = copy: 로컬 파일 → S3 업로드

# ── 폴더 경로 지정 업로드 ──────────────────────────────────
echo ""
echo "[4] 폴더 경로 지정 업로드"
awslocal s3 cp hello.txt s3://devops-bucket-jsy/logs/hello.txt
# S3에는 실제 폴더가 없고 키(경로) 이름으로 구분

# ── 버킷 내 파일 목록 확인 ─────────────────────────────────
echo ""
echo "[5] 버킷 내 파일 목록 (전체)"
awslocal s3 ls s3://devops-bucket-jsy/ --recursive
# --recursive: 하위 경로 전부 표시

# ── 파일 다운로드 ──────────────────────────────────────────
echo ""
echo "[6] 파일 다운로드"
awslocal s3 cp s3://devops-bucket-jsy/hello.txt ./downloaded.txt
# S3 → 로컬로 다운로드
cat downloaded.txt
# → Hello DevOps! 출력되면 성공

# ── 폴더 동기화 (sync) ─────────────────────────────────────
echo ""
echo "[7] 폴더 동기화 (sync)"
mkdir -p ./myfiles
echo "file1 content" > ./myfiles/file1.txt
echo "file2 content" > ./myfiles/file2.txt
awslocal s3 sync ./myfiles s3://devops-bucket-jsy/myfiles/
# sync: 변경된 파일만 업로드 (전체 cp보다 효율적)
# CI/CD에서 빌드 결과물 배포 시 자주 사용

# ── 전체 목록 재확인 ────────────────────────────────────────
echo ""
echo "[8] 전체 목록 재확인"
awslocal s3 ls s3://devops-bucket-jsy/ --recursive

# ── 파일 삭제 ──────────────────────────────────────────────
echo ""
echo "[9] 파일 삭제"
awslocal s3 rm s3://devops-bucket-jsy/hello.txt
# 단일 파일 삭제

# ── 정리: 버킷 전체 삭제 ────────────────────────────────────
echo ""
echo "[10] 버킷 삭제"
awslocal s3 rb s3://devops-bucket-jsy --force
# --force: 내용물 있어도 강제 삭제

# ── 임시 파일 정리 ─────────────────────────────────────────
rm -f hello.txt downloaded.txt
rm -rf myfiles

echo ""
echo "========================================"
echo "  S3 실습 완료"
echo "========================================"