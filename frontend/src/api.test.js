/**
 * Characterization tests for src/api.ts
 *
 * Locks in the existing behaviour: that api.* properties exist, hold the
 * right API-client class instances, and are configured from the env vars.
 * The SDK classes themselves are mocked – we are not testing the SDK.
 */
import { describe, it, expect, vi } from "vitest";
// ---------------------------------------------------------------------------
// Mock the SDK modules before importing api.ts
// vi.mock() is hoisted to the top of the file by Vitest, so factories must
// not reference variables declared in the module body.
// ---------------------------------------------------------------------------
vi.mock("@xr7-sdk/apis", () => ({
    // use function constructors so `new XxxApi(config)` works
    ArtistsApi: vi.fn(function () { return { _isMock: true }; }),
    ClaimsApi: vi.fn(function () { return { _isMock: true }; }),
    DashboardApi: vi.fn(function () { return { _isMock: true }; }),
    IngestionApi: vi.fn(function () { return { _isMock: true }; }),
    OnboardingApi: vi.fn(function () { return { _isMock: true }; }),
    TermsApi: vi.fn(function () { return { _isMock: true }; }),
}));
vi.mock("@xr7-sdk/runtime", () => ({
    // Configuration is called with `new`; use a real function constructor
    Configuration: vi.fn(function (opts) {
        Object.assign(this, opts, { _isConfig: true });
    }),
}));
// ---------------------------------------------------------------------------
// Import under test (after mocks are installed)
// ---------------------------------------------------------------------------
import { api } from "./api";
import { Configuration } from "@xr7-sdk/runtime";
import { ArtistsApi, ClaimsApi, DashboardApi, IngestionApi, OnboardingApi, TermsApi, } from "@xr7-sdk/apis";
// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------
describe("api – shape", () => {
    it("exports an api object", () => {
        expect(api).toBeDefined();
        expect(typeof api).toBe("object");
    });
    it("has an artists property", () => {
        expect(api.artists).toBeDefined();
    });
    it("has a terms property", () => {
        expect(api.terms).toBeDefined();
    });
    it("has an onboarding property", () => {
        expect(api.onboarding).toBeDefined();
    });
    it("has an ingestion property", () => {
        expect(api.ingestion).toBeDefined();
    });
    it("has a dashboard property", () => {
        expect(api.dashboard).toBeDefined();
    });
    it("has a claims property", () => {
        expect(api.claims).toBeDefined();
    });
});
describe("api – correct client classes instantiated", () => {
    it("artists is an ArtistsApi instance", () => {
        expect(ArtistsApi).toHaveBeenCalled();
    });
    it("claims is a ClaimsApi instance", () => {
        expect(ClaimsApi).toHaveBeenCalled();
    });
    it("dashboard is a DashboardApi instance", () => {
        expect(DashboardApi).toHaveBeenCalled();
    });
    it("ingestion is an IngestionApi instance", () => {
        expect(IngestionApi).toHaveBeenCalled();
    });
    it("onboarding is an OnboardingApi instance", () => {
        expect(OnboardingApi).toHaveBeenCalled();
    });
    it("terms is a TermsApi instance", () => {
        expect(TermsApi).toHaveBeenCalled();
    });
});
describe("api – Configuration", () => {
    function firstConfigurationCall() {
        const first = vi.mocked(Configuration).mock.calls[0];
        expect(first).toBeDefined();
        return (first?.[0] ?? {});
    }
    it("Configuration is constructed once", () => {
        expect(Configuration).toHaveBeenCalledTimes(1);
    });
    it("Configuration receives a basePath", () => {
        const call = firstConfigurationCall();
        expect(call).toHaveProperty("basePath");
        expect(typeof call.basePath).toBe("string");
    });
    it("Configuration receives an accessToken function", () => {
        const call = firstConfigurationCall();
        expect(typeof call.accessToken).toBe("function");
    });
    it("basePath falls back to localhost:8000 when env var is absent", () => {
        // VITE_API_BASE_URL is not set in the test environment
        const call = firstConfigurationCall();
        expect(call.basePath).toBe("http://localhost:8000");
    });
});
