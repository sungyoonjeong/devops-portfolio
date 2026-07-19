# CI/CD D2 — ArgoCD GitOps 실습

목표: 이미 떠 있는 PF2 K8s 리소스(`PortFolio/PF-K8s/k8s/`)를 ArgoCD로 관리 전환한다. 개념은 [ARGOCD_STUDY.md](ARGOCD_STUDY.md) 참조, 여기는 실제로 실행한 명령과 결과 기록.

---

## 1. ArgoCD 설치

`argocd`라는 별도 네임스페이스에, 공식 설치 매니페스트로 컨트롤러·API 서버·repo 서버 등을 한 번에 설치한다.

```bash
$ kubectl create namespace argocd
namespace/argocd created

$ kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

한 가지 에러가 났다:

```
The CustomResourceDefinition "applicationsets.argoproj.io" is invalid: metadata.annotations: Too long: may not be more than 262144 bytes
```

**원인**: `kubectl apply`는 기본적으로 "마지막으로 적용한 설정 전체"를 리소스의 annotation(`kubectl.kubernetes.io/last-applied-configuration`)에 통째로 저장해두는데, ArgoCD의 CRD 정의 자체가 워낙 커서 그 annotation이 etcd가 허용하는 annotation 최대 크기(256KiB)를 넘어버렸다. 즉 리소스 자체가 문제가 아니라 apply 방식이 문제였다.

**해결**: `--server-side` 옵션으로 재시도. 서버사이드 apply는 변경 이력을 저장하는 방식이 달라서(필드별 소유권 추적, 전체 설정을 annotation에 우겨넣지 않음) 이 크기 제한에 걸리지 않는다.

```bash
$ kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml --server-side --force-conflicts
service/argocd-server-metrics serverside-applied
deployment.apps/argocd-server serverside-applied
...

$ kubectl get crd | grep argoproj
applications.argoproj.io      2026-07-19T13:51:57Z
applicationsets.argoproj.io   2026-07-19T13:52:11Z
appprojects.argoproj.io       2026-07-19T13:51:57Z
```

파드가 다 뜨는 데 시간이 좀 걸린다(이미지가 500MB대라 pull에 시간 소요). 기다리는 중 `argocd-redis` 하나가 유독 `Init:0/1`에서 멈췄다 — describe로 보니 init 컨테이너 자체는 정상 실행 중인데 응답이 없었다. 그 워커 노드(`minikube-m03`)의 일시적인 문제로 보고 파드를 지워서 다른 노드로 재스케줄링했다:

```bash
$ kubectl delete pod -n argocd argocd-redis-75d59bd487-78bnj
pod "argocd-redis-75d59bd487-78bnj" deleted

$ kubectl get pods -n argocd -o wide | grep redis
argocd-redis-75d59bd487-5rrfr   1/1   Running   0   31s   10.244.1.7   minikube-m02
```

`minikube-m02`로 다시 뜨자 바로 정상화됐다. 전체 상태 확인:

```bash
$ kubectl get pods -n argocd
NAME                                               READY   STATUS    RESTARTS   AGE
argocd-application-controller-0                    1/1     Running   0          7m21s
argocd-applicationset-controller-fb85f95b8-pgqdw   1/1     Running   0          7m21s
argocd-dex-server-58bfb96c55-85jgr                 1/1     Running   0          7m21s
argocd-notifications-controller-688c844f96-wvn6g   1/1     Running   0          7m21s
argocd-redis-75d59bd487-5rrfr                      1/1     Running   0          36s
argocd-repo-server-7dfdcc5485-c8f7x                1/1     Running   0          7m21s
argocd-server-6984669db8-q5kqv                     1/1     Running   0          7m21s
```

7개 컴포넌트 전부 `Running` — [ARGOCD_STUDY.md](ARGOCD_STUDY.md) 1장에서 정리한 구성 요소(server·repo-server·application-controller·applicationset-controller·dex-server·redis·notifications-controller) 그대로다.

---

## 2. CLI 설치 + 로그인

`argocd`는 GUI(웹 화면)와 CLI 둘 다 제공한다. CLI 바이너리를 받아서 설치:

```bash
$ curl -sSL -o /tmp/argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
$ chmod +x /tmp/argocd && cp /tmp/argocd ~/.local/bin/argocd
$ argocd version --client
argocd: v3.4.5+564b949
```

ArgoCD 서버는 클러스터 내부에만 떠 있어서(`ClusterIP` 서비스) 바깥에서 바로 접근이 안 된다. `kubectl port-forward`로 로컬 포트를 그 서비스에 연결해야 CLI든 브라우저든 접근할 수 있다:

```bash
$ kubectl port-forward svc/argocd-server -n argocd 8080:443 &
```

초기 admin 비밀번호는 설치할 때 자동 생성돼서 시크릿에 저장돼 있다(최초 1회만 확인하고, 실제로는 로그인 후 바꾸는 게 정석):

```bash
$ kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

