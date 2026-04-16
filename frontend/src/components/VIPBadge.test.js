import { jsx as _jsx } from "react/jsx-runtime";
/**
 * Characterization tests for src/components/VIPBadge.tsx
 *
 * Covers:
 *  (1) Typical inputs      – default props, each tierLevel, each size
 *  (2) Edge cases          – unknown tierLevel, empty className, animated flag
 *  (3) Error / guard paths – unknown tierLevel falls back gracefully
 *
 * No component code is changed.
 */
import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { VIPBadge } from "./VIPBadge";
// ---------------------------------------------------------------------------
// (1) Typical inputs
// ---------------------------------------------------------------------------
describe("VIPBadge – typical inputs", () => {
    it("renders without crashing with defaults", () => {
        expect(() => render(_jsx(VIPBadge, {}))).not.toThrow();
    });
    it("shows 'Founders Circle' for FOUNDERS_CIRCLE tier", () => {
        render(_jsx(VIPBadge, { tierLevel: "FOUNDERS_CIRCLE" }));
        expect(screen.getByText("Founders Circle")).toBeInTheDocument();
    });
    it("shows 'VIP Member' for VIP tier", () => {
        render(_jsx(VIPBadge, { tierLevel: "VIP" }));
        expect(screen.getByText("VIP Member")).toBeInTheDocument();
    });
    it("default tierLevel is FOUNDERS_CIRCLE", () => {
        render(_jsx(VIPBadge, {}));
        expect(screen.getByText("Founders Circle")).toBeInTheDocument();
    });
    it("title attribute includes tier label", () => {
        const { container } = render(_jsx(VIPBadge, { tierLevel: "FOUNDERS_CIRCLE" }));
        const span = container.querySelector("span[title]");
        expect(span?.getAttribute("title")).toContain("Founders Circle");
    });
    it("title attribute includes 'Invite-Only Premier Experience'", () => {
        const { container } = render(_jsx(VIPBadge, {}));
        const span = container.querySelector("span[title]");
        expect(span?.getAttribute("title")).toContain("Invite-Only Premier Experience");
    });
});
// ---------------------------------------------------------------------------
// (2) Edge cases – sizes and animation
// ---------------------------------------------------------------------------
describe("VIPBadge – size prop", () => {
    it.each(["sm", "md", "lg"])("renders at size %s without crashing", (size) => {
        expect(() => render(_jsx(VIPBadge, { size: size }))).not.toThrow();
    });
    it("default size is md", () => {
        // The md class is 'text-sm px-3 py-1 gap-1.5'
        const { container } = render(_jsx(VIPBadge, {}));
        const span = container.querySelector("span[title]");
        expect(span?.className).toContain("text-sm");
    });
});
describe("VIPBadge – animated prop", () => {
    it("applies glow class when animated=true (default)", () => {
        const { container } = render(_jsx(VIPBadge, { animated: true }));
        const span = container.querySelector("span[title]");
        expect(span?.className).toContain("vip-badge-glow");
    });
    it("does NOT apply glow class when animated=false", () => {
        const { container } = render(_jsx(VIPBadge, { animated: false }));
        const span = container.querySelector("span[title]");
        expect(span?.className).not.toContain("vip-badge-glow");
    });
    it("applies pulse class to icon when animated=true", () => {
        const { container } = render(_jsx(VIPBadge, { animated: true }));
        const svg = container.querySelector("svg[aria-hidden]");
        // SVG elements expose className as SVGAnimatedString; use getAttribute instead
        expect(svg?.getAttribute("class")).toContain("vip-icon-pulse");
    });
    it("does NOT apply pulse class when animated=false", () => {
        const { container } = render(_jsx(VIPBadge, { animated: false }));
        const svg = container.querySelector("svg[aria-hidden]");
        expect(svg?.getAttribute("class") ?? "").not.toContain("vip-icon-pulse");
    });
});
describe("VIPBadge – className prop", () => {
    it("merges custom className into the span", () => {
        const { container } = render(_jsx(VIPBadge, { className: "my-custom-class" }));
        const span = container.querySelector("span[title]");
        expect(span?.className).toContain("my-custom-class");
    });
    it("empty className does not add blank token", () => {
        const { container } = render(_jsx(VIPBadge, { className: "" }));
        const span = container.querySelector("span[title]");
        // className should not contain double spaces from an empty string token
        expect(span?.className).not.toContain("  ");
    });
});
// ---------------------------------------------------------------------------
// (3) Error / guard paths – unknown tierLevel
// ---------------------------------------------------------------------------
describe("VIPBadge – unknown tierLevel", () => {
    it("falls back to 'VIP' label for an unrecognised tier", () => {
        // Cast to bypass TypeScript so we can test the runtime fallback
        render(_jsx(VIPBadge, { tierLevel: "PLATINUM" }));
        expect(screen.getByText("VIP")).toBeInTheDocument();
    });
    it("does not crash for an unrecognised tier", () => {
        expect(() => render(_jsx(VIPBadge, { tierLevel: "UNKNOWN_TIER" }))).not.toThrow();
    });
});
// ---------------------------------------------------------------------------
// Structural / accessibility
// ---------------------------------------------------------------------------
describe("VIPBadge – structure", () => {
    it("renders a span as the root element", () => {
        const { container } = render(_jsx(VIPBadge, {}));
        expect(container.querySelector("span[title]")).not.toBeNull();
    });
    it("contains an svg icon", () => {
        const { container } = render(_jsx(VIPBadge, {}));
        expect(container.querySelector("svg")).not.toBeNull();
    });
    it("svg is aria-hidden", () => {
        const { container } = render(_jsx(VIPBadge, {}));
        expect(container.querySelector("svg")).toHaveAttribute("aria-hidden", "true");
    });
});
