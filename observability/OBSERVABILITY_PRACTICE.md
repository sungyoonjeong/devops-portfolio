# Observability 실습 — Prometheus + Grafana + AlertManager 설치, PF2 연동, 대시보드 1개, 알람 1개

목표: PF2에 실제 Prometheus 지표를 붙이고, 그 지표를 Grafana 대시보드로 보고, 장애 상황에서 알람이 실제로 울리는 것까지 전 과정을 검증한다. 개념은 [OBSERVABILITY_STUDY.md](OBSERVABILITY_STUDY.md) 참조.

---

## 1. kube-prometheus-stack 설치 (Helm)

Prometheus·Grafana·AlertManager·각종 exporter를 각각 따로 설치하는 대신, 이 네 가지를 한 번에 구성해주는 커뮤니티 Helm 차트 `kube-prometheus-stack`을 썼다. Helm은 여기서 "차트를 직접 작성"하는 게 아니라 **이미 만들어진 차트를 설치(consume)하는 용도**로만 쓴다 — Helm 차트를 직접 작성하는 연습은 PF1에서 별도로 진행할 예정.

```bash
$ curl -fsSL -o /tmp/get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
$ HELM_INSTALL_DIR=~/.local/bin USE_SUDO=false /tmp/get_helm.sh
helm installed into /home/jsy/.local/bin/helm

$ helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
$ helm repo update
```

리소스가 제한적인 minikube 환경에 맞게 최소 설정(retention 6시간, 낮은 CPU/메모리 요청량)을 값 파일로 지정:

```yaml
# /tmp/prom-values.yaml
grafana:
  adminPassword: "admin1234"
  service:
    type: ClusterIP
alertmanager:
  alertmanagerSpec:
    resources:
      requests: { cpu: 50m, memory: 64Mi }
prometheus:
  prometheusSpec:
    resources:
      requests: { cpu: 100m, memory: 256Mi }
    retention: 6h
```

```bash
$ kubectl create namespace monitoring
$ helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
    --namespace monitoring -f /tmp/prom-values.yaml --wait --timeout 5m

NAME: kube-prometheus-stack
STATUS: deployed

$ kubectl get pods -n monitoring
NAME                                                        READY   STATUS    RESTARTS   AGE
alertmanager-kube-prometheus-stack-alertmanager-0           2/2     Running   0          96s
kube-prometheus-stack-grafana-5d48c79f97-pqmvh              3/3     Running   0          108s
kube-prometheus-stack-kube-state-metrics-7f5c47f68c-zgllb   1/1     Running   0          108s
kube-prometheus-stack-operator-55c66c7495-hlshw             1/1     Running   0          108s
kube-prometheus-stack-prometheus-node-exporter-467v9        1/1     Running   0          108s
kube-prometheus-stack-prometheus-node-exporter-jsfwc        1/1     Running   0          108s
kube-prometheus-stack-prometheus-node-exporter-lst74        1/1     Running   0          108s
prometheus-kube-prometheus-stack-prometheus-0               2/2     Running   0          96s
```

노드마다 하나씩 뜨는 `node-exporter`(3개, 3노드라서), 클러스터 리소스 현황을 지표로 변환하는 `kube-state-metrics`, 실제 두뇌인 `prometheus-operator`, 그리고 `prometheus`·`alertmanager`·`grafana` 본체까지 총 8개 파드가 정상 기동됐다.

---

## 2. PF2 코드 수정 — JSON 지표를 Prometheus 포맷으로 전환

기존 PF2의 `/metrics`는 직접 만든 JSON을 반환하고 있었다(`main.go`의 원래 주석에도 "Prometheus 연동 전 단계로, 커스텀 JSON 지표를 노출하는 가장 간단한 패턴"이라고 미리 적어뒀던 부분). 이번에 실제로 그 다음 단계로 넘어갔다.

**Before** (커스텀 JSON):
```go
func metricsHandler(w http.ResponseWriter, r *http.Request) {
	atomic.AddInt64(&requestsTotal, 1)
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]interface{}{
		"requests_total": atomic.LoadInt64(&requestsTotal),
		"uptime_seconds": int(time.Since(startTime).Seconds()),
	})
}
```