```bash
$ argocd login localhost:8080 --username admin --password <위 비밀번호> --insecure
'admin:login' logged in successfully
Context 'localhost:8080' updated
```

`--insecure`는 ArgoCD 서버의 TLS 인증서가 자체서명(self-signed)이라 브라우저/CLI가 신뢰하지 않기 때문에 붙였다 — 로컬 실습이라 문제없지만, 실무에서는 정식 인증서를 붙이는 게 원칙이다.

---

## 3. Application 등록 — PF2를 GitOps로 전환

`argocd/pf2-application.yaml`(이 폴더에 커밋됨):

```yaml
# ArgoCD Application - PF2를 GitOps 방식으로 관리하겠다는 선언
# 이 리소스 자체는 kubectl apply로 한 번만 넣는다 - 그 뒤로는 PortFolio/PF-K8s/k8s/의
# YAML을 고쳐서 git push하면 ArgoCD가 알아서 클러스터에 반영한다 (kubectl apply를 다시 안 쳐도 됨)
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: pf2
  namespace: argocd              # Application 리소스는 항상 argocd 네임스페이스에 둔다
spec:
  project: default
  source:
    repoURL: https://github.com/sungyoonjeong/devops-portfolio.git
    targetRevision: main
    path: PortFolio/PF-K8s/k8s   # 이 경로의 deployment.yaml/service.yaml/ingress.yaml을 감시
  destination:
    server: https://kubernetes.default.svc   # ArgoCD가 떠 있는 이 클러스터 자신
    namespace: default
  syncPolicy:
    automated:
      prune: true                # Git에서 파일이 사라지면 클러스터에서도 삭제
      selfHeal: true              # 클러스터를 수동으로 고쳐도 Git 상태로 되돌림
    syncOptions:
      - CreateNamespace=true
```

```bash
$ kubectl apply -f argocd/pf2-application.yaml
application.argoproj.io/pf2 created

$ argocd app get pf2
...
Sync Status:        Synced to main (d0764c1)
Health Status:      Healthy

GROUP              KIND        NAMESPACE  NAME         STATUS  HEALTH   MESSAGE
                   Service     default    pf2-svc      Synced  Healthy  service/pf2-svc configured
apps               Deployment  default    pf2          Synced  Healthy  deployment.apps/pf2 configured
networking.k8s.io  Ingress     default    pf2-ingress  Synced  Healthy  ingress.networking.k8s.io/pf2-ingress configured
```

PF2는 이미 `kubectl apply`로 떠 있던 상태였는데, ArgoCD가 그 기존 리소스를 그대로 "인식"해서 `Synced`·`Healthy`로 관리에 편입시켰다 — Git의 YAML과 클러스터의 실제 상태가 이미 같았기 때문에 별다른 변경 없이 바로 동기화 완료로 판정된 것. 이 시점부터 이 3개 리소스(Deployment·Service·Ingress)는 더 이상 수동 `kubectl apply` 대상이 아니라 ArgoCD 관리 대상이다.

---

## 4. selfHeal 실증 — 수동으로 클러스터를 건드려도 되돌아오는지 확인

`syncPolicy.automated.selfHeal: true`가 실제로 동작하는지, replicas를 강제로 3 → 1로 줄여봤다:

```bash
$ kubectl scale deployment pf2 --replicas=1
deployment.apps/pf2 scaled

$ kubectl get deploy pf2      # 직후
NAME   READY   UP-TO-DATE   AVAILABLE   AGE
pf2    1/3     3            1           2d21h

$ sleep 30 && kubectl get deploy pf2      # 30초 뒤
NAME   READY   UP-TO-DATE   AVAILABLE   AGE
pf2    3/3     3            3           2d21h
```

수동으로 1로 줄인 지 30초 만에 ArgoCD가 스스로 다시 3으로 되돌렸다 — `kubectl apply`를 다시 실행한 사람은 아무도 없다. **Git에 `replicas: 3`이라고 적혀 있는 한, 클러스터를 아무리 수동으로 건드려도 결국 그 상태로 수렴한다**는 selfHeal의 동작을 직접 확인한 것.

---

## 5. Git → 클러스터 자동 동기화 실증

이번엔 반대 방향 — Git의 YAML을 실제로 고쳐서 push하면, `kubectl apply`를 한 번도 안 쳤는데도 클러스터가 그 내용으로 바뀌는지 확인한다.

