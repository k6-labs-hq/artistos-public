import React from "react";

import { detectUiLanguage, t } from "@/shared/i18n";

type ErrorBoundaryProps = {
  children: React.ReactNode;
  name: string;
};

type ErrorBoundaryState = {
  hasError: boolean;
};

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false };

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { hasError: true };
  }

  componentDidCatch(error: Error) {
    console.error(`ErrorBoundary(${this.props.name})`, error);
  }

  render() {
    if (this.state.hasError) {
      const language = detectUiLanguage();
      return (
        <section className="panel" role="alert" aria-live="assertive">
          <h2>{t(language, "unavailableTitle", { name: this.props.name })}</h2>
          <p>{t(language, "unavailableBody")}</p>
        </section>
      );
    }

    return this.props.children;
  }
}