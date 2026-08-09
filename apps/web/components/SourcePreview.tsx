import { StatusBadge } from "./StatusBadge";
import type { SourcePreviewData } from "./types";
import { sourceLabel } from "./types";

interface SourcePreviewProps {
  preview: SourcePreviewData | null;
  onClose: () => void;
}

export function SourcePreview({ preview, onClose }: SourcePreviewProps) {
  return (
    <aside className="panel preview" role="dialog" aria-modal="false" aria-labelledby="preview-heading">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">Source preview</p>
          <h2 id="preview-heading">Verify the evidence</h2>
        </div>
        <button className="text-button" type="button" onClick={onClose} aria-label="Close source preview">Close</button>
      </div>

      {!preview ? (
        <div className="empty-state">
          <StatusBadge state="unavailable" />
          <p>No source is selected. Choose a citation to request a fresh permission check.</p>
        </div>
      ) : (
        <>
          <div className="card-heading">
            <div>
              <h3>{preview.title}</h3>
              <p className="meta">{sourceLabel(preview.sourceType)} · {preview.locator}</p>
            </div>
            <StatusBadge state={preview.lifecycleState} />
          </div>
          <p className="preview-excerpt">{preview.excerpt}</p>
          <dl className="metric-list">
            <div><dt className="data-label">Request check</dt><dd><StatusBadge state={preview.recheckState} /></dd></div>
            <div><dt className="data-label">Updated</dt><dd className="meta">{preview.updatedAt}</dd></div>
            <div><dt className="data-label">Indexed</dt><dd className="meta">{preview.indexedAt}</dd></div>
          </dl>
          <div className="result-actions">
            <span className="meta">{preview.itemId}</span>
            <a className="text-button" href={preview.deepLink} target="_blank" rel="noreferrer">Open source ↗</a>
          </div>
        </>
      )}
    </aside>
  );
}
