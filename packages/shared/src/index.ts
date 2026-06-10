/** Tipos compartilhados web — expandir conforme OpenAPI (CARD-002+) */
export type HealthStatus = "ok";

export interface HealthResponse {
  status: HealthStatus;
}