**After** (Prometheus 공식 클라이언트 라이브러리 사용):
```go
// requestsTotal: Prometheus Counter — 누적 요청 수
// promauto.NewCounter를 쓰면 카운터 생성과 동시에 전역 레지스트리에 등록돼 /metrics에서 자동으로 노출된다
var requestsTotal = promauto.NewCounter(prometheus.CounterOpts{
	Name: "pf2_requests_total",
	Help: "PF2 서버가 받은 총 HTTP 요청 수 (/health 호출 기준)",
})

func healthHandler(w http.ResponseWriter, r *http.Request) {
	requestsTotal.Inc()   // atomic.AddInt64 대신 Counter.Inc() - 내부적으로 동일하게 원자적 연산
	...
}

func main() {
	http.HandleFunc("/health", healthHandler)
	// /metrics 경로 - 직접 만든 JSON 대신 promhttp.Handler()를 붙인다.
	// Go 런타임 지표(고루틴 수·GC·메모리)까지 자동으로 함께 노출된다.
	http.Handle("/metrics", promhttp.Handler())
	...
}
```

의존성 추가(로컬에 Go 툴체인이 없어 컨테이너 안에서 `go get`):

```bash
$ docker run --rm -v "$PWD":/app -w /app golang:1.22-alpine sh -c "
    apk add --no-cache git
    go get github.com/prometheus/client_golang@v1.20.5
    go mod tidy"
```

최신 버전(`v1.23.x`)은 Go 1.23 이상을 요구해서 프로젝트가 고정하고 있는 Go 1.22와 충돌 — `v1.20.5`(Go 1.22와 호환되는 최신 버전)로 명시해서 해결했다.

테스트 코드도 JSON 파싱 대신 Prometheus 텍스트 포맷을 검증하도록 갱신(`main_test.go`) — `# HELP`·`# TYPE` 라인과 실제 지표 라인이 포함돼 있는지 확인:

```bash
$ docker run --rm -v "$PWD":/app -w /app golang:1.22-alpine sh -c "gofmt -w . && gofmt -l . ; go vet ./... && go test -v ./..."
=== RUN   TestHealthHandler
--- PASS: TestHealthHandler (0.00s)
=== RUN   TestMetricsHandler
--- PASS: TestMetricsHandler (0.00s)
PASS
ok  	pf2	0.009s
```

이 변경을 GitHub Flow에 따라 브랜치→커밋→머지로 반영하고, 이미지를 새로 빌드해서 `PortFolio/PF-K8s/k8s/deployment.yaml`의 태그를 갱신 → git push → ArgoCD가 자동으로 새 이미지로 롤링 업데이트(이 부분은 `argocd/ARGOCD_PRACTICE.md`에서 이미 검증한 GitOps 흐름을 그대로 재사용):

```bash
$ kubectl get pods -l app=pf2 -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[0].image}{"\n"}{end}'
pf2-7cfcd7bbff-mrrhx	pf2:6fb38d0
pf2-7cfcd7bbff-sgszw	pf2:6fb38d0
pf2-7cfcd7bbff-vzgdk	pf2:6fb38d0

$ kubectl exec deploy/pf2 -- wget -qO- http://localhost:8080/metrics | grep -A2 pf2_requests_total
# HELP pf2_requests_total PF2 서버가 받은 총 HTTP 요청 수 (/health 호출 기준)
# TYPE pf2_requests_total counter
pf2_requests_total 7
```

실제로 Prometheus 텍스트 포맷이 나오는 것 확인.

---

## 3. ServiceMonitor 등록 — 겪은 버그와 해결

`observability/manifests/pf2-servicemonitor.yaml`:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: pf2
  labels:
    release: kube-prometheus-stack   # 이 라벨이 없으면 Prometheus가 무시한다
spec:
  selector:
    matchLabels:
      app: pf2
  endpoints:
    - port: http
      path: /metrics
      interval: 15s
