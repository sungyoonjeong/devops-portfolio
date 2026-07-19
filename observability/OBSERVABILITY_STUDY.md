# Observability(관측성) 개념 정리 — Prometheus · Grafana · AlertManager

Observability 학습 — "지금 이 서버가 잘 돌아가고 있는지 어떻게 아는가"라는 질문에서 시작한다. CI/CD·ArgoCD와 마찬가지로 완전 처음 듣는다는 전제로 0장부터 쓴다.

---

## 0. Observability(관측성)가 뭔가

### 지금까지는 어떻게 서버 상태를 확인했나

`PortFolio/PF2/main.go`에는 원래 `/health`라는 엔드포인트가 있다 — 호출하면 "지금 서버가 살아있다"는 것만 알려준다. K8s의 livenessProbe·readinessProbe도 이 엔드포인트를 주기적으로 찔러서 "죽었으면 재시작"만 한다.

이 방식의 한계:
- **"지금 살아있다/죽었다"만 알지, "얼마나 바쁜지", "요청이 늘고 있는지 줄고 있는지", "평소보다 느려졌는지"는 전혀 모른다.**
- 문제가 생겨도 "언제부터 이상해졌는지"를 알 방법이 없다 — 누군가 우연히 `/health`를 호출해서 실패를 봐야만 안다.
- 서버가 여러 대(지금은 PF2 파드 3개)로 늘어나면, 한 대씩 SSH로 들어가서 로그를 보는 건 현실적으로 불가능해진다.

### Observability = 시스템 내부 상태를 외부에서 유추할 수 있는 능력

**Observability(관측성)**란 "시스템을 직접 뜯어보지 않고도, 그 시스템이 밖으로 내보내는 신호만 보고 내부에서 무슨 일이 일어나는지 알 수 있는 정도"를 뜻한다. 이 신호는 보통 3가지로 나뉜다(관측성의 3대 축):

| 종류 | 무엇인가 | 예시 | 이번에 다루는 것 |
|---|---|---|---|
| **메트릭(Metrics)** | 숫자로 된 시계열 데이터 — "이 시각에 이 값이 얼마였다"를 계속 쌓는다 | 요청 수, 응답시간, CPU 사용률 | ✅ **이번 실습의 핵심** |
| **로그(Logs)** | 각 이벤트를 텍스트로 그대로 남긴 기록 | "12:03:01 GET /health 200" | (다음 단계, EFK 등에서) |
| **트레이스(Traces)** | 요청 하나가 여러 서비스를 거칠 때 그 전체 경로를 추적 | 요청이 A→B→C를 거치며 각 구간 소요시간 | (PF1에서 Tempo로) |

이번 실습은 이 중 **메트릭**을 다룬다 — PF2가 지표를 내보내고(export), 그 지표를 주기적으로 수집(scrape)하고, 그래프로 보여주고(visualize), 이상하면 알려주는(alert) 파이프라인 전체를 만든다.

### 왜 Prometheus + Grafana + AlertManager 세 개를 같이 쓰는가

세 도구가 역할이 완전히 다르다 — 하나가 다른 걸 대체하지 않는다:

```
PF2(지표를 만듦) → Prometheus(수집·저장·조건 평가) → ┬→ Grafana(그래프로 시각화)
                                                    └→ AlertManager(조건 만족 시 알림 발송)
```

- **Prometheus**: 지표를 주기적으로 긁어와서(scrape) 시계열 데이터베이스에 저장하고, "이 조건이 참이면 알람"이라는 규칙을 계속 평가하는 엔진.
- **Grafana**: Prometheus(등 여러 데이터소스)에 저장된 데이터를 사람이 보기 좋은 그래프·대시보드로 그려주는 시각화 도구. Prometheus 없이도 다른 DB를 붙일 수 있고, Prometheus도 자체 웹 UI가 있지만 Grafana가 훨씬 보기 좋다.
- **AlertManager**: Prometheus가 "이 알람 조건이 참이다"라고 판단한 걸 실제로 어디에(Slack, 이메일 등) 어떻게(중복 제거, 그룹핑, 조용한 시간대 설정) 보낼지 처리하는 별도 컴포넌트. Prometheus는 "판단"만 하고, "전달"은 AlertManager가 한다 — 이렇게 나뉜 이유는 알람 라우팅 규칙(누구한테 언제 어떻게 보낼지)이 지표 수집 로직과는 완전히 다른 관심사라서다.

