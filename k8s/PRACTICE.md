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
