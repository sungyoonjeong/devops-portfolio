# K8S 실습 기록

개념은 [K8S_STUDY.md](K8S_STUDY.md), 환경은 [SETUP.md](SETUP.md) 참조. 여기는 날짜별 실습 로그.
환경: minikube 3노드 (마스터 minikube + 워커 m02·m03).

사용한 yaml 파일들은 이 폴더에 그대로 있음:

```
webserver.pod.yaml   run으로 만든 파드를 --dry-run -o yaml로 뽑아 저장한 것
nginx.yaml           mypod (namespace 실습용, 포트 80/443)
orange-ns.yaml       Namespace를 dry-run으로 뽑은 것
practice-pod.yaml    선언형 Pod 생성용 (yaml-pod)
liveness-pod.yaml    livenessProbe 실패 유도 실습
init-pod.yaml        init container 실습
resource-pod.yaml    requests/limits 실습
env-pod.yaml         환경변수 주입 실습
rc-nginx.yaml        ReplicationController 실습 (replicas 3, selector app=webui)
deploy-nginx.yaml    Deployment 실습 — 같은 스펙, kind만 Deployment
deployment-exam1.yaml  롤링업데이트 실습 (app-deploy, 컨테이너명 web)
deployment-exam2.yaml  strategy 필드 실습용 — maxSurge·maxUnavailable·change-cause annotation
rs-nginx.yaml        ReplicaSet 실습 — RC와 같은 스펙, selector만 matchLabels 문법
redis.yaml           RC 라벨 실험용 — 일부러 같은 app=webui 라벨을 단 파드
```

---

## 7/7 — Namespace와 Context (4-2강)

### ns 만들기 두 가지 — 명령형, 그리고 dry-run으로 yaml 뽑기

blue는 명령형으로 바로 만들고, orange는 yaml을 뽑아서 만들었다:

```bash
kubectl create namespace blue
kubectl create namespace orange --dry-run -o yaml > orange-ns.yaml
kubectl create -f orange-ns.yaml
```

![dry-run으로 ns yaml 뽑기](images/ns-01-dryrun-yaml.png)

`--dry-run`만 쓰면 deprecated 경고가 뜬다 — 지금은 `--dry-run=client`가 정식 표기 (강의 시절 문법과의 차이).

![yaml로 orange ns 생성](images/ns-02-create-from-yaml.png)

`kubectl get ns` 하면 기본 4개(default·kube-system·kube-public·kube-node-lease) 옆에 blue·orange가 나란히 선다.

### 매번 -n 붙이기 귀찮으면 — context

특정 ns에서 계속 작업할 거면 그 ns를 기본값으로 하는 context를 만들 수 있다:

```bash
kubectl config set-context blue@minikube --cluster=minikube --user=minikube --namespace=blue
kubectl config view          # contexts에 blue@minikube 추가된 것 확인
```

![blue ns 전용 context 생성](images/ns-03-context-create.png)
![config view로 구조 확인](images/ns-04-config-view.png)

config view로 보면 kubeconfig의 3층 구조가 보인다 — **clusters**(접속할 apiserver 주소·인증서) / **users**(내 인증 정보) / **contexts**(cluster + user + namespace 조합). context = "어느 클러스터에, 누구로, 어느 ns를 기본으로" 세트.

```bash
kubectl config current-context               # minikube
kubectl config use-context blue@minikube     # 전환
kubectl config current-context               # blue@minikube — 이제 -n 없이도 blue가 기본
```

![context 전환](images/ns-05-context-switch.png)

### 다른 namespace에 파드 만들기

```bash
kubectl create -f nginx.yaml -n blue
kubectl get pods -n blue
```

![blue ns에 mypod 생성](images/ns-06-pod-in-blue.png)
![blue ns 조회](images/ns-07-get-pods-blue.png)

### namespace에 따라 조회 결과가 완전히 달라진다

```bash
kubectl get pods -n default
kubectl get pods -n kube-system
kubectl get pods --all-namespaces    # = -A
```

![네임스페이스별 조회](images/ns-08-pods-by-namespace.png)

kube-system을 보면서 얻어걸린 확인 하나 — **kindnet(CNI)과 kube-proxy가 정확히 3개씩** 있다. 노드가 3개니까. "모든 노드에 하나씩"은 6장에서 배울 DaemonSet의 동작이고, control plane 4종(etcd·apiserver·controller-manager·scheduler)은 이름 뒤에 노드명(-minikube)이 붙은 채 마스터에만 1개씩 있다.

### ns 삭제 — 안의 것들도 같이 죽는다

```bash
kubectl delete ns orange
```

![ns 삭제](images/ns-09-delete.png)

ns를 지우면 그 안의 리소스가 통째로 같이 삭제된다. 실습 후 blue도 정리하고 context는 원복:

```bash
kubectl config use-context minikube
```

---

## 7/7 — Pod·Deployment 기본 (5-1강 + 6장 예습)

### 명령형으로 Pod 2개 (nginx, httpd)

```bash
kubectl run nginx-pod --image=nginx --port=80
kubectl run httpd-pod --image=httpd --port=80
kubectl get pods -o wide
```
```
NAME        READY   STATUS    RESTARTS   AGE   IP           NODE
httpd-pod   1/1     Running   0          22s   10.244.1.4   minikube-m02
nginx-pod   1/1     Running   0          22s   10.244.2.6   minikube-m03
```

같은 명령인데 nginx는 m03, httpd는 m02로 갔다 — scheduler가 알아서 분산 배치한다는 걸 눈으로 확인.

`describe`의 Events를 보면 상태 흐름이 그대로 찍힌다: `Scheduled → Pulling → Pulled(19.9초, 이미지 161MB) → Created → Started`. 5장 "Pod 동작 flow"의 그 단계다.

### 클러스터 안에서 curl 확인

WSL에서 파드 IP로 바로 curl은 안 되니(파드 네트워크는 클러스터 내부 전용) 노드 안에서 확인:

```bash
minikube ssh -- curl -s 10.244.2.6 | head -3    # nginx 기본 페이지
minikube ssh -- curl -s 10.244.1.4 | head -3    # httpd 기본 페이지
```

둘 다 각 웹서버의 기본 환영 페이지 HTML이 반환됨.

### index.html 수정 — 수정이 즉시 반영되는지

```bash
kubectl exec nginx-pod -- sh -c 'echo "<h1>7/7 K8s Pod 실습 - 정성윤</h1>" > /usr/share/nginx/html/index.html'
minikube ssh -- curl -s 10.244.2.6
```
```
<h1>7/7 K8s Pod 실습 - 정성윤</h1>
```

