# K8s 실습 환경 구축 (7/6)

K8s 학습 시작(7/7) 전날에 환경만 미리 세팅. WSL2 Ubuntu 22.04 + Docker 위에 minikube 단일 노드 클러스터.

| 구성 | 버전 |
|------|------|
| kubectl | v1.36.2 |
| minikube | v1.38.1 (driver: docker) |
| Kubernetes | v1.35.1 |

## 왜 minikube인가

진짜 K8s 클러스터는 서버 여러 대(컨트롤플레인 + 워커)에 부품을 나눠 설치해야 한다.
minikube는 그 과정을 대신해서 **Docker 컨테이너 하나를 가상 서버 삼아 1노드 클러스터**를 만들어준다.
`docker ps` 치면 `minikube` 컨테이너 한 개가 보이는데, 그 상자 안에서 K8s 전체가 돈다.

kubectl 사용법은 클러스터가 뭐든 동일하다 — minikube로 배운 게 그대로 실무·EKS·CKA로 이어진다.
(스펙트럼: minikube/kind = 로컬 학습용 → kubeadm = 실서버 직접 설치 → EKS = AWS 관리형)

## 설치

```bash
# kubectl — 클러스터에 명령을 쏘는 CLI (리모컨)
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# minikube — 로컬 미니 클러스터 생성 도구
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# 클러스터 기동 (첫 실행은 이미지 다운로드로 몇 분 소요, CPU 2개·메모리 3GB 자동 할당)
minikube start --driver=docker
```

![설치와 클러스터 기동](images/setup-01-install-minikube-start.png)

## 검증

```bash
kubectl get nodes     # STATUS Ready 확인
kubectl get pods -A   # 시스템 파드 확인
```

![Ready + 시스템 파드](images/setup-02-nodes-ready-system-pods.png)

kube-system 네임스페이스에 뜬 것들이 K8s의 부품 실물이다:

- `etcd` — 클러스터의 모든 상태가 저장되는 장부
- `kube-apiserver` — kubectl 명령의 수신부. 모든 요청이 여기로
- `kube-scheduler` — 파드를 어느 노드에 둘지 배치 결정
- `kube-controller-manager` — "선언된 상태 = 실제 상태" 상시 유지 (Ansible 멱등성의 24시간 실행 버전)
- `kube-proxy` — 노드의 네트워크 규칙 담당
- `coredns` — 클러스터 내부 DNS (기동 직후 0/1이었다가 곧 1/1)
- `storage-provisioner` — minikube 부가기능, PV 자동 생성용

## 일상 운영

```bash
minikube stop     # 재우기 — 상태 보존, 안 쓸 때 CPU·메모리 절약
minikube start    # 깨우기 — 첫 설치보다 훨씬 빠름
kubectl get nodes # 아침 학습 시작 전 Ready 확인
```

`minikube delete`는 클러스터 통째 삭제라 실수 금지.

## 메모

- 다운로드한 설치 파일(kubectl 59MB, minikube 134MB)은 `sudo install`로 /usr/local/bin에 복사된 뒤 삭제 — 레포에 바이너리 커밋 금지
- 다음: Pod → Deployment → Service 순서로 실습 (7/7~)

---

## 3노드 재구축 (7/7)

강의(마스터1+워커2)와 같은 토폴로지로 맞추려고 단일 노드를 지우고 3노드로 재구축.

```bash
minikube delete --all
minikube start --nodes 3 --driver=docker --memory 2048 --cpus 2   # 노드당 2GB/2CPU
kubectl get nodes
# minikube       Ready   control-plane      ← 강의의 master
# minikube-m02   Ready   <none>             ← worker1 (워커엔 role 라벨이 없어 <none>)
# minikube-m03   Ready   <none>             ← worker2
```

### 겪은 문제: 기존 클러스터에 node add 하면 안 된다

처음엔 단일 노드 클러스터를 살려둔 채 `minikube node add` / 별도 프로필 `--nodes 3`을 시도했는데 둘 다 실패.

- `node add`로 붙인 노드가 NotReady 지속 — 단일 노드로 시작한 클러스터엔 멀티노드용 CNI(kindnet)가 없어서. "CNI 없으면 노드가 NotReady + coredns Pending"을 실물로 확인
- 별도 프로필은 m03에서 join 타임아웃(NotFound) — 클러스터 2개 동시 기동으로 WSL 메모리(7.7GB) 경쟁이 유력
- 결론: **멀티노드는 처음부터 `--nodes N`으로 시작**해야 CNI가 제대로 깔린다. 기존 것과 병행하지 말고 하나만

### 운영 변경점

- stop/start가 노드 3개 단위 — 기동이 더 걸리고 메모리도 더 먹으니 안 쓸 때 `minikube stop` 습관이 더 중요해짐
- 노드 안에 들어갈 일이 있으면 `minikube ssh -n minikube-m02` 처럼 `-n`으로 대상 지정
