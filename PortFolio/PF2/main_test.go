package main

import (
	"io"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/prometheus/client_golang/prometheus/promhttp"
)

// TestHealthHandler: GET /health 가 200 OK와 status=ok JSON을 반환하는지 검증
func TestHealthHandler(t *testing.T) {
	req := httptest.NewRequest(http.MethodGet, "/health", nil)
	rec := httptest.NewRecorder()

	healthHandler(rec, req)

	if rec.Code != http.StatusOK {
		t.Fatalf("want 200, got %d", rec.Code)
	}

	body := rec.Body.String()
	if !strings.Contains(body, `"status":"ok"`) {
		t.Fatalf("want status=ok in body, got %s", body)
	}
}

// TestMetricsHandler: GET /metrics 가 Prometheus 텍스트 포맷으로
// pf2_requests_total 지표를 노출하는지 검증 (JSON이 아니라 "이름 값" 라인 형식)
func TestMetricsHandler(t *testing.T) {
	// /health를 한 번 호출해서 카운터를 최소 1 이상으로 만들어둔다
	healthHandler(httptest.NewRecorder(), httptest.NewRequest(http.MethodGet, "/health", nil))

	req := httptest.NewRequest(http.MethodGet, "/metrics", nil)
	rec := httptest.NewRecorder()

	promhttp.Handler().ServeHTTP(rec, req)

	if rec.Code != http.StatusOK {
		t.Fatalf("want 200, got %d", rec.Code)
	}

	respBody, err := io.ReadAll(rec.Body)
	if err != nil {
		t.Fatalf("failed to read response body: %v", err)
	}
	body := string(respBody)

	// Prometheus 텍스트 포맷의 필수 요소: HELP·TYPE 메타데이터 + 실제 지표 라인
	if !strings.Contains(body, "# HELP pf2_requests_total") {
		t.Fatalf("want HELP line for pf2_requests_total, got:\n%s", body)
	}
	if !strings.Contains(body, "# TYPE pf2_requests_total counter") {
		t.Fatalf("want TYPE line marking pf2_requests_total as counter, got:\n%s", body)
	}
	if !strings.Contains(body, "pf2_requests_total ") {
		t.Fatalf("want pf2_requests_total metric line with a value, got:\n%s", body)
	}
}
