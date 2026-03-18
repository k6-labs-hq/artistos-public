type ConfidenceMeterProps = {
  value: number;
  label?: string;
};

export function ConfidenceMeter({ value, label = "Confidence" }: ConfidenceMeterProps) {
  const normalized = Math.max(0, Math.min(1, Number.isFinite(value) ? value : 0));
  const pct = Math.round(normalized * 100);
  const angle = -90 + 180 * normalized;
  const color = pct >= 75 ? "#10b981" : pct >= 50 ? "#f59e0b" : "#ef4444";

  return (
    <article className="sovereignty-card confidence-meter" aria-label={`${label} ${pct} percent`}>
      <h3>{label}</h3>
      <svg viewBox="0 0 220 140" role="img" aria-hidden="true">
        <path d="M20 110 A90 90 0 0 1 200 110" fill="none" stroke="#334155" strokeWidth="16" strokeLinecap="round" />
        <path
          d="M20 110 A90 90 0 0 1 200 110"
          fill="none"
          stroke={color}
          strokeWidth="16"
          strokeLinecap="round"
          strokeDasharray={`${Math.PI * 90 * normalized} ${Math.PI * 90}`}
        />
        <line
          x1="110"
          y1="110"
          x2={110 + 72 * Math.cos((Math.PI * angle) / 180)}
          y2={110 + 72 * Math.sin((Math.PI * angle) / 180)}
          stroke={color}
          strokeWidth="6"
          strokeLinecap="round"
        />
        <circle cx="110" cy="110" r="8" fill={color} />
        <text x="110" y="96" textAnchor="middle" fill="#e2e8f0" fontSize="30" fontWeight="800">
          {pct}%
        </text>
      </svg>
      <p>Model confidence for current recovery prioritization and payout likelihood.</p>
    </article>
  );
}
