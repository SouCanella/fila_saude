package middleware

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/go-chi/chi/v5"
)

func TestLogging_GeneratesRequestIDWhenAbsent(t *testing.T) {
	logger, capture := NewTestLogger()
	r := chi.NewRouter()
	r.Use(Logging(logger))
	r.Get("/health", func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusOK)
	})

	req := httptest.NewRequest(http.MethodGet, "/health", nil)
	rec := httptest.NewRecorder()
	r.ServeHTTP(rec, req)

	rid := rec.Header().Get("X-Request-ID")
	if rid == "" {
		t.Fatal("expected X-Request-ID header")
	}
	if len(capture.Records) == 0 {
		t.Fatal("expected log record")
	}
	last := capture.Records[len(capture.Records)-1]
	if last["request_id"] != rid {
		t.Fatalf("log request_id %v != header %q", last["request_id"], rid)
	}
}

func TestLogging_ReusesClientRequestID(t *testing.T) {
	logger, capture := NewTestLogger()
	r := chi.NewRouter()
	r.Use(Logging(logger))
	r.Get("/health", func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusOK)
	})

	const clientID = "client-req-id-12345"
	req := httptest.NewRequest(http.MethodGet, "/health", nil)
	req.Header.Set("X-Request-ID", clientID)
	rec := httptest.NewRecorder()
	r.ServeHTTP(rec, req)

	if got := rec.Header().Get("X-Request-ID"); got != clientID {
		t.Fatalf("header %q, want %q", got, clientID)
	}
	last := capture.Records[len(capture.Records)-1]
	if last["request_id"] != clientID {
		t.Fatalf("log request_id %v, want %q", last["request_id"], clientID)
	}
}

func TestLogging_ContainsRequiredFields(t *testing.T) {
	logger, capture := NewTestLogger()
	r := chi.NewRouter()
	r.Use(Logging(logger))
	r.Get("/health", func(w http.ResponseWriter, _ *http.Request) {
		w.WriteHeader(http.StatusOK)
	})

	req := httptest.NewRequest(http.MethodGet, "/health", nil)
	rec := httptest.NewRecorder()
	r.ServeHTTP(rec, req)

	last := capture.Records[len(capture.Records)-1]
	for _, key := range []string{"request_id", "method", "path", "status", "duration_ms", "level", "msg"} {
		if _, ok := last[key]; !ok {
			t.Fatalf("missing log field %q in %+v", key, last)
		}
	}
}
