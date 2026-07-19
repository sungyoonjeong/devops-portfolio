package main

// CI verified 2026-07-19

import (
	"encoding/json" // JSON 직렬화·역직렬화 표준 라이브러리 (헬스체크 응답용)
	"log"           // 서버 시작 로그 출력용
	"net/http"      // HTTP 서버 및 핸들러 등록 표준 라이브러리
	"time"          // 서버 가동 시작 시각 기록 로그용

	"github.com/prometheus/client_golang/prometheus"          // Counter·Gauge 등 지표 타입 정의
	"github.com/prometheus/client_golang/prometheus/promauto" // 지표 생성과 동시에 자동 등록해주는 헬퍼
	"github.com/prometheus/client_golang/prometheus/promhttp" // /metrics 엔드포인트를 Prometheus 텍스트 포맷으로 노출하는 핸들러
)

// startTime: 서버가 처음 시작된 시각 — 가동 로그 출력용
var startTime = time.Now()

// requestsTotal: Prometheus Counter — 누적 요청 수
// 이전에는 int64 + atomic으로 직접 구현했지만, promauto.NewCounter를 쓰면
// 카운터 생성과 동시에 전역 레지스트리에 등록돼 /metrics에서 자동으로 노출된다
var requestsTotal = promauto.NewCounter(prometheus.CounterOpts{
	Name: "pf2_requests_total", // 관례상 접두사(pf2_)를 붙여 다른 앱 지표와 구분
	Help: "PF2 서버가 받은 총 HTTP 요청 수 (/health 호출 기준)",
})

// healthHandler: GET /health — 서버가 살아있는지 확인하는 헬스체크 엔드포인트
// 로드밸런서나 오케스트레이터(K8s)가 주기적으로 호출해 서버 상태를 판단한다
func healthHandler(w http.ResponseWriter, r *http.Request) {
	// w http.ResponseWriter : 응답을 쓰는 통로(클라이언트한테 보내는쪽)
	// r *http.Request : 들어온 정보(URL,헤더,바디 등). 지금은 안씀

	// 요청이 들어올 때마다 카운터를 1 증가 (Counter.Inc()는 내부적으로 atomic 연산이라 동시 요청에도 안전)
	requestsTotal.Inc()

	// 응답 Content-Type을 application/JSON으로 지정 — 클라이언트가 파싱 방식(아 이거 json이구나)을 알 수 있도록
	// 응답 헤더 설정
	w.Header().Set("Content-Type", "application/json")

	// HTTP 200 OK 에 JSON 바디를 직접 인코딩해 응답 (별도 버퍼 없이 스트리밍)
	// w(응답)에 직접 json 을 스트리밍. 중간버퍼 없이 바로 씀
	json.NewEncoder(w).Encode(map[string]string{
		// go에서 json 객체를 만드는 가장 간단한 방법.
		// 키-값 쌍의 맵을 만들고, encode에 넘기면 자동으로 {"status":"ok","timestamp":"2026-.."} 됨
		"status":    "ok",                            // 서버 정상 여부
		"timestamp": time.Now().Format(time.RFC3339), // 현재 시각 (ISO 8601 형식)
	})
}

func main() {
	// /health 경로로 들어오는 모든 요청을 healthHandler 함수로 라우팅
	http.HandleFunc("/health", healthHandler)

	// /metrics 경로 — 직접 만든 JSON 대신 promhttp.Handler()를 붙인다.
	// 이 핸들러가 requestsTotal뿐 아니라 Go 런타임 지표(고루틴 수, GC 시간, 메모리 등)까지
	// Prometheus가 읽을 수 있는 표준 텍스트 포맷("# HELP ...", "# TYPE ...", "지표명{라벨} 값")으로 자동 출력한다.
	// 사람이 보기 좋은 JSON이 아니라 Prometheus가 파싱하기 위한 포맷이라, 브라우저로 열면 텍스트 그대로 보인다.
	http.Handle("/metrics", promhttp.Handler())

	log.Println("서버 시작: :8080")
	log.Println("가동 시작 시각:", startTime.Format(time.RFC3339))

	// :8080 포트에서 HTTP 요청 수신 대기 — nil은 기본 ServeMux(위에서 등록한 라우터) 사용
	// ListenAndServe는 정상 종료가 없으므로, 에러 발생 시 즉시 종료
	log.Fatal(http.ListenAndServe(":8080", nil))
}
