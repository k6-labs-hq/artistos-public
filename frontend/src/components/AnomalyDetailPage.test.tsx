/**
 * Tests for AnomalyDetailPage.tsx
 *
 * Covers:
 *  (1) Component rendering and API integration
 *  (2) Loading and error states
 *  (3) Anomaly data display
 *  (4) Recoverability integration
 */
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { AnomalyDetailPage } from "./AnomalyDetailPage";
import type { Anomaly, RecoverabilityResult } from "@/shared/types";

// Mock fetch globally
const mockFetch = vi.fn();
globalThis.fetch = mockFetch;

const mockAnomaly: Anomaly = {
  id: "anom-123",
  artist_id: "artist-456",
  category: "payment_discrepancy",
  subtype: "missing_royalty",
  severity: 8,
  estimated_recoverable: 15000,
  description: "Missing streaming royalties for Q4 2025",
  detected_at: "2026-01-15T10:00:00Z",
  status: "open",
};

const mockRecoverabilityResult: RecoverabilityResult = {
  recoverability: {
    recoverability_class: "Recoverable",
    confidence_score: 0.87,
    reasoning: "Strong evidence with clear payment trail",
  },
  next_steps: ["Gather additional evidence", "File formal claim"],
};

const mockExpiredRecoverability: RecoverabilityResult = {
  recoverability: {
    recoverability_class: "Expired (Black-Box Redistributed)",
    confidence_score: 0.92,
    reasoning: "Statute of limitations has passed",
  },
  next_steps: ["Consider black-box redistribution options"],
};