---

## 1. Prometheus — 어떻게 지표를 모으는가

### Pull 방식 — ArgoCD의 GitOps와 같은 발상

Prometheus는 **각 서버가 알아서 지표를 밀어 보내는(push) 게 아니라, Prometheus가 각 서버에 직접 찾아가서 당겨온다(pull).** 정해진 주기마다(예: 15초) PF2의 `/metrics` 엔드포인트를 HTTP GET으로 호출해서 그 순간의 값을 읽어간다 — 이 동작을 **스크레이핑(scraping)**이라 부른다.

(참고: `argocd/ARGOCD_STUDY.md`에서 GitOps도 "클러스터가 Git을 당겨온다(pull)"는 같은 철학이었다 — pull 방식이 "중앙 수집기가 각 대상의 존재를 스스로 확인하러 간다"는 점에서 아키텍처적으로 더 신뢰할 수 있다는 공통된 이유가 있다.)

### `/metrics` 엔드포인트 — Prometheus 텍스트 포맷

Prometheus가 이해하는 형식은 JSON이 아니라 아래처럼 생긴 **전용 텍스트 포맷**이다:

```
# HELP pf2_requests_total PF2 서버가 받은 총 HTTP 요청 수
# TYPE pf2_requests_total counter
pf2_requests_total 83
```

- `# HELP`: 이 지표가 무엇을 뜻하는지 설명(사람이 읽는 용도)
- `# TYPE`: 지표의 종류(아래 참조)
- 마지막 줄: `지표이름{라벨="값"} 숫자` — 라벨이 없으면 `{}` 생략 가능

이 포맷을 앱이 직접 손으로 만들 필요는 없다 — Go라면 `prometheus/client_golang` 같은 공식 라이브러리가 있는 언어별 지표를 이 포맷으로 자동 변환해 내보내는 HTTP 핸들러를 제공한다(실습에서 실제로 이걸 썼다).

### 지표 타입 4가지

| 타입 | 뜻 | 예시 |
|---|---|---|
| **Counter** | 계속 증가만 하는 누적값(재시작하면 0으로 리셋) | 총 요청 수, 총 에러 수 |
| **Gauge** | 오르락내리락하는 값 | 현재 메모리 사용량, 현재 동시 연결 수 |
| **Histogram** | 값의 분포를 구간(bucket)별로 집계 | 응답시간 분포(0.1s 미만 몇 건, 0.5s 미만 몇 건...) |
| **Summary** | Histogram과 비슷하지만 분위수(p50, p99 등)를 클라이언트가 직접 계산 | 응답시간 p99 |

PF2에서 쓴 `pf2_requests_total`은 계속 늘어나기만 하는 값이라 **Counter**다.

### PromQL — 저장된 지표에 질문하는 언어

Prometheus에 쌓인 시계열 데이터에 질문하는 전용 쿼리 언어가 **PromQL**이다. 실습에서 실제로 쓴 쿼리:

```promql
pf2_requests_total                    # 현재 값 그대로 (파드별로 각각)
sum(pf2_requests_total)               # 모든 파드 합산
sum(rate(pf2_requests_total[5m]))     # 최근 5분간 초당 증가율 (Counter는 누적값이라
                                       # 그 자체보다 "얼마나 빠르게 느는가"가 더 유용한 경우가 많다)
up{job="pf2-svc"}                     # 이 job의 각 인스턴스가 살아있는지(1) 죽었는지(0)
absent(up{job="pf2-svc"})             # 이 job에 해당하는 시계열이 "아예 존재하지 않는지"
```

