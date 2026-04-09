/**
 * Characterization tests for src/components/ConfidenceMeter.tsx
 *
 * Covers:
 *  (1) Typical inputs      – values in [0, 1]
 *  (2) Edge cases          – 0, 1, NaN, Infinity, values outside [0, 1]
 *  (3) Error / guard paths – non-finite values clamped or replaced
 *
 * No component code is changed.
 */

import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ConfidenceMeter } from "./ConfidenceMeter";

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

function renderMeter(value: number, label?: string) {
  return render(<ConfidenceMeter value={value} label={label} />);
}

// ---------------------------------------------------------------------------
// (1) Typical inputs
// ---------------------------------------------------------------------------

describe("ConfidenceMeter – typical inputs", () => {
  it("renders without crashing for a mid-range value", () => {
    expect(() => renderMeter(0.75)).not.toThrow();
  });

  it("displays default label 'Confidence' when no label prop", () => {
    renderMeter(0.5);
    expect(screen.getByRole("article")).toHaveAttribute(
      "aria-label",
      expect.stringContaining("Confidence")
    );
  });

  it("renders a custom label", () => {
    renderMeter(0.6, "Recovery Likelihood");
    expect(screen.getByRole("article")).toHaveAttribute(
      "aria-label",
      expect.stringContaining("Recovery Likelihood")
    );
  });

  it("shows 75% for value 0.75", () => {
    renderMeter(0.75);
    expect(screen.getByText("75%")).toBeInTheDocument();
  });

  it("shows 50% for value 0.5", () => {
    renderMeter(0.5);
    expect(screen.getByText("50%")).toBeInTheDocument();
  });

  it("shows 1% for value 0.01", () => {
    renderMeter(0.01);
    expect(screen.getByText("1%")).toBeInTheDocument();
  });

  it("shows 99% for value 0.99", () => {
    renderMeter(0.99);
    expect(screen.getByText("99%")).toBeInTheDocument();
  });

  it("aria-label includes the computed percentage", () => {
    renderMeter(0.8);
    expect(screen.getByRole("article")).toHaveAttribute(
      "aria-label",
      expect.stringContaining("80")
    );
  });
});

// ---------------------------------------------------------------------------
// (2) Edge cases – boundary values
// ---------------------------------------------------------------------------

describe("ConfidenceMeter – edge cases", () => {
  it("shows 0% for value 0", () => {
    renderMeter(0);
    expect(screen.getByText("0%")).toBeInTheDocument();
  });

  it("shows 100% for value 1", () => {
    renderMeter(1);
    expect(screen.getByText("100%")).toBeInTheDocument();
  });

  it("clamps value > 1 to 100%", () => {
    renderMeter(1.5);
    expect(screen.getByText("100%")).toBeInTheDocument();
  });

  it("clamps value < 0 to 0%", () => {
    renderMeter(-0.3);
    expect(screen.getByText("0%")).toBeInTheDocument();
  });
});

// ---------------------------------------------------------------------------
// (3) Error paths – non-finite / bad values coerced to 0
// ---------------------------------------------------------------------------

describe("ConfidenceMeter – error paths", () => {
  it("renders 0% for NaN (non-finite guard)", () => {
    renderMeter(NaN);
    expect(screen.getByText("0%")).toBeInTheDocument();
  });

  it("renders without crashing for NaN", () => {
    expect(() => renderMeter(NaN)).not.toThrow();
  });

  it("renders 0% for Infinity (Number.isFinite guard treats it as 0)", () => {
    // Number.isFinite(Infinity) === false, so the component substitutes 0
    renderMeter(Infinity);
    expect(screen.getByText("0%")).toBeInTheDocument();
  });

  it("renders 0% for -Infinity (clamped from below)", () => {
    renderMeter(-Infinity);
    expect(screen.getByText("0%")).toBeInTheDocument();
  });
});

// ---------------------------------------------------------------------------
// Structural / accessibility
// ---------------------------------------------------------------------------

describe("ConfidenceMeter – structure", () => {
  it("renders an article element", () => {
    renderMeter(0.5);
    expect(screen.getByRole("article")).toBeInTheDocument();
  });

  it("renders an svg inside the article", () => {
    const { container } = renderMeter(0.5);
    expect(container.querySelector("svg")).not.toBeNull();
  });

  it("svg has aria-hidden", () => {
    const { container } = renderMeter(0.5);
    expect(container.querySelector("svg")).toHaveAttribute("aria-hidden", "true");
  });

  it("renders descriptive paragraph text", () => {
    renderMeter(0.5);
    // The paragraph contains the word 'confidence' alongside other words; use a
    // substring match against the exact prose rather than a short regex that also
    // matches the <h3>Confidence</h3> heading.
    expect(
      screen.getByText(/model confidence for current recovery/i)
    ).toBeInTheDocument();
  });
});
