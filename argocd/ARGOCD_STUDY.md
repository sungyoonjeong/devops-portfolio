# ArgoCD / GitOps 개념 정리

CI/CD D2 학습 — CI가 끝난 뒤(이미지가 레지스트리에 올라간 뒤) 그 이미지를 실제 클러스터에 배포하는 부분을 ArgoCD로 자동화한다. 여기도 0장부터 — GitOps라는 말을 처음 듣는다는 전제로 시작한다.

---

## 0. GitOps가 뭔가 — 지금까지 방식과 뭐가 다른가

### 지금까지 K8s에 배포하던 방식 (수동 push 방식)

`k8s/`, `PortFolio/PF-K8s/k8s/` 실습에서는 전부 이렇게 배포했다:

```bash
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml
```

이 방식의 문제는:
1. **누가 언제 뭘 배포했는지 기록이 안 남는다** — 터미널 히스토리를 뒤지지 않는 한, 지금 클러스터 상태가 어떤 커밋에서 나온 건지 알 수 없다.
2. **로컬 kubectl 자격증명이 있는 사람은 누구나 클러스터를 직접 바꿀 수 있다** — YAML 파일과 무관하게 `kubectl edit`으로 즉석에서 고쳐버리면, Git에 있는 파일(코드)과 클러스터의 실제 상태(런타임)가 조용히 어긋난다 — 이걸 **드리프트(drift)**라고 부른다.
3. **롤백이 번거롭다** — 이전 버전으로 되돌리려면 이전 YAML을 다시 찾아서 수동으로 apply해야 한다.

### GitOps — "Git이 곧 정답"이라는 원칙

GitOps는 이 문제를 뒤집는다: **클러스터에 뭘 배포할지 사람이 `kubectl apply`로 직접 넣는 게 아니라, Git 저장소에 있는 YAML 파일을 클러스터가 스스로 계속 확인해서 그것과 똑같아지도록 자기 자신을 맞춘다.**

핵심 규칙 3가지:
1. **Git 저장소의 YAML이 "원하는 상태(desired state)"의 유일한 정답이다.** 클러스터를 직접 고치는 게 아니라 Git의 YAML을 고치고 커밋한다.
2. **클러스터 안에서 도는 에이전트(여기선 ArgoCD)가 Git을 계속 지켜보며 스스로 동기화(sync)한다.** 사람이 배포 명령을 실행하는 게 아니라, 에이전트가 "Git과 클러스터가 다르네? 클러스터를 Git에 맞추자"를 반복한다.
3. **모든 변경 이력이 Git 커밋 로그에 그대로 남는다.** 누가 언제 뭘 바꿨는지, 이전 상태로 되돌리려면 어느 커밋으로 되돌리면 되는지가 전부 Git 히스토리에 있다.

### Push 방식 vs Pull 방식 — 이 차이가 진짜 핵심

- **Push 방식(지금까지 CI가 하던 방식)**: CI 서버(GitHub Actions)가 클러스터에 접속할 수 있는 자격증명을 들고, **CI 쪽에서 클러스터로 명령을 밀어 넣는다**(`kubectl apply` 실행). 이건 CI 서버가 클러스터 접근 권한을 갖고 있어야 한다는 뜻이라, CI 서버가 뚫리면 클러스터도 위험해진다.
- **Pull 방식(GitOps/ArgoCD)**: 클러스터 안에 있는 ArgoCD가 **클러스터 쪽에서 Git 저장소를 계속 당겨(pull) 온다.** 외부(CI)가 클러스터에 접근할 필요가 아예 없다 — ArgoCD가 클러스터 내부에서 바깥의 Git을 읽기만 하면 되니, 공격 표면이 훨씬 좁아진다.

이번 실습에서 만든 CI(`pf2-ci.yml`)는 **이미지를 빌드해서 ECR에 올리는 것까지만** 하고, 그 이미지를 실제로 클러스터에 배포하는 마지막 단계는 하지 않는다 — 그 역할을 여기서부터 ArgoCD가 넘겨받는다.

---

## 1. ArgoCD 아키텍처 — 구성 요소

ArgoCD를 설치하면 `argocd` 네임스페이스 안에 여러 컴포넌트가 뜬다:

| 컴포넌트 | 역할 |
|---|---|
| `argocd-server` | API 서버 + 웹 UI를 제공. `argocd` CLI나 웹 브라우저가 여길 통해 ArgoCD와 대화한다. |
| `argocd-repo-server` | Git 저장소를 실제로 clone/pull해서 그 안의 YAML(또는 Helm 차트)을 해석하는 역할. |
| `argocd-application-controller` | **핵심 두뇌** — Git에서 읽은 "원하는 상태"와 클러스터의 "실제 상태"를 계속 비교(diff)하고, 다르면 동기화를 실행한다. |
| `argocd-applicationset-controller` | 여러 개의 Application을 템플릿으로 한 번에 관리할 때 쓴다(지금은 안 씀, Application 1개만 등록). |
| `argocd-dex-server` | SSO 로그인(구글·GitHub 계정 등) 연동용 — 지금은 기본 admin 계정만 쓰므로 실질적으로 안 씀. |
| `argocd-redis` | 캐시 저장소. |

이 중에서 개념적으로 제일 중요한 건 **application-controller**다 — "Git과 클러스터를 비교해서 다르면 맞춘다"는 GitOps의 핵심 동작이 여기서 일어난다.

