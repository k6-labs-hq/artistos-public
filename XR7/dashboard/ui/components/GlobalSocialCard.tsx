type Opportunity = {
  platform: string;
  territory: string;
  estimated_recoverable: number;
  confidence: number;
};

type GlobalSocialCardProps = {
  opportunities: Opportunity[];
};

export function GlobalSocialCard({ opportunities }: GlobalSocialCardProps) {
  return (
    <section
      style={{
        border: "1px solid rgba(17,24,39,0.15)",
        borderRadius: "14px",
        padding: "12px",
        background: "rgba(255,255,255,0.85)",
      }}
    >
      <h3 style={{ margin: "0 0 8px", fontSize: "1rem" }}>Global Social Opportunities</h3>
      {opportunities.length === 0 ? (
        <p style={{ margin: 0, opacity: 0.8 }}>No opportunities detected yet.</p>
      ) : (
        <ul style={{ margin: 0, paddingLeft: "18px", display: "grid", gap: "6px" }}>
          {opportunities.map((row, index) => (
            <li key={`${row.platform}-${row.territory}-${index}`}>
              <strong>{row.platform}</strong> in {row.territory}: ${row.estimated_recoverable.toFixed(2)}
              {" "}(confidence {row.confidence.toFixed(2)})
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
