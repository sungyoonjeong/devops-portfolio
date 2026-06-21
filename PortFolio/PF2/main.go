package main

import (
	"encoding/json" // JSON 직렬화·역직렬화 표준 라이브러리
	"log"           // 서버 시작 로그 출력용
	"net/http"      // HTTP 서버 및 핸들러 등록 표준 라이브러리
	"sync/atomic"   // 동시 요청에서 안전한 카운터 증감 (뮤텍스 없이 원자적 연산)
	"time"          // 서버 가동 시작 시각 기록 및 uptime 계산용
)

// startTime: 서버가 처음 시작된 시각 — uptime 계산의 기준점
var startTime = time.Now()

// requestsTotal: 전체 요청 수 카운터 — int64로 선언해야 atomic 연산 가능
var requestsTotal int64

// healthHandler: GET /health — 서버가 살아있는지 확인하는 헬스체크 엔드포인트
// 로드밸런서나 오케스트레이터(K8s)가 주기적으로 호출해 서버 상태를 판단한다
func healthHandler(w http.ResponseWriter, r *http.Request) {
	// w http.ResponseWriter : 응답을 쓰는 통로(클라이언트한테 보내는쪽)
	// r *http.Request : 들어온 정보(URL,헤더,바디 등). 지금은 안씀

	// 요청이 들어올 때마다 카운터를 1 증가 (atomic: 동시 요청 시 race condition 방지)
	atomic.AddInt64(&requestsTotal, 1)

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

// metricsHandler: GET /metrics — 서버 내부 지표를 JSON으로 반환하는 엔드포인트
// Prometheus 연동 전 단계로, 커스텀 JSON 지표를 노출하는 가장 간단한 패턴
func metricsHandler(w http.ResponseWriter, r *http.Request) {
	// 이 요청 자체도 카운터에 포함 (헬스체크와 동일 카운터 공유)
	atomic.AddInt64(&requestsTotal, 1)

	w.Header().Set("Content-Type", "application/json")

	// atomic.LoadInt64: 현재 카운터 값을 원자적으로 읽기 (쓰기와 동시에 읽어도 안전)
	json.NewEncoder(w).Encode(map[string]interface{}{
		"requests_total": atomic.LoadInt64(&requestsTotal),     // 누적 요청 수, atomic으로 읽음
		"uptime_seconds": int(time.Since(startTime).Seconds()), // 서버 가동 시간(초)
		//지금 시각에서 시작시각을 빼서 초 단위로 변환
	})
}

func main() {
	// /health 경로로 들어오는 모든 요청을 healthHandler 함수로 라우팅
	http.HandleFunc("/health", healthHandler)

	// /metrics 경로로 들어오는 모든 요청을 metricsHandler 함수로 라우팅
	http.HandleFunc("/metrics", metricsHandler)

	log.Println("서버 시작: :8080")

	// :8080 포트에서 HTTP 요청 수신 대기 — nil은 기본 ServeMux(위에서 등록한 라우터) 사용
	// ListenAndServe는 정상 종료가 없으므로, 에러 발생 시 즉시 종료
	log.Fatal(http.ListenAndServe(":8080", nil))
}
