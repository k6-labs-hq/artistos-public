import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useMemo, useState } from "react";
import { RecoverabilityExplainer } from "./RecoverabilityExplainer";
export function AnomalyDetailPage({ anomalyId }) {
    const apiBase = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [anomaly, setAnomaly] = useState(null);
    const [explain, setExplain] = useState(null);
    useEffect(() => {
        let mounted = true;
        async function run() {
            try {
                const anomalyResp = await fetch(`${apiBase}/anomalies/${anomalyId}`);
                if (!anomalyResp.ok) {
                    throw new Error(`Failed to load anomaly ${anomalyId}`);
                }
                const anomalyData = (await anomalyResp.json());
                let explainData = null;
                if (anomalyData.artist_id) {
                    const explainResp = await fetch(`${apiBase}/artists/${anomalyData.artist_id}/anomalies/${anomalyId}/explain`);
                    if (explainResp.ok) {
                        explainData = (await explainResp.json());
                    }
                }
                if (!mounted)
                    return;
                setAnomaly(anomalyData);
                setExplain(explainData);
            }
            catch (err) {
                if (!mounted)
                    return;
                setError(String(err));
            }
            finally {
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
        if (!cls)
            return {};
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
        return (_jsx("section", { className: "anomaly-detail-page", children: _jsx("p", { children: "Loading anomaly detail..." }) }));
    }
    if (error || !anomaly) {
        return (_jsxs("section", { className: "anomaly-detail-page", children: [_jsx("h2", { children: "Anomaly Detail" }), _jsxs("p", { children: ["Unable to load anomaly: ", error || anomalyId] })] }));
    }
    return (_jsxs("section", { className: "anomaly-detail-page", "data-reveal": "true", children: [_jsxs("header", { className: "section-head", children: [_jsx("h2", { children: "Anomaly Detail" }), _jsxs("p", { children: [anomaly.category, " / ", anomaly.subtype, " \u00B7 Severity ", anomaly.severity] })] }), _jsxs("div", { className: "anomaly-detail-kpis", children: [_jsxs("article", { children: [_jsx("span", { children: "Anomaly ID" }), _jsx("strong", { children: anomaly.id })] }), _jsxs("article", { children: [_jsx("span", { children: "Artist ID" }), _jsx("strong", { children: anomaly.artist_id })] }), _jsxs("article", { children: [_jsx("span", { children: "Estimated Recoverable" }), _jsxs("strong", { children: ["$", amount.toLocaleString(undefined, { maximumFractionDigits: 2 })] })] })] }), _jsx(RecoverabilityExplainer, { title: "Anomaly Recoverability", recoverableAmount: recoverableAmount, expiredAmount: expiredAmount, byClass: byClass, eventDate: anomaly.created_at, expirationDate: explain?.black_box_expiration?.expiration_date || null, discoveryDate: new Date().toISOString().slice(0, 10), claimWindowLabel: "Derived from society window + contract/damages pathways" }), _jsx("div", { className: "anomaly-detail-actions", children: _jsx("a", { href: "/", className: "ghost large", children: "Back to XR7 Home" }) })] }));
}
