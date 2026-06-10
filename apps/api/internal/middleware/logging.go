package middleware

import (
	"bytes"
	"context"
	"encoding/json"
	"log/slog"
	"net/http"
	"strings"
	"time"

	"github.com/google/uuid"
)

type ctxKey int

const requestIDKey ctxKey = iota

// RequestIDFromContext returns the request ID stored by Logging middleware.
func RequestIDFromContext(ctx context.Context) string {
	if v, ok := ctx.Value(requestIDKey).(string); ok {
		return v
	}
	return ""
}

// Logging emits structured JSON logs with request correlation.
func Logging(logger *slog.Logger) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			start := time.Now()
			rid := strings.TrimSpace(r.Header.Get("X-Request-ID"))
			if rid == "" || !isValidRequestID(rid) {
				rid = uuid.New().String()
			}
			ctx := context.WithValue(r.Context(), requestIDKey, rid)
			r = r.WithContext(ctx)

			wrapped := &statusWriter{ResponseWriter: w, status: http.StatusOK}
			w.Header().Set("X-Request-ID", rid)
			next.ServeHTTP(wrapped, r)

			duration := time.Since(start).Milliseconds()
			level := slog.LevelInfo
			if wrapped.status >= 500 {
				level = slog.LevelError
			} else if wrapped.status >= 400 {
				level = slog.LevelWarn
			}

			logger.Log(r.Context(), level, "http_request",
				slog.String("request_id", rid),
				slog.String("method", r.Method),
				slog.String("path", r.URL.Path),
				slog.Int("status", wrapped.status),
				slog.Int64("duration_ms", duration),
			)
		})
	}
}

func isValidRequestID(s string) bool {
	return len(s) >= 8 && len(s) <= 128
}

type statusWriter struct {
	http.ResponseWriter
	status int
}

func (w *statusWriter) WriteHeader(code int) {
	w.status = code
	w.ResponseWriter.WriteHeader(code)
}

// JSONLogHandler captures slog output for tests.
type JSONLogHandler struct {
	Records []map[string]any
}

func (h *JSONLogHandler) Enabled(_ context.Context, _ slog.Level) bool {
	return true
}

func (h *JSONLogHandler) Handle(_ context.Context, r slog.Record) error {
	m := map[string]any{
		"level": r.Level.String(),
		"msg":   r.Message,
	}
	r.Attrs(func(a slog.Attr) bool {
		m[a.Key] = a.Value.Any()
		return true
	})
	h.Records = append(h.Records, m)
	return nil
}

func (h *JSONLogHandler) WithAttrs(_ []slog.Attr) slog.Handler {
	return h
}

func (h *JSONLogHandler) WithGroup(_ string) slog.Handler {
	return h
}

func NewTestLogger() (*slog.Logger, *JSONLogHandler) {
	h := &JSONLogHandler{}
	return slog.New(h), h
}

func LogContainsField(records []map[string]any, key string) bool {
	for _, rec := range records {
		if _, ok := rec[key]; ok {
			return true
		}
	}
	return false
}

func MarshalLogRecord(rec map[string]any) ([]byte, error) {
	var buf bytes.Buffer
	enc := json.NewEncoder(&buf)
	if err := enc.Encode(rec); err != nil {
		return nil, err
	}
	return buf.Bytes(), nil
}
