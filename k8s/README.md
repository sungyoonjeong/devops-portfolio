# Kubernetes 학습

따배쿠 입문 강의(1~11장) 기준 개념 정리 + minikube 3노드 클러스터에서 직접 실습. 이론은 `K8S_STUDY.md`, 실습 기록(명령·결과·스크린샷)은 `PRACTICE.md`, 최초 환경 구축은 `SETUP.md`.

## 구성

- `SETUP.md` — minikube 환경 구축(WSL2 + Docker, 단일→3노드)
- `K8S_STUDY.md` — 1장 소개 ~ 11장 Secret + 부록(구버전 대조표, kubectl 치트시트, 배포전략 비교, 복습질문)
- `PRACTICE.md` — 날짜별 실습 기록: Namespace·Pod·Deployment(7/7) → ReplicationController(7/8) → DaemonSet·Job·CronJob·Service 5종·Ingress·ConfigMap·Secret(7/16) → PF2 배포(7/17)
- `images/` — 실습 스크린샷
- `*.yaml` — 실습하며 만든 매니페스트 원본(아래 표)

### 매니페스트 목록

| 파일 | 내용 |
|---|---|
| `webserver.pod.yaml`, `redis.yaml`, `nginx.yaml` | 기본 Pod |
| `init-pod.yaml`, `liveness-pod.yaml`, `env-pod.yaml`, `resource-pod.yaml` | Pod 심화(init container·livenessProbe·환경변수·리소스 제한) |
| `pod-cm.yaml`, `pod-secret.yaml`, `pod-nodeselector.yaml` | ConfigMap·Secret 주입, nodeSelector |
| `rc-nginx.yaml`, `rs-nginx.yaml` | ReplicationController·ReplicaSet |
| `deploy-nginx.yaml`, `deploy-web.yaml`, `deployment-exam1.yaml`, `deployment-exam2.yaml` | Deployment |
| `job-hello.yaml`, `cronjob-date.yaml` | Job·CronJob |
| `svc-headless.yaml`, `svc-extname.yaml` | Service(headless·ExternalName) |
| `ingress-web.yaml` | Ingress 기본 |
| `shop-configmaps.yaml`, `shop-deploy.yaml`, `shop-ingress.yaml` | 다중 앱(메인·결제) path 라우팅 시나리오 |
| `orange-ns.yaml` | Namespace |
| `practice-pod.yaml` | 잡다한 명령형→선언형 변환 연습 |

PF2 K8s 배포(Deployment·Service·Ingress 3종)는 이 폴더가 아니라 `PortFolio/PF-K8s/k8s/`에 있다 — 학습용 매니페스트와 실제 포트폴리오 산출물을 분리했다.

## 메모

- v1.35 기준으로 강의(구버전)와 달라진 부분은 `K8S_STUDY.md` 부록 A에 정리 — 특히 `kubectl run`이 이제 Deployment가 아니라 Pod 1개만 만드는 게 최대 함정.
- Helm·HPA·RBAC은 여기서 다루지 않음(누락 아님) — Helm·HPA는 PF1에서 차트 작성·부하테스트로, RBAC은 CKA 드릴에서 실습 예정(`_system/PROGRESS.md` 계획표 참조).
- 다음: CI/CD D2에서 `PortFolio/PF-K8s/k8s/*.yaml`을 ArgoCD로 GitOps 전환.