`PortFolio/PF-K8s/k8s/deployment.yaml`의 메모리 limit을 64Mi → 96Mi로 수정(GitHub Flow에 따라 `feature/argocd-gitops-demo` 브랜치에서 작업 후 `main`에 머지):

```bash
$ git checkout -b feature/argocd-gitops-demo
$ sed -n '27,30p' PortFolio/PF-K8s/k8s/deployment.yaml
          limits:
            cpu: 200m
            memory: 96Mi
$ git add PortFolio/PF-K8s/k8s/deployment.yaml
$ git commit -m "chore(pf-k8s): ArgoCD GitOps 동기화 실증 - 메모리 limit 64Mi->96Mi"
$ git checkout main && git merge --no-ff feature/argocd-gitops-demo && git push origin main
```

ArgoCD는 기본적으로 3분 주기로 Git을 polling한다. 실습에서는 그 주기를 기다리는 대신 `--refresh`로 즉시 최신 커밋을 확인하게 했다(운영에서는 GitHub webhook을 걸어 push 즉시 알림받는 방식을 쓴다 — polling보다 훨씬 빠르고, ArgoCD 공식 문서가 권장하는 방식):

```bash
$ argocd app get pf2 --refresh
Sync Status:        OutOfSync from main (44b2576)   # 새 커밋을 감지, 아직 반영 전

$ sleep 15 && argocd app get pf2
Sync Status:        Synced to main (44b2576)         # automated sync가 자동 실행돼 반영 완료
Health Status:      Healthy
```

실제로 파드가 새로 떴는지 확인:

```bash
$ kubectl get rs -l app=pf2
NAME             DESIRED   CURRENT   READY   AGE
pf2-67d4cd7cc8   3         3         3       26s     # 새 이미지 스펙으로 새 ReplicaSet 생성
pf2-fc4cc5777    0         0         0       2d21h    # 이전 ReplicaSet은 0으로 축소(롤링 업데이트)

$ kubectl get pods -l app=pf2 -o wide
NAME                   READY   STATUS    RESTARTS   AGE   NODE
pf2-67d4cd7cc8-7drzh   1/1     Running   0          30s   minikube
pf2-67d4cd7cc8-84bn6   1/1     Running   0          36s   minikube-m03
pf2-67d4cd7cc8-l8z86   1/1     Running   0          27s   minikube-m02
```

3노드 클러스터에 새 파드 3개가 골고루 분산 배치되며 롤링 업데이트가 일어났다. `kubectl apply`는 단 한 번도 실행하지 않았다 — **git push 한 번이 곧 배포**가 되는 GitOps의 핵심을 실제로 확인.

배포 이력도 Git 커밋과 1:1로 남는다:

```bash
$ argocd app history pf2
ID      DATE                           REVISION
0       2026-07-19 23:01:55 +0900 KST  main (d0764c1)   # 최초 인식 시점
1       2026-07-19 23:03:27 +0900 KST  main (44b2576)   # 메모리 limit 변경 반영
```

이전 상태로 되돌리고 싶으면 `argocd app rollback pf2 0`으로 리비전 0(커밋 `d0764c1` 시점)으로 즉시 되돌릴 수 있다 — Git revert 없이도 클러스터만 빠르게 이전 상태로 되돌리는 롤백 기능이다(단, `selfHeal`이 켜져 있으면 다음 sync 때 다시 최신 Git 상태로 돌아가므로, 진짜 되돌리려면 Git 쪽도 revert해야 한다).

---

## 6. 다음 단계

- 지금은 로컬 minikube 이미지(`pf2:021c651`, `imagePullPolicy: Never`)를 그대로 GitOps로 관리하는 구조 — PF1 단계에서 ECR에 올라간 실제 이미지(`ecr-push` job 산출물)를 pull하도록 전환하고, ECR 접근용 `imagePullSecrets`도 함께 구성 예정.
- ArgoCD `Sync Status`를 웹 UI에서도 확인 가능(`kubectl port-forward` 후 `https://localhost:8080`) — CLI로 충분히 확인했지만, 다음 실습 때 브라우저로 그래프 뷰(리소스 트리)도 한 번 볼 것.
- CI(`pf2-ci.yml`)가 이미지 태그를 만든 뒤 `PortFolio/PF-K8s/k8s/deployment.yaml`의 `image:` 태그를 자동으로 갱신해 커밋하는 단계까지 이어붙이면, "push 한 번으로 빌드부터 배포까지 전부 자동"인 완전한 CI/CD 파이프라인이 완성된다(PF1 목표).
