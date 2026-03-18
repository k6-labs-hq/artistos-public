import { useMemo, useState } from "react";

const roleOptions = [
  "Writer (TV/Film)",
  "Screenwriter",
  "Showrunner",
  "Director",
  "Producer",
  "Actor",
  "Voice Actor",
  "Stunt Performer",
  "Editor",
  "Cinematographer",
  "Composer",
  "VFX Artist",
  "Animator",
  "Crew (Grip, Gaffer, PA, etc.)",
  "Reality TV Participant",
  "Documentary Creator",
  "Talent Agency",
  "Management Company",
  "Law Firm",
  "Production Company",
];

const trustEvents = [
  "Matching episode-season hierarchies against statement rows",
  "Applying union and studio compensation rules",
  "Scoring SOL risk across productions and territories",
  "Preparing evidence-backed claim packets and forecasts",
];

const dashboardRows = [
  ["Residuals Discovered", "$486,000", "21 productions", "SAG-AFTRA / WGA"],
  ["Production Payments", "$72,400", "Overtime + penalties", "IATSE / Crew"],
  ["Distribution & Licensing", "$214,300", "Syndication + FAST", "Studios / Streamers"],
  ["Streaming Reuse", "$180,200", "14 window mismatches", "Netflix / Hulu / Max"],
  ["UGC & Clips", "$39,800", "92 clip detections", "YouTube / TikTok / IG"],
  ["Backend Participation", "$96,000", "5 participation gaps", "Studio backend"],
];

export function TVFilmWorkspace(): JSX.Element {
  const [selectedRole, setSelectedRole] = useState<string>(roleOptions[5] ?? "Actor");
  const [agencyMode, setAgencyMode] = useState<boolean>(false);
  const [rosterCount, setRosterCount] = useState<number>(480);

  const roleExplanation = useMemo(() => {
    if (selectedRole === "Talent Agency") {
      return "Run portfolio-wide historical analyses across multiple unions, roles, productions, and studios with bulk claim drafting and SOL risk mapping.";
    }
    if (selectedRole === "Stunt Performer") {
      return "XR7 prioritizes stunt adjustments, turnaround penalties, hazard premiums, and reuse category mismatches for stunt-heavy productions.";
    }
    if (selectedRole === "Writer (TV/Film)" || selectedRole === "Screenwriter" || selectedRole === "Showrunner") {
      return "XR7 focuses on residual windows, credited episode counts, backend participation, and foreign residual lag factors.";
    }
    return "XR7 maps every compensation line to role, market, production, and reuse window so missing payments can be explained in plain language before claim filing.";
  }, [selectedRole]);

  return (
    <section className="tvfilm-workspace" data-reveal="true">
      <div className="section-head">
        <h2>TV/Film Onboarding and Enterprise Workspace</h2>
        <p>Role-specific onboarding, live trust messaging, and agency-scale portfolio operations in one surface.</p>
      </div>

      <div className="tvfilm-grid">
        <article className="tvfilm-card onboarding-card">
          <p className="eyebrow small">Which role best describes you?</p>
          <label className="stacked-field">
            <span>Role</span>
            <select value={selectedRole} onChange={(event) => setSelectedRole(event.target.value)}>
              {roleOptions.map((role) => (
                <option key={role} value={role}>
                  {role}
                </option>
              ))}
            </select>
          </label>
          <label className="toggle-row">
            <input type="checkbox" checked={agencyMode} onChange={(event) => setAgencyMode(event.target.checked)} />
            <span>Enable enterprise agency mode</span>
          </label>
          <p className="support-copy">{roleExplanation}</p>
          <div className="chip-row">
            <span>{agencyMode ? "Portfolio Mode" : "Individual Mode"}</span>
            <span>{selectedRole}</span>
          </div>
        </article>

        <article className="tvfilm-card roster-card">
          <div className="card-head">
            <h3>Agency Roster Intake</h3>
            <span className="chip teal">CSV / XLSX / API</span>
          </div>
          <p>Upload 100s to 10,000+ clients across unions, productions, and platforms.</p>
          <label className="stacked-field">
            <span>Roster Size</span>
            <input type="range" min="100" max="10000" step="100" value={rosterCount} onChange={(event) => setRosterCount(Number(event.target.value))} />
          </label>
          <div className="roster-meter">
            <strong>{rosterCount.toLocaleString()} clients</strong>
            <p>Bulk metadata repair, bulk forecasting, and bulk evidence generation are ready for this roster.</p>
          </div>
          <div className="mini-metrics">
            <div>
              <span>Total Missing</span>
              <strong>${(rosterCount * 1280).toLocaleString()}</strong>
            </div>
            <div>
              <span>High SOL Risk</span>
              <strong>{Math.max(12, Math.round(rosterCount * 0.09))}</strong>
            </div>
            <div>
              <span>Union Coverage</span>
              <strong>5 unions</strong>
            </div>
          </div>
        </article>

        <article className="tvfilm-card trust-card">
          <div className="card-head">
            <h3>What XR7 Is Doing Now</h3>
            <span className={`signal-dot ${agencyMode ? "live" : "idle"}`} />
          </div>
          <ul className="trust-feed">
            {trustEvents.map((event, index) => (
              <li key={event} style={{ animationDelay: `${index * 0.08}s` }}>
                {event}
              </li>
            ))}
          </ul>
          <p className="support-copy">
            {agencyMode
              ? "Agency mode is aggregating roster-wide role, union, and platform deltas into a single recovery pipeline."
              : `XR7 is preparing a ${selectedRole} explanation layer before any legal step is taken.`}
          </p>
        </article>
      </div>

      <div className="tvfilm-dashboard-table">
        <div className="card-head">
          <h3>TV/Film Dashboard Sections</h3>
          <span className="chip success">Market-ready surface</span>
        </div>
        <table>
          <caption>Role-aware recovery dashboard</caption>
          <thead>
            <tr>
              <th>Section</th>
              <th>Value</th>
              <th>Signal</th>
              <th>Primary Lens</th>
            </tr>
          </thead>
          <tbody>
            {dashboardRows.map((row) => (
              <tr key={row[0]}>
                <td>{row[0]}</td>
                <td>{row[1]}</td>
                <td>{row[2]}</td>
                <td>{row[3]}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
