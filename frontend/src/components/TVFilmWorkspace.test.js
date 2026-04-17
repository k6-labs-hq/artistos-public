import { jsx as _jsx } from "react/jsx-runtime";
/**
 * Tests for TVFilmWorkspace.tsx
 *
 * Covers:
 *  (1) Component rendering and role selection
 *  (2) Agency mode toggle and roster controls
 *  (3) Role-specific messaging and state updates
 */
import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { TVFilmWorkspace } from "./TVFilmWorkspace";
describe("TVFilmWorkspace", () => {
    describe("Basic rendering", () => {
        it("renders without crashing", () => {
            expect(() => render(_jsx(TVFilmWorkspace, {}))).not.toThrow();
        });
        it("displays the main heading", () => {
            render(_jsx(TVFilmWorkspace, {}));
            expect(screen.getByText("TV/Film Onboarding and Enterprise Workspace")).toBeInTheDocument();
        });
        it("displays the section description", () => {
            render(_jsx(TVFilmWorkspace, {}));
            expect(screen.getByText(/Role-specific onboarding, live trust messaging/)).toBeInTheDocument();
        });
        it("renders role selector with default value", () => {
            render(_jsx(TVFilmWorkspace, {}));
            const select = screen.getByRole("combobox", { name: /Role/i });
            expect(select).toBeInTheDocument();
            expect(select).toHaveValue("Actor");
        });
    });
    describe("Role selection", () => {
        it("changes role when selecting from dropdown", () => {
            render(_jsx(TVFilmWorkspace, {}));
            const select = screen.getByRole("combobox", { name: /Role/i });
            fireEvent.change(select, { target: { value: "Writer (TV/Film)" } });
            expect(select).toHaveValue("Writer (TV/Film)");
        });
        it("shows writer-specific explanation when writer role selected", () => {
            render(_jsx(TVFilmWorkspace, {}));
            const select = screen.getByRole("combobox", { name: /Role/i });
            fireEvent.change(select, { target: { value: "Writer (TV/Film)" } });
            expect(screen.getByText(/residual windows, credited episode counts/i)).toBeInTheDocument();
        });
        it("shows stunt performer explanation when stunt role selected", () => {
            render(_jsx(TVFilmWorkspace, {}));
            const select = screen.getByRole("combobox", { name: /Role/i });
            fireEvent.change(select, { target: { value: "Stunt Performer" } });
            expect(screen.getByText(/stunt adjustments, turnaround penalties/i)).toBeInTheDocument();
        });
        it("shows agency explanation when agency role selected", () => {
            render(_jsx(TVFilmWorkspace, {}));
            const select = screen.getByRole("combobox", { name: /Role/i });
            fireEvent.change(select, { target: { value: "Talent Agency" } });
            expect(screen.getByText(/portfolio-wide historical analyses/i)).toBeInTheDocument();
        });
        it("shows default explanation for non-special roles", () => {
            render(_jsx(TVFilmWorkspace, {}));
            const select = screen.getByRole("combobox", { name: /Role/i });
            fireEvent.change(select, { target: { value: "Editor" } });
            expect(screen.getByText(/XR7 maps every compensation line/i)).toBeInTheDocument();
        });
    });
    describe("Agency mode toggle", () => {
        it("renders agency mode checkbox", () => {
            render(_jsx(TVFilmWorkspace, {}));
            const checkbox = screen.getByRole("checkbox", { name: /Enable enterprise agency mode/i });
            expect(checkbox).toBeInTheDocument();
        });
        it("starts with agency mode disabled", () => {
            render(_jsx(TVFilmWorkspace, {}));
            const checkbox = screen.getByRole("checkbox", { name: /Enable enterprise agency mode/i });
            expect(checkbox).not.toBeChecked();
        });
        it("displays 'Individual Mode' chip when agency mode disabled", () => {
            render(_jsx(TVFilmWorkspace, {}));
            expect(screen.getByText("Individual Mode")).toBeInTheDocument();
        });
        it("toggles agency mode when checkbox clicked", () => {
            render(_jsx(TVFilmWorkspace, {}));
            const checkbox = screen.getByRole("checkbox", { name: /Enable enterprise agency mode/i });
            fireEvent.click(checkbox);
            expect(checkbox).toBeChecked();
        });
        it("displays 'Portfolio Mode' chip when agency mode enabled", () => {
            render(_jsx(TVFilmWorkspace, {}));
            const checkbox = screen.getByRole("checkbox", { name: /Enable enterprise agency mode/i });
            fireEvent.click(checkbox);
            expect(screen.getByText("Portfolio Mode")).toBeInTheDocument();
        });
    });
    describe("Roster controls", () => {
        it("displays Agency Roster Intake section", () => {
            render(_jsx(TVFilmWorkspace, {}));
            expect(screen.getByText("Agency Roster Intake")).toBeInTheDocument();
        });
        it("shows upload format chips", () => {
            render(_jsx(TVFilmWorkspace, {}));
            expect(screen.getByText("CSV / XLSX / API")).toBeInTheDocument();
        });
        it("renders roster size input", () => {
            render(_jsx(TVFilmWorkspace, {}));
            // The component uses "Roster Size" as label
            expect(screen.getByText("Roster Size")).toBeInTheDocument();
        });
    });
    describe("Dashboard table", () => {
        it("displays residuals discovered row", () => {
            render(_jsx(TVFilmWorkspace, {}));
            expect(screen.getByText("Residuals Discovered")).toBeInTheDocument();
            expect(screen.getByText("$486,000")).toBeInTheDocument();
        });
        it("displays production payments row", () => {
            render(_jsx(TVFilmWorkspace, {}));
            expect(screen.getByText("Production Payments")).toBeInTheDocument();
            expect(screen.getByText("$72,400")).toBeInTheDocument();
        });
        it("displays streaming reuse row", () => {
            render(_jsx(TVFilmWorkspace, {}));
            expect(screen.getByText("Streaming Reuse")).toBeInTheDocument();
            expect(screen.getByText("$180,200")).toBeInTheDocument();
        });
        it("displays UGC & Clips row", () => {
            render(_jsx(TVFilmWorkspace, {}));
            expect(screen.getByText("UGC & Clips")).toBeInTheDocument();
            expect(screen.getByText("$39,800")).toBeInTheDocument();
        });
    });
    describe("Trust messaging", () => {
        it("displays trust events section", () => {
            render(_jsx(TVFilmWorkspace, {}));
            expect(screen.getByText(/Matching episode-season hierarchies/i)).toBeInTheDocument();
        });
        it("shows all trust events", () => {
            render(_jsx(TVFilmWorkspace, {}));
            expect(screen.getByText(/Applying union and studio compensation rules/i)).toBeInTheDocument();
            expect(screen.getByText(/Scoring SOL risk/i)).toBeInTheDocument();
            expect(screen.getByText(/Preparing evidence-backed claim packets/i)).toBeInTheDocument();
        });
    });
    describe("Accessibility", () => {
        it("has proper section landmark", () => {
            const { container } = render(_jsx(TVFilmWorkspace, {}));
            const section = container.querySelector("section#tv-film-workspace");
            expect(section).toBeInTheDocument();
        });
        it("role selector has accessible label", () => {
            render(_jsx(TVFilmWorkspace, {}));
            const select = screen.getByRole("combobox", { name: /Role/i });
            expect(select).toHaveAccessibleName();
        });
        it("checkbox has accessible label", () => {
            render(_jsx(TVFilmWorkspace, {}));
            const checkbox = screen.getByRole("checkbox");
            expect(checkbox).toHaveAccessibleName(/enterprise agency mode/i);
        });
    });
});
