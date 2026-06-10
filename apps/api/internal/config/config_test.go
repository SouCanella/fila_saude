package config

import (
	"os"
	"testing"
)

func TestLoad_RequiresDatabaseURL(t *testing.T) {
	t.Setenv("DATABASE_URL", "")
	t.Setenv("REDIS_URL", "redis://localhost:6379/0")

	_, err := Load()
	if err == nil {
		t.Fatal("expected error when DATABASE_URL missing")
	}
}

func TestLoad_RequiresRedisURL(t *testing.T) {
	t.Setenv("DATABASE_URL", "postgresql://u:p@localhost:5432/db")
	t.Setenv("REDIS_URL", "")

	_, err := Load()
	if err == nil {
		t.Fatal("expected error when REDIS_URL missing")
	}
}

func TestLoadWithDefaults_PortDefault8000(t *testing.T) {
	os.Unsetenv("APP_PORT")
	os.Unsetenv("OSRM_BASE_URL")

	cfg := LoadWithDefaults()
	if cfg.AppPort != 8000 {
		t.Fatalf("expected port 8000, got %d", cfg.AppPort)
	}
	if cfg.OSRMBaseURL != "http://localhost:5000" {
		t.Fatalf("expected default OSRM URL, got %q", cfg.OSRMBaseURL)
	}
}

func TestLoad_Success(t *testing.T) {
	t.Setenv("DATABASE_URL", "postgresql://filasaude:filasaude@localhost:5432/filasaude")
	t.Setenv("REDIS_URL", "redis://localhost:6379/0")
	t.Setenv("APP_PORT", "9000")

	cfg, err := Load()
	if err != nil {
		t.Fatalf("Load() error: %v", err)
	}
	if cfg.AppPort != 9000 {
		t.Fatalf("expected port 9000, got %d", cfg.AppPort)
	}
}
