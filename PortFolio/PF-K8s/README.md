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

### 2026-07-17 — 첫 조각 배포 완료 (deployment·service·ingress)

**이 마일스톤의 목표**: PF2는 6월에 이미 "K8s가 이 /health를 호출할 것"을 전제로 만든 서버였다(`main.go` 주석에 "로드밸런서나 오케스트레이터(K8s)가 주기적으로 호출해 서버 상태를 판단한다"고 이미 적혀 있음). 지금까지 K8s 강의(1~11장)로 배운 Pod·Controller·Service·Ingress·프로브 개념을 흩어진 실습이 아니라 **실제 내 애플리케이션 하나에 전부 꿰어서 적용**하는 것이 이번 조각의 목적이다. 동시에 이건 PF1·캡스톤에서 훨씬 큰 스케일로 반복할 "이미지 빌드 → 클러스터 배포 → 외부 노출 → 헬스체크 검증" 파이프라인의 최소 버전이기도 하다 — 여기서 막힌 걸 오늘 풀어두면 PF1에서는 규모만 커질 뿐 새로 배울 개념이 없다.

과정과 스크린샷·트러블슈팅 상세는 [../../k8s/PRACTICE.md](../../k8s/PRACTICE.md)의 "PF2 K8s 배포" 절 참고. 여기서는 무엇을 왜 그렇게 만들었는지만 정리한다.

**아키텍처**

```
클라이언트
    │ curl -H "Host: pf2.local" http://<minikube ip>/health
    ▼
┌─────────────────────────┐
│  Ingress (pf2-ingress)  │  L7 라우터, nginx ingress controller가 처리
│  host: pf2.local         │  rewrite-target: / 로 path를 백엔드에 "/"로 넘김
└────────────┬─────────────┘
             │
             ▼
┌─────────────────────────┐
│  Service (pf2-svc)      │  ClusterIP, 80 → 8080
│  selector: app=pf2       │  kube-proxy가 아래 3개 파드에 균등 분배
└──┬───────────┬───────────┬┘
   ▼           ▼           ▼
 pf2-pod    pf2-pod     pf2-pod
(minikube)  (m02)       (m03)      ← Deployment가 3노드에 흩어 배치, 하나 죽으면 self-healing
```

**만든 것과 각각의 이유**

| 구성 요소 | 선택 | 이유 |
|---|---|---|
| 이미지 태그 | `pf2:021c651`(커밋 해시) | PF2 `deploy.sh`와 동일한 전략 — 이미지·코드·(나중엔 Trivy 리포트까지)를 1:1 추적, `latest` 태그가 주는 "지금 뭐가 떠 있는지 모름" 문제를 원천 차단 |
| 이미지 전달 | `docker build` → `minikube image load` | 아직 레지스트리(ECR)가 없는 단계라 로컬 빌드를 클러스터 3노드 런타임에 직접 밀어넣음. **한계**: 이 방식은 minikube 전용 임시 수단이고, 실제 다중 노드 프로덕션에서는 안 통한다 — 7/17~18 CI/CD에서 ECR push로 교체 예정(아래 "다음 단계" 참고) |
| `imagePullPolicy: Never` | 명시 지정 | 위 로컬 로드 방식과 짝 — 안 걸면 K8s가 Docker Hub에서 `pf2` 이미지를 찾다가 실패(`ImagePullBackOff`)한다. ECR로 옮기면 이 필드도 `IfNotPresent`로 바뀔 예정 |
| `replicas: 3` | 3 | 3노드 전체를 쓰는 배치를 눈으로 확인하기 위해 노드 수와 맞춤. scheduler가 실제로 minikube·m02·m03에 하나씩 배치하는 것까지 확인 |
| readiness/liveness 둘 다 `/health` | 같은 엔드포인트, 다른 목적 | PF2가 엔드포인트를 하나만 노출하므로 동일 경로를 재사용. readiness는 "당장 트래픽 받아도 되나"(실패 시 Service에서만 제외), liveness는 "프로세스가 살아있나"(실패 시 재시작) — 목적이 다르므로 앞으로 엔드포인트를 분리할지(예: `/ready` vs `/healthz`)는 PF1에서 실제 부하가 생기면 재검토 |
| resources 50m/32Mi ~ 200m/200m | 가볍게 | Go 정적 바이너리 + alpine 10MB 이미지라 실측 사용량이 매우 작음. limits를 넉넉히 잡지 않은 이유는 "요청도 못 받는 프로세스가 자원을 무제한 예약"하는 걸 막기 위함(5장에서 배운 requests=스케줄링 기준·limits=제재 기준의 실전 적용) |
| Ingress `rewrite-target: /` | 명시 지정 | 7/16 메인·결제 페이지 실습에서 이거 없이 path 라우팅을 걸었다가 404를 만났던 함정을 알고 시작 — 지금은 path가 `/` 하나뿐이라 사실상 no-op이지만, PF1에서 서비스가 여러 개로 늘어나 path가 갈라질 때 그대로 재사용할 습관을 들여둠 |

