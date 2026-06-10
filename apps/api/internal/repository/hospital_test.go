package repository

import (
	"context"
	"testing"

	"github.com/SouCanella/fila_saude/apps/api/internal/domain"
)

type mockHospitalRepo struct {
	insertFn func(ctx context.Context, h domain.Hospital) (int64, error)
	findFn   func(ctx context.Context, id int64) (domain.Hospital, error)
}

func (m *mockHospitalRepo) Insert(ctx context.Context, h domain.Hospital) (int64, error) {
	return m.insertFn(ctx, h)
}

func (m *mockHospitalRepo) FindByID(ctx context.Context, id int64) (domain.Hospital, error) {
	return m.findFn(ctx, id)
}

func TestMockHospitalRepo_InsertFind(t *testing.T) {
	var stored domain.Hospital
	repo := &mockHospitalRepo{
		insertFn: func(_ context.Context, h domain.Hospital) (int64, error) {
			stored = h
			return 42, nil
		},
		findFn: func(_ context.Context, id int64) (domain.Hospital, error) {
			stored.ID = id
			return stored, nil
		},
	}

	id, err := repo.Insert(context.Background(), domain.NewHospital("Test", "RJ"))
	if err != nil || id != 42 {
		t.Fatalf("insert: id=%d err=%v", id, err)
	}
	got, err := repo.FindByID(context.Background(), 42)
	if err != nil || got.Name != "Test" {
		t.Fatalf("find: %+v err=%v", got, err)
	}
}
