import type { SearchRequest, SourceType } from "@/components/types";

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "/api";

export function buildSearchRequest(
  query: string,
  sourceTypes: SourceType[] = [],
  freshness: SearchRequest["freshness"] = "all",
): SearchRequest {
  return { query, sourceTypes, freshness };
}
