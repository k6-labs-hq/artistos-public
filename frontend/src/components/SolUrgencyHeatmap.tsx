type SolCell = {
  label: string;
  value: number;
};

type SolUrgencyHeatmapProps = {
  cells: SolCell[];
};

function tone(value: number): string {
  if (value >= 8) return "#ef4444";
  if (value >= 4) return "#f97316";
  if (value >= 2) return "#f59e0b";
  return "#22c55e";
}

export function SolUrgencyHeatmap({ cells }: SolUrgencyHeatmapProps) {
  const items = cells.length ? cells : [
    { label: "US", value: 1 },
    { label: "UK", value: 0 },
    { label: "DE", value: 2 },
    { label: "FR", value: 1 },
  ];

  return (
    <article className="sovereignty-card sol-heatmap">
      <h3>SOL Urgency Heatmap</h3>
      <div className="sol-grid">
        {items.map((cell) => (
          <div key={cell.label} className="sol-cell" style={{ background: tone(cell.value) }}>
            <strong>{cell.label}</strong>
            <span>{cell.value}</span>
          </div>
        ))}
      </div>
      <p>Higher intensity indicates more claims nearing statute-of-limitations deadlines.</p>
    </article>
  );
}
