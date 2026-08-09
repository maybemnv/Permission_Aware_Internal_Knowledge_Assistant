"use client";

import Link from "next/link";
import { useState } from "react";
import { CONNECTOR_FIXTURES, type ConnectorStatus } from "./types";
import { StatusBadge } from "./StatusBadge";

type AdminSurface = "connectors" | "permissions" | "unanswered" | "evaluation" | "audit";

const ADMIN_SURFACES: Array<{ id: AdminSurface; label: string }> = [
  { id: "connectors", label: "Connectors" },
  { id: "permissions", label: "Permissions" },
  { id: "unanswered", label: "Unanswered" },
  { id: "evaluation", label: "Evaluation" },
  { id: "audit", label: "Audit" },
];

function AdminHeader({ surface, onSurfaceChange }: { surface: AdminSurface; onSurfaceChange: (surface: AdminSurface) => void }) {
  return (
    <>
      <div className="topbar">
        <div className="brand-lockup"><Link className="brand-mark" href="/">Evidence Desk</Link><p className="eyebrow">Admin / governance workbench</p></div>
        <nav className="topnav" aria-label="Primary navigation"><Link className="nav-link" href="/">Workbench</Link><Link className="nav-link" href="/admin" aria-current="page">Admin surfaces</Link></nav>
      </div>
      <div className="page-intro"><div><p className="eyebrow">Operations / fixture mode</p><h1>Make the system legible</h1><p>Review source health, access mappings, knowledge gaps, evaluation outcomes, and audit-safe traces without handling provider credentials in the browser.</p></div><StatusBadge state="fixture" /></div>
      <nav className="admin-tabs" aria-label="Admin surfaces" role="tablist">
        {ADMIN_SURFACES.map((item) => <button key={item.id} className="admin-tab" type="button" role="tab" aria-selected={surface === item.id} onClick={() => onSurfaceChange(item.id)}>{item.label}</button>)}
      </nav>
    </>
  );
}

function ConnectorCard({ connector, onSync, syncing }: { connector: ConnectorStatus; onSync: (id: string) => void; syncing: boolean }) {
  return (
    <article className="connector-card">
      <div className="card-heading"><h3>{connector.name}</h3><StatusBadge state={connector.state} /></div>
      <p>{connector.detail}</p>
      <div className="meta">{connector.itemCount} · last run {connector.lastRun}</div>
      <button className="secondary-button" type="button" onClick={() => onSync(connector.id)} disabled={syncing}>{syncing ? "Sync pending…" : "Start fixture sync"}</button>
    </article>
  );
}

function ConnectorsSurface({ connectors, onSync, syncing }: { connectors: ConnectorStatus[]; onSync: (id: string) => void; syncing: string | null }) {
  return (
    <section className="panel" aria-labelledby="connectors-heading">
      <div className="panel-heading"><div><p className="eyebrow">Connector status</p><h2 id="connectors-heading">Eight source boundaries</h2></div><StatusBadge state="fixture" label="Fixture mode" /></div>
      <p>Every adapter reports its capability honestly. Sync actions are local fixture transitions until a secure connector service is integrated.</p>
      <div className="connector-grid">{connectors.map((connector) => <ConnectorCard key={connector.id} connector={connector} onSync={onSync} syncing={syncing === connector.id} />)}</div>
    </section>
  );
}

function PermissionsSurface() {
  return (
    <section className="panel" aria-labelledby="permissions-heading">
      <div className="panel-heading"><div><p className="eyebrow">Permissions / deny by default</p><h2 id="permissions-heading">Access mappings in plain view</h2></div><StatusBadge state="answered" label="Mappings visible" /></div>
      <div className="mapping-list">
        <div className="state-card"><div className="card-heading"><h3>regional.employee</h3><StatusBadge state="fresh" label="Allowed" /></div><p>tenant-demo · travel group · us-east region</p><span className="meta">2 source ACL snapshots · last checked 12 minutes ago</span></div>
        <div className="state-card"><div className="card-heading"><h3>changed-group.employee</h3><StatusBadge state="pending_recheck" /></div><p>Group membership changed; citation opens request a current check.</p><span className="meta">No content is shown while the mapping is unresolved.</span></div>
        <div className="state-card"><div className="card-heading"><h3>unmapped.principal</h3><StatusBadge state="no_accessible_context" /></div><p>Safe absence is returned until a tenant and group mapping are known.</p><span className="meta">No source reference or existence signal is available.</span></div>
      </div>
    </section>
  );
}

