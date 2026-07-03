# ★ 캡스톤 — 하이브리드 클라우드 신뢰성 플랫폼

> **On-Prem ↔ AWS 하이브리드 배포 + 자동 페일오버 + MTTR 실측**
> 작업 예정: 2026년 7월
> 기술: `k3s(On-Prem)` `EKS(AWS)` `Ansible` `Terraform` `WireGuard` `ArgoCD` `Prometheus` `Grafana` `k6`

---

## 개요

애플리케이션을 **온프렘(가상화 위 k3s)** 과 **AWS(EKS)** 두 환경에 동시 배포하고,
한쪽 환경에 장애가 발생하면 트래픽이 자동으로 다른 환경으로 전환되는 것을
**수치(MTTR)로 증명**하는 하이브리드 운영 플랫폼.

일반적인 클라우드 단일환경 파이프라인을 넘어, 온프렘↔클라우드를 잇는
실무형 하이브리드 구조와 신뢰성(SRE) 관점을 다룬다.

## 아키텍처

```
          [사용자] → DNS/LB (헬스체크 기반 라우팅)
                 │
      ┌──────────┴───────────┐
  [온프렘]                  [AWS]
  VM 위 k3s (Ansible)       EKS (Terraform)
  앱 + PostgreSQL           앱 + RDS
      └──── WireGuard 사이트투사이트 VPN ────┘
                 │
  GitHub Actions → ArgoCD → 양쪽 클러스터 동시 배포
                 │
  Prometheus 페더레이션 → Grafana 통합 → AlertManager→Slack
```

## 핵심 구성

- **하이브리드 인프라** — 온프렘 k3s(Ansible 프로비저닝) ↔ AWS EKS(Terraform)
- **하이브리드 네트워킹** — WireGuard 사이트투사이트 VPN으로 두 환경 연결
- **GitOps** — ArgoCD가 양쪽 클러스터에 동일 앱 동시 배포
- **통합 관측** — Prometheus 페더레이션 → Grafana 단일 대시보드 + Slack 알림
- **자동 페일오버** — DNS/LB 헬스체크 기반 전환 + **MTTR(복구시간) 실측**
- **부하 검증** — k6로 정상·페일오버 상황 처리량·지연 측정

## 산출물

- 아키텍처 다이어그램 + 판단 기록 README
- 페일오버 실험 리포트 (장애 주입 → 전환 → MTTR 수치)
- 운영 런북 + 부하테스트 결과

## 상태

🔄 예정 (2026년 7월) — 부트캠프 표준 캡스톤(순수 클라우드 단일환경)을
하이브리드 + 신뢰성으로 확장한 대표 프로젝트.
