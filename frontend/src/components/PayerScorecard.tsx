type PayerRow = {
  payer: string;
  responsiveness: number;
  resistance: number;
};

type PayerScorecardProps = {
  rows: PayerRow[];
};

function asPct(v: number): string {
  return `${Math.round(Math.max(0, Math.min(1, v)) * 100)}%`;
}

export function PayerScorecard({ rows }: PayerScorecardProps) {
  const items = rows.length
    ? rows
    : [
        { payer: "ASCAP", responsiveness: 0.72, resistance: 0.28 },
        { payer: "Distributor", responsiveness: 0.43, resistance: 0.57 },
        { payer: "Platform", responsiveness: 0.61, resistance: 0.39 },
      ];

  return (
    <article className="sovereignty-card payer-scorecard">
      <h3>Payer Scorecard</h3>
      <table>
        <thead>
          <tr>
            <th>Payer</th>
            <th>Responsiveness</th>
            <th>Resistance</th>
          </tr>
        </thead>
        <tbody>
          {items.map((row) => (
            <tr key={row.payer}>
              <td>{row.payer}</td>
              <td>{asPct(row.responsiveness)}</td>
              <td>{asPct(row.resistance)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </article>
  );
}
