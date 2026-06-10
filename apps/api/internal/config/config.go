package config

import (
	"fmt"
	"os"
	"strconv"
)

// Config holds runtime settings loaded from environment variables.
type Config struct {
	AppPort     int
	DatabaseURL string
	RedisURL    string
	OSRMBaseURL string
	LogLevel    string
}

// Load reads configuration from environment. DATABASE_URL and REDIS_URL are required for full stack.
func Load() (Config, error) {
	port := 8000
	if v := os.Getenv("APP_PORT"); v != "" {
		p, err := strconv.Atoi(v)
		if err != nil {
			return Config{}, fmt.Errorf("APP_PORT invalid: %w", err)
		}
		port = p
	}

	dbURL := os.Getenv("DATABASE_URL")
	if dbURL == "" {
		return Config{}, fmt.Errorf("DATABASE_URL is required")
	}

	redisURL := os.Getenv("REDIS_URL")
	if redisURL == "" {
		return Config{}, fmt.Errorf("REDIS_URL is required")
	}

	osrm := os.Getenv("OSRM_BASE_URL")
	if osrm == "" {
		osrm = "http://localhost:5000"
	}

	logLevel := os.Getenv("LOG_LEVEL")
	if logLevel == "" {
		logLevel = "info"
	}

	return Config{
		AppPort:     port,
		DatabaseURL: dbURL,
		RedisURL:    redisURL,
		OSRMBaseURL: osrm,
		LogLevel:    logLevel,
	}, nil
}

// LoadWithDefaults is used in tests when optional vars may be absent.
func LoadWithDefaults() Config {
	port := 8000
	if v := os.Getenv("APP_PORT"); v != "" {
		if p, err := strconv.Atoi(v); err == nil {
			port = p
		}
	}
	osrm := os.Getenv("OSRM_BASE_URL")
	if osrm == "" {
		osrm = "http://localhost:5000"
	}
	logLevel := os.Getenv("LOG_LEVEL")
	if logLevel == "" {
		logLevel = "info"
	}
	return Config{
		AppPort:     port,
		DatabaseURL: os.Getenv("DATABASE_URL"),
		RedisURL:    os.Getenv("REDIS_URL"),
		OSRMBaseURL: osrm,
		LogLevel:    logLevel,
	}
}
