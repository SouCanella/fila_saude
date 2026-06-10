//go:build integration

package repository_test

import (
	"context"
	"os"
	"testing"
	"time"

	"github.com/SouCanella/fila_saude/apps/api/internal/domain"
	"github.com/SouCanella/fila_saude/apps/api/internal/migrate"
	"github.com/SouCanella/fila_saude/apps/api/internal/repository"
	"github.com/SouCanella/fila_saude/apps/api/tests/testutil"
	"github.com/jackc/pgx/v5/pgxpool"
)

func setupRepo(t *testing.T) (*repository.HospitalRepository, func()) {
	t.Helper()
	testutil.SkipUnlessIntegration(t)
	ctx := context.Background()
	dir := os.Getenv("MIGRATIONS_DIR")
	if dir == "" {
		dir = "../../../migrations"
	}
	if err := migrate.Run(ctx, os.Getenv("DATABASE_URL"), dir); err != nil {
		t.Fatalf("migrate: %v", err)
	}
	pool, err := pgxpool.New(ctx, os.Getenv("DATABASE_URL"))
	if err != nil {
		t.Fatalf("pool: %v", err)
	}
	return repository.NewHospitalRepository(pool), func() { pool.Close() }
}

func TestHospitalGeo_ST_DWithin(t *testing.T) {
	repo, cleanup := setupRepo(t)
	defer cleanup()
	ctx := context.Background()

	// Hospital near Rio center
	h := domain.NewHospital("Hospital Rio", "RJ")
	h.Latitude = -22.9068
	h.Longitude = -43.1729
	id, err := repo.Insert(ctx, h)
	if err != nil {
		t.Fatalf("insert: %v", err)
	}
	h.ID = id

	count, err := repo.CountWithinRadiusKm(ctx, -22.91, -43.18, 25)
	if err != nil {
		t.Fatalf("count: %v", err)
	}
	if count < 1 {
		t.Fatalf("expected at least 1 hospital within 25km, got %d", count)
	}
}

func TestSnapshot_FKViolation(t *testing.T) {
	repo, cleanup := setupRepo(t)
	defer cleanup()
	ctx := context.Background()

	specID, err := repo.EnsureSpecialty(ctx, "geral", "Clínica Geral")
	if err != nil {
		t.Fatalf("specialty: %v", err)
	}

	s := domain.QueueSnapshot{
		HospitalID:  999999,
		SpecialtyID: specID,
		RiskLevel:   domain.RiskVerde,
		SourceName:  "test",
		CapturedAt:  time.Now().UTC(),
	}
	_, err = repo.InsertSnapshot(ctx, s)
	if err == nil {
		t.Fatal("expected FK violation for orphan hospital_id")
	}
}

func TestHospitalRepo_RoundTrip(t *testing.T) {
	repo, cleanup := setupRepo(t)
	defer cleanup()
	ctx := context.Background()

	specID, err := repo.EnsureSpecialty(ctx, "pediatria", "Pediatria")
	if err != nil {
		t.Fatalf("specialty: %v", err)
	}

	h := domain.NewHospital("Hospital Teste CARD-001", "RJ")
	h.Latitude = -22.9
	h.Longitude = -43.2
	hid, err := repo.Insert(ctx, h)
	if err != nil {
		t.Fatalf("insert hospital: %v", err)
	}

	wait24 := 45
	_, err = repo.InsertSnapshot(ctx, domain.QueueSnapshot{
		HospitalID:        hid,
		SpecialtyID:       specID,
		RiskLevel:         domain.RiskAmarelo,
		WaitingCount:      12,
		AvgWaitMinutes24h: &wait24,
		SourceName:        "mock-test",
		CapturedAt:        time.Now().UTC(),
	})
	if err != nil {
		t.Fatalf("insert snapshot: %v", err)
	}

	got, err := repo.FindByID(ctx, hid)
	if err != nil {
		t.Fatalf("find: %v", err)
	}
	if got.Name != h.Name || got.UF != "RJ" {
		t.Fatalf("round trip mismatch: %+v", got)
	}
}
