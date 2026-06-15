#!/bin/bash
# ============================================================
# elb_autoscaling_practice.sh
# 목적: AWS LocalStack ELB + Auto Scaling 실습
# 실행: bash elb_autoscaling_practice.sh
# 전제: localstack이 실행 중이어야 함
# ============================================================

echo "========================================"
echo "  ELB + Auto Scaling 실습 시작"
echo "========================================"

# ── 사전 준비: VPC·서브넷·보안그룹 ──────────────────────
echo ""
echo "[사전 준비] VPC·서브넷·보안그룹 생성"

VPC_ID=$(awslocal ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --query 'Vpc.VpcId' --output text)
echo "  → VPC: $VPC_ID"

SUBNET1=$(awslocal ec2 create-subnet \
  --vpc-id $VPC_ID --cidr-block 10.0.1.0/24 \
  --availability-zone us-east-1a \
  --query 'Subnet.SubnetId' --output text)
SUBNET2=$(awslocal ec2 create-subnet \
  --vpc-id $VPC_ID --cidr-block 10.0.2.0/24 \
  --availability-zone us-east-1b \
  --query 'Subnet.SubnetId' --output text)
echo "  → 서브넷1: $SUBNET1 / 서브넷2: $SUBNET2"

SG_ID=$(awslocal ec2 create-security-group \
  --group-name elb-sg --description "ELB SG" \
  --vpc-id $VPC_ID --query 'GroupId' --output text)
awslocal ec2 authorize-security-group-ingress \
  --group-id $SG_ID --protocol tcp --port 80 --cidr 0.0.0.0/0
echo "  → 보안그룹: $SG_ID (HTTP 80 허용)"

# ── STEP 1. ALB 생성 ──────────────────────────────────────
echo ""
echo "[STEP 1] Application Load Balancer 생성"
ALB_ARN=$(awslocal elbv2 create-load-balancer \
  --name my-alb \
  --subnets $SUBNET1 $SUBNET2 \
  --security-groups $SG_ID \
  --type application \
  --query 'LoadBalancers[0].LoadBalancerArn' \
  --output text)
# ALB = L7 로드밸런서 (HTTP/HTTPS 기반 지능적 라우팅)
# type: application(ALB), network(NLB), gateway(GWLB)
# subnets: 최소 2개 AZ의 서브넷 필요 (고가용성)
echo "  → ALB ARN: $ALB_ARN"

# ALB DNS 주소 확인
ALB_DNS=$(awslocal elbv2 describe-load-balancers \
  --names my-alb \
  --query 'LoadBalancers[0].DNSName' \
  --output text)
echo "  → ALB DNS: $ALB_DNS"
# 실제 AWS: 이 DNS로 접속하면 트래픽 분산됨
# IP 대신 DNS 사용 → Failover 시 자동으로 새 IP 가리킴

# ── STEP 2. 타겟 그룹 생성 ────────────────────────────────
echo ""
echo "[STEP 2] 타겟 그룹 생성"
TG_ARN=$(awslocal elbv2 create-target-group \
  --name my-targets \
  --protocol HTTP \
  --port 80 \
  --vpc-id $VPC_ID \
  --health-check-path / \
  --health-check-interval-seconds 30 \
  --query 'TargetGroups[0].TargetGroupArn' \
  --output text)
# 타겟 그룹 = ALB가 트래픽을 보낼 대상들의 집합
# health-check-path: "/" 경로로 헬스체크
# health-check-interval: 30초마다 상태 확인
echo "  → 타겟 그룹 ARN: $TG_ARN"

# ── STEP 3. 리스너 생성 ───────────────────────────────────
echo ""
echo "[STEP 3] 리스너 생성 (80포트 → 타겟 그룹)"
LISTENER_ARN=$(awslocal elbv2 create-listener \
  --load-balancer-arn $ALB_ARN \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=$TG_ARN \
  --query 'Listeners[0].ListenerArn' \
  --output text)
# 리스너 = ALB의 80포트를 감시하다가 들어오는 요청을 타겟 그룹으로 전달
# Type=forward: 타겟 그룹으로 전달
echo "  → 리스너 ARN: $LISTENER_ARN"

# ── STEP 4. EC2 인스턴스 → 타겟 그룹 등록 ───────────────
echo ""
echo "[STEP 4] EC2 인스턴스 생성 후 타겟 그룹 등록"

# 인스턴스 2개 생성
INSTANCE1=$(awslocal ec2 run-instances \
  --image-id ami-785db401 \
  --instance-type t2.micro \
  --count 1 \
  --query 'Instances[0].InstanceId' --output text)
INSTANCE2=$(awslocal ec2 run-instances \
  --image-id ami-785db401 \
  --instance-type t2.micro \
  --count 1 \
  --query 'Instances[0].InstanceId' --output text)
echo "  → 인스턴스1: $INSTANCE1"
echo "  → 인스턴스2: $INSTANCE2"