컨테이너 안 파일을 고치면 재시작 없이 바로 반영 — D5에서 nginx html 고치던 것과 같은 원리(파일은 요청마다 새로 읽힘). 다만 파드가 재생성되면 사라지는 임시 수정이라는 것도 같이 기억할 것 (10장 ConfigMap이 정식 해법).

### YAML로 선언형 Pod 생성

[practice-pod.yaml](practice-pod.yaml)로:

```bash
kubectl apply -f practice-pod.yaml
```
```
pod/yaml-pod created
```

명령형(`run`)과 결과는 똑같은 Pod지만, 파일이 남아 재현·리뷰가 가능하다는 차이.

### Deployment — replicas 3 → self-healing → replicas 5

```bash
kubectl create deployment web-deploy --image=nginx --replicas=3
kubectl get deployment,rs,pods -l app=web-deploy -o wide
```
```
NAME                         READY   UP-TO-DATE   AVAILABLE
deployment.apps/web-deploy   3/3     3            3

NAME                                   DESIRED   CURRENT   READY
replicaset.apps/web-deploy-5fcbd96c7   3         3         3

NAME                             STATUS    IP            NODE
web-deploy-5fcbd96c7-lks85       Running   10.244.0.4    minikube
web-deploy-5fcbd96c7-nbc4r       Running   10.244.1.5    minikube-m02
web-deploy-5fcbd96c7-z52xb       Running   10.244.2.8    minikube-m03
```

3개가 마스터·워커1·워커2에 하나씩.

self-healing — 파드 하나를 직접 지워본다:

```bash
kubectl delete pod web-deploy-5fcbd96c7-z52xb
kubectl get pods -l app=web-deploy -o wide
```
```
NAME                          STATUS              AGE   NODE
web-deploy-5fcbd96c7-lks85    Running             52s   minikube
web-deploy-5fcbd96c7-nbc4r    Running             52s   minikube-m02
web-deploy-5fcbd96c7-x9vbm    ContainerCreating   6s    minikube-m03   ← 새로 생긴 것
```

지운 지 몇 초 만에 이름이 다른 새 파드가 채워진다 — ReplicaSet이 "3개 유지"를 계속 감시한다는 증거.

`kubectl edit deployment web-deploy`로 replicas 3→5로 고치면 파드가 5개로 늘어난다. `scale`로도 같은 결과:

```bash
kubectl scale deployment web-deploy --replicas=5
```
```
NAME                          STATUS    NODE
web-deploy-5fcbd96c7-dpvr7    Running   minikube
web-deploy-5fcbd96c7-lks85    Running   minikube
web-deploy-5fcbd96c7-nbc4r    Running   minikube-m02
web-deploy-5fcbd96c7-x9vbm    Running   minikube-m03
web-deploy-5fcbd96c7-xmdfn    Running   minikube-m03
```

`edit`이든 `scale`이든 결국 같은 `spec.replicas` 필드를 바꾸는 것.

### 파드 전체 삭제 — 그런데 Deployment 파드는 되살아난다

```bash
kubectl delete pod --all
kubectl get pods -o wide
```
```
NAME                          STATUS    AGE   NODE
web-deploy-5fcbd96c7-7p7dv    Running   7s    minikube-m02   ← 방금 다시 생성됨
web-deploy-5fcbd96c7-fk4wt    Running   7s    minikube-m03
web-deploy-5fcbd96c7-frtbv    Running   7s    minikube-m03
web-deploy-5fcbd96c7-sbnhs    Running   7s    minikube-m02
web-deploy-5fcbd96c7-vm7vx    Running   7s    minikube
```

독립 파드들은 지운 대로 사라졌는데, Deployment 소속 5개는 삭제하자마자 새 이름으로 전부 재생성됐다. `delete pod`는 파드만 지울 뿐 "5개를 유지하라"는 선언(Deployment)이 살아있기 때문:

```bash
kubectl delete deployment web-deploy    # 컨트롤러째 지워야 진짜로 없어짐
```

핵심 결론: **"파드를 지운다"와 "그 파드를 관리하는 컨트롤러를 지운다"는 다른 일이다.**

---

## 7/7 — Pod 심화: livenessProbe · init · static · 리소스 · 환경변수 (5-2 ~ 5-7강)

yaml 4개를 한 번에 던지고 관찰:

```bash
kubectl apply -f liveness-pod.yaml -f init-pod.yaml -f resource-pod.yaml -f env-pod.yaml
kubectl get pods
```
```
NAME           READY   STATUS              RESTARTS   AGE
env-pod        0/1     ContainerCreating   0          4s
init-pod       0/1     Init:0/1            0          4s      ← init 단계
liveness-pod   0/1     ContainerCreating   0          4s
resource-pod   1/1     Running             0          4s
```

### init container — main보다 먼저, 성공해야 다음

init-pod만 STATUS가 `Init:0/1` — init 컨테이너(sleep 10)가 도는 동안 main(nginx)은 시작 대기. 10초 뒤 Running으로 넘어갔고, init 로그도 남는다:

```bash
kubectl logs init-pod -c wait-something
```
```
init 작업 시작
init 완료
```

### livenessProbe — 일부러 실패시켜 self-healing 보기

[liveness-pod.yaml](liveness-pod.yaml)은 nginx에 없는 경로 `/healthz`를 검사시킨 것. 404 → 연속 3회 실패 → kubelet이 컨테이너 재시작. RESTARTS가 실제로 올라간다:

```bash
kubectl get pod liveness-pod
```
```
NAME           READY   STATUS    RESTARTS      AGE
liveness-pod   1/1     Running   2 (17s ago)   58s
```

describe Events에 이유가 그대로 찍힌다:

```
Normal  Killing  17s (x2 over 37s)  kubelet  Container nginx failed liveness probe, will be restarted
```

파드가 재생성되는 게 아니라 **같은 파드 안에서 컨테이너만** 다시 뜬다(RESTARTS 카운트 증가, 파드 이름·IP 유지). 실무라면 여기서 probe 경로를 앱의 진짜 헬스 엔드포인트로 고치면 끝 — PF2 Go 서버의 `/health`가 정확히 이 자리에 꽂힐 물건.

### 리소스 requests/limits — scheduler의 장부에 기록된다

[resource-pod.yaml](resource-pod.yaml)로 requests(cpu 200m/mem 128Mi)를 준 파드를 만들고, 배치된 노드의 장부를 확인:

