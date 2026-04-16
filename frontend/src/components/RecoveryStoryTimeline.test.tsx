/**
 * Tests for RecoveryStoryTimeline.tsx
 *
 * Covers:
 *  (1) Component rendering and API integration
 *  (2) Timeline event display and formatting
 *  (3) Category icons and coloring
 *  (4) VIP milestone handling
 */
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { RecoveryStoryTimeline } from "./RecoveryStoryTimeline";
import type { TimelineEvent } from "./RecoveryStoryTimeline";

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch;

const mockEvents: TimelineEvent[] = [
  {
    id: "evt-1",
    date: "2026-01-15T10:00:00Z",
    category: "onboarding",
    title: "Joined XR7",
    description: "Welcome to your recovery journey",
  },
  {
    id: "evt-2",
    date: "2026-02-01T14:30:00Z",
    category: "evidence",
    title: "Evidence Collected",
    description: "Spotify streaming data verified",
    platform: "Spotify",
    confidence: 0.95,
  },
  {
    id: "evt-3",
    date: "2026-02-15T09:00:00Z",
    category: "claim",
    title: "Claim Filed",
    description: "Underpayment claim submitted",
    amount: 5000,
    currency: "$",
    platform: "Spotify",
  },
  {
    id: "evt-4",
    date: "2026-03-01T16:45:00Z",
    category: "payment",
    title: "Recovery Received",
    amount: 5000,
    currency: "$",
    platform: "Spotify",
  },
];

const mockVIPEvent: TimelineEvent = {
  id: "evt-vip",
  date: "2026-03-10T12:00:00Z",
  category: "milestone",
  title: "Founders Circle Membership",
  description: "Elevated to VIP status",
  is_vip_milestone: true,
};