```

`kubectl apply`까지는 성공했지만, Prometheus의 타겟 목록에 PF2가 전혀 안 잡혔다:

```bash
$ curl -s 'http://localhost:9090/api/v1/targets' | python3 -c "..."
all jobs: {'node-exporter', 'kube-state-metrics', 'kubelet', ...}   # pf2 없음
```

**원인 조사**: ServiceMonitor 자체는 정상 등록됐고, Prometheus의 `serviceMonitorNamespaceSelector`도 `{}`(전체 네임스페이스 허용)라 문제가 없었다. 직접 `pf2-svc`의 라벨을 확인해보니:

```bash
$ kubectl get svc pf2-svc --show-labels
NAME      TYPE        CLUSTER-IP     PORT(S)   AGE   LABELS
pf2-svc   ClusterIP   10.96.201.249  80/TCP    ...   <none>
```

**`LABELS`가 비어 있었다.** `service.yaml`에는 `spec.selector: {app: pf2}`(트래픽을 보낼 파드를 고르는 라벨)만 있었지, Service 자기 자신의 `metadata.labels`는 아예 없었던 것 — ServiceMonitor의 `selector.matchLabels`는 후자를 보는데 말이다. 이름이 비슷한 두 필드를 헷갈린 전형적인 실수(`OBSERVABILITY_STUDY.md` 5장에 개념적으로 정리해둠).

**수정** — `service.yaml`에 `metadata.labels` 추가:

```yaml
metadata:
  name: pf2-svc
  labels:
    app: pf2    # Service "자기 자신"에 붙는 라벨 - ServiceMonitor가 보는 건 이것
spec:
  selector:
    app: pf2    # 파드를 고르는 라벨 - 위와는 다른 용도
```

GitHub Flow로 커밋·머지·push → ArgoCD 자동 반영 확인 후 재검증:

```bash
$ kubectl get svc pf2-svc --show-labels
NAME      LABELS
pf2-svc   app=pf2

$ curl -s 'http://localhost:9090/api/v1/targets' | python3 -c "..."
pf2-svc http://10.244.0.9:8080/metrics up
pf2-svc http://10.244.1.10:8080/metrics up
pf2-svc http://10.244.2.12:8080/metrics up
```

3개 파드 전부 `up`(스크레이핑 성공) — 해결. 실제 값도 확인:

```bash
$ curl -s 'http://localhost:9090/api/v1/query?query=pf2_requests_total' | python3 -m json.tool
# 파드 3개 각각 pf2_requests_total = 82~83 (readiness/liveness probe 트래픽이 누적된 값)
```

---

## 4. Grafana 대시보드 1개 — ConfigMap으로 코드화

웹 UI로 클릭해서 만드는 대신, 대시보드 JSON을 `grafana_dashboard: "1"` 라벨 붙인 ConfigMap으로 apply해서 sidecar가 자동으로 Grafana에 등록하게 했다 — 전체 정의는 [`manifests/pf2-grafana-dashboard-configmap.yaml`](manifests/pf2-grafana-dashboard-configmap.yaml).

패널 4개:
1. **요청 처리율(req/s, 5분 평균)** — `sum(rate(pf2_requests_total[5m]))`
2. **살아있는 PF2 인스턴스 수** — `sum(up{job="pf2-svc"})`
3. **누적 요청 수(전체 파드 합산)** — `sum(pf2_requests_total)`
4. **파드별 요청 수** — `pf2_requests_total` (라벨별로 자동 분리돼서 파드 3개 라인이 각각 그려짐)

```bash
$ kubectl apply -f observability/manifests/pf2-grafana-dashboard-configmap.yaml
configmap/pf2-dashboard created

$ curl -s -u admin:admin1234 'http://localhost:3000/api/search?query=PF2'
[{"uid": "pf2-overview", "title": "PF2 Overview", "url": "/d/pf2-overview/pf2-overview", ...}]

$ curl -s -u admin:admin1234 'http://localhost:3000/api/dashboards/uid/pf2-overview' | python3 -c "..."
panel count: 4
- 요청 처리율 (req/s, 5분 평균)
- 살아있는 PF2 인스턴스 수
- 누적 요청 수 (전체 파드 합산)
- 파드별 요청 수
```

sidecar가 ConfigMap을 감지해서 대시보드로 자동 변환한 것을 API로 확인. `admin` 비밀번호는 values 파일에 지정한 값을 그대로 씀(실습용 — 실제 운영이라면 Secret으로 분리하고 재발급이 필요).

---

## 5. 알람 규칙 1개 — 실제로 발동시켜서 끝까지 검증

`observability/manifests/pf2-alertrule.yaml`에 처음엔 알람 하나만 만들었다:

```yaml
- alert: PF2Down
  expr: up{job="pf2-svc"} == 0
  for: 30s
