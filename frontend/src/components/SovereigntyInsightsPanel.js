import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { ConfidenceMeter } from "./ConfidenceMeter";
import { SolUrgencyHeatmap } from "./SolUrgencyHeatmap";
import { RecoverableWaterfallChart } from "./RecoverableWaterfallChart";
import { PayerScorecard } from "./PayerScorecard";
export function SovereigntyInsightsPanel({ confidence, solCells, waterfall, payerRows, }) {
    return (_jsxs("section", { className: "sovereignty-grid", "aria-label": "Sovereignty analytics", children: [_jsx(ConfidenceMeter, { value: confidence }), _jsx(SolUrgencyHeatmap, { cells: solCells }), _jsx(RecoverableWaterfallChart, { steps: waterfall }), _jsx(PayerScorecard, { rows: payerRows })] }));
}
