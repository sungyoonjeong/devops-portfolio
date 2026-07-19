# Observability 실습 — Prometheus + Grafana + AlertManager

PF2에 실제 지표를 붙이고, 그 지표를 대시보드로 보고, 장애가 나면 알람이 울리는 것까지 전 과정을 minikube에서 검증했다.

이론은 `OBSERVABILITY_STUDY.md`(관측성이 뭔지부터), 실습 기록은 `OBSERVABILITY_PRACTICE.md`.

## 구성

- `OBSERVABILITY_STUDY.md` — 관측성(메트릭/로그/트레이스)이란 무엇인가, Prometheus pull 모델·PromQL, ServiceMonitor·PrometheusRule, Grafana, AlertManager 개념
- `OBSERVABILITY_PRACTICE.md` — kube-prometheus-stack 설치, PF2 `/metrics`를 Prometheus 포맷으로 전환, ServiceMonitor 버그와 해결, Grafana 대시보드 1개, 알람 1개를 실제로 발동시켜 검증
- `manifests/` — 실제로 적용한 ServiceMonitor·PrometheusRule·Grafana 대시보드 ConfigMap(전부 한 줄 주석 포함)

## 실행

```bash
kubectl port-forward -n monitoring svc/kube-prometheus-stack-prometheus 9090:9090 &
kubectl port-forward -n monitoring svc/kube-prometheus-stack-grafana 3000:80 &
kubectl port-forward -n monitoring svc/kube-prometheus-stack-alertmanager 9093:9093 &
# Grafana: http://localhost:3000 (admin / admin1234)
# Prometheus: http://localhost:9090
```

## 메모

- Prometheus Operator의 `selector`는 대상 리소스의 `metadata.labels`를 본다 — Service의 `spec.selector`(파드를 고르는 라벨)와 헷갈리지 말 것.
- `up{job="X"} == 0`은 "일부 인스턴스가 응답 없음"만 잡는다. 인스턴스가 전멸하면 시계열 자체가 사라져서 `absent(up{job="X"})`로 따로 잡아야 한다.
- 다음: AlertManager Slack 연동, 로그(EFK)·트레이싱(Tempo)은 PF1 범위.