```

이 상태로 PF2를 강제로 죽여서 알람이 뜨는지 확인해봤다:

```bash
$ kubectl scale deployment pf2 --replicas=0
```

그런데 30초, 1분이 지나도 `PF2Down`이 `inactive`인 채로 안 바뀌었다. 원인을 찾아보니 —

```bash
$ curl -s 'http://localhost:9090/api/v1/targets' | python3 -c "..."
active pf2 targets: []
```

**파드가 0개가 되면 Prometheus의 서비스 디스커버리가 스크레이핑할 대상 자체를 못 찾는다.** 그러면 `up{job="pf2-svc"}`라는 시계열 자체가 아예 존재하지 않는 상태가 되고, `== 0`은 "존재하는 시계열 중 값이 0인 것"만 찾기 때문에 아무것도 매칭이 안 돼 알람이 조용히 안 울린 것이다(`OBSERVABILITY_STUDY.md` 5장에 개념 정리).

**"인스턴스 일부 다운"과 "전체 다운"은 서로 다른 알람이 필요하다**는 걸 실제로 겪고, 알람을 하나 더 추가했다:

```yaml
- alert: PF2Absent
  expr: absent(up{job="pf2-svc"})   # "이 시계열이 하나도 없다"를 직접 감지
  for: 30s
  labels:
    severity: critical
  annotations:
    summary: "PF2가 Prometheus에서 완전히 사라짐"
```

### 실제 발동 검증

ArgoCD의 `selfHeal`이 켜져 있으면 `replicas: 0`으로 스케일해도 Git의 `replicas: 3`으로 곧바로 되돌려버려서, 장애 상태를 유지하며 관찰할 시간이 없다. 그래서 알람 테스트 동안만 자동 동기화를 잠깐 꺼뒀다:

```bash
# 1) ArgoCD 자동 동기화 일시 중지 (테스트 중 selfHeal이 즉시 복구하지 않도록)
$ kubectl patch application pf2 -n argocd --type merge -p '{"spec":{"syncPolicy":{"automated":null}}}'

# 2) 의도적 장애 발생
$ kubectl scale deployment pf2 --replicas=0

# 3) 알람 상태 변화 관찰
$ curl -s 'http://localhost:9090/api/v1/rules' | python3 -c "..."
PF2Absent firing    # inactive → (30초 후) → firing
```

Prometheus에서 `firing`으로 바뀐 걸 확인한 뒤, AlertManager까지 실제로 전달됐는지 최종 확인:

```bash
$ curl -s 'http://localhost:9093/api/v2/alerts' | python3 -c "..."
PF2Absent active PF2가 Prometheus에서 완전히 사라짐
```

**Prometheus 룰 평가(firing) → AlertManager 활성 알람 목록(active)까지 실제 경로가 전부 확인됐다.**

### 복구

```bash
# ArgoCD 자동 동기화 복원 + 강제 재동기화
$ kubectl apply -f argocd/pf2-application.yaml
$ argocd app sync pf2
...
Health Status:      Healthy

$ kubectl get pods -l app=pf2
pf2-7cfcd7bbff-d5glp   1/1   Running
pf2-7cfcd7bbff-jvbvx   1/1   Running
pf2-7cfcd7bbff-w6q8c   1/1   Running   # 3개 다시 정상

$ curl -s 'http://localhost:9090/api/v1/rules' | python3 -c "..."
PF2Down    inactive
PF2Absent  inactive    # 알람도 자동으로 해제됨
```

파드가 복구되자 알람도 자동으로 `inactive`로 돌아왔다 — 사람이 알람을 수동으로 끌 필요가 없다(조건이 거짓이 되면 자동 해제되는 게 정상 동작).

---

## 6. 다음 단계

- AlertManager의 실제 알림 채널(Slack webhook 등) 연동 — PF3에서 이미 Slack 알림을 구현한 적이 있어 그 자격증명 재사용 예정
- 로그(Logs) 수집 — EFK(Elasticsearch+Fluentd+Kibana) 스택은 PF1 범위
- 분산 트레이싱(Traces) — Tempo는 PF1 범위 (마이크로서비스가 여러 개로 늘어났을 때 의미가 커짐)
- `PF2Down`(부분 장애) 알람은 아직 실제로 발동시켜 검증 못 함 — 파드 일부만 죽이고 나머지는 살려두는 시나리오로 다음에 검증