`rate()`가 특히 중요한 함수다 — Counter는 계속 증가만 하니, "지금 몇 명 접속 중이냐"보다 "초당 몇 건씩 늘고 있냐(=트래픽량)"를 보려면 `rate()`로 증가 속도로 변환해야 의미 있는 그래프가 나온다.

---

## 2. Kubernetes 환경에서 Prometheus를 어떻게 연결하는가 — Prometheus Operator

Kubernetes 위에서 Prometheus를 매번 "이 서비스를 스크레이핑 대상에 추가"하려고 Prometheus 설정 파일을 손으로 고치고 재시작하는 건 비효율적이다. **Prometheus Operator**는 이 과정을 K8s 커스텀 리소스(CRD)로 선언하면 자동으로 Prometheus 설정에 반영해주는 컨트롤러다. 이번 실습은 `kube-prometheus-stack`이라는 Helm 차트로 Prometheus Operator + Prometheus + Grafana + AlertManager를 한 번에 설치했다(각각 따로 설치하는 것보다 훨씬 표준적인 방법).

### ServiceMonitor — "이 Service를 스크레이핑해라"

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: pf2
  labels:
    release: kube-prometheus-stack   # Prometheus가 "이 라벨 붙은 것만 본다"고 설정돼 있음
spec:
  selector:
    matchLabels:
      app: pf2       # 이 라벨이 붙은 "Service"를 찾는다
  endpoints:
    - port: http     # 그 Service의 어느 포트를 스크레이핑할지
      path: /metrics
      interval: 15s
```

**중요한 함정**: `selector.matchLabels`는 대상 **Service의 `metadata.labels`**를 보는 것이지, Service의 `spec.selector`(파드를 고르는 라벨)를 보는 게 아니다. 이 둘은 이름이 비슷해서 헷갈리기 쉽지만 완전히 다른 필드다 — 이 실수를 실제로 했고 어떻게 알아챘는지는 `OBSERVABILITY_PRACTICE.md`에 그대로 남겼다.

### PrometheusRule — "이 조건이면 알람"

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  labels:
    release: kube-prometheus-stack
spec:
  groups:
    - name: pf2.rules
      rules:
        - alert: PF2Down
          expr: up{job="pf2-svc"} == 0
          for: 30s
          labels:
            severity: critical
          annotations:
            summary: "PF2 인스턴스 응답 없음"
```

- `expr`: PromQL 조건식. 이게 참이 되는 순간부터 카운트를 시작한다.
- `for`: 이 조건이 **끊기지 않고 계속** 이 시간만큼 참이어야 진짜로 알람이 울린다(순간적인 튐으로 오탐 발생하는 걸 막는 역할). `for` 동안은 `pending`(대기) 상태, 그 시간을 채우면 `firing`(발동) 상태로 바뀐다.
- `labels.severity`: 알람의 심각도 — AlertManager가 이 라벨을 보고 라우팅 규칙(누구한테 보낼지)을 정한다.

---

## 3. Grafana — 지표를 대시보드로

### 대시보드 / 패널 / 데이터소스

- **데이터소스(Data source)**: 데이터를 가져올 곳 — 여기선 Prometheus. Grafana 자체는 데이터를 저장하지 않고, 그때그때 데이터소스에 쿼리를 던져서 받아온 걸 그린다.
- **패널(Panel)**: 그래프 하나, 숫자 하나 같은 시각화 단위. 각 패널이 PromQL 쿼리 하나(이상)를 갖는다.
- **대시보드(Dashboard)**: 여러 패널을 모아놓은 화면 하나.

### 대시보드를 "코드로" 관리하기