```bash
kubectl describe node minikube-m03 | grep -A8 "Allocated resources"
```
```
  Resource           Requests    Limits
  --------           --------    ------
  cpu                300m (2%)   600m (5%)
  memory             178Mi (2%)  306Mi (3%)
```

내가 예약한 200m가 노드 합계에 반영돼 있다(나머지는 kindnet 등 시스템 몫). **실제 사용량이 아니라 예약량** — scheduler는 이 장부를 보고 다음 파드를 어디 둘지 정한다.

### static pod — control plane의 실체

마스터 노드에 들어가 kubelet의 manifests 디렉토리를 직접 확인:

```bash
minikube ssh -- ls /etc/kubernetes/manifests/
```
```
etcd.yaml            kube-controller-manager.yaml
kube-apiserver.yaml  kube-scheduler.yaml
```

이 yaml 4개가 곧 control plane이다. kubelet이 이 디렉토리를 감시하다 직접 띄우는 static pod라서, kube-system 조회에서 이름 뒤에 노드명이 붙는다:

```
etcd-minikube                      1/1   Running
kube-apiserver-minikube            1/1   Running
kube-controller-manager-minikube   1/1   Running
kube-scheduler-minikube            1/1   Running
```

### 환경변수 주입

[env-pod.yaml](env-pod.yaml)로 넣고 컨테이너 안에서 확인:

```bash
kubectl exec env-pod -- env | grep -E "DB_HOST|APP_MODE"
```
```
DB_HOST=pf-db.example.com
APP_MODE=dev
```

PF3에서 `-e SLACK_WEBHOOK_URL`로 주입하던 것의 K8s 문법. 값을 yaml에 직접 박는 건 임시고, 정식으로는 ConfigMap/Secret(10·11장)에서 가져온다.

실습 후 `kubectl delete -f`로 4개 전부 정리, default 네임스페이스 비움 확인.

---

## 7/8 — ReplicationController (6-1강)

### RC 생성과 조회

[rc-nginx.yaml](rc-nginx.yaml)로 생성 — replicas 3, selector `app: webui`, 템플릿은 nginx:1.14. RC는 selector가 ReplicaSet처럼 matchLabels 블록이 아니라 등호 매칭 한 줄이라는 것도 yaml에서 확인.

```bash
kubectl create -f rc-nginx.yaml
kubectl get replicationcontrollers   # 풀네임
kubectl get rc                       # 축약형, 같은 결과
```

![get rc](images/rc-01-get.png)

DESIRED 3 / CURRENT 3 / READY 3. describe로 속을 보면 selector·라벨·Pod Template이 그대로 보이고, Events에 replication-controller가 파드 3개를 SuccessfulCreate한 기록이 남는다:

![describe rc](images/rc-02-describe.png)

파드 이름이 `rc-nginx-wqms5`처럼 랜덤 suffix로 만들어지는 것 확인 — 템플릿의 `name: nginx-pod`는 무시되고 RC 이름 + 랜덤 문자열이 붙는다.

### 라벨 실험, edit vs scale, 삭제 후 보충

![라벨 실험과 scale](images/rc-03-edit-scale.png)

순서대로 한 것:

```bash
kubectl get pods --show-labels        # 3개 전부 app=webui
kubectl create -f redis.yaml          # 일부러 app=webui 라벨을 단 redis 파드 투입
kubectl edit pod rc-nginx             # → NotFound 에러
kubectl edit rc rc-nginx              # 실행 중인 RC 스펙을 vi로 직접 수정
kubectl scale rc rc-nginx --replicas=2
kubectl get rc                        # DESIRED 2 / CURRENT 2 / READY 2
kubectl delete pod rc-nginx-cf496     # 파드 하나 삭제 → RC가 즉시 새로 보충
```

여기서 얻은 것 세 가지.

**RC는 라벨만 본다.** redis 파드에 같은 `app=webui`를 달아 투입하면 RC 입장에선 관리 대상이 4개가 된 것 — 초과분을 바로 죽인다. redis라는 이름도, 이미지가 다르다는 것도 안 본다. 이후 `get pods --show-labels`에 redis가 없는 이유.

**`edit pod rc-nginx`는 NotFound.** rc-nginx는 RC 이름이지 파드 이름이 아니다. 파드는 랜덤 suffix가 붙은 이름으로 존재하니까, 고치려면 컨트롤러(`edit rc rc-nginx`)를 고쳐야 한다.

**edit vs scale.** edit는 스펙 전체(이미지 버전 등)를 열어서 고치는 범용 수단, scale은 replicas 숫자 하나만 바꾸는 단축 명령. 결과는 같은 원리 — RC가 desired와 current의 차이를 보고 맞춘다. 마지막에 파드를 지워도 RC가 desired 2를 유지하려고 즉시 보충하는 것까지 확인(어제 Deployment self-healing과 같은 동작, 이번엔 1세대 컨트롤러로).

### ReplicaSet — 같은 내용을 2세대 문법으로

[rs-nginx.yaml](rs-nginx.yaml)은 rc-nginx.yaml과 완전히 같은 스펙(replicas 3, app=webui, nginx:1.14)이고 다른 건 문법뿐 — apiVersion이 `apps/v1`, selector가 `matchLabels` 블록. 생성·조회·scale·삭제 전부 RC와 똑같이 동작한다 (`kubectl get rs`).

### RC와 RS를 같은 라벨로 동시에 — 서로 안 싸운다?

RS 파드 3개가 떠 있는 상태에서 같은 `app=webui` selector의 RC를 만들어봤다:

![RC·RS 같은 라벨 동거 실험](images/rs-01-rc-rs-same-label.png)

예상은 "라벨만 보니까 둘이 싸우겠지"였는데, 결과는 **6개 공존** — RS 것 3개(21s) + RC 것 3개(6s)가 전부 Running. redis는 초과분이라고 바로 죽였으면서 왜 서로의 파드는 안 건드리나.

답은 **ownerReferences**. 컨트롤러가 만든 파드에는 metadata에 소유자 표시가 박힌다(`kubectl get pod <이름> -o yaml`에서 `ownerReferences` 확인 가능). 컨트롤러는 selector에 맞는 파드 중 **자기 소유거나 주인이 없는(고아) 파드만** 관리 대상으로 센다. 그래서:

- redis 파드 = 라벨은 맞고 주인은 없음 → RC가 입양 → desired 초과 → 정리됨
- RS 소속 파드 = 라벨은 맞지만 주인이 RS → RC는 자기 것만 3개 새로 만들고 남의 것은 무시