## 2. Application — ArgoCD가 관리하는 배포 단위

ArgoCD에 "이 Git 경로에 있는 YAML을 이 클러스터의 이 네임스페이스에 계속 동기화해줘"라고 알려주는 게 **Application**이라는 커스텀 리소스(CRD)다. 최소 구성은 이렇다:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: pf2                    # ArgoCD 안에서 이 배포를 부르는 이름
  namespace: argocd            # Application 리소스 자체는 항상 argocd 네임스페이스에 둔다
spec:
  project: default             # 여러 Application을 묶는 논리적 그룹(RBAC 경계) - 기본값 사용
  source:                      # "원하는 상태"를 어디서 읽을지
    repoURL: https://github.com/sungyoonjeong/devops-portfolio.git
    targetRevision: main       # 어느 브랜치를 기준으로 볼지
    path: PortFolio/PF-K8s/k8s # 그 저장소 안의 어느 경로에 YAML이 있는지
  destination:                 # 그 상태를 어디에 반영할지
    server: https://kubernetes.default.svc   # 배포 대상 클러스터 (지금은 ArgoCD가 떠 있는 클러스터 자신)
    namespace: default         # 배포 대상 네임스페이스
  syncPolicy:
    automated:                 # 자동 동기화 - 이게 없으면 매번 수동으로 "Sync" 버튼을 눌러야 한다
      prune: true              # Git에서 파일이 삭제되면 클러스터에서도 그 리소스를 삭제
      selfHeal: true           # 클러스터를 직접 kubectl로 고쳐도(드리프트) 다시 Git 상태로 되돌림
```

`prune`과 `selfHeal`이 GitOps의 "Git이 유일한 정답"이라는 원칙을 실제로 강제하는 옵션이다 — 이 둘을 켜두면, Git의 YAML을 지우면 클러스터에서도 지워지고(prune), 클러스터를 직접 수동으로 고쳐도 ArgoCD가 다시 Git 상태로 되돌려버린다(selfHeal, 반대로 얘기하면 "수동 hotfix가 자동으로 무효화된다"는 뜻이니 운영 중엔 이게 의도한 동작인지 주의해서 켜야 한다).

## 3. Sync — 동기화가 실제로 일어나는 과정

1. `argocd-repo-server`가 주기적으로(기본 3분) Git 저장소를 polling(또는 GitHub webhook으로 즉시 알림받기)해서 최신 커밋을 가져온다.
2. `argocd-application-controller`가 그 YAML이 정의하는 "원하는 상태"와 클러스터의 "현재 상태"를 비교한다.
3. 차이가 있으면 **OutOfSync** 상태로 표시하고, `syncPolicy.automated`가 켜져 있으면 자동으로 `kubectl apply`에 해당하는 작업을 실행해 클러스터를 Git 상태로 맞춘다(수동 모드면 사람이 UI에서 "Sync" 버튼을 눌러야 함).
4. 반영이 끝나면 **Synced** 상태로 바뀌고, 각 리소스(Pod, Service 등)가 정상 기동됐는지까지 확인해 **Healthy**로 표시한다.

즉 ArgoCD 화면에서 보는 상태는 항상 두 축이다 — **Sync 상태**(Git과 클러스터가 같은가?)와 **Health 상태**(그 리소스가 실제로 잘 떠 있는가?).

## 4. 지금까지 만든 CI/CD 흐름에 어떻게 이어붙는가

```
① 코드 push → GitHub Actions CI(pf2-ci.yml)
   lint → test → docker-build → trivy-scan → ecr-push
   (이미지가 ECR에 새 태그로 올라감)

② PortFolio/PF-K8s/k8s/deployment.yaml 의 image 태그를 그 새 태그로 갱신 → Git commit·push
   (지금은 이 갱신을 수동으로 한다 — CI가 이 커밋까지 자동으로 만들게 하는 건
    "이미지 태그 자동 업데이트"라는 별도 주제라 PF1 단계에서 다룰 예정)

③ ArgoCD가 Git의 변경을 감지 → OutOfSync 판정 → 자동 Sync
   (클러스터의 kubectl apply를 ArgoCD가 대신 실행)

④ 클러스터에 새 이미지로 Pod가 재기동됨
```

②까지는 사람(또는 별도 자동화)이 "이미지 태그를 Git에 반영"하는 역할이고, ③~④가 ArgoCD의 몫이다 — **CI는 빌드까지, CD(GitOps)는 그 다음부터**라는 경계가 명확해진다.

---

## 5. 배운 것 — 왜 이 구조가 "더 안전하다"고 하는가

- **최소 권한**: CI 서버(GitHub Actions)는 이제 클러스터 자격증명을 아예 몰라도 된다 — ECR에 이미지를 올리는 권한만 있으면 끝. 클러스터에 뭔가를 반영하는 건 클러스터 내부의 ArgoCD가 스스로 하니, "외부 시스템이 내 클러스터를 조작할 수 있는 통로" 자체가 하나 줄어든다.
- **감사(audit) 용이성**: "지금 운영 중인 게 정확히 어느 커밋인가?"라는 질문에 항상 Git 커밋 해시로 답할 수 있다.
- **자기 치유(selfHeal)**: 누가 실수로 `kubectl scale --replicas=0` 같은 걸 쳐도, ArgoCD가 Git에 정의된 `replicas: 3`으로 금방 되돌린다.
