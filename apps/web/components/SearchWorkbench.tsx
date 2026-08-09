"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { AnswerPanel } from "./AnswerPanel";
import { PREVIEWS, ANSWER_FIXTURE, SEARCH_FIXTURE, sourceLabel, type Citation, type SearchResult, type SourcePreviewData, type UiState } from "./types";
import { SourcePreview } from "./SourcePreview";
import { StatusBadge } from "./StatusBadge";

type WorkbenchPhase = "search" | "results" | "answer";

const STATE_REFERENCE: UiState[] = [
  "loading",
  "stale",
  "deleted",
  "pending_recheck",
  "unavailable",
  "insufficient_context",
  "refused",
  "failed",
  "no_accessible_context",
];

function Topbar() {
  return (
    <header className="topbar">
      <div className="brand-lockup">
        <Link className="brand-mark" href="/">Evidence Desk</Link>
        <p className="eyebrow">Permission-aware internal knowledge</p>
      </div>
      <nav className="topnav" aria-label="Primary navigation">
        <Link className="nav-link" href="/" aria-current="page">Workbench</Link>
        <Link className="nav-link" href="/admin">Admin surfaces</Link>
      </nav>
    </header>
  );
}

function StatStrip() {
  return (
    <section className="stat-strip" aria-label="Workbench status">
      <div className="stat-card"><span className="data-label">Fresh evidence</span><strong>01</strong><span>of 02 permitted sources</span></div>
      <div className="stat-card"><span className="data-label">Answer coverage</span><strong>100%</strong><span>citations validated in fixture</span></div>
      <div className="stat-card"><span className="data-label">Connector view</span><strong>08</strong><span>status cards available to admins</span></div>
    </section>
  );
}

function SearchForm({ query, onQueryChange, onSubmit }: { query: string; onQueryChange: (value: string) => void; onSubmit: (event: FormEvent<HTMLFormElement>) => void }) {
  return (
    <form className="search-form" onSubmit={onSubmit} aria-label="Search the knowledge base">
      <div className="search-input-row">
        <label className="sr-only" htmlFor="knowledge-query">Ask a question</label>
        <input id="knowledge-query" className="search-input" value={query} onChange={(event) => onQueryChange(event.target.value)} placeholder="Ask about a policy, process, or source" />
        <button className="primary-button" type="submit">Search evidence</button>
      </div>
      <div className="filter-row" aria-label="Source filters">
        <label className="filter-chip"><input type="checkbox" defaultChecked /> All permitted sources</label>
        <label className="filter-chip"><input type="checkbox" /> Fresh only</label>
        <span className="source-chip">Principal: regional employee</span>
      </div>
    </form>
  );
}

function SearchHome({ query, onQueryChange, onSubmit, onUseDemo }: { query: string; onQueryChange: (value: string) => void; onSubmit: (event: FormEvent<HTMLFormElement>) => void; onUseDemo: () => void }) {
  return (
    <>
      <section className="hero" aria-labelledby="search-heading">
        <div className="hero-copy">
          <p className="eyebrow">Search / evidence first</p>
          <h1 id="search-heading">Find the answer. See why it is safe.</h1>
          <p>Search returns only the context the active principal can access. Follow every answer to its source, freshness, and request-time check.</p>
          <SearchForm query={query} onQueryChange={onQueryChange} onSubmit={onSubmit} />
        </div>
        <aside className="hero-side" aria-label="Current request context">
          <div>
            <p className="data-label">Current identity</p>
            <strong>regional.employee</strong>
            <p className="meta">tenant-demo / travel group</p>
          </div>
          <div>
            <p className="data-label">Request posture</p>
            <StatusBadge state="loading" />
            <p className="meta">A query ID is created before evidence loads.</p>
          </div>
          <button className="secondary-button" type="button" onClick={onUseDemo}>Use the seeded travel question</button>
        </aside>
      </section>
      <StatStrip />
      <section className="panel" aria-labelledby="recent-heading">
        <div className="panel-heading">
          <div><p className="eyebrow">Recent query</p><h2 id="recent-heading">A small, inspectable starting point</h2></div>
          <StatusBadge state="fixture" />
        </div>
        <p>Use the seeded policy question to see two authorized sources, a cited answer, and a safe preview. No inaccessible title or placeholder is shown when context is unavailable.</p>
        <button className="text-button" type="button" onClick={onUseDemo}>Open the travel-policy fixture →</button>
      </section>
    </>
  );
}

function FilterRail() {
  return (
    <aside className="panel" aria-label="Search filters">
      <div className="panel-heading"><div><p className="eyebrow">Filter rail</p><h2>Evidence scope</h2></div></div>
      <div className="stack">
        <div><p className="data-label">Source</p><div className="stack"><label className="filter-chip"><input type="checkbox" defaultChecked /> Notion</label><label className="filter-chip"><input type="checkbox" defaultChecked /> Google Drive</label></div></div>
        <div><p className="data-label">Freshness</p><div className="stack"><label className="filter-chip"><input type="radio" name="freshness" defaultChecked /> All states</label><label className="filter-chip"><input type="radio" name="freshness" /> Fresh only</label></div></div>
        <div className="state-card"><StatusBadge state="no_accessible_context" /><p>No accessible context is included in the result set.</p></div>
      </div>
    </aside>
  );
}

