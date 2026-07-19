# Sungyoon Jeong | DevOps Engineer Portfolio

> **목표**: DevOps Engineer   
> **준비 기간**: 2026년 상반기 ~ 9월 하반기 공채  
> **자격증**: CCNP · AWS Cloud Practitioner (취득) · **AWS SAA · CKA** (2026년 예정)

---

## 완료 포트폴리오 프로젝트

| 프로젝트 | 기술 스택 | 설명 | 상태 |
|---------|----------|------|------|
| [PF3 — 서버 모니터링 시스템](PortFolio/PF3/) | `Python` `psutil` `Logging` `Bash` `Slack` | CPU/메모리/디스크 5분 주기 수집 + 임계값 초과 시 Slack 자동 알림 + 로그 분석 리포트 | ✅ 완료 |
| [PF2 — Go + Docker 배포 자동화](PortFolio/PF2/) | `Go` `Docker` `Docker Compose` `nginx` `Trivy` `Bash` | Go API 서버 멀티스테이지 빌드(~10MB) + nginx 리버스프록시 + Trivy 보안 스캔 + `deploy.sh` 한 줄 배포 | ✅ 완료 |
| [Terraform IaC (D1~D5)](terraform/) | `Terraform` `AWS` `LocalStack` `checkov` | VPC·SG·IAM·EC2·RDS 모듈화 + 원격 state(S3 backend + DynamoDB 락) + Workspace 환경분리 + 3-tier 통합 스택(d5-final) | ✅ 완료 |
| [PF-IaC — Terraform + Ansible 연동](PortFolio/PF-IaC/) | `Terraform` `Ansible` `AWS EC2` `nginx` `Docker` | 실 AWS EC2 프로비저닝 → 수동 서버구성 선행 → Ansible로 nginx·docker 재구성 + 멱등성 검증(changed=0) · 실행 증적 포함 | ✅ 완료 |

---

## 진행 중 · 로드맵 (2026년 7월)

| 프로젝트 | 기술 스택 | 설명 | 상태 |
|---------|----------|------|------|
| [PF-K8s — Kubernetes 앱 운영](PortFolio/PF-K8s/) | `Kubernetes` `Helm` `Ingress` `RBAC` `HPA` | Deployment·Service·Ingress·HPA·RBAC·NetworkPolicy + Helm 차트 패키징 | 🔄 진행 중 |
| [CI/CD 파이프라인](cicd/) | `GitHub Actions` `Jenkins` `Trivy` `ECR` | GitHub Flow + 5-job(lint→test→build→scan→push) CI 실그린 검증 완료 | 🔄 진행 중 |
| [ArgoCD GitOps](argocd/) | `ArgoCD` `Kubernetes` | PF2 K8s 리소스를 Git 기준 자동 동기화로 전환, selfHeal·자동배포 실증 완료 | 🔄 진행 중 |
| [Observability](observability/) | `Prometheus` `Grafana` `AlertManager` | PF2 `/metrics` Prometheus 연동, 대시보드 1개·알람 2종 실발동 검증 완료 | 🔄 진행 중 |
| 관측성 스택 | `Prometheus` `Grafana` `AlertManager` | 메트릭 수집·통합 대시보드·SLO·Slack 알림 | 🔄 진행 중 |
| [**PF1 — End-to-End DevOps 파이프라인**](PortFolio/PF1/) | `GitHub Actions` `ArgoCD` `EKS` `Helm` `Terraform` `Prometheus` | 코드 push → CI → 이미지 빌드 → GitOps 자동배포(EKS) → 모니터링 (앱 전주기 통합) | 🔄 예정 |
| [**★ 캡스톤 — 하이브리드 클라우드 신뢰성 플랫폼**](PortFolio/PF-Hybrid/) | `k3s(On-Prem)` `EKS(AWS)` `WireGuard` `ArgoCD` `Prometheus` `k6` | 온프렘 ↔ AWS 하이브리드 배포 + 장애 시 자동 페일오버 + **MTTR 실측** | 🔄 예정 |

---

## 기술 스택

### Infrastructure & Cloud
![AWS](https://img.shields.io/badge/AWS-232F3E?style=flat&logo=amazon-aws&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-7B42BC?style=flat&logo=terraform&logoColor=white)
![Ansible](https://img.shields.io/badge/Ansible-EE0000?style=flat&logo=ansible&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=flat&logo=kubernetes&logoColor=white)

### Languages & Tools
![Go](https://img.shields.io/badge/Go-00ADD8?style=flat&logo=go&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Bash](https://img.shields.io/badge/Bash-4EAA25?style=flat&logo=gnu-bash&logoColor=white)

### Monitoring & CI/CD
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=flat&logo=prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/Grafana-F46800?style=flat&logo=grafana&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat&logo=github-actions&logoColor=white)
![ArgoCD](https://img.shields.io/badge/ArgoCD-EF7B4D?style=flat&logo=argo&logoColor=white)
![Jenkins](https://img.shields.io/badge/Jenkins-D24939?style=flat&logo=jenkins&logoColor=white)
![Helm](https://img.shields.io/badge/Helm-0F1689?style=flat&logo=helm&logoColor=white)

---

## 학습 영역

```
OS/          반효경 교수 28강 (KOCW) — 프로세스·스케줄링·동기화·메모리·파일시스템
Network/     이석복 교수 23강 (KOCW) — TCP/IP·혼잡제어·DNS·TLS·방화벽
Go/          Go Tour 70챕터 — 고루틴·채널·인터페이스·에러처리
bash/        14챕터 + 실습 스크립트 — 정규식·파이프·프로세스 관리
Docker/      따배도 25강 — Dockerfile·Compose·Volume·Network
awscloud/    VPC·EC2·RDS·IAM·LocalStack 실습 전체
terraform/   D1~D5 IaC 실습 — 모듈화·원격 state·Workspace·3-tier 통합(d5-final)
ansible/     Ansible 101 정리집 + D1~D5 실습 — 인벤토리·Playbook·Role·Vault + Terraform 연동(pf-IaC)
k8s/         따배쿠 입문 1~11장 + minikube 3노드 실습 — Pod·Controller·Service·Ingress·ConfigMap·Secret
cicd/        GitHub Actions 5-job CI — 브랜치 전략·lint·test·docker-build·trivy-scan·ecr-push 실그린 검증
argocd/      ArgoCD GitOps — Application 등록·selfHeal·Git→클러스터 자동 동기화 실증
observability/ Prometheus+Grafana+AlertManager — PF2 /metrics 연동·대시보드·알람 규칙
python/      자료구조 38챕터 — 연결리스트·트리·힙·AVL·BIT·Red-Black Tree
코딩테스트/   프로그래머스 Level 1 완료 (64문제+) → Level 2 진행 중
기술면접/     면접 예상질문 Q&A + 리눅스 트러블슈팅 실습 기록
PortFolio/   PF3·PF2·PF-IaC·PF-K8s·PF1 + ★하이브리드 캡스톤(PF-Hybrid)
```

---

## 자격증 로드맵

```
✅ CCNP Enterprise
✅ AWS Cloud Practitioner
🔄 AWS SAA-C03          → 2026년 8월 취득 목표
🔄 CKA                  → 2026년 8월 취득 목표
🔄 OPIc IH              → 2026년 8월 취득 목표
```

---

> 학습 노트는 각 폴더 내 `.md` 파일을 참조.  
> 포트폴리오 상세는 `PortFolio/` 폴더 참조.