**검증**

```bash
kubectl rollout status deployment pf2       # 3/3 successfully rolled out
kubectl get pod -l app=pf2 -o wide          # 3노드에 하나씩 분산 확인
curl -H "Host: pf2.local" http://$(minikube ip)/health
# {"status":"ok","timestamp":"2026-07-16T16:16:42Z"}
curl -H "Host: pf2.local" http://$(minikube ip)/metrics
# {"requests_total":13,"uptime_seconds":38}
```

`requests_total`이 실제 curl 호출(2번)보다 훨씬 큰 이유: readiness(5초)·liveness(10초) 프로브가 파드 3개에서 계속 `/health`를 때리고 있고, PF2 코드가 프로브 요청도 동일 카운터에 합산하기 때문. 실 트래픽과 헬스체크 트래픽이 지표에서 안 갈라진다는 걸 여기서 발견 — 8월 Observability에서 Prometheus 지표를 설계할 때 이 문제를 어떻게 가를지(예: 프로브 User-Agent로 필터링) 이어서 고려할 대상.

**다음 단계 (남은 것)**

표의 hpa·network-policy·rbac·helm은 PF1·CKA 단계에서 이어서 채운다:

- **hpa.yaml** — PF1(7/20~)에서 실제 부하테스트와 함께 CPU 60% 기준 오토스케일링 실습
- **helm/app-chart** — PF1에서 지금의 3개 yaml을 차트로 패키징, values.yaml로 dev/prod 분리
- **rbac/** — CKA 준비(8/14~) 핵심 범위와 겸해서 진행
- **network-policy.yaml** — PF1에서 다른 서비스(캡스톤 등)와 네임스페이스가 분리될 때 추가
- **이미지 전달 방식 교체** — CI/CD D1(7/17~18)에서 `minikube image load` → ECR push + `imagePullPolicy: IfNotPresent`로 전환, 이번 조각이 임시 수단이었음을 실제로 해소

**면접 포인트 요약**

| 질문 | 핵심 답변 |
|---|---|
| readinessProbe와 livenessProbe를 같은 경로에 걸었는데 문제 없나요? | 목적이 다르므로 지금 규모(단일 엔드포인트)에선 문제없지만, 트래픽이 늘면 readiness에 의존성 체크(DB 연결 등)를 추가로 얹고 liveness는 프로세스 생존만 보는 식으로 분리하는 게 정석 |
| 왜 이미지를 레지스트리에 안 올리고 로컬 로드를 썼나요? | CI/CD 파이프라인(ECR push)이 아직 구축 전 단계였기 때문. `minikube image load`는 로컬 실습 전용 임시 수단이고, `imagePullPolicy: Never`가 그 임시성을 명시적으로 드러낸다. CI/CD 구축 후 ECR로 교체 예정 |
| requests_total 지표에 프로브 트래픽이 섞이는 게 왜 문제인가요? | 실제 사용자 트래픽 양을 지표로 오판할 수 있다. Prometheus 등으로 모니터링을 붙일 때는 헬스체크 경로를 지표 집계에서 제외하거나 별도 레이블로 구분해야 한다 |
| 3 replicas인데 굳이 3으로 맞춘 이유는? | 지금은 트래픽 근거가 아니라 3노드 클러스터 전체에 분산 배치가 실제로 되는지 검증하려는 학습 목적. 운영에서는 트래픽·가용성 요구사항(예: 1노드 다운 시에도 서비스 유지)에 따라 정하고, 이후 hpa.yaml이 붙으면 고정값 대신 min/max 범위로 바뀐다 |