"컨트롤러는 라벨만 본다"의 정확한 버전: **라벨이 맞으면서 주인이 없는 파드만 입양한다.**

마무리는 컨트롤러째 삭제 — 소속 파드도 같이 사라진다:

```bash
kubectl delete rc rc-nginx
kubectl delete rs rs-nginx
```

### Deployment — 3층 구조 눈으로 확인 (6-2강)

[deploy-nginx.yaml](deploy-nginx.yaml)은 rs-nginx.yaml에서 kind만 Deployment로 바꾼 것. 생성하고 세 층을 한 번에 조회:

```bash
kubectl create -f deploy-nginx.yaml
kubectl get deploy,rs,rc      # rc는 없음 — 빈 결과
kubectl get deploy,rs,pod
```

![Deployment 3층 구조](images/deploy-01-3layer.png)

**Deployment는 파드를 직접 만들지 않는다.** deploy-nginx가 ReplicaSet `deploy-nginx-745577c69`를 만들고, RS가 파드 3개를 만든다. 파드 이름을 뜯어보면 구조가 그대로 보인다: `deploy-nginx`(Deployment) + `745577c69`(RS 해시) + `4gtx4`(랜덤). 이 RS 해시가 나중에 롤링업데이트에서 버전 구분자 역할을 한다.

곁다리 오타 교훈: `kubectl get delete rs ...`라고 치면 `the server doesn't have a resource type "delete"` — kubectl은 동사(get) 다음 인자를 리소스 타입으로 해석한다.

정리는 두 단계로 해봤다. `delete rs`로 RS만 지워도 Deployment가 살아 있는 한 새 RS를 만들어 되살린다(파드 지우면 RS가 보충하던 것과 같은 원리, 한 층 위). 그래서 진짜 삭제는 `delete deploy`.

### 롤링업데이트 — set image, rollout history/status/pause (6-2강 계속)

[deployment-exam1.yaml](deployment-exam1.yaml)로 app-deploy 생성(nginx:1.14, 컨테이너 이름 web). 처음 만들 땐 서버가 이런 에러를 뱉었다:

```
strict decoding error: unknown field "spec.template.spec.containers[0].ports[0].contaierPort"
```

containerPort에서 n이 빠진 오타. `unknown field "경로"`는 따옴표 안이 곧 범인 위치라 에러 메시지만 제대로 읽으면 바로 잡힌다.

**--record와 CHANGE-CAUSE.** 그냥 만들면 rollout history의 CHANGE-CAUSE가 `<none>`이다. 지우고 `--record`를 붙여 다시 만들면 어떤 명령으로 이 리비전이 생겼는지가 남는다:

```bash
kubectl create -f deployment-exam1.yaml --record
kubectl set image deployment app-deploy web=nginx:1.15 --record
kubectl rollout history deployment app-deploy
```
```
REVISION  CHANGE-CAUSE
1         kubectl create --filename=deployment-exam1.yaml --record=true
2         kubectl set image deployment app-deploy web=nginx:1.15 --record=true
```

![--record와 rollout history](images/rollout-01-record-history.png)

`--record`는 deprecated 경고가 뜨지만 아직 동작한다(부록A 참고 — 요즘은 change-cause annotation을 직접 다는 쪽).

**롤링업데이트가 실제로 굴러가는 모습.** 1.15→1.16으로 한 번 더 올리면서 `rollout status`로 지켜봤다:

![rollout status 실시간](images/rollout-02-status-live.png)

```
1 out of 3 new replicas have been updated...
2 out of 3 new replicas have been updated...
1 old replicas are pending termination...
deployment "app-deploy" successfully rolled out
```

새 버전 파드를 하나 만들고 → 준비되면 옛 파드 하나 죽이고 → 반복. 전체가 한 번에 내려가는 구간이 없어서 서비스가 안 끊긴다. 이게 Deployment가 RS를 하나 더 만들어서 하는 일 — 새 RS(1.16)를 0→3으로 키우고 옛 RS(1.15)를 3→0으로 줄이는 과정이다.

**pause/resume**도 해봤다(스크린샷은 안 남김): `kubectl rollout pause deployment app-deploy` 상태에서는 set image를 해도 롤아웃이 시작되지 않고, `rollout resume` 하는 순간 쌓인 변경이 반영된다. 여러 변경을 모아서 한 번의 롤아웃으로 내보낼 때 쓰는 것.

### 롤링업데이트 전략 필드 — maxSurge · maxUnavailable (6-3강, 강의 정리)

이건 직접 돌린 건 아니고 강의 내용 정리. 위에서 set image로 굴렸던 롤링업데이트가 "어떤 규칙으로" 교체되는지를 yaml에 명시하는 부분이다. [deployment-exam2.yaml](deployment-exam2.yaml)로 만들어둠:

```yaml
spec:
  progressDeadlineSeconds: 600
  revisionHistoryLimit: 10
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 25%
```

핵심은 strategy 두 필드. replicas 3 기준으로 계산하면:

- **maxSurge 25%**: 교체 중 desired를 초과해서 만들 수 있는 최대치. 3×0.25=0.75 → **올림 1** → 파드가 순간 최대 4개까지 뜰 수 있다
- **maxUnavailable 25%**: 교체 중 동시에 죽어 있어도 되는 최대치. 3×0.25=0.75 → **내림 0** → 가용 파드가 3개 밑으로 절대 안 내려간다

그러니까 25%/25% 기본값에서 replicas 3이면 "새 것 1개 추가(4개) → 준비되면 옛 것 1개 제거(3개) → 반복"이 된다. 위 rollout status 화면에서 정확히 하나씩 교체됐던 이유가 이 계산. maxSurge를 키우면 교체가 빨라지는 대신 순간 자원을 더 먹고, maxUnavailable을 키우면 자원은 아끼지만 가용량이 출렁인다.

나머지 필드:

- **revisionHistoryLimit 10**: 옛 ReplicaSet을 10개까지 보관 — rollout undo로 돌아갈 수 있는 범위
- **progressDeadlineSeconds 600**: 600초 안에 롤아웃이 진전 없으면 실패로 판정
- **annotations의 kubernetes.io/change-cause**: deprecated된 --record의 정식 대체. yaml에 박아두면 apply할 때마다 rollout history의 CHANGE-CAUSE에 이 문구가 남는다 (버전 올릴 때 image와 change-cause를 같이 고쳐서 apply)

