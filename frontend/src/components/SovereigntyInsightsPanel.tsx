import { ConfidenceMeter } from "./ConfidenceMeter";
import { SolUrgencyHeatmap } from "./SolUrgencyHeatmap";
import { RecoverableWaterfallChart } from "./RecoverableWaterfallChart";
import { PayerScorecard } from "./PayerScorecard";

type SovereigntyInsightsPanelProps = {
  confidence: number;
  solCells: Array<{ label: string; value: number }>;
  waterfall: Array<{ label: string; amount: number }>;
  payerRows: Array<{ payer: string; responsiveness: number; resistance: number }>;
};

export function SovereigntyInsightsPanel({
  confidence,
  solCells,
  waterfall,
  payerRows,
}: SovereigntyInsightsPanelProps) {
  return (
    <section className="sovereignty-grid" aria-label="Sovereignty analytics">
      <ConfidenceMeter value={confidence} />
      <SolUrgencyHeatmap cells={solCells} />
      <RecoverableWaterfallChart steps={waterfall} />
      <PayerScorecard rows={payerRows} />
    </section>
  );
}
