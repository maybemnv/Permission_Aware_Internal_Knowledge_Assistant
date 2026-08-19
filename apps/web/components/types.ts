export type UiState =
  | "loading" | "fresh" | "stale" | "deleted" | "pending_recheck" | "unavailable"
  | "insufficient_context" | "refused" | "failed" | "no_accessible_context" | "answered"
  | "fixture" | "blocked" | "unverified";

export type SourceType = "notion" | "google_drive" | "sharepoint" | "slack" | "teams" | "confluence" | "jira" | "github";
export type DemoPrincipal = "allowed-user" | "denied-user" | "unmapped-user" | "changed-group-user" | "cross-tenant-user" | "admin-user";

export interface SearchRequest { query: string; sourceTypes: SourceType[]; freshness: "all" | "fresh" | "stale"; }
export interface SearchResult { resultId: string; itemId: string; title: string; sourceType: SourceType; safeSnippet: string; locator: string; indexedAt: string; sourceUpdatedAt: string | null; lifecycleState: "active" | "stale" | "deleted" | "pending_recheck"; score: number; }
export interface SearchResponse { queryId: string; results: SearchResult[]; answerAvailable: boolean; noAccessibleContext: boolean; freshnessSummary: { freshCount: number; staleCount: number; unknownCount: number; }; }
export interface Citation { citationId: string; itemId: string; sourceType: SourceType; title: string; locator: string; indexedAt: string; coverageState: "supports" | "partial"; }
export interface AnswerResponse { answerId: string; queryId: string; status: "answered" | "insufficient_context" | "refused" | "failed" | "unavailable"; answerText: string | null; citations: Citation[]; caveats: string[]; freshness: "fresh" | "stale" | "mixed" | "unknown"; generatedAt: string; }
export interface SourcePreviewData { resultId: string; itemId: string; title: string; sourceType: SourceType; excerpt: string; locator: string; sourceUpdatedAt: string | null; indexedAt: string; lifecycleState: "active" | "stale" | "deleted" | "pending_recheck"; canonicalUrl: string | null; }
export interface ConnectorStatus { connectorId: string; sourceType: SourceType; status: "healthy" | "degraded" | "configured"; capabilityLabel: "fixture" | "blocked" | "unverified"; itemCount: number; errorCount: number; freshness: "fresh" | "stale" | "mixed" | "unknown"; capabilityGaps: string[]; }
export interface SyncRun { syncRunId: string; connectorId: string; status: "completed" | "failed"; errorCount: number; }
export interface UnansweredRecord { queryId: string; tenantId: string; category: string; queryHash: string; createdAt: string; safeSummary: string; }
export interface EvaluationRun { status: string; permissionLeaks: number; citationCoverage: number; totalCases: number; passedCases: number; datasetVersion: string; }
export interface AuditEvent { eventId: string; eventType: string; reasonCode: string | null; createdAt: string; metadata: Record<string, string | number | boolean>; }

export const sourceLabel = (sourceType: SourceType) => ({ google_drive: "Google Drive", sharepoint: "SharePoint", slack: "Slack", teams: "Teams", notion: "Notion", confluence: "Confluence", jira: "Jira", github: "GitHub" })[sourceType];
export const lifecycleState = (state: SourcePreviewData["lifecycleState"] | SearchResult["lifecycleState"]): UiState => ({ active: "fresh", stale: "stale", deleted: "deleted", pending_recheck: "pending_recheck" } as const)[state];