강의 흐름은 apply → vi로 image 1.15 + change-cause 수정 → 재apply(선언형 업데이트) → `rollout history` → `rollout undo`(롤백). undo는 아직 안 해봤으니 이 yaml로 직접 돌려볼 것.

### 롤백 — undo · --to-revision, 그리고 annotate 방식 change-cause (6-3강)

deployment-exam1.yaml로 리비전 3개(1.14→1.15→1.16, 전부 --record)를 다시 쌓아놓고 롤백을 굴려봤다.

**undo는 "직전"으로.** 1.16에서 `rollout undo` 하면 1.15로 돌아간다:

```bash
kubectl rollout undo deployment app-deploy
kubectl rollout history deployment app-deploy
```
```
REVISION  CHANGE-CAUSE
1         kubectl create --filename=deployment-exam1.yaml --record=true
3         kubectl set image deployment app-deploy web=nginx:1.16 --record=true
4         kubectl set image deployment app-deploy web=nginx:1.15 --record=true
```

리비전 2가 사라지고 4로 재등장 — **돌아간 리비전은 번호를 재사용하지 않고 맨 뒤 번호를 새로 받는다.**

**특정 리비전으로 가려면 --to-revision.** 처음(1.14)으로:

```bash
kubectl rollout undo deployment app-deploy --to-revision=1
```
```
REVISION  CHANGE-CAUSE
3         kubectl set image deployment app-deploy web=nginx:1.16 --record=true
4         kubectl set image deployment app-deploy web=nginx:1.15 --record=true
5         kubectl create --filename=deployment-exam1.yaml --record=true
```

이미지 확인하면 nginx:1.14. 리비전 1이 5번으로 옮겨간 것도 같은 규칙.

**annotate 방식 change-cause — 그리고 함정 하나.** --record 없이 1.17로 올리고 history를 봤더니:

```
REVISION  CHANGE-CAUSE
5         kubectl create --filename=deployment-exam1.yaml --record=true
6         kubectl create --filename=deployment-exam1.yaml --record=true
```

리비전 6은 set image로 만든 건데 CHANGE-CAUSE가 create라고 거짓말을 한다. change-cause는 Deployment 오브젝트에 붙은 annotation이 새 리비전에 **그대로 복사**되는 구조라서, 갱신 없이 새 롤아웃을 하면 옛 문구를 물려받기 때문. 그래서 annotate로 제대로 박아준다:

```bash
kubectl annotate deployment app-deploy kubernetes.io/change-cause="nginx 1.17로 업데이트 - annotate 방식"
```
```
REVISION  CHANGE-CAUSE
6         nginx 1.17로 업데이트 - annotate 방식
```

정리하면 — --record는 deprecated고, annotate 방식은 "롤아웃 후 change-cause를 갱신"까지가 한 세트다. 안 그러면 history가 거짓말한다.

실습 후 app-deploy 삭제, minikube stop으로 마감.

## 7/16 — DaemonSet 실물 확인 · Job · CronJob (6장 마무리)

### DaemonSet — 새로 만들 필요 없이 이미 돌고 있다

DaemonSet은 "노드마다 1개씩"이 전부라서, 만들어보기 전에 클러스터에 이미 있는 실물부터 확인했다:

```bash
kubectl get daemonset -n kube-system
kubectl get pods -n kube-system -o wide --no-headers | grep -e kindnet -e kube-proxy
```
```
NAME         DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR
kindnet      3         3         3       3            3           <none>
kube-proxy   3         3         3       3            3           kubernetes.io/os=linux
```

kindnet(CNI)과 kube-proxy가 둘 다 DaemonSet이고, DESIRED가 replicas 설정값이 아니라 **노드 수 3**이다. -o wide로 보면 파드가 minikube·m02·m03에 정확히 1개씩 — RC/RS/Deployment가 "총 몇 개"를 보장한다면 DaemonSet은 "어느 노드에나 있음"을 보장한다. 그래서 spec에 replicas 필드 자체가 없다. 네트워크 에이전트·로그 수집기·모니터링 에이전트가 전부 이 패턴인 이유.

![ds](images/ds-01-kindnet-kubeproxy-per-node.png)

### Job — 끝나는 게 정상인 워크로드

지금까지의 컨트롤러는 전부 "계속 떠 있게"였는데 Job은 반대로 "완료까지"를 보장한다. job-hello.yaml:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: job-hello
spec:
  backoffLimit: 2
  template:
    spec:
      containers:
      - name: hello
        image: busybox:1.36
        command: ["sh", "-c", "echo hello from job; sleep 15"]
      restartPolicy: Never
```

apply 직후 Running 0/1 → 15초 뒤:

```
NAME                  STATUS     COMPLETIONS   DURATION   AGE
job.batch/job-hello   Complete   1/1           23s        34s

NAME                  READY   STATUS      RESTARTS   AGE
pod/job-hello-5psj6   0/1     Completed   0          34s
```

관찰 포인트 셋. 파드가 끝나도 **삭제되지 않고 Completed로 남는다**(로그 조회용 — `kubectl logs job/job-hello`가 잡 이름으로 바로 된다). RESTARTS 0 — Deployment였다면 컨테이너가 끝나는 순간 되살렸을 텐데 Job은 정상 종료로 친다. 그리고 template의 restartPolicy가 **Never/OnFailure만 허용**된다 — Always면 "완료"라는 개념 자체가 성립 안 하니까. backoffLimit 2는 실패 시 재시도 한도.

![job](images/job-01-create-running.png)
![job](images/job-02-complete-logs.png)

### CronJob — Job 위에 스케줄 한 겹

yaml이 3중 중첩이다: CronJob spec 안에 jobTemplate(Job spec 그대로), 그 안에 template(Pod spec). 컨트롤러가 컨트롤러를 만드는 구조가 yaml에도 그대로 보인다.

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: cj-date
spec:
  schedule: "*/1 * * * *"
  successfulJobsHistoryLimit: 3
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: date
            image: busybox:1.36
            command: ["sh", "-c", "date"]
          restartPolicy: OnFailure
```

매분 실행으로 걸어두고 2분 기다렸더니:

```
NAME                          STATUS     COMPLETIONS   DURATION   AGE
job.batch/cj-date-29736763    Complete   1/1           7s         94s
job.batch/cj-date-29736764    Complete   1/1           3s         34s
```

