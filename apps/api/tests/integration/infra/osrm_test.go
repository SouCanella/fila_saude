//go:build integration

package integration_test

import (
	"context"
	"os"
	"testing"
	"time"

	"github.com/SouCanella/fila_saude/apps/api/tests/testutil"
)

func TestOSRM_Responds(t *testing.T) {
	testutil.SkipUnlessOSRM(t)
	base := os.Getenv("OSRM_BASE_URL")
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	status, err := testutil.HTTPGetStatus(ctx, base+"/")
	if err != nil {
		// stub may respond on root
		status, err = testutil.HTTPGetStatus(ctx, base)
	}
	if err != nil {
		t.Fatalf("osrm request: %v", err)
	}
	if status < 200 || status >= 500 {
		t.Fatalf("unexpected status %d from OSRM stub", status)
	}
}
