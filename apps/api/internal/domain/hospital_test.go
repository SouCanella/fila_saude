package domain

import "testing"

func TestNewHospital_ActiveDefaultTrue(t *testing.T) {
	h := NewHospital("Hospital Teste", "RJ")
	if !h.Active {
		t.Fatal("expected Active=true by default")
	}
	if h.UF != "RJ" {
		t.Fatalf("expected UF=RJ, got %q", h.UF)
	}
}