로그를 찍어보면 `Thu Jul 16 12:43:04 UTC 2026` / `Thu Jul 16 12:44:00 UTC 2026` — 정확히 1분 간격. Job 이름 뒤에 붙는 숫자 29736763은 랜덤이 아니라 **스케줄 시각의 분 단위 epoch**(×60 하면 그 시각의 unix time). successfulJobsHistoryLimit 3이라 완료된 Job은 3개까지만 남고 오래된 것부터 정리된다.

![cj](images/cj-01-schedule-two-runs.png)

실습 후 `kubectl delete -f`로 둘 다 삭제. 

## 7/16 — Service 5종 · Ingress · Label · ConfigMap · Secret (7~11장 이어서)

### 준비 — Deployment와 ClusterIP, 그리고 Endpoints

nginx 2대(deploy-web.yaml, label `app: web`)를 띄우고 expose로 ClusterIP Service를 만들었다:

```bash
kubectl apply -f deploy-web.yaml
kubectl expose deployment web --port=80 --name=svc-clusterip
kubectl get endpoints svc-clusterip
```

파드 IP가 10.244.1.4 / 10.244.2.3인데 endpoints가 정확히 `10.244.1.4:80,10.244.2.3:80` — **Service가 트래픽을 보낼 실제 목적지 명단이 Endpoints다.** selector(`app=web`)에 맞는 파드가 뜨고 죽을 때마다 이 명단이 자동 갱신된다. 여기가 비어 있으면 selector/label 불일치라는 뜻이라 Service 장애 진단 1순위. `get endpoints`에 deprecated 경고가 뜨는 건 EndpointSlice로 세대교체 중이라서(v1.33+).

![svc](images/svc-01-clusterip-endpoints.png)

### 클러스터 DNS — IP가 아니라 이름으로

임시 파드에서 Service **이름**으로 접근:

```bash
kubectl run tmp --rm -it --restart=Never --image=busybox:1.36 -- sh -c "wget -qO- http://svc-clusterip | head -4"
```

`Welcome to nginx!` — IP를 어디에도 안 적었다. coredns가 `svc-clusterip` → ClusterIP로 풀어준 것. 앱 설정에 DB 주소를 IP가 아니라 서비스 이름으로 적는 이유가 이거다. `--rm -it --restart=Never`는 일회용 디버그 파드 패턴으로 외워둘 것.

![svc](images/svc-02-dns-wget.png)

### NodePort · LoadBalancer — 외부 노출 두 단계

```bash
kubectl expose deployment web --type=NodePort --port=80 --name=svc-nodeport
kubectl expose deployment web --type=LoadBalancer --port=80 --name=svc-lb
kubectl get svc
curl -s http://$(minikube ip):32500 | grep -i title
```

NodePort는 PORT(S)가 `80:32500/TCP`로 나온다 — port 80, nodePort 32500(30000~32767 자동 할당). 노드 IP:32500으로 바로 nginx 응답. **LoadBalancer는 EXTERNAL-IP가 `<pending>`에서 안 움직인다** — LB를 실제로 만들어줄 클라우드가 없기 때문. AWS였으면 여기서 ELB가 자동 생성돼 IP가 박힌다. minikube에선 `minikube tunnel`로 흉내낼 수 있다는 것만 확인하고 넘어감.

![svc](images/svc-03-nodeport-lb.png)

### headless — DNS가 파드 IP를 직접 준다

svc-headless.yaml(`clusterIP: None`)을 만들고 같은 파드 집합에 대해 DNS 조회를 비교했다:

```bash
kubectl run tmp --rm -it --restart=Never --image=busybox:1.36 -- sh -c \
  "nslookup svc-clusterip.default.svc.cluster.local; nslookup svc-headless.default.svc.cluster.local"
```

- svc-clusterip → **10.110.89.188 하나** (가상 IP, 뒤에서 kube-proxy가 분배)
- svc-headless → **10.244.2.3, 10.244.1.4 둘 다** (파드 IP 직접)

같은 파드들인데 답이 다르다. headless는 "LB 거치지 말고 개별 파드에 직접 붙겠다"용 — StatefulSet+DB처럼 0번(프라이머리)을 지목해야 하는 상황의 재료. FQDN 형식 `서비스명.네임스페이스.svc.cluster.local`도 이 실습에서 눈에 익혀둠.

![svc](images/svc-04-headless-dns.png)

### ExternalName — 바깥 도메인의 별명

```bash
kubectl apply -f svc-extname.yaml    # externalName: www.google.com
```

get svc에 EXTERNAL-IP 자리에 www.google.com이 박히고, 클러스터 안에서 `svc-extname`을 조회하면 `canonical name = www.google.com`(CNAME)이 반환된다. selector도 endpoints도 없는 유일한 타입 — 용도는 "외부 RDS 주소를 클러스터 안에서 우리 이름으로 부르기". 나중에 RDS로 갈아탈 때 앱 설정 대신 Service만 바꾸면 된다.

![svc](images/svc-05-extname.png)

### Ingress — 컨트롤러 설치와 host 라우팅

리소스만 만들면 아무 일도 안 일어난다 — 규칙을 실행할 컨트롤러부터:

```bash
minikube addons enable ingress
kubectl get pods -n ingress-nginx
```

controller가 Running, admission-create/patch는 `Completed` — **오전에 배운 Job의 실물이 여기서 바로 재등장**(설치 시 한 번만 돌고 끝나는 작업). ingress-web.yaml은 `host: web.local` → svc-clusterip:80 규칙 하나.

```bash
curl -s -H "Host: web.local" http://192.168.49.2/ | grep -i title   # → Welcome to nginx!
curl -s http://192.168.49.2/ | head -3                              # → 404 Not Found
```

**같은 IP인데 Host 헤더가 있으면 nginx, 없으면 404.** Ingress가 L7에서 host를 보고 분기한다는 걸 이 두 줄이 증명한다. /etc/hosts 안 건드리고 `-H "Host:"`로 테스트하는 트릭도 같이 확보.

![ing](images/ing-01-addon-controller.png)
![ing](images/ing-02-host-routing.png)

### Label · Annotation · nodeSelector (9장)

`--show-labels`를 쳐보니 내가 단 `app=web` 말고 **`pod-template-hash=c77955c54`가 자동으로** 붙어 있다 — 파드 이름 중간의 그 RS 해시가 label로도 달리는 것(롤링업데이트 때 신·구 RS가 파드를 안 섞는 장치). label 하나 달고 selector로 걸러보고, annotation과의 차이 확인:

```bash
kubectl label pod web-c77955c54-8wqf9 env=dev
kubectl get pods -l env=dev                          # 그 파드만 나옴
kubectl annotate pod web-c77955c54-8wqf9 owner=jsy   # describe에는 보이지만 -l로는 검색 불가
```