# 타겟 그룹에 등록
awslocal elbv2 register-targets \
  --target-group-arn $TG_ARN \
  --targets Id=$INSTANCE1,Port=80 Id=$INSTANCE2,Port=80
# 두 인스턴스를 타겟 그룹에 등록
# ALB가 트래픽을 번갈아 분산 (Round Robin 기본)
echo "  → 두 인스턴스 타겟 그룹 등록 완료"

# ── STEP 5. 타겟 헬스 상태 확인 ──────────────────────────
echo ""
echo "[STEP 5] 타겟 헬스 상태 확인"
awslocal elbv2 describe-target-health \
  --target-group-arn $TG_ARN \
  --query 'TargetHealthDescriptions[*].[Target.Id,TargetHealth.State]' \
  --output table
# State: healthy(정상) / unhealthy(비정상) / initial(확인 중)
# unhealthy 인스턴스는 ALB가 자동으로 트래픽 제외

# ── STEP 6. Auto Scaling 시작 구성 ───────────────────────
echo ""
echo "[STEP 6] Auto Scaling 시작 구성 생성"
awslocal autoscaling create-launch-configuration \
  --launch-configuration-name my-lc \
  --image-id ami-785db401 \
  --instance-type t2.micro
# 시작 구성 = Auto Scaling이 새 인스턴스 생성 시 사용하는 설정
# AMI, 인스턴스 타입, 보안 그룹, 키 페어 등 지정
echo "  → 시작 구성 생성 완료: my-lc"

# ── STEP 7. Auto Scaling 그룹 생성 ───────────────────────
echo ""
echo "[STEP 7] Auto Scaling 그룹 생성"
awslocal autoscaling create-auto-scaling-group \
  --auto-scaling-group-name my-asg \
  --launch-configuration-name my-lc \
  --min-size 2 \
  --max-size 6 \
  --desired-capacity 2 \
  --availability-zones us-east-1a us-east-1b \
  --target-group-arns $TG_ARN \
  --health-check-type ELB \
  --health-check-grace-period 300
# min-size: 최소 인스턴스 수 (항상 유지)
# max-size: 최대 인스턴스 수 (비용 상한)
# desired-capacity: 현재 원하는 인스턴스 수
# health-check-type: ELB (웹서버 프로세스까지 확인, EC2보다 정확)
# health-check-grace-period: 인스턴스 시작 후 헬스체크 대기시간(초)
echo "  → ASG 생성 완료 (min:2 / max:6 / desired:2)"

# ── STEP 8. Auto Scaling 상태 확인 ───────────────────────
echo ""
echo "[STEP 8] Auto Scaling 그룹 상태 확인"
awslocal autoscaling describe-auto-scaling-groups \
  --auto-scaling-group-names my-asg \
  --query 'AutoScalingGroups[*].[AutoScalingGroupName,MinSize,MaxSize,DesiredCapacity]' \
  --output table

# ── STEP 9. 스케일링 정책 생성 (CPU 기반) ────────────────
echo ""
echo "[STEP 9] CPU 기반 스케일링 정책 생성"
awslocal autoscaling put-scaling-policy \
  --auto-scaling-group-name my-asg \
  --policy-name cpu-scaling \
  --policy-type TargetTrackingScaling \
  --target-tracking-configuration file:///dev/stdin << 'POLICY'
{
  "PredefinedMetricSpecification": {
    "PredefinedMetricType": "ASGAverageCPUUtilization"
  },
  "TargetValue": 60.0
}
POLICY
# TargetTrackingScaling: CPU가 60% 되도록 자동 조정
# CPU 60% 초과 → 인스턴스 추가
# CPU 60% 미만 → 인스턴스 제거
echo "  → CPU 60% 기준 자동 스케일링 정책 생성"

# ── STEP 10. ELB·ASG 전체 확인 ───────────────────────────
echo ""
echo "[STEP 10] ELB 전체 목록"
awslocal elbv2 describe-load-balancers \
  --query 'LoadBalancers[*].[LoadBalancerName,State.Code,Type]' \
  --output table

echo ""
echo "========================================"
echo "  ELB + Auto Scaling 실습 완료"
echo ""
echo "  구성 요약:"
echo "  ALB DNS: $ALB_DNS"
echo "  타겟 그룹: $TG_ARN"
echo "  Auto Scaling: min2 / max6 / desired2"
echo ""
echo "  트래픽 흐름:"
echo "  인터넷 → ALB(80포트) → 타겟 그룹 → EC2×2"
echo "  CPU 60% 초과 시 → ASG가 EC2 자동 추가 (최대 6대)"
echo "  EC2 장애 시 → ELB 헬스체크로 감지 → ASG가 새 인스턴스 생성"
echo ""
echo "  ⚠️ 실습 후 정리 방법:"
echo "  1. ASG min/max/desired를 모두 0으로 변경"
echo "  2. ASG 삭제"
echo "  3. ELB 삭제"
echo "  (ASG 인스턴스만 삭제하면 ASG가 새로 만들어버림 주의!)"
echo "========================================"