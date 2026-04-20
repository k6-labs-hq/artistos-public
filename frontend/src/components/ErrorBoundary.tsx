import { Component, ErrorInfo, ReactNode } from "react";

interface Props {
  name?: string;
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error(`ErrorBoundary [${this.props.name ?? "unnamed"}]`, error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback;
      return (
        <div
          role="alert"
          style={{
            padding: "1.5rem",
            border: "1px solid #fca5a5",
            borderRadius: 8,
            background: "#fef2f2",
            color: "#991b1b",
            margin: "1rem 0",
          }}
        >
          <strong>{this.props.name ?? "Component"} failed to render.</strong>
          <div style={{ marginTop: "0.5rem", fontSize: "0.875rem" }}>
            {this.state.error?.message ?? "Unknown error"}
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
