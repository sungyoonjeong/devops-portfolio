# AWS Cloud

> AWS 클라우드 기초~심화 학습 정리 + LocalStack 실습

## 파일 목록

| 파일 | 내용 |
|------|------|
| `AWS클라우드.md` | IAM·EC2·S3·VPC·RDS 기초 전체 |
| `vpc_advanced_guide.md` | VPC 심화 (퍼블릭·프라이빗 서브넷·NAT·보안그룹·NACL) |
| `RDS_guide.md` | RDS 구성·Multi-AZ·Read Replica·파라미터 그룹 |
| `aws_localstack실습.md` | LocalStack으로 S3·EC2·VPC 로컬 시뮬레이션 실습 |

## AWS SAA 갭 (집중 보완 필요)

CloudFront · Route53 · Lambda · SQS/SNS · ECS/EKS · Aurora · DynamoDB · Auto Scaling · CloudWatch

> SAA 준비: 7/1~7/21 (Examtopics 500문제 + Mock 3회)

## DevOps 연결

Terraform으로 이 모든 서비스를 IaC로 관리 (PF-IaC).  
EKS = K8s 클러스터를 AWS 위에서 운영 (PF-K8s, PF1).  
CloudWatch + Prometheus = 통합 모니터링 (PF1).