nodeSelector는 3노드라 실습이 제대로 된다. m02에만 `disk=ssd`를 달고 pod-nodeselector.yaml(`nodeSelector: {disk: ssd}`)을 던지면:

```bash
kubectl label node minikube-m02 disk=ssd
kubectl get nodes -L disk        # m02에만 ssd 컬럼
kubectl apply -f pod-nodeselector.yaml
kubectl get pod pod-ssd -o wide  # NODE → minikube-m02
```

스케줄러가 라벨 조건에 맞는 노드로만 보낸다. 조건 맞는 노드가 없으면 Pending 무한 대기.

![label](images/label-01-selector-annotation.png)
![label](images/label-02-nodeselector.png)

### ConfigMap — env와 volume 두 방식 (10장)

```bash
kubectl create configmap app-config --from-literal=APP_MODE=dev --from-literal=LOG_LEVEL=debug
```

pod-cm.yaml에서 같은 ConfigMap을 **두 방식으로 동시에** 주입했다: `envFrom`(key 전부가 환경변수로) + volume 마운트(/etc/config에 key가 파일명, value가 내용으로).

```bash
kubectl exec pod-cm -- sh -c "env | grep -e APP_MODE -e LOG_LEVEL"   # APP_MODE=dev, LOG_LEVEL=debug
kubectl exec pod-cm -- ls /etc/config                                # APP_MODE  LOG_LEVEL
kubectl exec pod-cm -- cat /etc/config/APP_MODE                      # dev
```

둘의 차이는 변경 반영 — volume은 수정하면 잠시 후 파일이 갱신되지만 env는 파드 재시작 전까지 그대로. 설정을 이미지 밖으로 빼는 이유(이미지 하나 + 환경별 ConfigMap)를 손으로 확인.

![cm](images/cm-01-create-describe.png)
![cm](images/cm-02-env-volume.png)

### Secret — base64는 암호화가 아니다 (11장)

```bash
kubectl create secret generic db-secret --from-literal=DB_PASSWORD=p@ssw0rd123
kubectl get secret db-secret -o jsonpath="{.data.DB_PASSWORD}"              # cEBzc3cwcmQxMjM=
kubectl get secret db-secret -o jsonpath="{.data.DB_PASSWORD}" | base64 -d  # p@ssw0rd123
```

base64가 파이프 한 번에 원문으로 풀린다 — **인코딩이지 암호화가 아니다.** Secret yaml을 레포에 커밋하면 평문 노출과 같다는 것(PF3 웹훅 사고와 같은 유형). pod-secret.yaml로 env(`secretKeyRef`)와 volume 주입 둘 다 확인했고, 마운트 경로를 df로 찍어보니:

```bash
kubectl exec pod-secret -- df -h /etc/secret
# Filesystem  ...  Mounted on
# tmpfs       ...  /etc/secret
```

**tmpfs** — Secret 볼륨은 노드 디스크가 아니라 램에 얹힌다는 실물 증거까지 확인.

![sec](images/sec-01-base64.png)
![sec](images/sec-02-inject-tmpfs.png)

실습 오브젝트 전부 삭제(deployment·svc 4종·ingress·pod 3종·cm·secret, m02의 disk 라벨도 제거). ingress 애드온은 다음 PF2 노출 실습에서 바로 쓸 거라 켜둔 채로 마감.

## 7/16 — Ingress path 라우팅으로 다중 앱 배포 (메인·결제 페이지 시나리오)

강의에서 Ingress로 메인페이지·결제페이지를 나눠 배포하는 실습이 있어서 같은 시나리오로 재현했다. 오늘 오후엔 host 기반 라우팅(`web.local`)만 했으니, 이번엔 **path 기반**으로 한 Ingress 뒤에 서비스 두 개를 나눠본다.

ConfigMap 두 개로 각각 다른 index.html을 만들고(`메인 페이지` / `결제 페이지`), nginx 파드 두 벌(main-page, payment-page)에 마운트, Service도 각각 하나씩. Ingress는 하나로 묶었다:

```yaml
spec:
  rules:
  - host: shop.local
    http:
      paths:
      - path: /main
        pathType: Prefix
        backend:
          service: { name: svc-main-page, port: { number: 80 } }
      - path: /pay
        pathType: Prefix
        backend:
          service: { name: svc-payment-page, port: { number: 80 } }
```

### 함정 — path가 백엔드로 그대로 전달된다

처음 apply하고 curl 했더니 둘 다 404:

```bash
curl -s -H "Host: shop.local" http://192.168.49.2/main
curl -s -H "Host: shop.local" http://192.168.49.2/pay
# 둘 다 → 404 Not Found (nginx가 준 진짜 404)
```

원인: nginx ingress controller는 기본적으로 **요청 path를 그대로 백엔드에 전달**한다. `/main`으로 들어온 요청이 main-page 파드에 `/main`이라는 경로로 그대로 도착하는데, 그 파드 안엔 `/`(index.html)만 있으니 404가 난 것. Ingress는 "어느 Service로 보낼지"만 정하지 "경로를 어떻게 바꿀지"는 별도 설정이 필요하다는 걸 몸으로 확인.

해결은 annotation 한 줄:

```yaml
metadata:
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
```

이게 있으면 controller가 백엔드로 넘기기 전에 매칭된 경로를 `/`로 바꿔준다(rewrite). 재apply 후:

```bash
curl -s -H "Host: shop.local" http://192.168.49.2/main   # <h1>메인 페이지</h1>
curl -s -H "Host: shop.local" http://192.168.49.2/pay    # <h1>결제 페이지</h1>
```

같은 IP·같은 포트인데 path만 다르게 줘서 서로 다른 페이지가 나온다 — Ingress가 L7 라우터라는 게 오전의 host 기반 실습보다 이걸로 더 명확하게 보인다.

![ing-path](images/ing-03-path-rewrite-target.png)

### ktcloud 포트포워딩(실제 인터넷 노출) 실습은 여기서 재현하지 않음

