import { useEffect, useMemo, useState } from "react";

import type { Anomaly, RecoverabilityResult } from "@/shared/types";
import { RecoverabilityExplainer } from "./RecoverabilityExplainer";

type AnomalyDetailPageProps = {
  anomalyId: string;
};

export function AnomalyDetailPage({ anomalyId }: AnomalyDetailPageProps): JSX.Element {
  const apiBase = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [anomaly, setAnomaly] = useState<Anomaly | null>(null);
  const [explain, setExplain] = useState<RecoverabilityResult | null>(null);

  useEffect(() => {
    let mounted = true;

    async function run() {
      try {
        const anomalyResp = await fetch(`${apiBase}/anomalies/${anomalyId}`);
        if (!anomalyResp.ok) {
          throw new Error(`Failed to load anomaly ${anomalyId}`);
        }
        const anomalyData = (await anomalyResp.json()) as Anomaly;

        let explainData: RecoverabilityResult | null = null;
        if (anomalyData.artist_id) {
          const explainResp = await fetch(`${apiBase}/artists/${anomalyData.artist_id}/anomalies/${anomalyId}/explain`);
          if (explainResp.ok) {
            explainData = (await explainResp.json()) as RecoverabilityResult;
          }
        }

        if (!mounted) return;
        setAnomaly(anomalyData);
        setExplain(explainData);
      } catch (err) {
        if (!mounted) return;
        setError(String(err));
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    run();
    return () => {
      mounted = false;
    };
  }, [anomalyId, apiBase]);

  const byClass = useMemo(() => {
    const cls = explain?.recoverability?.recoverability_class;
    const amount = Number(anomaly?.estimated_recoverable || 0);
    if (!cls) return {};
    return {
      [cls]: {
        count: 1,
        amount,
      },
    };
  }, [explain, anomaly]);

  const recoverabilityClass = explain?.recoverability?.recoverability_class || "Recoverable";
  const amount = Number(anomaly?.estimated_recoverable || 0);
  const expiredAmount = recoverabilityClass === "Expired (Black-Box Redistributed)" ? amount : 0;
  const recoverableAmount = expiredAmount > 0 ? 0 : amount;

  if (loading) {
    return (
      <section className="anomaly-detail-page">
        <p>Loading anomaly detail...</p>
      </section>
    );
  }

  if (error || !anomaly) {
    return (
      <section className="anomaly-detail-page">
        <h2>Anomaly Detail</h2>
        <p>Unable to load anomaly: {error || anomalyId}</p>
      </section>
    );
  }

  return (
    <section className="anomaly-detail-page" data-reveal="true">
      <header className="section-head">
        <h2>Anomaly Detail</h2>
        <p>
          {anomaly.category} / {anomaly.subtype} · Severity {anomaly.severity}
        </p>
      </header>

      <div className="anomaly-detail-kpis">
        <article>
          <span>Anomaly ID</span>
          <strong>{anomaly.id}</strong>
        </article>
        <article>
          <span>Artist ID</span>
          <strong>{anomaly.artist_id}</strong>
        </article>
        <article>
          <span>Estimated Recoverable</span>
          <strong>${amount.toLocaleString(undefined, { maximumFractionDigits: 2 })}</strong>
        </article>
      </div>

      <RecoverabilityExplainer
        title="Anomaly Recoverability"
        recoverableAmount={recoverableAmount}
        expiredAmount={expiredAmount}
        byClass={byClass}
        eventDate={anomaly.created_at}
        expirationDate={explain?.black_box_expiration?.expiration_date || null}
        discoveryDate={new Date().toISOString().slice(0, 10)}
        claimWindowLabel="Derived from society window + contract/damages pathways"
      />

      <div className="anomaly-detail-actions">
        <a href="/" className="ghost large">
          Back to XR7 Home
        </a>
      </div>
    </section>
  );
}
