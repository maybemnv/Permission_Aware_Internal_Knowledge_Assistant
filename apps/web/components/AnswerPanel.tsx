import { StatusBadge } from "./StatusBadge";
import type { AnswerResponse, Citation } from "./types";
import { sourceLabel } from "./types";

interface AnswerPanelProps {
  answer: AnswerResponse;
  onOpenCitation: (citation: Citation) => void;
}

export function AnswerPanel({ answer, onOpenCitation }: AnswerPanelProps) {
  return (
    <section className="panel answer-panel" aria-labelledby="answer-heading">
      <div className="answer-heading">
        <div>
          <p className="eyebrow">Answer / evidence check</p>
          <h2 id="answer-heading">A cited answer, with its limits</h2>
        </div>
        <StatusBadge state={answer.status} />
      </div>

      {answer.status !== "answered" ? (
        <div className="state-card" role="alert">
          <p className="data-label">Safe answer state</p>
          <p>{answer.status === "insufficient_context" ? "There is not enough authorized evidence to answer this question." : "The answer is not available from the current authorized context."}</p>
          <button className="secondary-button" type="button">Retry from current sources</button>
        </div>
      ) : (
        <>
          <p className="answer-copy">{answer.text}</p>
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Provenance first</p>
              <h3>Supporting citations</h3>
            </div>
            <span className="meta">Generated {answer.generatedAt}</span>
          </div>
          <ol className="citation-list" aria-label="Answer citations">
            {answer.citations.map((citation, index) => (
              <li key={citation.citationId}>
                <button className="citation-button" type="button" onClick={() => onOpenCitation(citation)}>
                  <span className="citation-marker" aria-hidden="true">{index + 1}</span>
                  <span>
                    <strong>{citation.title}</strong>
                    <small>{sourceLabel(citation.sourceType)} · {citation.locator}</small>
                  </span>
                  <span className="meta">Open preview →</span>
                </button>
              </li>
            ))}
          </ol>
          <div className="chip-row" aria-label="Answer freshness and caveats">
            <StatusBadge state={answer.freshness} />
            {answer.caveats.map((caveat) => <span className="source-chip" key={caveat}>{caveat}</span>)}
          </div>
          <div className="feedback-row" aria-label="Answer feedback">
            <span className="meta">Was this evidence useful?</span>
            <button className="secondary-button" type="button">Yes, grounded</button>
            <button className="secondary-button" type="button">Report a gap</button>
          </div>
        </>
      )}
    </section>
  );
}
