import type { AnswerResponse, AuditEvent, ConnectorStatus, DemoPrincipal, EvaluationRun, SearchRequest, SearchResponse, SourcePreviewData, SyncRun, UnansweredRecord } from "@/components/types";

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api";

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}/backend${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", ...init.headers },
  });
  if (!response.ok) throw new Error("The fixture API is unavailable.");
  return response.json() as Promise<T>;
}

export function buildSearchRequest(query: string, sourceTypes: SearchRequest["sourceTypes"] = [], freshness: SearchRequest["freshness"] = "all"): SearchRequest {
  return { query, sourceTypes, freshness };
}

export const api = {
  setDemoPrincipal: (principal: DemoPrincipal) => fetch("/api/demo-principal", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ principal }) }),
  search: (query: string) => request<SearchResponse>("/v1/search", { method: "POST", body: JSON.stringify({ query }) }),
  answer: (question: string, queryId?: string) => request<AnswerResponse>("/v1/answers", { method: "POST", body: JSON.stringify({ question, queryId }) }),
  preview: (resultId: string) => request<SourcePreviewData>(`/v1/results/${encodeURIComponent(resultId)}/preview`),
  connectors: () => request<ConnectorStatus[]>("/v1/connectors"),
  sync: (connectorId: string) => request<SyncRun>(`/v1/connectors/${encodeURIComponent(connectorId)}/sync`, { method: "POST", body: JSON.stringify({ mode: "initial", idempotencyKey: `showcase-${connectorId}-${Date.now()}` }) }),
  syncHistory: (connectorId: string) => request<SyncRun[]>(`/v1/connectors/${encodeURIComponent(connectorId)}/sync-runs`),
  unanswered: () => request<UnansweredRecord[]>("/v1/admin/unanswered"),
  evaluations: () => request<EvaluationRun[]>("/v1/admin/evaluations"),
  startEvaluation: () => request<EvaluationRun>("/v1/admin/evaluations", { method: "POST", body: JSON.stringify({ datasetVersion: "demo-v1" }) }),
  audit: () => request<AuditEvent[]>("/v1/admin/audit"),
};
