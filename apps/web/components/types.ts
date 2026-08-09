export type UiState =
  | "loading"
  | "fresh"
  | "stale"
  | "deleted"
  | "pending_recheck"
  | "unavailable"
  | "insufficient_context"
  | "refused"
  | "failed"
  | "no_accessible_context"
  | "answered"
  | "fixture"
  | "blocked"
  | "unverified";

export type SourceType =
  | "notion"
  | "google_drive"
  | "sharepoint"
  | "slack"
  | "teams"
  | "confluence"
  | "jira"
  | "github";

export interface SearchRequest {
  query: string;
  sourceTypes: SourceType[];
  freshness: "all" | "fresh" | "stale";
}

export interface SearchResult {
  itemId: string;
  title: string;
  sourceType: SourceType;
  snippet: string;
  locator: string;
  indexedAt: string;
  updatedAt: string;
  freshness: Extract<UiState, "fresh" | "stale" | "pending_recheck">;
  score: string;
}

export interface Citation {
  citationId: string;
  itemId: string;
  sourceType: SourceType;
  title: string;
  locator: string;
  indexedAt: string;
  coverageState: "supports";
}

export interface SearchResponse {
  queryId: string;
  results: SearchResult[];
  answerAvailable: boolean;
  noAccessibleContext: boolean;
  freshnessSummary: {
    freshCount: number;
    staleCount: number;
    unknownCount: number;
  };
}

export interface AnswerResponse {
  answerId: string;
  queryId: string;
  status: Extract<UiState, "answered" | "insufficient_context" | "refused" | "failed" | "unavailable">;
  text: string;
  citations: Citation[];
  caveats: string[];
  freshness: "fresh" | "stale";
  generatedAt: string;
}

export interface SourcePreviewData {
  itemId: string;
  title: string;
  sourceType: SourceType;
  excerpt: string;
  locator: string;
  updatedAt: string;
  indexedAt: string;
  lifecycleState: Extract<UiState, "fresh" | "stale" | "deleted" | "pending_recheck" | "unavailable">;
  recheckState: Extract<UiState, "fresh" | "pending_recheck" | "unavailable">;
  deepLink: string;
}

export interface ConnectorStatus {
  id: string;
  name: string;
  itemCount: string;
  lastRun: string;
  detail: string;
  state: Extract<UiState, "fixture" | "blocked" | "unverified" | "stale" | "failed" | "pending_recheck">;
}

export const sourceLabel = (sourceType: SourceType) =>
  ({
    google_drive: "Google Drive",
    sharepoint: "SharePoint",
    slack: "Slack",
    teams: "Teams",
    notion: "Notion",
    confluence: "Confluence",
    jira: "Jira",
    github: "GitHub",
  })[sourceType];

export const SEARCH_FIXTURE: SearchResponse & { query: string } = {
  query: "What is the travel reimbursement policy for my region and role?",
  queryId: "query-demo-1042",
  results: [
    {
      itemId: "item-travel-policy",
      title: "Travel reimbursement policy",
      sourceType: "notion",
      snippet: "Employees can claim transport, lodging, and meals within the regional limits approved for their role.",
      locator: "Policy / Reimbursement limits",
      indexedAt: "12 minutes ago",
      updatedAt: "Today, 09:18",
      freshness: "fresh",
      score: "0.96",
    },
    {
      itemId: "item-approval-form",
      title: "Travel expense approval form",
      sourceType: "google_drive",
      snippet: "Attach itemized receipts and route the completed form to the role-based approver before reimbursement.",
      locator: "Section 2 / Required evidence",
      indexedAt: "2 days ago",
      updatedAt: "Aug 07, 16:42",
      freshness: "stale",
      score: "0.88",
    },
  ],
  answerAvailable: true,
  noAccessibleContext: false,
  freshnessSummary: { freshCount: 1, staleCount: 1, unknownCount: 0 },
};

export const ANSWER_FIXTURE: AnswerResponse = {
  answerId: "answer-demo-1042",
  queryId: SEARCH_FIXTURE.queryId,
  status: "answered",
  text: "For your region and role, submit transport, lodging, and meal expenses within the regional limits, then attach itemized receipts to the travel expense approval form and route it to the role-based approver. The policy source is current; the form is indexed but marked stale, so confirm the latest approval wording before submitting.",
  citations: [
    {
      citationId: "citation-policy",
      itemId: "item-travel-policy",
      sourceType: "notion",
      title: "Travel reimbursement policy",
      locator: "Policy / Reimbursement limits",
      indexedAt: "12 minutes ago",
      coverageState: "supports",
    },
    {
      citationId: "citation-form",
      itemId: "item-approval-form",
      sourceType: "google_drive",
      title: "Travel expense approval form",
      locator: "Section 2 / Required evidence",
      indexedAt: "2 days ago",
      coverageState: "supports",
    },
  ],
  caveats: ["One supporting source is stale; the request-time preview check remains required."],
  freshness: "stale",
  generatedAt: "Today, 09:25",
};

export const PREVIEWS: Record<string, SourcePreviewData> = {
  "item-travel-policy": {
    itemId: "item-travel-policy",
    title: "Travel reimbursement policy",
    sourceType: "notion",
    excerpt: "Regional limits apply to transport, lodging, and meals. Employees should use the approved expense category for their role and retain itemized receipts.",
    locator: "Policy / Reimbursement limits",
    updatedAt: "Today, 09:18",
    indexedAt: "12 minutes ago",
    lifecycleState: "fresh",
    recheckState: "fresh",
    deepLink: "https://fixture.invalid/notion/travel-policy",
  },
  "item-approval-form": {
    itemId: "item-approval-form",
    title: "Travel expense approval form",
    sourceType: "google_drive",
    excerpt: "Attach itemized receipts and route the completed form to the role-based approver before reimbursement.",
    locator: "Section 2 / Required evidence",
    updatedAt: "Aug 07, 16:42",
    indexedAt: "2 days ago",
    lifecycleState: "stale",
    recheckState: "pending_recheck",
    deepLink: "https://fixture.invalid/drive/approval-form",
  },
};

export const CONNECTOR_FIXTURES: ConnectorStatus[] = [
  { id: "google-drive", name: "Google Drive", itemCount: "128 items", lastRun: "12 min ago", detail: "Fixture sync · ACL snapshot current", state: "fixture" },
  { id: "sharepoint", name: "SharePoint", itemCount: "96 items", lastRun: "31 min ago", detail: "Fixture sync · regional groups mapped", state: "fixture" },
  { id: "slack", name: "Slack", itemCount: "64 items", lastRun: "1 hr ago", detail: "Fixture sync · thread export bounded", state: "fixture" },
  { id: "teams", name: "Teams", itemCount: "44 items", lastRun: "1 hr ago", detail: "Fixture sync · channel roles mapped", state: "fixture" },
  { id: "notion", name: "Notion", itemCount: "82 items", lastRun: "12 min ago", detail: "Fixture sync · policy pages current", state: "fixture" },
  { id: "confluence", name: "Confluence", itemCount: "0 items", lastRun: "Never", detail: "Capability not verified in fixture mode", state: "unverified" },
  { id: "jira", name: "Jira", itemCount: "18 items", lastRun: "3 hr ago", detail: "Fixture sync · one stale project", state: "stale" },
  { id: "github", name: "GitHub", itemCount: "0 items", lastRun: "Paused", detail: "Connector blocked pending scope review", state: "blocked" },
];
