package domain

import "time"

// QueueSnapshot represents a point-in-time queue state for a hospital specialty.
type QueueSnapshot struct {
	ID                 int64
	HospitalID         int64
	SpecialtyID        int64
	RiskLevel          RiskLevel
	WaitingCount       int
	AvgWaitMinutes24h  *int
	AvgWaitMinutes7d   *int
	SourceName         string
	CapturedAt         time.Time
}

func (s QueueSnapshot) Validate() error {
	return ValidateRiskLevel(s.RiskLevel)
}
