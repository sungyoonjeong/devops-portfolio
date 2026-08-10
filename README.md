# 정성윤 — 인프라 · 클라우드 학습 기록

전자공학 전공 후 인프라·클라우드로 방향을 잡고 공부한 내용을 정리한 저장소입니다.
강의를 들으며 직접 작성한 정리 노트와, 손으로 돌려본 실습 기록이 들어 있습니다.

> 이 저장소는 **학습 기록**입니다. 완성된 제품이 아니라 공부한 흔적이고,
> 각 폴더의 README에 **어디까지 직접 했고 어디부터가 아직 부족한지** 그대로 적어 두었습니다.

---

## 보유 자격

| 자격 | 상태 |
|------|------|
| CCNP Enterprise | 취득 |
| CCNA | 취득 |
| AWS Cloud Practitioner | 취득 |
| HPE 하이브리드 클라우드 아카데미 (512시간) | 수료 |

---

## 학습 노트 — 강의를 들으며 직접 정리

| 폴더 | 내용 | 분량 |
|------|------|------|
| [`OS/`](OS/) | 반효경 교수 운영체제 (KOCW) — 프로세스·스케줄링·동기화·가상메모리·파일시스템 | 28강 정리 |
| [`Network/`](Network/) | 이석복 교수 컴퓨터네트워크 (KOCW) — TCP/IP·혼잡제어·DNS·라우팅 | 23강 정리 |
| [`python/자료구조/`](python/자료구조/) | 자료구조·알고리즘 — 연결리스트·트리·힙·AVL·해시·그래프·최단경로·정렬 | 41개 주제 |
| [`Docker/`](Docker/) | 컨테이너 기초 — 이미지·레이어·Dockerfile·Compose·볼륨·네트워크 | 25강 정리 |
| [`Go/`](Go/) | Go Tour — 문법·고루틴·채널·인터페이스 | 70챕터 |
| [`bash/`](bash/) | 셸 스크립팅 — 정규식·파이프·프로세스 제어 | 14챕터 + 실습 |
| [`awscloud/`](awscloud/) | AWS 기초 · VPC 심화 · RDS · LocalStack 실습 | 정리 + 실습 |
| [`기술면접/`](기술면접/) | 면접 대비 Q&A · 리눅스 트러블슈팅 실습 기록 | — |
| [`코딩테스트/`](코딩테스트/) | 프로그래머스 Level 1 완료 → Level 2 진행 | 풀이 기록 |

---

## 실습 기록

| 폴더 | 내용 |
|------|------|
| [`terraform/`](terraform/) | HCL 기초 → 변수·모듈 → State·원격 백엔드(S3+DynamoDB) → IAM·SG → 3-tier 통합 구성 |
| [`ansible/`](ansible/) | 인벤토리·Ad-hoc·Playbook·Role·Vault, 멱등성(`changed=0`) 확인 |
| [`k8s/`](k8s/) | minikube 3노드 — Pod·Deployment·Service·Ingress·ConfigMap·Secret |
| [`cicd/`](cicd/) | GitHub Actions 5-job 파이프라인 (lint→test→build→scan→push) |
| [`argocd/`](argocd/) | ArgoCD로 Git 기준 자동 동기화(GitOps) 전환 |
| [`observability/`](observability/) | Prometheus·Grafana·AlertManager 연동, 알람 발화 검증 |
| [`jenkins/`](jenkins/) | 같은 파이프라인을 Jenkins로 재현해 GitHub Actions와 비교 |

---

## 만들어 본 것

### [PF3 — 서버 리소스 모니터링](PortFolio/PF3/)
`Python` `psutil` `Bash`

CPU·메모리·디스크를 주기적으로 수집해 임계값을 넘으면 Slack으로 알림. 로그는 크기 제한으로 순환시키고, 오래된 로그는 자동 정리.

측정 함수 인자를 잘못 줘서 **CPU가 항상 0%로 보고되던 문제**를 겪었습니다. 에러가 아니라 "정상"으로 보였기 때문에 한동안 몰랐고, 모니터링에서는 거짓 정상이 거짓 경보보다 위험하다는 걸 여기서 배웠습니다.

### [PF2 — Go HTTP 서버 + 컨테이너 배포](PortFolio/PF2/)
`Go` `Docker` `Docker Compose` `nginx` `Trivy`

`/health`·`/metrics` 엔드포인트를 가진 Go 서버. 멀티스테이지 빌드로 이미지를 약 19MB까지 줄였고, nginx를 앞에 두어 앱을 직접 노출하지 않도록 구성. 배포 스크립트에 Trivy 이미지 스캔을 넣었습니다.

최근 스스로 코드 리뷰를 하며 세 가지를 고쳤습니다 — 컨테이너가 root로 실행되던 것, `go.sum`을 복사하지 않아 모듈 체크섬 검증이 빠지던 것, `.dockerignore`가 없어 빌드 컨텍스트가 불필요하게 커지던 것.

### [PF-IaC — Terraform + Ansible](PortFolio/PF-IaC/)
`Terraform` `Ansible` `AWS EC2` `nginx`

실제 AWS에 EC2를 프로비저닝하고, **먼저 손으로 nginx를 설치·설정해 본 뒤** 같은 작업을 Ansible로 옮겼습니다. 자동화가 실패했을 때 원인을 못 찾으면 의미가 없다고 생각해서 수동 과정을 일부러 먼저 거쳤습니다.

실행 화면 11장을 증적으로 남겼고, 그 과정에서 통신사 구간의 HTTP 가로채기와 charset 미적용 문제를 직접 진단했습니다.

### [PF-K8s — 쿠버네티스 배포](PortFolio/PF-K8s/)
`Kubernetes` `minikube`

PF2 이미지를 minikube 3노드에 Deployment(3 replica) + Service + Ingress로 배포. readiness/liveness probe를 붙여 동작을 확인했습니다.

---

## 사용해 본 기술

**클라우드·인프라** AWS · Terraform · Ansible · Docker · Kubernetes
**언어** Python · Go · Bash
**CI/CD·관측** GitHub Actions · ArgoCD · Jenkins · Prometheus · Grafana

---

## 지금 하고 있는 것

기본기를 다시 다지고 있습니다. 그동안 넓게 훑는 데 시간을 많이 썼는데,
설명할 수 있는 수준까지 가지 못한 부분이 있다고 판단해서
리눅스·네트워크·클라우드 핵심 개념을 **직접 손으로 다시 확인하는 중**입니다.
