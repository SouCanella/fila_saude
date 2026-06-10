package repository

import (
	"context"
	"fmt"

	"github.com/SouCanella/fila_saude/apps/api/internal/domain"
	"github.com/jackc/pgx/v5/pgxpool"
)

// HospitalRepository persists hospitals.
type HospitalRepository struct {
	pool *pgxpool.Pool
}

func NewHospitalRepository(pool *pgxpool.Pool) *HospitalRepository {
	return &HospitalRepository{pool: pool}
}

// Insert creates a hospital with geo point.
func (r *HospitalRepository) Insert(ctx context.Context, h domain.Hospital) (int64, error) {
	const q = `
		INSERT INTO hospital (name, address, location, rating, reviews_count, google_place_id, uf, active)
		VALUES ($1, $2, ST_SetSRID(ST_MakePoint($3, $4), 4326)::geography, $5, $6, $7, $8, $9)
		RETURNING id
	`
	var id int64
	err := r.pool.QueryRow(ctx, q,
		h.Name, h.Address, h.Longitude, h.Latitude,
		h.Rating, h.ReviewsCount, h.GooglePlaceID, h.UF, h.Active,
	).Scan(&id)
	if err != nil {
		return 0, fmt.Errorf("insert hospital: %w", err)
	}
	return id, nil
}

// FindByID loads a hospital by primary key.
func (r *HospitalRepository) FindByID(ctx context.Context, id int64) (domain.Hospital, error) {
	const q = `
		SELECT id, name, COALESCE(address, ''), ST_Y(location::geometry), ST_X(location::geometry),
		       rating, reviews_count, google_place_id, uf, active
		FROM hospital WHERE id = $1
	`
	var h domain.Hospital
	var rating *float64
	var gpid *string
	err := r.pool.QueryRow(ctx, q, id).Scan(
		&h.ID, &h.Name, &h.Address, &h.Latitude, &h.Longitude,
		&rating, &h.ReviewsCount, &gpid, &h.UF, &h.Active,
	)
	if err != nil {
		return domain.Hospital{}, fmt.Errorf("find hospital: %w", err)
	}
	h.Rating = rating
	h.GooglePlaceID = gpid
	return h, nil
}

// CountWithinRadiusKm returns hospitals within radius of a point.
func (r *HospitalRepository) CountWithinRadiusKm(ctx context.Context, lat, lng float64, radiusKm float64) (int, error) {
	const q = `
		SELECT COUNT(*) FROM hospital
		WHERE active = TRUE
		  AND ST_DWithin(
		    location,
		    ST_SetSRID(ST_MakePoint($1, $2), 4326)::geography,
		    $3
		  )
	`
	var count int
	meters := radiusKm * 1000
	err := r.pool.QueryRow(ctx, q, lng, lat, meters).Scan(&count)
	if err != nil {
		return 0, fmt.Errorf("count within radius: %w", err)
	}
	return count, nil
}

// InsertSnapshot stores a queue snapshot row.
func (r *HospitalRepository) InsertSnapshot(ctx context.Context, s domain.QueueSnapshot) (int64, error) {
	if err := s.Validate(); err != nil {
		return 0, err
	}
	const q = `
		INSERT INTO queue_snapshot (
			hospital_id, specialty_id, risk_level, waiting_count,
			avg_wait_minutes_24h, avg_wait_minutes_7d, source_name, captured_at
		) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
		RETURNING id
	`
	var id int64
	err := r.pool.QueryRow(ctx, q,
		s.HospitalID, s.SpecialtyID, string(s.RiskLevel), s.WaitingCount,
		s.AvgWaitMinutes24h, s.AvgWaitMinutes7d, s.SourceName, s.CapturedAt,
	).Scan(&id)
	if err != nil {
		return 0, fmt.Errorf("insert snapshot: %w", err)
	}
	return id, nil
}

// EnsureSpecialty returns specialty id, creating if needed (test helper).
func (r *HospitalRepository) EnsureSpecialty(ctx context.Context, slug, name string) (int64, error) {
	const q = `
		INSERT INTO specialty (slug, name) VALUES ($1, $2)
		ON CONFLICT (slug) DO UPDATE SET name = EXCLUDED.name
		RETURNING id
	`
	var id int64
	if err := r.pool.QueryRow(ctx, q, slug, name).Scan(&id); err != nil {
		return 0, fmt.Errorf("ensure specialty: %w", err)
	}
	return id, nil
}
