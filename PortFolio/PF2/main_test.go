package main

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
)

// TestHealthHandler: GET /health 가 200 OK와 status=ok JSON을 반환하는지 검증
func TestHealthHandler(t *testing.T) {
	req := httptest.NewRequest(http.MethodGet, "/health", nil)
	rec := httptest.NewRecorder()

	healthHandler(rec, req)

	if rec.Code != http.StatusOK {
		t.Fatalf("want 200, got %d", rec.Code)
	}

	var body map[string]string
	if err := json.NewDecoder(rec.Body).Decode(&body); err != nil {
		t.Fatalf("invalid JSON response: %v", err)
	}
	if body["status"] != "ok" {
		t.Fatalf("want status=ok, got %s", body["status"])
	}
}

// TestMetricsHandler: GET /metrics 호출 시 requests_total 카운터가 1 증가하는지 검증
func TestMetricsHandler(t *testing.T) {
	before := requestsTotal

	req := httptest.NewRequest(http.MethodGet, "/metrics", nil)
	rec := httptest.NewRecorder()

	metricsHandler(rec, req)

	if rec.Code != http.StatusOK {
		t.Fatalf("want 200, got %d", rec.Code)
	}

	var body map[string]interface{}
	if err := json.NewDecoder(rec.Body).Decode(&body); err != nil {
		t.Fatalf("invalid JSON response: %v", err)
	}

	got := int64(body["requests_total"].(float64))
	if got != before+1 {
		t.Fatalf("want requests_total=%d, got %d", before+1, got)
	}
}