function ResultCard({ result, onOpenPreview, onAnswer }: { result: SearchResult; onOpenPreview: (result: SearchResult) => void; onAnswer: () => void }) {
  return (
    <article className="result-card">
      <div className="card-heading">
        <div><p className="eyebrow">{sourceLabel(result.sourceType)}</p><h3>{result.title}</h3></div>
        <StatusBadge state={result.freshness} />
      </div>
      <p>{result.snippet}</p>
      <div className="meta">{result.locator} · indexed {result.indexedAt} · match {result.score}</div>
      <div className="result-actions">
        <span className="source-chip">Updated {result.updatedAt}</span>
        <div className="chip-row"><button className="text-button" type="button" onClick={() => onOpenPreview(result)}>Open safe preview</button><button className="text-button" type="button" onClick={onAnswer}>Use in answer</button></div>
      </div>
    </article>
  );
}

function ResultsView({ onOpenPreview, onAnswer }: { onOpenPreview: (result: SearchResult) => void; onAnswer: () => void }) {
  return (
    <>
      <div className="page-intro"><div><p className="eyebrow">Results / query-demo-1042</p><h1>Permitted evidence for your question</h1></div><StatusBadge state="fresh" /></div>
      <div className="workspace-grid">
        <FilterRail />
        <main className="panel" aria-labelledby="results-heading">
          <div className="panel-heading"><div><p className="eyebrow">02 results</p><h2 id="results-heading">Ranked after permission filtering</h2></div><span className="meta">Fresh 01 · Stale 01</span></div>
          <div className="result-list">
            {SEARCH_FIXTURE.results.map((result) => <ResultCard key={result.itemId} result={result} onOpenPreview={onOpenPreview} onAnswer={onAnswer} />)}
          </div>
          <div className="state-card" style={{ marginTop: 16 }}><StatusBadge state="no_accessible_context" /><p>Safe absence is explicit: unavailable evidence is omitted before ranking, answering, or preview.</p></div>
        </main>
        <aside className="panel" aria-label="Search summary">
          <div className="panel-heading"><div><p className="eyebrow">Query summary</p><h2>Request trace</h2></div></div>
          <dl className="metric-list"><div><dt className="data-label">Query ID</dt><dd className="meta">{SEARCH_FIXTURE.queryId}</dd></div><div><dt className="data-label">Authorized context</dt><dd><StatusBadge state="answered" label="2 sources" /></dd></div><div><dt className="data-label">Freshness</dt><dd className="meta">1 fresh · 1 stale</dd></div></dl>
          <button className="primary-button" type="button" onClick={onAnswer}>Generate cited answer</button>
        </aside>
      </div>
    </>
  );
}

function StateReference() {
  return (
    <section className="panel" aria-labelledby="state-reference-heading">
      <div className="panel-heading"><div><p className="eyebrow">Interaction contract</p><h2 id="state-reference-heading">States stay readable without color</h2></div><span className="meta">Keyboard and reduced-motion ready</span></div>
      <div className="status-reference">{STATE_REFERENCE.map((state) => <StatusBadge key={state} state={state} />)}</div>
    </section>
  );
}

export function SearchWorkbench() {
  const [phase, setPhase] = useState<WorkbenchPhase>("search");
  const [query, setQuery] = useState(SEARCH_FIXTURE.query);
  const [requestState, setRequestState] = useState<UiState>("fresh");
  const [preview, setPreview] = useState<SourcePreviewData | null>(PREVIEWS["item-travel-policy"]);

  const runSearch = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setRequestState("loading");
    setPhase("results");
    window.setTimeout(() => setRequestState("fresh"), 240);
  };

  const useDemoQuestion = () => {
    setQuery(SEARCH_FIXTURE.query);
    setPhase("results");
    setRequestState("fresh");
  };

  const openCitation = (citation: Citation) => setPreview(PREVIEWS[citation.itemId] ?? null);

  return (
    <>
      <Topbar />
      {phase === "search" && <SearchHome query={query} onQueryChange={setQuery} onSubmit={runSearch} onUseDemo={useDemoQuestion} />}
      {phase === "results" && <>
        {requestState === "loading" && <div className="state-card" role="status" style={{ marginBottom: 16 }}><StatusBadge state="loading" /><p>Loading the query trace. Unavailable context is never represented as a result.</p></div>}
        <ResultsView onOpenPreview={(result) => setPreview(PREVIEWS[result.itemId] ?? null)} onAnswer={() => setPhase("answer")} />
      </>}
      {phase === "answer" && <>
        <div className="page-intro"><div><p className="eyebrow">Answer / {ANSWER_FIXTURE.answerId}</p><h1>Evidence you can inspect</h1><p>{query}</p></div><StatusBadge state={ANSWER_FIXTURE.status} /></div>
        <div className="workspace-grid">
          <FilterRail />
          <main><AnswerPanel answer={ANSWER_FIXTURE} onOpenCitation={openCitation} /></main>
          <SourcePreview preview={preview} onClose={() => setPreview(null)} />
        </div>
      </>}
      {phase !== "answer" && <StateReference />}
    </>
  );
}
