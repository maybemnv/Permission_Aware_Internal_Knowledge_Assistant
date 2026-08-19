"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import { StatusBadge } from "./StatusBadge";
import { sourceLabel, type AuditEvent, type ConnectorStatus, type DemoPrincipal, type EvaluationRun, type UnansweredRecord } from "./types";

type AdminSurface = "connectors" | "permissions" | "unanswered" | "evaluation" | "audit";
const surfaces: AdminSurface[] = ["connectors", "permissions", "unanswered", "evaluation", "audit"];

function PrincipalSelector({ principal, onChange }: { principal: DemoPrincipal; onChange: (principal: DemoPrincipal) => void }) {
  return <label className="source-chip">Fixture principal <select aria-label="Fixture principal" value={principal} onChange={(event) => onChange(event.target.value as DemoPrincipal)}><option value="allowed-user">regional employee</option><option value="denied-user">denied employee</option><option value="unmapped-user">unmapped employee</option><option value="changed-group-user">changed-group employee</option><option value="cross-tenant-user">cross-tenant employee</option><option value="admin-user">fixture administrator</option></select></label>;
}

function ConnectorCard({ connector, onSync }: { connector: ConnectorStatus; onSync: (id: string) => void }) {
  return <article className="connector-card"><div className="card-heading"><h3>{sourceLabel(connector.sourceType)}</h3><StatusBadge state={connector.capabilityLabel} /></div><p>{connector.capabilityGaps.join(" · ") || "Fixture connector"}</p><div className="meta">{connector.itemCount} items · {connector.errorCount} errors</div><button className="secondary-button" type="button" onClick={() => onSync(connector.connectorId)}>Start fixture sync</button></article>;
}

export function ConnectorGrid({ initialPrincipal = "allowed-user" }: { initialPrincipal?: DemoPrincipal }) {
  const [principal, setPrincipal] = useState<DemoPrincipal>(initialPrincipal);
  const [surface, setSurface] = useState<AdminSurface>("connectors");
  const [connectors, setConnectors] = useState<ConnectorStatus[]>([]);
  const [unanswered, setUnanswered] = useState<UnansweredRecord[]>([]);
  const [evaluation, setEvaluation] = useState<EvaluationRun | null>(null);
  const [audit, setAudit] = useState<AuditEvent[]>([]);
  const [syncResult, setSyncResult] = useState<string>("");
  const [failed, setFailed] = useState(false);

  const load = useCallback(async () => {
    setFailed(false);
    try {
      if (surface === "connectors") setConnectors(await api.connectors());
      if (surface === "unanswered") setUnanswered(await api.unanswered());
      if (surface === "evaluation") { const runs = await api.evaluations(); setEvaluation(runs.at(-1) ?? null); }
      if (surface === "audit") setAudit(await api.audit());
    } catch { setFailed(true); }
  }, [surface]);
  useEffect(() => { void load(); }, [surface, principal, load]);
  const changePrincipal = async (next: DemoPrincipal) => { setPrincipal(next); await api.setDemoPrincipal(next); };
  const startSync = async (connectorId: string) => { try { const result = await api.sync(connectorId); setSyncResult(`Fixture sync ${result.status}`); await load(); } catch { setFailed(true); } };
  const runEvaluation = async () => { try { setEvaluation(await api.startEvaluation()); } catch { setFailed(true); } };

  return <><header className="topbar"><div className="brand-lockup"><Link className="brand-mark" href="/">Evidence Desk</Link><p className="eyebrow">Admin / governance workbench</p></div><nav className="topnav"><Link className="nav-link" href="/">Workbench</Link><PrincipalSelector principal={principal} onChange={changePrincipal} /></nav></header><div className="page-intro"><div><p className="eyebrow">Operations / fixture mode</p><h1>Make the system legible</h1><p>Returned connector, governance, evaluation, and audit records are server-authorized fixture data.</p></div><StatusBadge state="fixture" /></div><nav className="admin-tabs" aria-label="Admin surfaces" role="tablist">{surfaces.map((item) => <button key={item} className="admin-tab" type="button" role="tab" aria-selected={surface === item} onClick={() => setSurface(item)}>{item[0].toUpperCase() + item.slice(1)}</button>)}</nav>{failed && <section className="state-card" role="alert"><StatusBadge state="failed" /><p>The fixture API is unavailable.</p></section>}{surface === "connectors" && <section className="panel"><div className="panel-heading"><div><p className="eyebrow">Connector status</p><h2>Eight source boundaries</h2></div><button className="secondary-button" type="button" onClick={() => void load()}>Refresh connector status</button></div><div className="connector-grid">{connectors.map((connector) => <ConnectorCard key={connector.connectorId} connector={connector} onSync={(id) => void startSync(id)} />)}</div><p className="meta">{syncResult}</p></section>}{surface === "permissions" && <section className="panel"><h2>Access mappings in plain view</h2><p>Authorization remains on the API boundary; the browser receives no ACL decision input.</p></section>}{surface === "unanswered" && <section className="panel"><h2>Where evidence is thin</h2>{unanswered.length === 0 ? <p className="meta">No redacted unanswered records have been generated.</p> : <ul>{unanswered.map((record) => <li key={record.queryId}><strong>{record.category}</strong> · {record.queryHash.slice(0, 12)} · {record.safeSummary}</li>)}</ul>}</section>}{surface === "evaluation" && <section className="panel"><h2>Evaluation / safety gates</h2><button className="primary-button" type="button" onClick={() => void runEvaluation()}>Run fixture evaluation</button>{evaluation && <div className="metric-grid"><div className="state-card"><span className="data-label">Permission leakage</span><strong>{evaluation.permissionLeaks}</strong></div><div className="state-card"><span className="data-label">Citation coverage</span><strong>{Math.round(evaluation.citationCoverage * 100)}%</strong></div></div>}</section>}{surface === "audit" && <section className="panel"><h2>What the system recorded</h2><div className="table-wrap"><table className="audit-table"><thead><tr><th>Time</th><th>Action</th><th>Reason</th></tr></thead><tbody>{audit.map((event) => <tr key={event.eventId}><td>{event.createdAt}</td><td>{event.eventType}</td><td>{event.reasonCode ?? "authorized"}</td></tr>)}</tbody></table></div></section>}</>;
}
