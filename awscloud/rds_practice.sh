#!/bin/bash
# ============================================================
# rds_practice.sh
# 목적: AWS LocalStack RDS 실습 (MySQL)
# 실행: bash rds_practice.sh
# 전제: localstack이 실행 중이어야 함
# ============================================================

echo "========================================"
echo "  RDS 실습 시작"
echo "========================================"

# ── STEP 1. DB 인스턴스 생성 ──────────────────────────────
echo ""
echo "[STEP 1] RDS MySQL 인스턴스 생성"
awslocal rds create-db-instance \
  --db-instance-identifier mydb \
  --db-instance-class db.t3.micro \
  --engine mysql \
  --master-username admin \
  --master-user-password password123 \
  --allocated-storage 20
# --db-instance-identifier: DB 고유 이름 (엔드포인트에 사용됨)
# --db-instance-class: 인스턴스 사양 (db.t3.micro = 프리티어)
# --engine: DB 엔진 종류 (mysql/postgres/mariadb/oracle 등)
# --master-username: 마스터 관리자 계정
# --master-user-password: 마스터 비밀번호 (8자 이상)
# --allocated-storage: 스토리지 크기(GB, 최소 20GB for MySQL)

# ── STEP 2. DB 인스턴스 목록 확인 ─────────────────────────
echo ""
echo "[STEP 2] DB 인스턴스 목록 확인"
awslocal rds describe-db-instances \
  --query 'DBInstances[*].[DBInstanceIdentifier,DBInstanceStatus,Engine,DBInstanceClass]' \
  --output table
# DBInstanceStatus: creating → available (실제 AWS에서 수 분 소요)

# ── STEP 3. 스냅샷 생성 (수동 백업) ──────────────────────
echo ""
echo "[STEP 3] 수동 스냅샷 생성"
awslocal rds create-db-snapshot \
  --db-instance-identifier mydb \
  --db-snapshot-identifier mydb-snapshot-20260615
# 특정 시점의 DB 상태를 스냅샷으로 저장
# 자동 백업 외에 중요 배포 전 수동으로 백업할 때 사용

# ── STEP 4. 스냅샷 목록 확인 ──────────────────────────────
echo ""
echo "[STEP 4] 스냅샷 목록 확인"
awslocal rds describe-db-snapshots \
  --query 'DBSnapshots[*].[DBSnapshotIdentifier,Status,Engine]' \
  --output table

# ── STEP 5. Read Replica 생성 (읽기 복제본) ───────────────
echo ""
echo "[STEP 5] Read Replica 생성"
awslocal rds create-db-instance-read-replica \
  --db-instance-identifier mydb-replica \
  --source-db-instance-identifier mydb
# 읽기 복제본 = 비동기 복제, 읽기 전용
# 주 DB의 읽기 부하를 분산
# 실제 AWS: 쓰기는 주 DB, 읽기는 복제본으로 분산

# ── STEP 6. Read Replica 확인 ─────────────────────────────
echo ""
echo "[STEP 6] 전체 DB 인스턴스 (주 DB + 복제본)"
awslocal rds describe-db-instances \
  --query 'DBInstances[*].[DBInstanceIdentifier,DBInstanceStatus,ReadReplicaSourceDBInstanceIdentifier]' \
  --output table
# ReadReplicaSourceDBInstanceIdentifier: 원본 DB 이름 있으면 복제본

# ── STEP 7. DB 파라미터 그룹 확인 ─────────────────────────
echo ""
echo "[STEP 7] DB 파라미터 그룹 목록"
awslocal rds describe-db-parameters \
  --db-parameter-group-name default.mysql8.0 2>/dev/null || \
awslocal rds describe-db-parameter-groups \
  --query 'DBParameterGroups[*].[DBParameterGroupName,DBParameterGroupFamily]' \
  --output table
# 파라미터 그룹 = DB 엔진 설정값 집합
# max_connections, character_set 등 설정 가능

# ── STEP 8. 스냅샷으로 새 인스턴스 복구 ──────────────────
echo ""
echo "[STEP 8] 스냅샷으로 새 DB 인스턴스 복구"
awslocal rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier mydb-restored \
  --db-snapshot-identifier mydb-snapshot-20260615
# 스냅샷 → 새 DB 인스턴스로 복구
# 기존 인스턴스 덮어쓰기 불가 (항상 새 인스턴스 생성)

echo ""
echo "[STEP 9] 복구된 DB 확인"
awslocal rds describe-db-instances \
  --query 'DBInstances[*].[DBInstanceIdentifier,DBInstanceStatus]' \
  --output table

# ── 정리 ──────────────────────────────────────────────────
echo ""
echo "[정리] DB 인스턴스 삭제"
awslocal rds delete-db-instance \
  --db-instance-identifier mydb-replica \
  --skip-final-snapshot
# 복제본 먼저 삭제

awslocal rds delete-db-instance \
  --db-instance-identifier mydb \
  --skip-final-snapshot
# --skip-final-snapshot: 삭제 시 최종 스냅샷 생략

awslocal rds delete-db-instance \
  --db-instance-identifier mydb-restored \
  --skip-final-snapshot

echo ""
echo "========================================"
echo "  RDS 실습 완료"
echo ""
echo "  핵심 정리:"
echo "  Multi-AZ    → 고가용성(HA), 동기 복제, 자동 Failover"
echo "  Read Replica → 읽기 성능 확장, 비동기 복제"
echo "  스냅샷       → 특정 시점 백업, 새 인스턴스로 복구"
echo "========================================"