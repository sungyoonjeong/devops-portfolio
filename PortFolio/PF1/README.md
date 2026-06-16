# PF1 — End-to-End DevOps 파이프라인 (최종 킬러 포트폴리오)

> 작업 예정: 2026-08-18 ~ 08-28  
> 기술: `Go` `Docker` `AWS ECR` `Kubernetes` `Helm` `Terraform` `GitHub Actions` `ArgoCD` `Prometheus` `Grafana`

## 아키텍처

```
소스코드(Go) ──→ GitHub Actions CI ──→ Docker 빌드 ──→ ECR 푸시
                                                          │
                        ArgoCD GitOps ←── 이미지 태그 업데이트
                             │
                     K8s Helm 자동배포 (EKS or Minikube)
                             │
              Prometheus + Grafana 모니터링 + AlertManager 알림
                             │
              Terraform으로 전체 AWS 인프라 IaC 관리
```

## 구성

```
PF1/
├── app/                 Go HTTP API 서버
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── terraform/           AWS 인프라 IaC
├── ansible/             EC2 초기설정 Playbook
├── k8s/helm/            Helm Chart
├── .github/workflows/
│   └── ci.yaml          테스트 → 빌드 → ECR 푸시
├── argocd/
│   └── application.yaml GitOps 자동배포
├── monitoring/
│   ├── prometheus/
│   └── grafana/
└── README.md            아키텍처 다이어그램 + 실행법 + 수치
```

## 핵심 수치 목표

- 코드 push → 배포 완료: **5분 이내**
- 장애 감지 → Slack 알림: **30초 이내**
- 인프라 프로비저닝: `terraform apply` **3분 이내**

<!-- 작업 시작 후 업데이트 예정 -->
