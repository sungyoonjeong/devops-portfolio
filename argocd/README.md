# ArgoCD GitOps 실습

CI(`../cicd/`)가 이미지를 만들어 ECR에 올리는 데까지였다면, 여기서는 그 다음 단계 — 실제 클러스터에 배포하는 과정을 ArgoCD로 자동화한다. `PortFolio/PF-K8s/k8s/`에 있는 PF2 매니페스트를 Git 기준으로 클러스터가 스스로 동기화하도록 전환했다.

이론은 `ARGOCD_STUDY.md`(GitOps 개념부터), 실습 기록은 `ARGOCD_PRACTICE.md`.

## 구성

- `ARGOCD_STUDY.md` — GitOps란 무엇인가, Push vs Pull 배포, ArgoCD 아키텍처, Application 리소스, Sync 동작 원리
- `ARGOCD_PRACTICE.md` — 설치 과정(+ 실제로 만난 에러 2건과 해결), Application 등록, selfHeal 실증, Git→클러스터 자동 동기화 실증
- `pf2-application.yaml` — 실제로 클러스터에 적용한 Application 정의(한 줄 주석 포함)

## 실행

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443 &
argocd login localhost:8080 --username admin --password <초기 비밀번호> --insecure
argocd app get pf2
```

## 메모

- ArgoCD가 관리하기 시작하면 그 리소스는 `kubectl apply`로 직접 건드리면 안 된다 — `selfHeal`이 켜져 있어 곧바로 Git 상태로 되돌아간다. 바꾸려면 항상 Git의 YAML을 고치고 push.
- CRD가 큰 리소스는 `kubectl apply`가 아니라 `kubectl apply --server-side`를 써야 annotation 크기 제한에 안 걸린다.
- 다음: PF1에서 ECR 실제 이미지로 전환 + CI가 이미지 태그를 자동으로 Git에 반영하는 단계까지 이어붙이기.

## 다음 — 이 시리즈의 순서

`../cicd/`(빌드) → **여기(배포)** → [`../observability/`](../observability/)(관측) 순서로 이어진다. 여기서 GitOps로 관리하게 된 PF2에 실제 Prometheus 지표를 붙이는 게 다음 단계다 — `observability/` 실습에서도 이미지 태그 갱신을 여기서 검증한 것과 똑같은 "Git 수정 → push → ArgoCD 자동 배포" 흐름을 그대로 재사용한다.
