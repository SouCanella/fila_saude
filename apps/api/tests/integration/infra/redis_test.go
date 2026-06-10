//go:build integration

package integration_test

import (
	"context"
	"os"
	"testing"
	"time"

	"github.com/SouCanella/fila_saude/apps/api/tests/testutil"
	"github.com/redis/go-redis/v9"
)

func TestRedis_PingPong(t *testing.T) {
	testutil.SkipUnlessRedis(t)
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	opt, err := redis.ParseURL(os.Getenv("REDIS_URL"))
	if err != nil {
		t.Fatalf("parse redis url: %v", err)
	}
	client := redis.NewClient(opt)
	defer client.Close()

	pong, err := client.Ping(ctx).Result()
	if err != nil {
		t.Fatalf("ping: %v", err)
	}
	if pong != "PONG" {
		t.Fatalf("expected PONG, got %q", pong)
	}
}
