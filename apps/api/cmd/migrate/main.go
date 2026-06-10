package main

import (
	"context"
	"log/slog"
	"os"

	"github.com/SouCanella/fila_saude/apps/api/internal/migrate"
)

func main() {
	url := os.Getenv("DATABASE_URL")
	if url == "" {
		slog.Error("DATABASE_URL required")
		os.Exit(1)
	}
	dir := migrate.MigrationsDir()
	if err := migrate.Run(context.Background(), url, dir); err != nil {
		slog.Error("migrate failed", slog.String("error", err.Error()))
		os.Exit(1)
	}
	slog.Info("migrations applied", slog.String("dir", dir))
}
