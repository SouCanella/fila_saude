-- +goose Up
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TYPE risk_level AS ENUM (
    'vermelho',
    'laranja',
    'amarelo',
    'verde',
    'azul'
);

CREATE TABLE specialty (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(64) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE hospital (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    location GEOGRAPHY(POINT, 4326),
    rating DECIMAL(2, 1),
    reviews_count INT NOT NULL DEFAULT 0,
    google_place_id VARCHAR(255),
    uf CHAR(2) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX hospital_location_gix ON hospital USING GIST (location);

CREATE TABLE queue_snapshot (
    id SERIAL PRIMARY KEY,
    hospital_id INT NOT NULL REFERENCES hospital (id) ON DELETE CASCADE,
    specialty_id INT NOT NULL REFERENCES specialty (id) ON DELETE CASCADE,
    risk_level risk_level NOT NULL,
    waiting_count INT NOT NULL DEFAULT 0,
    avg_wait_minutes_24h INT,
    avg_wait_minutes_7d INT,
    source_name VARCHAR(255) NOT NULL,
    captured_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX queue_snapshot_hospital_idx ON queue_snapshot (hospital_id, captured_at DESC);

CREATE TABLE data_source (
    id SERIAL PRIMARY KEY,
    type VARCHAR(64) NOT NULL,
    url TEXT,
    sla_minutes INT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE integration_health (
    id SERIAL PRIMARY KEY,
    source_id INT REFERENCES data_source (id) ON DELETE SET NULL,
    hospital_id INT REFERENCES hospital (id) ON DELETE SET NULL,
    last_ok_at TIMESTAMPTZ,
    lag_minutes INT,
    status VARCHAR(32) NOT NULL
);

-- +goose Down
DROP TABLE IF EXISTS integration_health;
DROP TABLE IF EXISTS data_source;
DROP TABLE IF EXISTS queue_snapshot;
DROP TABLE IF EXISTS hospital;
DROP TABLE IF EXISTS specialty;
DROP TYPE IF EXISTS risk_level;
