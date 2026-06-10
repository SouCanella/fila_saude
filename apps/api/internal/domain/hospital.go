package domain

import "fmt"

// RiskLevel Manchester triage colors.
type RiskLevel string

const (
	RiskVermelho RiskLevel = "vermelho"
	RiskLaranja  RiskLevel = "laranja"
	RiskAmarelo  RiskLevel = "amarelo"
	RiskVerde    RiskLevel = "verde"
	RiskAzul     RiskLevel = "azul"
)

var validRiskLevels = map[RiskLevel]struct{}{
	RiskVermelho: {},
	RiskLaranja:  {},
	RiskAmarelo:  {},
	RiskVerde:    {},
	RiskAzul:     {},
}

func (r RiskLevel) Valid() bool {
	_, ok := validRiskLevels[r]
	return ok
}

func ValidateRiskLevel(r RiskLevel) error {
	if !r.Valid() {
		return fmt.Errorf("invalid risk_level: %q", r)
	}
	return nil
}

// Hospital core entity.
type Hospital struct {
	ID            int64
	Name          string
	Address       string
	Latitude      float64
	Longitude     float64
	Rating        *float64
	ReviewsCount  int
	GooglePlaceID *string
	UF            string
	Active        bool
}

// NewHospital applies defaults for hospital creation.
func NewHospital(name, uf string) Hospital {
	return Hospital{
		Name:   name,
		UF:     uf,
		Active: true,
	}
}
