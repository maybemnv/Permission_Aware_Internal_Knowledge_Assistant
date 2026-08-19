"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { api } from "@/lib/api";
import { AnswerPanel } from "./AnswerPanel";
import { SourcePreview } from "./SourcePreview";
import { StatusBadge } from "./StatusBadge";
import { lifecycleState, sourceLabel, type AnswerResponse, type Citation, type DemoPrincipal, type SearchResponse, type SearchResult, type SourcePreviewData, type UiState } from "./types";

const canonicalQuestion = "What is the travel reimbursement policy for my region and role?";
const stateReference: UiState[] = ["loading", "stale", "deleted", "pending_recheck", "unavailable", "insufficient_context", "refused", "failed", "no_accessible_context"];

function PrincipalSelector({ principal, onChange }: { principal: DemoPrincipal; onChange: (principal: DemoPrincipal) => void }) {
  return <label className="source-chip">Fixture principal <select aria-label="Fixture principal" value={principal} onChange={(event) => onChange(event.target.value as DemoPrincipal)}><option value="allowed-user">regional employee</option><option value="denied-user">denied employee</option><option value="unmapped-user">unmapped employee</option><option value="changed-group-user">changed-group employee</option><option value="cross-tenant-user">cross-tenant employee</option><option value="admin-user">fixture administrator</option></select></label>;
}

function Topbar({ principal, onPrincipalChange }: { principal: DemoPrincipal; onPrincipalChange: (principal: DemoPrincipal) => void }) {
  return <header className="topbar"><div className="brand-lockup"><Link className="brand-mark" href="/">Evidence Desk</Link><p className="eyebrow">Permission-aware internal knowledge</p></div><nav className="topnav" aria-label="Primary navigation"><Link className="nav-link" href="/" aria-current="page">Workbench</Link><Link className="nav-link" href="/admin">Admin surfaces</Link><PrincipalSelector principal={principal} onChange={onPrincipalChange} /></nav></header>;
}

function SearchForm({ query, onQueryChange, onSubmit }: { query: string; onQueryChange: (value: string) => void; onSubmit: (event: FormEvent<HTMLFormElement>) => void }) {
  return <form className="search-form" onSubmit={onSubmit} aria-label="Search the knowledge base"><div className="search-input-row"><label className="sr-only" htmlFor="knowledge-query">Ask a question</label><input id="knowledge-query" className="search-input" value={query} onChange={(event) => onQueryChange(event.target.value)} placeholder="Ask about a policy, process, or source" /><button className="primary-button" type="submit">Search evidence</button></div><div className="filter-row"><span className="source-chip">Authorization happens before evidence is rendered.</span></div></form>;
}

function ResultCard({ result, onOpenPreview, onAnswer }: { result: SearchResult; onOpenPreview: (result: SearchResult) => void; onAnswer: () => void }) {
  return <article className="result-card"><div className="card-heading"><div><p className="eyebrow">{sourceLabel(result.sourceType)}</p><h3>{result.title}</h3></div><StatusBadge state={lifecycleState(result.lifecycleState)} /></div><p>{result.safeSnippet}</p><div className="meta">{result.locator} · match {result.score.toFixed(2)}</div><div className="result-actions"><button className="text-button" type="button" onClick={() => onOpenPreview(result)}>Open safe preview</button><button className="text-button" type="button" onClick={onAnswer}>Use in answer</button></div></article>;
}

