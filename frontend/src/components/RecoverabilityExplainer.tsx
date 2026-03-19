import { useMemo, useState } from "react";

type RecoverabilityClassSummary = {
  count?: number;
  amount?: number;
  estimated_recoverable?: number;
};

type RecoverabilityExplainerProps = {
  title?: string;
  recoverableAmount: number;
  expiredAmount: number;
  byClass?: Record<string, RecoverabilityClassSummary>;
  eventDate?: string;
  expirationDate?: string | null;
  discoveryDate?: string;
  claimWindowLabel?: string;
  probabilityNarrative?: string;
  contractClauseCitation?: string;
  compact?: boolean;
};

function money(value: number): string {
  return `$${Number(value || 0).toLocaleString(undefined, { maximumFractionDigits: 2 })}`;
}

function itemAmount(row: RecoverabilityClassSummary | undefined): number {
  if (!row) return 0;
  if (typeof row.amount === "number") return row.amount;
  if (typeof row.estimated_recoverable === "number") return row.estimated_recoverable;
  return 0;
}

export function RecoverabilityExplainer({
  title = "Recoverability Explainer",
  recoverableAmount,
  expiredAmount,
  byClass,
  eventDate,
  expirationDate,
  discoveryDate,
  claimWindowLabel = "Varies by payer/society",
  probabilityNarrative,
  contractClauseCitation,
  compact = false,
}: RecoverabilityExplainerProps): JSX.Element {
  const [showDetails, setShowDetails] = useState(false);

  const timelineItems = useMemo(
    () => [
      { key: "event", label: "Event date", value: eventDate || "Unknown", state: "neutral" },
      { key: "expiration", label: "Expiration date", value: expirationDate || "Contract-governed or unknown", state: expiredAmount > 0 ? "expired" : "active" },
      { key: "discovery", label: "Discovery date", value: discoveryDate || new Date().toISOString().slice(0, 10), state: "active" },
      { key: "claim", label: "Claim window", value: claimWindowLabel, state: recoverableAmount > 0 ? "active" : "neutral" },
    ],
    [eventDate, expirationDate, discoveryDate, claimWindowLabel, expiredAmount, recoverableAmount],
  );

  const topRule = useMemo(() => {
    if (!byClass) return "ASCAP redistributes unmatched royalties after 2-3 years.";
    if (byClass["Expired (Black-Box Redistributed)"]) {
      return "Foreign societies often redistribute unmatched royalties after 6-18 months.";
    }
    return "MLC redistributes unmatched digital mechanicals after 3 years.";
  }, [byClass]);

  const classEntries = Object.entries(byClass || {});

  return (
    <section className={`recoverability-explainer ${compact ? "compact" : ""}`} data-reveal="true">
      <header className="recoverability-head">
        <h3>{title}</h3>
        <button type="button" className="learn-more-btn" onClick={() => setShowDetails(true)}>
          Learn more
        </button>
      </header>

      <div className="recoverability-grid">
        <article className="recoverability-card can-recover" title="Recoverable, contract-based, and copyright-damages classes are actionable.">
          <p className="label">Here is what you can still recover</p>
          <strong>{money(recoverableAmount)}</strong>
          <p>XR7 can still pursue this through claim windows, contract enforcement, or damages pathways.</p>
        </article>

        <article className="recoverability-card expired" title="Expired amounts are generally redistributed by payer/society black-box rules.">
          <p className="label">Here is what expired</p>
          <strong>{money(expiredAmount)}</strong>
          <p>These funds likely crossed redistribution windows and are now prevention signals.</p>
        </article>

        <article className="recoverability-card why" title="Rule logic depends on payer/society and royalty type.">
          <p className="label">Here is why</p>
          <p>{topRule}</p>
          <p>Rule windows are applied to event date, then compared to discovery date.</p>
          {probabilityNarrative && <p>{probabilityNarrative}</p>}
          {contractClauseCitation && <p>Contract clause: {contractClauseCitation}</p>}
        </article>

        <article className="recoverability-card prevention" title="Expired and low-confidence anomalies still improve future recovery outcomes.">
          <p className="label">Here is what XR7 prevents going forward</p>
          <ul>
            <li>Metadata repair</li>
            <li>Identifier normalization</li>
            <li>Cross-system linking</li>
            <li>Future leakage prevention</li>
            <li>UGC fingerprinting</li>
            <li>Foreign society crosswalks</li>
          </ul>
        </article>
      </div>

      <div className="recoverability-timeline" aria-label="Recoverability timeline">
        {timelineItems.map((item) => (
          <div key={item.key} className={`timeline-item ${item.state}`}>
            <span className="dot" />
            <div>
              <p>{item.label}</p>
              <strong>{item.value}</strong>
            </div>
          </div>
        ))}
      </div>

      {classEntries.length > 0 && (
        <div className="recoverability-class-grid">
          {classEntries.map(([key, value]) => (
            <article key={key} className="class-row">
              <span>{key}</span>
              <strong>{money(itemAmount(value))}</strong>
              <small>{Number(value.count || 0)} items</small>
            </article>
          ))}
        </div>
      )}

      {showDetails && (
        <div className="recoverability-modal-backdrop" role="dialog" aria-modal="true" aria-label="Recoverability details">
          <div className="recoverability-modal">
            <h4>Recoverability details</h4>
            <p>
              XR7 classifies anomalies into recoverable, contract-based, expired black-box, copyright damages, and future-prevention classes.
              Claim drafting is enabled only for the legally actionable classes.
            </p>
            <ul>
              <li>ASCAP redistributes unmatched royalties after 2-3 years.</li>
              <li>MLC redistributes unmatched digital mechanicals after 3 years.</li>
              <li>Foreign societies often redistribute after 6-18 months.</li>
              <li>Studio backend and streaming reuse are contract-governed.</li>
            </ul>
            <button type="button" className="learn-more-btn" onClick={() => setShowDetails(false)}>
              Close
            </button>
          </div>
        </div>
      )}
    </section>
  );
}
