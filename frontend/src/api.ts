import {
  ArtistsApi,
  ClaimsApi,
  DashboardApi,
  IngestionApi,
  OnboardingApi,
  TermsApi,
} from "@xr7-sdk/apis";
import { Configuration } from "@xr7-sdk/runtime";

const basePath = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";
const token = import.meta.env.VITE_ARTIST_TOKEN || "";

const config = new Configuration({
  basePath,
  accessToken: () => token,
});

export const api = {
  artists: new ArtistsApi(config),
  terms: new TermsApi(config),
  onboarding: new OnboardingApi(config),
  ingestion: new IngestionApi(config),
  dashboard: new DashboardApi(config),
  claims: new ClaimsApi(config),
};
