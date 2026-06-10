package testutil

import (
	"context"
	"net"
	"net/http"
	"os"
	"testing"
	"time"
)

// IntegrationEnabled returns true when DATABASE_URL is set for integration tests.
func IntegrationEnabled() bool {
	return os.Getenv("DATABASE_URL") != ""
}

// SkipUnlessIntegration skips the test when infra is unavailable.
func SkipUnlessIntegration(t *testing.T) {
	t.Helper()
	if !IntegrationEnabled() {
		t.Skip("DATABASE_URL not set — skip integration test")
	}
}

// RedisEnabled returns true when REDIS_URL is set.
func RedisEnabled() bool {
	return os.Getenv("REDIS_URL") != ""
}

// SkipUnlessRedis skips when Redis is not configured.
func SkipUnlessRedis(t *testing.T) {
	t.Helper()
	if !RedisEnabled() {
		t.Skip("REDIS_URL not set — skip redis integration test")
	}
}

// OSRMEnabled returns true when OSRM_BASE_URL is set.
func OSRMEnabled() bool {
	return os.Getenv("OSRM_BASE_URL") != ""
}

// SkipUnlessOSRM skips when OSRM is not configured.
func SkipUnlessOSRM(t *testing.T) {
	t.Helper()
	if !OSRMEnabled() {
		t.Skip("OSRM_BASE_URL not set — skip osrm integration test")
	}
}

// WaitTCP waits until host:port accepts connections or timeout.
func WaitTCP(hostPort string, timeout time.Duration) error {
	deadline := time.Now().Add(timeout)
	for time.Now().Before(deadline) {
		conn, err := net.DialTimeout("tcp", hostPort, 500*time.Millisecond)
		if err == nil {
			_ = conn.Close()
			return nil
		}
		time.Sleep(200 * time.Millisecond)
	}
	return context.DeadlineExceeded
}

// HTTPGetStatus performs GET and returns status code.
func HTTPGetStatus(ctx context.Context, url string) (int, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return 0, err
	}
	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return 0, err
	}
	defer resp.Body.Close()
	return resp.StatusCode, nil
}
