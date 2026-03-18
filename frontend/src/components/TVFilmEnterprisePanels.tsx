import React from "react";

const componentNames = [
  "Production Timeline Viewer",
  "Episode/Season Tree",
  "Residuals Waterfall Chart",
  "Distribution Window Map",
  "Syndication Heatmap",
  "Streaming Reuse Tracker",
  "Payroll Audit Breakdown",
  "Stunt Adjustment Calculator",
  "Backend Participation Forecast",
  "Agency Portfolio Dashboard",
  "Agency Recovery Pipeline",
  "Agency SOL Risk Map",
];

export function TVFilmEnterprisePanels(): JSX.Element {
  return (
    <section className="tvfilm-enterprise-panels" data-reveal="true" aria-label="TV and Film enterprise dashboard modules">
      <div className="section-head">
        <h2>TV/Film Enterprise Modules</h2>
        <p>Portfolio-scale views for agencies, management firms, production companies, and legal operations.</p>
      </div>
      <div className="feature-grid">
        {componentNames.map((name) => (
          <article className="feature-card" key={name}>
            <h3>{name}</h3>
            <p>Production-ready XR7 panel with role-aware filtering, evidence traceability, and bulk action support.</p>
          </article>
        ))}
      </div>
    </section>
  );
}