function UnansweredSurface() {
  return (
    <section className="panel" aria-labelledby="unanswered-heading">
      <div className="panel-heading"><div><p className="eyebrow">Governance / unanswered</p><h2 id="unanswered-heading">Where evidence is thin</h2></div><StatusBadge state="fixture" /></div>
      <div className="metric-grid"><div className="state-card"><span className="data-label">Needs source</span><strong>14</strong><span className="meta">queries in the last 7 days</span></div><div className="state-card"><span className="data-label">Insufficient context</span><strong>06</strong><span className="meta">safe answer refusals</span></div><div className="state-card"><span className="data-label">Stale evidence</span><strong>09</strong><span className="meta">follow-up candidates</span></div></div>
      <div className="stack"><div className="state-card"><div className="card-heading"><strong>Process / expense policy</strong><span className="meta">6 queries</span></div><p>Latest example is shown as an aggregate category; source content remains permission-filtered.</p></div><div className="state-card"><div className="card-heading"><strong>Role / approval path</strong><span className="meta">4 queries</span></div><p>Coverage is missing across two fixture connectors.</p></div></div>
    </section>
  );
}

function EvaluationSurface() {
  return (
    <section className="panel" aria-labelledby="evaluation-heading">
      <div className="panel-heading"><div><p className="eyebrow">Evaluation / safety gates</p><h2 id="evaluation-heading">A repeatable fixture report</h2></div><StatusBadge state="fixture" /></div>
      <div className="metric-grid"><div className="state-card"><span className="data-label">Permission leakage</span><strong>0</strong><span className="meta">unauthorized outputs</span></div><div className="state-card"><span className="data-label">Citation coverage</span><strong>100%</strong><span className="meta">2 of 2 labeled claims</span></div><div className="state-card"><span className="data-label">Policy cases</span><strong>08 / 08</strong><span className="meta">fixture cases evaluated</span></div></div>
      <div className="state-card"><div className="card-heading"><div><p className="data-label">Dataset version</p><h3>demo-policy-v1</h3></div><StatusBadge state="answered" label="Pass threshold met" /></div><p>Provider ACL fidelity, model quality, retention, residency, and live connector parity remain unverified until tested against live systems.</p></div>
    </section>
  );
}

function AuditSurface() {
  const auditRows = [
    ["09:25", "regional.employee", "answer.citation", "allowed", "item-travel-policy"],
    ["09:24", "regional.employee", "source.preview", "allowed", "item-approval-form"],
    ["09:18", "unmapped.principal", "search", "no_accessible_context", "—"],
    ["09:12", "admin.fixture", "connector.sync", "pending_recheck", "notion"],
  ];

  return (
    <section className="panel" aria-labelledby="audit-heading">
      <div className="panel-heading"><div><p className="eyebrow">Audit / redacted trace</p><h2 id="audit-heading">What the system recorded</h2></div><StatusBadge state="answered" label="Safe fields only" /></div>
      <p>Source references appear only when the event was authorized. Denied events retain a reason code without content or existence metadata.</p>
      <div className="table-wrap"><table className="audit-table"><caption className="sr-only">Permission-safe audit events</caption><thead><tr><th>Time</th><th>Actor</th><th>Action</th><th>Decision</th><th>Source ref</th></tr></thead><tbody>{auditRows.map((row) => <tr key={`${row[0]}-${row[2]}`}><td className="meta">{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td><span className="meta">{row[3]}</span></td><td className="meta">{row[4]}</td></tr>)}</tbody></table></div>
    </section>
  );
}

export function ConnectorGrid() {
  const [surface, setSurface] = useState<AdminSurface>("connectors");
  const [connectors, setConnectors] = useState(CONNECTOR_FIXTURES);
  const [syncing, setSyncing] = useState<string | null>(null);

  const startSync = (id: string) => {
    setSyncing(id);
    setConnectors((current) => current.map((connector) => connector.id === id ? { ...connector, state: "pending_recheck" } : connector));
    window.setTimeout(() => {
      setConnectors((current) => current.map((connector) => connector.id === id ? { ...connector, state: "fixture", lastRun: "just now", detail: "Fixture sync · checkpoint complete" } : connector));
      setSyncing(null);
    }, 520);
  };

  return (
    <>
      <AdminHeader surface={surface} onSurfaceChange={setSurface} />
      {surface === "connectors" && <ConnectorsSurface connectors={connectors} onSync={startSync} syncing={syncing} />}
      {surface === "permissions" && <PermissionsSurface />}
      {surface === "unanswered" && <UnansweredSurface />}
      {surface === "evaluation" && <EvaluationSurface />}
      {surface === "audit" && <AuditSurface />}
    </>
  );
}
