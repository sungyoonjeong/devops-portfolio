# PF-K8s — Kubernetes + Helm 앱 운영

> 작업 예정: 2026-07-07 ~ 07-25  
> 기술: `Kubernetes` `Helm` `Nginx Ingress` `RBAC` `HPA`

## 구성

```
PF-K8s/
├── k8s/
│   ├── deployment.yaml      Go 앱 Deployment (3 replicas)
│   ├── service.yaml         ClusterIP
│   ├── ingress.yaml         Nginx Ingress + TLS
│   ├── hpa.yaml             CPU 60% 기준 오토스케일링
│   ├── network-policy.yaml  네임스페이스 간 통신 제한
│   └── rbac/
│       ├── dev-role.yaml    개발자용 ServiceAccount
│       └── ops-role.yaml    운영자용 ServiceAccount
├── helm/
│   └── app-chart/           values.yaml로 환경별 설정 분리
└── README.md
```

## 목표

- PF2 Go 서버를 K8s 위에서 운영
- Helm Chart 패키징으로 dev/prod 환경 분리 배포
- RBAC + NetworkPolicy로 보안 강화
- CKA 준비와 동시 진행

<!-- 작업 시작 후 업데이트 예정 -->