function ResultsView({ search, state, onOpenPreview, onAnswer }: { search: SearchResponse | null; state: UiState; onOpenPreview: (result: SearchResult) => void; onAnswer: () => void }) {
  if (state === "loading") return <section className="state-card" role="status"><StatusBadge state="loading" /><p>Checking which evidence you may see.</p></section>;
  if (state === "failed") return <section className="state-card" role="alert"><StatusBadge state="failed" /><p>The fixture API is unavailable. No stale browser fixture is shown.</p></section>;
  if (!search || search.results.length === 0) return <section className="state-card"><StatusBadge state="no_accessible_context" /><p>No accessible context is available for this request.</p><button className="secondary-button" type="button" onClick={onAnswer}>Generate safe answer</button></section>;
  return <><div className="page-intro"><div><p className="eyebrow">Results / {search.queryId}</p><h1>Permitted evidence for your question</h1></div><StatusBadge state="fresh" /></div><div className="workspace-grid"><main className="panel"><div className="panel-heading"><div><p className="eyebrow">{search.results.length.toString().padStart(2, "0")} results</p><h2>Ranked after permission filtering</h2></div></div><div className="result-list">{search.results.map((result) => <ResultCard key={result.itemId} result={result} onOpenPreview={onOpenPreview} onAnswer={onAnswer} />)}</div></main><aside className="panel"><p className="eyebrow">Query summary</p><h2>Request trace</h2><p className="meta">{search.freshnessSummary.freshCount} fresh · {search.freshnessSummary.staleCount} stale</p><button className="primary-button" type="button" onClick={onAnswer}>Generate cited answer</button></aside></div></>;
}

export function SearchWorkbench({ initialPrincipal = "allowed-user" }: { initialPrincipal?: DemoPrincipal }) {
  const [principal, setPrincipal] = useState<DemoPrincipal>(initialPrincipal);
  const [query, setQuery] = useState(canonicalQuestion);
  const [phase, setPhase] = useState<"search" | "results" | "answer">("search");
  const [requestState, setRequestState] = useState<UiState>("fresh");
  const [search, setSearch] = useState<SearchResponse | null>(null);
  const [answer, setAnswer] = useState<AnswerResponse | null>(null);
  const [preview, setPreview] = useState<SourcePreviewData | null>(null);

  const changePrincipal = async (next: DemoPrincipal) => { setPrincipal(next); await api.setDemoPrincipal(next); setSearch(null); setAnswer(null); setPreview(null); setPhase("search"); };
  const runSearch = async (event?: FormEvent<HTMLFormElement>, question?: string) => { event?.preventDefault(); const effective = question ?? query; setQuery(effective); setRequestState("loading"); setPhase("results"); setPreview(null); try { setSearch(await api.search(effective)); setRequestState("fresh"); } catch { setSearch(null); setRequestState("failed"); } };
  const generateAnswer = async () => { setRequestState("loading"); try { setAnswer(await api.answer(query, search?.queryId)); setPhase("answer"); setRequestState("fresh"); } catch { setRequestState("failed"); } };
  const openPreview = async (result: SearchResult | Citation) => { try { setPreview(await api.preview("resultId" in result ? result.resultId : `result-${result.itemId}`)); } catch { setPreview(null); setRequestState("unavailable"); } };

  return <><Topbar principal={principal} onPrincipalChange={changePrincipal} />{phase === "search" && <section className="hero"><div className="hero-copy"><p className="eyebrow">Search / evidence first</p><h1>Find the answer. See why it is safe.</h1><p>Only server-authorized context reaches the browser.</p><SearchForm query={query} onQueryChange={setQuery} onSubmit={runSearch} /></div><aside className="hero-side"><StatusBadge state="fixture" /><button className="secondary-button" type="button" onClick={() => void runSearch(undefined, canonicalQuestion)}>Use the seeded travel question</button></aside></section>}{phase === "results" && <ResultsView search={search} state={requestState} onOpenPreview={(result) => void openPreview(result)} onAnswer={() => void generateAnswer()} />}{phase === "answer" && answer && <><div className="page-intro"><div><p className="eyebrow">Answer / {answer.answerId}</p><h1>Evidence you can inspect</h1><p>{query}</p></div><StatusBadge state={answer.status} /></div><div className="workspace-grid"><main><AnswerPanel answer={answer} onOpenCitation={(citation) => void openPreview(citation)} /></main><SourcePreview preview={preview} onClose={() => setPreview(null)} /></div></>}<section className="panel"><p className="eyebrow">Interaction contract</p><div className="status-reference">{stateReference.map((state) => <StatusBadge key={state} state={state} />)}</div></section></>;
}
