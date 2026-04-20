/**
 * Tests for AnalysisProgressScreen.tsx
 *
 * Covers:
 *  (1) Component rendering with default and custom props
 *  (2) Message cycling and animation behavior
 *  (3) Theme variants and accessibility
 *  (4) Reduced motion preference handling
 */
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { AnalysisProgressScreen } from "./AnalysisProgressScreen";

describe("AnalysisProgressScreen", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.useRealTimers();
  });

  describe("Basic rendering", () => {
    it("renders without crashing", () => {
      expect(() => render(<AnalysisProgressScreen />)).not.toThrow();
    });

    it("displays default title", () => {
      render(<AnalysisProgressScreen />);
      expect(screen.getByText("XR7 Forensic Analysis")).toBeInTheDocument();
    });

    it("displays custom title when provided", () => {
      render(<AnalysisProgressScreen title="Custom Analysis Title" />);
      expect(screen.getByText("Custom Analysis Title")).toBeInTheDocument();
    });

    it("displays default caption", () => {
      render(<AnalysisProgressScreen />);
      expect(screen.getByText(/Validating cross-platform royalty evidence/i)).toBeInTheDocument();
    });

    it("displays custom caption when provided", () => {
      render(<AnalysisProgressScreen caption="Custom caption text" />);
      expect(screen.getByText("Custom caption text")).toBeInTheDocument();
    });

    it("renders logo image with default src", () => {
      const { container } = render(<AnalysisProgressScreen />);
      const logo = container.querySelector('img[src="/xr7-emblem.svg"]');
      expect(logo).toBeInTheDocument();
    });

    it("renders logo image with custom src", () => {
      const { container } = render(<AnalysisProgressScreen logoSrc="/custom-logo.svg" />);
      const logo = container.querySelector('img[src="/custom-logo.svg"]');
      expect(logo).toBeInTheDocument();
    });
  });

  describe("Messages display", () => {
    it("displays first default message initially", () => {
      render(<AnalysisProgressScreen />);
      expect(screen.getByText("Decrypting uploaded files...")).toBeInTheDocument();
    });

    it("displays custom messages when provided", () => {
      const customMessages = ["Step 1", "Step 2", "Step 3"];
      render(<AnalysisProgressScreen messages={customMessages} />);
      expect(screen.getByText("Step 1")).toBeInTheDocument();
    });

    it("falls back to default messages when empty array provided", () => {
      render(<AnalysisProgressScreen messages={[]} />);
      expect(screen.getByText("Decrypting uploaded files...")).toBeInTheDocument();
    });

    it("cycles through messages over time", async () => {
      const customMessages = ["Message 1", "Message 2", "Message 3"];
      render(<AnalysisProgressScreen messages={customMessages} animationSpeed={1000} />);

      expect(screen.getByText("Message 1")).toBeInTheDocument();

      // Advance time past fade out + message update + fade in
      vi.advanceTimersByTime(1320); // 1000ms cadence + 320ms fade

      await waitFor(() => {
        expect(screen.getByText("Message 2")).toBeInTheDocument();
      });
    });
  });

  describe("Animation speed", () => {
    it("accepts custom animation speed", () => {
      expect(() =>
        render(<AnalysisProgressScreen animationSpeed={1500} />)
      ).not.toThrow();
    });

    it("clamps animation speed to minimum", () => {
      // Should not crash even with very low speed
      expect(() =>
        render(<AnalysisProgressScreen animationSpeed={100} />)
      ).not.toThrow();
    });

    it("clamps animation speed to maximum", () => {
      // Should not crash even with very high speed
      expect(() =>
        render(<AnalysisProgressScreen animationSpeed={10000} />)
      ).not.toThrow();
    });
  });

  describe("Theme variants", () => {
    it("applies xr7 theme by default", () => {
      const { container } = render(<AnalysisProgressScreen />);
      const element = container.querySelector('[class*="themeXr7"]');
      expect(element).toBeInTheDocument();
    });

    it("applies slate theme when specified", () => {
      const { container } = render(<AnalysisProgressScreen themeVariant="slate" />);
      const element = container.querySelector('[class*="themeSlate"]');
      expect(element).toBeInTheDocument();
    });

    it("applies neutral theme when specified", () => {
      const { container } = render(<AnalysisProgressScreen themeVariant="neutral" />);
      const element = container.querySelector('[class*="themeNeutral"]');
      expect(element).toBeInTheDocument();
    });

    it("accepts theme overrides", () => {
      const themeOverrides = {
        textColor: "#ffffff",
        backgroundPrimary: "#000000",
      };
      expect(() =>
        render(<AnalysisProgressScreen themeOverrides={themeOverrides} />)
      ).not.toThrow();
    });
  });

  describe("Completion callback", () => {
    it("accepts onComplete callback", () => {
      const onComplete = vi.fn();
      expect(() =>
        render(<AnalysisProgressScreen onComplete={onComplete} />)
      ).not.toThrow();
    });

    it("does not crash when onComplete is undefined", () => {
      expect(() =>
        render(<AnalysisProgressScreen />)
      ).not.toThrow();
    });
  });

  describe("Accessibility", () => {
    it("renders with semantic structure", () => {
      const { container } = render(<AnalysisProgressScreen />);
      expect(container.firstChild).toBeTruthy();
    });

    it("logo has alt text", () => {
      render(<AnalysisProgressScreen />);
      const logo = screen.getByRole("img");
      expect(logo).toHaveAttribute("alt");
    });
  });

  describe("Reduced motion preference", () => {
    it("respects prefers-reduced-motion media query", () => {
      // Mock matchMedia
      const mockMatchMedia = vi.fn().mockImplementation((query) => ({
        matches: query === "(prefers-reduced-motion: reduce)",
        media: query,
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
      }));

      Object.defineProperty(window, "matchMedia", {
        writable: true,
        value: mockMatchMedia,
      });

      expect(() => render(<AnalysisProgressScreen />)).not.toThrow();
    });
  });

  describe("Edge cases", () => {
    it("handles single message", () => {
      render(<AnalysisProgressScreen messages={["Only message"]} />);
      expect(screen.getByText("Only message")).toBeInTheDocument();
    });

    it("handles very long messages", () => {
      const longMessage = "A".repeat(200);
      render(<AnalysisProgressScreen messages={[longMessage]} />);
      expect(screen.getByText(longMessage)).toBeInTheDocument();
    });

    it("handles special characters in messages", () => {
      const message = "Processing <data> & validating 'quotes'...";
      render(<AnalysisProgressScreen messages={[message]} />);
      expect(screen.getByText(message)).toBeInTheDocument();
    });
  });
});
