package server

import (
	"log/slog"
	"net/http"
	"os"

	"github.com/SouCanella/fila_saude/apps/api/internal/handler"
	"github.com/SouCanella/fila_saude/apps/api/internal/middleware"
	"github.com/go-chi/chi/v5"
)

// NewRouter builds the HTTP router with observability middleware.
func NewRouter(logger *slog.Logger) http.Handler {
	r := chi.NewRouter()
	r.Use(middleware.Logging(logger))

	r.Get("/health", handler.Health)

	r.NotFound(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusNotFound)
		_, _ = w.Write([]byte(`{"code":"NOT_FOUND","message":"route not found"}`))
	})

	return r
}

// NewLogger creates JSON slog logger to stdout.
func NewLogger(level string) *slog.Logger {
	var lvl slog.Level
	switch level {
	case "debug":
		lvl = slog.LevelDebug
	case "warn":
		lvl = slog.LevelWarn
	case "error":
		lvl = slog.LevelError
	default:
		lvl = slog.LevelInfo
	}
	return slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{Level: lvl}))
}
