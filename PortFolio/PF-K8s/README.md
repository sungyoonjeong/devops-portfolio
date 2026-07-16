# PF-K8s — Kubernetes + Helm 앱 운영

> 작업 기간: 2026-07-07 ~ 07-25 (K8s 학습 병행) · 첫 조각 배포 2026-07-17  
> 기술: `Kubernetes` `Helm` `Nginx Ingress` `RBAC` `HPA`

## 구성

```
PF-K8s/
├── k8s/
│   ├── deployment.yaml      PF2 Go 서버 Deployment (3 replicas) ✅ 완료
│   ├── service.yaml         ClusterIP (pf2-svc, 80→8080) ✅ 완료
│   ├── ingress.yaml         Nginx Ingress, host 기반 라우팅 ✅ 완료
│   ├── hpa.yaml             CPU 60% 기준 오토스케일링 ⬜ PF1(7/20~)에서 추가
│   ├── network-policy.yaml  네임스페이스 간 통신 제한 ⬜ PF1에서 추가
│   └── rbac/
│       ├── dev-role.yaml    개발자용 ServiceAccount ⬜ CKA 준비(8/14~)와 겸함
│       └── ops-role.yaml    운영자용 ServiceAccount ⬜ CKA 준비(8/14~)와 겸함
├── helm/
│   └── app-chart/           values.yaml로 환경별 설정 분리 ⬜ PF1(7/20~)에서 차트로 패키징
└── README.md
```

## 목표

- PF2 Go 서버를 K8s 위에서 운영
- Helm Chart 패키징으로 dev/prod 환경 분리 배포
- RBAC + NetworkPolicy로 보안 강화
- CKA 준비와 동시 진행

## 진행 상황

**2026-07-17 — 첫 조각 배포 완료 (deployment·service·ingress)**

PF2(Go HTTP 서버, `/health` `/metrics`)를 minikube 3노드 클러스터에 배포하고 Ingress로 노출했다. 과정과 트러블슈팅은 [../../k8s/PRACTICE.md](../../k8s/PRACTICE.md)의 "PF2 K8s 배포" 절에 스크린샷과 함께 기록.

```
이미지: pf2:021c651 (커밋 해시 태그, PF2/deploy.sh와 동일 전략)
        docker build → minikube image load (레지스트리 없이 3노드 전체에 로컬 로드)
        imagePullPolicy: Never — 로컬 이미지이므로 Docker Hub에서 pull 시도 방지

Deployment: replicas 3, readinessProbe·livenessProbe 둘 다 /health:8080
            requests(50m/32Mi) / limits(200m/64Mi)
Service:    pf2-svc, ClusterIP, 80 → 8080
Ingress:    pf2-ingress, host: pf2.local, rewrite-target: / (7/16 밤 실습에서 익힌 함정 반영)

검증: curl -H "Host: pf2.local" http://$(minikube ip)/health   → {"status":"ok",...}
      curl -H "Host: pf2.local" http://$(minikube ip)/metrics  → requests_total 카운터 증가 확인
```

남은 것(hpa·network-policy·rbac·helm)은 표에 표시한 대로 PF1·CKA 단계에서 이어서 채운다 — 오늘은 "PF-K8s 첫 조각"까지가 목표였다.
