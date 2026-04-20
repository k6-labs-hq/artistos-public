export function NotFoundPage() {
  return (
    <main className="xr7-app" id="main-content">
      <section className="hero" data-reveal="true">
        <div className="hero-bg" aria-hidden="true" />
        <p className="eyebrow">XR7 Routing</p>
        <h1>404 - Page Not Found</h1>
        <p className="hero-copy">
          The page you requested does not exist or may have moved.
        </p>
        <div className="hero-actions">
          <a className="cta large pulse" href="/">
            Go To Dashboard
          </a>
        </div>
      </section>
    </main>
  );
}