Grafana 웹 UI에서 클릭으로 패널을 만들 수도 있지만, 그러면 그 대시보드는 Grafana 안에만 존재하고 Git에는 안 남는다 — 사람이 실수로 지우면 그걸로 끝이다. 이번 실습에서는 대시보드 정의를 **JSON 파일로 작성해서 ConfigMap에 담아 클러스터에 apply**했다. `kube-prometheus-stack`이 Grafana와 함께 설치한 사이드카 컨테이너가 `grafana_dashboard: "1"` 라벨이 붙은 ConfigMap을 자동으로 찾아서 Grafana 안에 등록해준다 — 이러면 대시보드 정의 자체가 Git에 커밋되는 파일이 되어, ArgoCD의 Application YAML처럼 "코드가 곧 정답"이 된다.

---

## 4. AlertManager — 알람을 어떻게 처리하는가

Prometheus가 "이 조건이 firing이다"라고 판단하면, 그 정보를 AlertManager로 보낸다. AlertManager가 하는 일:

- **그룹핑(Grouping)**: 같은 원인으로 동시에 여러 알람이 뜨면(예: 노드 하나가 죽어서 그 위 파드 10개가 한꺼번에 다운) 그걸 하나로 묶어서 보낸다 — 안 그러면 알람이 스팸처럼 쏟아진다.
- **라우팅(Routing)**: `severity: critical`이면 Slack 긴급 채널로, `severity: warning`이면 이메일로처럼 알람 라벨에 따라 다른 곳으로 보낸다(이번 실습은 receiver 설정 없이 "발동되는지"까지만 확인 — 실제 Slack 연동은 PF3에서 이미 한 적 있고, 여기 붙이는 건 다음 단계).
- **중복 억제(Inhibition)**: 더 큰 장애(전체 클러스터 다운) 알람이 떴을 때, 그 하위 알람(개별 파드 다운)은 억제해서 노이즈를 줄인다.
- **뮤트(Silence)**: 점검 시간대처럼 알람이 뜨는 걸 알면서도 일부러 잠깐 꺼둘 때 쓴다.

이번 실습에서는 실제로 알람을 발동시켜서(`OBSERVABILITY_PRACTICE.md` 참조) 그 알람이 Prometheus 룰 평가 → AlertManager의 활성 알람 목록까지 실제로 도달하는 전체 경로를 확인했다.

---

## 5. 배운 것 — 실제로 겪은 개념적 함정 2가지

### `up == 0` 과 `absent()`는 다른 걸 감지한다

`up{job="X"} == 0`은 "**존재하는 시계열의 값이 0**"인 경우를 잡는다 — 즉 Prometheus가 그 대상을 스크레이핑 "시도"는 했는데 실패한 경우(인스턴스는 등록돼 있는데 응답이 없음)다. 반면 인스턴스가 **아예 하나도 없어서** service discovery가 스크레이핑 대상 자체를 못 찾으면, `up{job="X"}`라는 시계열 자체가 존재하지 않는다 — 이때 `== 0` 비교는 "존재하지 않는 것과 0을 비교"이므로 아무것도 매칭되지 않아 **알람이 조용히 안 울린다.** 이 경우를 잡으려면 `absent(up{job="X"})`(그 시계열이 하나도 없다는 사실 자체를 감지)가 필요하다 — 흔히 "부분 장애(일부 인스턴스 다운)"와 "전체 장애(전부 다운)"를 서로 다른 알람 규칙으로 나눠서 각각 대응해야 하는 이유가 여기 있다.

### Service의 두 가지 "selector"를 헷갈리지 말 것

```yaml
apiVersion: v1
kind: Service
metadata:
  labels:        # ← ①  Service "자기 자신"에 붙는 라벨. ServiceMonitor가 찾는 건 이거다.
    app: pf2
spec:
  selector:      # ← ②  이 Service가 트래픽을 보낼 "파드"를 고르는 라벨. 완전히 다른 용도.
    app: pf2
```

값이 같은 `app: pf2`라서 헷갈리기 쉽지만 ①과 ②는 목적이 완전히 다르다. ServiceMonitor·PrometheusRule 같은 Prometheus Operator 리소스의 `selector`는 전부 **①번(리소스 자신의 라벨)**을 보고 매칭한다는 걸 기억해야 한다.