describe("RecoveryStoryTimeline", () => {
  beforeEach(() => {
    mockFetch.mockClear();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe("Basic rendering", () => {
    it("renders without crashing", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ events: [] }),
      });

      expect(() => render(<RecoveryStoryTimeline artistId="artist-123" />)).not.toThrow();
    });

    it("fetches timeline data on mount", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ events: mockEvents }),
      });

      render(<RecoveryStoryTimeline artistId="artist-123" />);

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("/artists/artist-123/recovery-story"),
          expect.any(Object)
        );
      });
    });

    it("uses custom API base when provided", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ events: [] }),
      });

      render(<RecoveryStoryTimeline artistId="artist-123" apiBase="https://api.example.com" />);

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining("https://api.example.com"),
          expect.any(Object)
        );
      });
    });
  });

  describe("Timeline events display", () => {
    it("displays timeline events after loading", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ events: mockEvents }),
      });

      render(<RecoveryStoryTimeline artistId="artist-123" />);

      await waitFor(() => {
        expect(screen.getByText("Joined XR7")).toBeInTheDocument();
      });
    });

    it("displays event titles", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ events: mockEvents }),
      });

      render(<RecoveryStoryTimeline artistId="artist-123" />);

      await waitFor(() => {
        expect(screen.getByText("Joined XR7")).toBeInTheDocument();
        expect(screen.getByText("Evidence Collected")).toBeInTheDocument();
        expect(screen.getByText("Claim Filed")).toBeInTheDocument();
        expect(screen.getByText("Recovery Received")).toBeInTheDocument();
      });
    });

    it("displays event descriptions", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ events: mockEvents }),
      });

      render(<RecoveryStoryTimeline artistId="artist-123" />);

      await waitFor(() => {
        expect(screen.getByText("Welcome to your recovery journey")).toBeInTheDocument();
        expect(screen.getByText("Spotify streaming data verified")).toBeInTheDocument();
      });
    });

    it("displays platform tags when present", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ events: mockEvents }),
      });

      render(<RecoveryStoryTimeline artistId="artist-123" />);

      await waitFor(() => {
        const spotifyTags = screen.getAllByText("Spotify");
        expect(spotifyTags.length).toBeGreaterThan(0);
      });
    });

    it("displays monetary amounts when present", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ events: mockEvents }),
      });

      render(<RecoveryStoryTimeline artistId="artist-123" />);

      await waitFor(() => {
        const amounts = screen.getAllByText(/\+\$5,000/);
        expect(amounts.length).toBeGreaterThan(0);
      });
    });
  });

  describe("Category styling", () => {
    it("displays category labels", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ events: mockEvents }),
      });

      render(<RecoveryStoryTimeline artistId="artist-123" />);

      await waitFor(() => {
        expect(screen.getByText("Onboarded")).toBeInTheDocument();
        expect(screen.getByText("Evidence Secured")).toBeInTheDocument();
        expect(screen.getByText("Claim Filed")).toBeInTheDocument();
        expect(screen.getByText("Recovery Received")).toBeInTheDocument();
      });
    });

    it("displays category icons as emojis", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ events: mockEvents }),
      });

      const { container } = render(<RecoveryStoryTimeline artistId="artist-123" />);

      await waitFor(() => {
        expect(container.textContent).toContain("🚀"); // onboarding
        expect(container.textContent).toContain("🔗"); // evidence
        expect(container.textContent).toContain("📋"); // claim
        expect(container.textContent).toContain("💸"); // payment
      });
    });
  });

  describe("VIP milestones", () => {
    it("displays VIP badge for VIP milestones", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ events: [mockVIPEvent] }),
      });

      render(<RecoveryStoryTimeline artistId="artist-123" vipActive={true} />);

      await waitFor(() => {
        expect(screen.getByText("★ VIP")).toBeInTheDocument();
      });
    });

    it("uses special icon for VIP milestones", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ events: [mockVIPEvent] }),
      });

      const { container } = render(<RecoveryStoryTimeline artistId="artist-123" />);

      await waitFor(() => {
        expect(container.textContent).toContain("⬡"); // VIP hexagon
      });
    });
  });

  describe("Date formatting", () => {
    it("formats dates in readable format", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ events: mockEvents }),
      });

      render(<RecoveryStoryTimeline artistId="artist-123" />);

      await waitFor(() => {
        // Check for month abbreviation pattern
        expect(screen.getByText(/Jan 15, 2026/)).toBeInTheDocument();
      });
    });

    it("handles invalid date gracefully", async () => {
      const invalidEvent: TimelineEvent = {
        id: "evt-invalid",
        date: "not-a-valid-date",
        category: "milestone",
        title: "Test Event",
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ events: [invalidEvent] }),
      });

      render(<RecoveryStoryTimeline artistId="artist-123" />);

      await waitFor(() => {
        expect(screen.getByText("Test Event")).toBeInTheDocument();
      });
    });
  });

  describe("Vertical filtering", () => {
    it("accepts vertical prop for music", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ events: [] }),
      });

      expect(() => 
        render(<RecoveryStoryTimeline artistId="artist-123" vertical="music" />)
      ).not.toThrow();
    });

    it("accepts vertical prop for tv_film", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ events: [] }),
      });

      expect(() => 
        render(<RecoveryStoryTimeline artistId="artist-123" vertical="tv_film" />)
      ).not.toThrow();
    });

    it("accepts vertical prop for both", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ events: [] }),
      });

      expect(() => 
        render(<RecoveryStoryTimeline artistId="artist-123" vertical="both" />)
      ).not.toThrow();
    });
  });

  describe("Error handling", () => {
    it("handles API errors gracefully", async () => {
      mockFetch.mockRejectedValueOnce(new Error("Network error"));

      render(<RecoveryStoryTimeline artistId="artist-123" />);

      // Should render without crashing
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalled();
      });
    });

    it("handles empty events array", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ events: [] }),
      });

      render(<RecoveryStoryTimeline artistId="artist-123" />);

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalled();
      });
    });
  });

  describe("Confidence display", () => {
    it("displays confidence scores when present", async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ events: mockEvents }),
      });

      render(<RecoveryStoryTimeline artistId="artist-123" />);

      await waitFor(() => {
        // Confidence is 0.95 = 95%
        expect(screen.getByText(/95%/)).toBeInTheDocument();
      });
    });
  });
});