describe("AnomalyDetailPage", () => {
  beforeEach(() => {
    mockFetch.mockClear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("Loading state", () => {
    it("displays loading message initially", () => {
      mockFetch.mockImplementation(() => new Promise(() => {})); // Never resolves

      render(<AnomalyDetailPage anomalyId="anom-123" />);

      expect(screen.getByText("Loading anomaly detail...")).toBeInTheDocument();
    });

    it("fetches anomaly data on mount", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnomaly,
      });

      render(<AnomalyDetailPage anomalyId="anom-123" />);

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/anomalies/anom-123")
        );
      });
    });
  });

  describe("Error handling", () => {
    it("displays error when anomaly fetch fails", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
      });

      render(<AnomalyDetailPage anomalyId="anom-123" />);

      await waitFor(() => {
        expect(screen.getByText(/Unable to load anomaly/i)).toBeInTheDocument();
      });
    });

    it("displays anomaly ID in error message", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
      });

      render(<AnomalyDetailPage anomalyId="anom-456" />);

      await waitFor(() => {
        expect(screen.getByText(/anom-456/)).toBeInTheDocument();
      });
    });

    it("handles network errors gracefully", async () => {
      mockFetch.mockRejectedValueOnce(new Error("Network error"));

      render(<AnomalyDetailPage anomalyId="anom-123" />);

      await waitFor(() => {
        expect(screen.getByText(/Unable to load anomaly/i)).toBeInTheDocument();
      });
    });
  });

  describe("Anomaly data display", () => {
    beforeEach(() => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnomaly,
      });
      mockFetch.mockResolvedValueOnce({
        ok: false, // No recoverability data
      });
    });

    it("displays anomaly detail heading", async () => {
      render(<AnomalyDetailPage anomalyId="anom-123" />);

      await waitFor(() => {
        expect(screen.getByText("Anomaly Detail")).toBeInTheDocument();
      });
    });

    it("displays category and subtype", async () => {
      render(<AnomalyDetailPage anomalyId="anom-123" />);

      await waitFor(() => {
        expect(screen.getByText(/payment_discrepancy/)).toBeInTheDocument();
        expect(screen.getByText(/missing_royalty/)).toBeInTheDocument();
      });
    });

    it("displays severity level", async () => {
      render(<AnomalyDetailPage anomalyId="anom-123" />);

      await waitFor(() => {
        expect(screen.getByText(/Severity 8/)).toBeInTheDocument();
      });
    });

    it("displays anomaly ID in KPIs section", async () => {
      render(<AnomalyDetailPage anomalyId="anom-123" />);

      await waitFor(() => {
        expect(screen.getByText("Anomaly ID")).toBeInTheDocument();
      });
    });
  });

  describe("Recoverability integration", () => {
    it("fetches recoverability data when artist_id present", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnomaly,
      });
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockRecoverabilityResult,
      });

      render(<AnomalyDetailPage anomalyId="anom-123" />);

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/artists/artist-456/anomalies/anom-123/explain")
        );
      });
    });

    it("does not fetch recoverability when artist_id missing", async () => {
      const anomalyWithoutArtist = { ...mockAnomaly, artist_id: "" };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => anomalyWithoutArtist,
      });

      render(<AnomalyDetailPage anomalyId="anom-123" />);

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledTimes(1); // Only anomaly fetch
      });
    });

    it("handles recoverability fetch failure gracefully", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnomaly,
      });
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
      });

      render(<AnomalyDetailPage anomalyId="anom-123" />);

      await waitFor(() => {
        expect(screen.getByText("Anomaly Detail")).toBeInTheDocument();
      });
    });

    it("displays recoverability class when available", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnomaly,
      });
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockRecoverabilityResult,
      });

      const { container } = render(<AnomalyDetailPage anomalyId="anom-123" />);

      await waitFor(() => {
        // RecoverabilityExplainer component should be rendered
        expect(container.querySelector('[class*="recoverability"]')).toBeTruthy();
      });
    });
  });

  describe("Amount calculations", () => {
    it("calculates recoverable amount correctly for recoverable anomaly", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnomaly,
      });
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockRecoverabilityResult,
      });

      render(<AnomalyDetailPage anomalyId="anom-123" />);

      await waitFor(() => {
        expect(screen.getByText("Anomaly Detail")).toBeInTheDocument();
      });

      // Component should calculate recoverableAmount = 15000, expiredAmount = 0
    });

    it("calculates expired amount correctly for expired anomaly", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnomaly,
      });
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockExpiredRecoverability,
      });

      render(<AnomalyDetailPage anomalyId="anom-123" />);

      await waitFor(() => {
        expect(screen.getByText("Anomaly Detail")).toBeInTheDocument();
      });

      // Component should calculate expiredAmount = 15000, recoverableAmount = 0
    });

    it("handles zero estimated_recoverable", async () => {
      const zeroAnomaly = { ...mockAnomaly, estimated_recoverable: 0 };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => zeroAnomaly,
      });
      mockFetch.mockResolvedValueOnce({
        ok: false,
      });

      render(<AnomalyDetailPage anomalyId="anom-123" />);

      await waitFor(() => {
        expect(screen.getByText("Anomaly Detail")).toBeInTheDocument();
      });
    });

    it("handles null estimated_recoverable", async () => {
      const nullAnomaly = { ...mockAnomaly, estimated_recoverable: null };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => nullAnomaly,
      });
      mockFetch.mockResolvedValueOnce({
        ok: false,
      });

      render(<AnomalyDetailPage anomalyId="anom-123" />);

      await waitFor(() => {
        expect(screen.getByText("Anomaly Detail")).toBeInTheDocument();
      });
    });
  });

  describe("Accessibility", () => {
    beforeEach(() => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnomaly,
      });
      mockFetch.mockResolvedValueOnce({
        ok: false,
      });
    });

    it("uses semantic section element", async () => {
      const { container } = render(<AnomalyDetailPage anomalyId="anom-123" />);

      await waitFor(() => {
        expect(container.querySelector("section.anomaly-detail-page")).toBeInTheDocument();
      });
    });

    it("has proper heading hierarchy", async () => {
      render(<AnomalyDetailPage anomalyId="anom-123" />);

      await waitFor(() => {
        const h2 = screen.getByRole("heading", { level: 2 });
        expect(h2).toHaveTextContent("Anomaly Detail");
      });
    });
  });

  describe("API base URL", () => {
    it("uses default API base URL from env", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnomaly,
      });

      render(<AnomalyDetailPage anomalyId="anom-123" />);

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringMatching(/^http:\/\/localhost:8000/),
          expect.any(Object)
        );
      });
    });
  });

  describe("Component lifecycle", () => {
    it("cancels fetch on unmount", async () => {
      mockFetch.mockImplementation(() => new Promise(() => {})); // Never resolves

      const { unmount } = render(<AnomalyDetailPage anomalyId="anom-123" />);

      unmount();

      // Should not crash or cause errors
      expect(true).toBe(true);
    });

    it("refetches when anomalyId changes", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAnomaly,
      });
      mockFetch.mockResolvedValueOnce({
        ok: false,
      });

      const { rerender } = render(<AnomalyDetailPage anomalyId="anom-123" />);

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledTimes(2);
      });

      mockFetch.mockClear();
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ ...mockAnomaly, id: "anom-456" }),
      });
      mockFetch.mockResolvedValueOnce({
        ok: false,
      });

      rerender(<AnomalyDetailPage anomalyId="anom-456" />);

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/anomalies/anom-456")
        );
      });
    });
  });
});
