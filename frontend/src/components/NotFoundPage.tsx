export function NotFoundPage() {
  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "2rem",
        textAlign: "center",
        background: "var(--bg-primary, #0F172A)",
        color: "var(--text-primary, #F8FAFC)",
      }}
    >
      <h1
        style={{
          fontSize: "6rem",
          fontWeight: "bold",
          margin: "0 0 1rem",
          background: "linear-gradient(135deg, #6520BD, #A855F7, #D6B1FF)",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
          backgroundClip: "text",
        }}
      >
        404
      </h1>
      <h2
        style={{
          fontSize: "1.5rem",
          fontWeight: "600",
          margin: "0 0 1rem",
        }}
      >
        Page Not Found
      </h2>
      <p
        style={{
          fontSize: "1rem",
          maxWidth: "480px",
          margin: "0 0 2rem",
          opacity: 0.8,
        }}
      >
        The page you're looking for doesn't exist or has been moved. Return to the homepage to continue exploring XR7.
      </p>
      <a
        href="/"
        style={{
          display: "inline-block",
          padding: "0.75rem 1.5rem",
          fontSize: "1rem",
          fontWeight: "600",
          color: "#F8FAFC",
          background: "linear-gradient(135deg, #6520BD, #A855F7)",
          border: "none",
          borderRadius: "0.5rem",
          textDecoration: "none",
          cursor: "pointer",
          transition: "transform 0.2s, box-shadow 0.2s",
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = "translateY(-2px)";
          e.currentTarget.style.boxShadow = "0 8px 16px rgba(101, 32, 189, 0.4)";
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = "translateY(0)";
          e.currentTarget.style.boxShadow = "none";
        }}
      >
        Return to Homepage
      </a>
    </div>
  );
}
