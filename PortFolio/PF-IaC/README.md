# PF-IaC — Terraform + Ansible AWS 인프라 자동화

> 작업 예정: 2026-06-23 ~ 07-02  
> 기술: `Terraform` `Ansible` `AWS` `LocalStack`

## 구성

```
PF-IaC/
├── terraform/
│   ├── main.tf          VPC + 서브넷 + EC2 + RDS + ALB
│   ├── variables.tf
│   ├── outputs.tf
│   └── modules/
│       ├── vpc/
│       ├── ec2/
│       └── rds/
├── ansible/
│   ├── inventory.ini
│   ├── site.yml          EC2 초기설정 (Docker + nginx 설치 + 앱 배포)
│   ├── roles/
│   │   ├── docker/
│   │   └── nginx/
│   └── vault/            DB 패스워드 암호화
└── README.md
```

## 목표

- `terraform apply` 한 번으로 AWS 3-tier 아키텍처 구성
- Ansible Playbook으로 EC2 초기설정 자동화
- LocalStack으로 로컬 검증 후 실 AWS 배포

<!-- 작업 시작 후 업데이트 예정 -->
