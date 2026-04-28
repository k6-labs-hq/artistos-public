/**
 * Tests the xr7Client fetch wrapper, especially the 401 interceptor that
 * keeps an expired-token user from getting stuck on a "Sign out" page that
 * silently 401s every call.
 */
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { UnauthorizedError, xr7Get } from "./xr7Client";

const ORIGINAL_LOCATION = window.location;

beforeEach(() => {
  localStorage.clear();
  // jsdom location can't be reassigned; spy on assign instead.
  Object.defineProperty(window, "location", {
    configurable: true,
    value: { ...ORIGINAL_LOCATION, pathname: "/dashboard", assign: vi.fn() },
  });
});

afterEach(() => {
  Object.defineProperty(window, "location", { configurable: true, value: ORIGINAL_LOCATION });
  vi.restoreAllMocks();
});

describe("xr7Client", () => {
  it("attaches the bearer token from localStorage", async () => {
    localStorage.setItem("xr7_access_token", "test-token-abc");
    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ ok: true }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      }),
    );

    await xr7Get("/auth/me");

    expect(fetchSpy).toHaveBeenCalledTimes(1);
    const init = fetchSpy.mock.calls[0]![1] as RequestInit;
    expect((init.headers as Record<string, string>).Authorization).toBe("Bearer test-token-abc");
  });

  it("throws UnauthorizedError, clears token, and redirects on 401", async () => {
    localStorage.setItem("xr7_access_token", "expired");
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response("nope", { status: 401 }),
    );

    await expect(xr7Get("/auth/me")).rejects.toBeInstanceOf(UnauthorizedError);
    expect(localStorage.getItem("xr7_access_token")).toBeNull();
    expect(window.location.assign).toHaveBeenCalledWith("/login");
  });

  it("does not redirect when already on /login (avoids redirect loop)", async () => {
    Object.defineProperty(window, "location", {
      configurable: true,
      value: { ...ORIGINAL_LOCATION, pathname: "/login", assign: vi.fn() },
    });
    localStorage.setItem("xr7_access_token", "expired");
    vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response("nope", { status: 401 }));

    await expect(xr7Get("/auth/me")).rejects.toBeInstanceOf(UnauthorizedError);
    expect(window.location.assign).not.toHaveBeenCalled();
  });

  it("surfaces non-401 errors with status + body", async () => {
    localStorage.setItem("xr7_access_token", "ok");
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response("server fell over", { status: 500 }),
    );

    await expect(xr7Get("/auth/me")).rejects.toThrow(/500.*server fell over/);
  });
});