강의는 ktcloud 인스턴스의 공인 IP로 포트포워딩까지 해서 실제 인터넷에 노출시키는데, 이 부분은 의도적으로 생략했다. 지금 환경(WSL2 + minikube)은애초에 공인 IP가 없어 포트포워딩 자체가 성립하지 않고, 설사 억지로 터널링(ngrok 등)을 붙여도 이 포트폴리오의 실제 목표 인프라는 ktcloud가 아니라 AWS다. 강의용 인프라를 흉내내는 데 시간을 쓰는 것보다, **PF1(7/20~)에서 AWS ALB+Route53+ACM으로 진짜 도메인·TLS까지 붙여서 한 번에 제대로** 하는 게 낫다는 판단. 원리(Ingress 뒤에 실제 공인 IP를 가진 로드밸런서가 오면 그대로 인터넷에 뜬다)는 이번 path 라우팅 실습으로 충분히 확인했다.

실습 오브젝트는 전부 삭제, ingress 애드온은 PF2 노출용으로 켜둔 채 유지.

## 7/17 — PF2 K8s 배포 (PF-K8s 첫 조각)

7/16 체크리스트 3번 — 지금까지 배운 Service·Ingress·프로브를 PF2(Go 서버, `/health` `/metrics`)에 실제로 적용하는 과제. 파일 위치는 `PortFolio/PF-K8s/k8s/`(PF-K8s README에 계획된 구조 그대로), 최종본은 그쪽에 있고 여기는 과정 기록.

### 이미지를 클러스터에 넣는 법 — 레지스트리 없이

PF2는 `deploy.sh`에서 커밋 해시를 태그로 쓰는 관례가 있어서 그대로 따랐다:

```bash
cd PortFolio/PF2
git rev-parse --short HEAD        # 021c651
docker build -t pf2:021c651 .
minikube image load pf2:021c651   # 3노드 전부에 로드되는지 확인
```

`minikube image load`가 핵심이다. minikube 노드들은 호스트 Docker와 별개의 컨테이너 런타임을 쓰기 때문에, 호스트에서 빌드한 이미지가 자동으로 노드에 보이지 않는다. 레지스트리(Docker Hub 등)에 push하고 pull하는 게 정석이지만, 로컬 실습에선 `minikube image load`로 호스트의 이미지를 노드 런타임에 직접 밀어넣을 수 있다. 3노드 각각 `docker images`로 확인해서 전부 들어간 것까지 봤다.

**함정 하나 미리 막기**: Deployment에 `imagePullPolicy: Never`를 반드시 넣어야 한다. 기본 정책(태그가 `latest`가 아니면 `IfNotPresent`지만 `pf2:021c651`처럼 커밋해시 태그라도 안 넣으면 상황에 따라 Docker Hub에서 `pf2` 이미지를 찾으려다 실패한다)이 로컬 전용 이미지와 안 맞아서, 안 걸어두면 4장에서 배운 `ImagePullBackOff`가 그대로 재현된다.

### deployment.yaml — 오늘 배운 프로브·리소스 전부 적용

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pf2
  labels:
    app: pf2
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pf2
  template:
    metadata:
      labels:
        app: pf2
    spec:
      containers:
      - name: pf2
        image: pf2:021c651
        imagePullPolicy: Never
        ports:
        - containerPort: 8080
        resources:
          requests: { cpu: 50m, memory: 32Mi }
          limits: { cpu: 200m, memory: 64Mi }
        readinessProbe:
          httpGet: { path: /health, port: 8080 }
          initialDelaySeconds: 2
          periodSeconds: 5
        livenessProbe:
          httpGet: { path: /health, port: 8080 }
          initialDelaySeconds: 5
          periodSeconds: 10
```

PF2가 이미 `/health` 엔드포인트를 갖고 있어서 5장에서 배운 readinessProbe·livenessProbe를 그대로 꽂을 자리였다. requests/limits는 Go 정적 바이너리 + alpine이라 아주 가볍게(50m/32Mi ~ 200m/64Mi) 잡았다.

apply 후 `kubectl rollout status`:

```
Waiting for deployment "pf2" rollout to finish: 0 of 3 updated replicas are available...
Waiting for deployment "pf2" rollout to finish: 1 of 3 updated replicas are available...
Waiting for deployment "pf2" rollout to finish: 2 of 3 updated replicas are available...
deployment "pf2" successfully rolled out
```

![pf2](images/pf2-01-apply-rollout.png)

파드 배치를 보면 scheduler가 3개를 3노드에 정확히 하나씩 흩뿌렸다(minikube, m02, m03) — 6장에서 본 self-healing·분산 배치가 내 앱에서도 그대로 동작.

![pf2](images/pf2-02-pod-svc-ingress.png)

### service.yaml · ingress.yaml — 7/16 함정을 미리 반영

```yaml
apiVersion: v1
kind: Service
metadata:
  name: pf2-svc
spec:
  selector:
    app: pf2
  ports:
  - port: 80
    targetPort: 8080
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: pf2-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: pf2.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service: { name: pf2-svc, port: { number: 80 } }
```

`rewrite-target: /`를 이번엔 처음부터 넣었다 — 7/16 메인/결제 페이지 실습에서 이거 없이 path 라우팅을 걸었다가 404를 만났던 그 함정을 아는 채로 시작한 것. path가 `/`(전체 prefix)라 사실 이번엔 없어도 됐을 수 있지만, 습관을 들이는 셈치고 넣었다.

### 검증

```bash
kubectl get ingress pf2-ingress   # ADDRESS 192.168.49.2 확인
curl -s -H "Host: pf2.local" http://192.168.49.2/health
curl -s -H "Host: pf2.local" http://192.168.49.2/metrics
```

```json
{"status":"ok","timestamp":"2026-07-16T16:16:42Z"}
{"requests_total":13,"uptime_seconds":38}
```

![pf2](images/pf2-03-health-metrics-ingress.png)

`requests_total`이 벌써 13인 게 재밌는 지점 — 실제 curl은 2번밖에 안 했는데 카운터가 13이다. readinessProbe(5초마다)·livenessProbe(10초마다)가 파드 3개에서 각각 `/health`를 계속 때리고 있고, PF2 코드(main.go)가 헬스체크 요청도 똑같이 `requestsTotal`에 합산하기 때문. **모니터링 지표를 설계할 때 "이 숫자엔 프로브 트래픽이 섞여 있는가"를 구분해야 한다**는 실전 교훈 — 8월 Observability에서 Prometheus 지표 설계할 때 다시 마주칠 문제.

외부→Ingress(L7, host 라우팅)→Service(ClusterIP, 로드밸런싱)→Pod(3개 중 하나, readiness 통과한 것만) 전체 경로가 지금까지 배운 장들의 합으로 완성됐다. 배포는 그대로 두고(PF-K8s 진행 중인 산출물이라 실습 데모처럼 삭제하지 않음), PF-K8s/README.md에 진행 상황을 기록.
