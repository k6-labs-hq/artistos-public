type WaterfallStep = {
  label: string;
  amount: number;
};

type RecoverableWaterfallChartProps = {
  steps: WaterfallStep[];
};

export function RecoverableWaterfallChart({ steps }: RecoverableWaterfallChartProps) {
  const items = steps.length
    ? steps
    : [
        { label: "Detected", amount: 120000 },
        { label: "Disputed", amount: -28000 },
        { label: "Accepted", amount: 76000 },
        { label: "Paid", amount: -19000 },
      ];

  const max = Math.max(...items.map((s) => Math.abs(s.amount)), 1);

  return (
    <article className="sovereignty-card waterfall">
      <h3>Recoverable Waterfall</h3>
      <ul>
        {items.map((step) => {
          const width = Math.max(8, Math.round((Math.abs(step.amount) / max) * 100));
          const positive = step.amount >= 0;
          return (
            <li key={step.label}>
              <span>{step.label}</span>
              <div className="bar-wrap">
                <div className={`bar ${positive ? "positive" : "negative"}`} style={{ width: `${width}%` }} />
              </div>
              <strong>{positive ? "+" : "-"}${Math.abs(step.amount).toLocaleString()}</strong>
            </li>
          );
        })}
      </ul>
    </article>
  );
}
