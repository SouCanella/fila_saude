//go:build integration

package integration_test

import (
	"context"
	"os"
	"testing"
	"time"

	"github.com/SouCanella/fila_saude/apps/api/internal/migrate"
	"github.com/SouCanella/fila_saude/apps/api/tests/testutil"
	"github.com/jackc/pgx/v5"
)

func TestPostgres_PostGISExtension(t *testing.T) {
	testutil.SkipUnlessIntegration(t)
	ctx := context.Background()

	conn, err := pgx.Connect(ctx, os.Getenv("DATABASE_URL"))
	if err != nil {
		t.Fatalf("connect: %v", err)
	}
	defer conn.Close(ctx)

	var ext bool
	err = conn.QueryRow(ctx, `
		SELECT EXISTS (
			SELECT 1 FROM pg_extension WHERE extname = 'postgis'
		)
	`).Scan(&ext)
	if err != nil {
		t.Fatalf("query postgis: %v", err)
	}
	if !ext {
		t.Fatal("postgis extension not enabled")
	}
}

func TestMigrations_Up(t *testing.T) {
	testutil.SkipUnlessIntegration(t)
	ctx := context.Background()
	dir := os.Getenv("MIGRATIONS_DIR")
	if dir == "" {
		dir = "../../migrations"
	}
	if err := migrate.Run(ctx, os.Getenv("DATABASE_URL"), dir); err != nil {
		t.Fatalf("migrate up: %v", err)
	}

	conn, err := pgx.Connect(ctx, os.Getenv("DATABASE_URL"))
	if err != nil {
		t.Fatalf("connect: %v", err)
	}
	defer conn.Close(ctx)

	for _, table := range []string{"hospital", "specialty", "queue_snapshot"} {
		var exists bool
		err := conn.QueryRow(ctx, `
			SELECT EXISTS (
				SELECT 1 FROM information_schema.tables
				WHERE table_schema = 'public' AND table_name = $1
			)
		`, table).Scan(&exists)
		if err != nil || !exists {
			t.Fatalf("table %q missing: err=%v exists=%v", table, err, exists)
		}
	}
}

func TestPostgres_Connectivity(t *testing.T) {
	testutil.SkipUnlessIntegration(t)
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	conn, err := pgx.Connect(ctx, os.Getenv("DATABASE_URL"))
	if err != nil {
		t.Fatalf("connect: %v", err)
	}
	defer conn.Close(ctx)

	var one int
	if err := conn.QueryRow(ctx, "SELECT 1").Scan(&one); err != nil || one != 1 {
		t.Fatalf("ping: err=%v one=%d", err, one)
	}
}
