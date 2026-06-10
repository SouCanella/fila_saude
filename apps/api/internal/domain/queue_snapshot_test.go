package domain

import "testing"

func TestValidateRiskLevel_ManchesterAllowed(t *testing.T) {
	levels := []RiskLevel{RiskVermelho, RiskLaranja, RiskAmarelo, RiskVerde, RiskAzul}
	for _, l := range levels {
		if err := ValidateRiskLevel(l); err != nil {
			t.Fatalf("level %q should be valid: %v", l, err)
		}
	}
}

func TestValidateRiskLevel_RejectsInvalid(t *testing.T) {
	if err := ValidateRiskLevel(RiskLevel("roxo")); err == nil {
		t.Fatal("expected error for invalid risk level")
	}
}
