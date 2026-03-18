import type { ChangeEvent } from "react";
import { useEffect, useMemo, useState } from "react";

import { api } from "@/api";
import AnalysisProgressScreen, {
  type AnalysisProgressThemeTokens,
  type AnalysisProgressThemeVariant,
} from "@/components/AnalysisProgressScreen";

type OnboardingFlowProps = {
  onReady: (artistId: string) => void;
};

type FlowState = {
  artistId: string;
  termsAccepted: boolean;
  statementUploaded: boolean;
  firstClaimDrafted: boolean;
  message: string;
};

type AgentStatusPayload = {
  agent_orchestra_status?: {
    current_step?: string | null;
  };
  comfort_messages?: string[];
  portal_guidance?: string[];
};

const STATUS_MESSAGE_BY_STEP: Record<string, string> = {
  ingestion: "Decrypting uploaded files...",
  fingerprinting: "Fingerprinting royalty sources...",
  normalization: "Matching statements across platforms...",
  reconciliation: "Reconciling historical earnings...",
  anomaly_detection: "Identifying missing payments...",
  metadata_validation: "Cross-checking metadata integrity...",
  distributor_analysis: "Analyzing distributor reports...",
  dashboard_build: "Building your recovery dashboard...",
};

const DEFAULT_LIVE_MESSAGES = [
  "Decrypting uploaded files...",
  "Matching statements across platforms...",
  "Cross-checking metadata integrity...",
  "Building your recovery dashboard...",
];

const initialState: FlowState = {
  artistId: "",
  termsAccepted: false,
  statementUploaded: false,
  firstClaimDrafted: false,
  message: "Create your account to begin automatic recovery.",
};

export function OnboardingFlow({ onReady }: OnboardingFlowProps) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [state, setState] = useState<FlowState>(initialState);
  const [loading, setLoading] = useState(false);
  const [analysisInProgress, setAnalysisInProgress] = useState(false);
  const [analysisMessages, setAnalysisMessages] = useState<string[]>(DEFAULT_LIVE_MESSAGES);

  const canCreate = useMemo(() => name.trim().length >= 2 && email.trim().length >= 5, [name, email]);
  const canAcceptTerms = state.artistId.length > 0 && !state.termsAccepted;
  const canUpload = state.artistId.length > 0 && state.termsAccepted && file !== null;

  const onFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    setFile(e.target.files?.item(0) || null);
  };

  const refreshStatus = async (artistId: string) => {
    const status = await api.onboarding.onboardingStatusArtistsArtistIdOnboardingStatusGet({ artistId });
    const gates = (status?.gates || {}) as Record<string, unknown>;
    const firstClaimDrafted = Boolean(gates.first_claim_drafted);
    setState((prev) => ({
      ...prev,
      artistId,
      termsAccepted: Boolean(gates.terms_accepted),
      statementUploaded: Boolean(gates.statement_uploaded),
      firstClaimDrafted,
      message: `Status: ${String(status?.status || "NEW")}`,
    }));
    if (firstClaimDrafted) {
      onReady(artistId);
    }

    return {
      firstClaimDrafted,
      statementUploaded: Boolean(gates.statement_uploaded),
    };
  };

  const fetchAgentStatus = async (artistId: string): Promise<AgentStatusPayload> => {
    const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"}/artists/${artistId}/agents/status`);
    if (!response.ok) {
      throw new Error(`Unable to read agent status (${response.status})`);
    }
    return (await response.json()) as AgentStatusPayload;
  };

  const mapAgentStatusToMessages = (payload: AgentStatusPayload): string[] => {
    const dynamic = new Set<string>();
    const step = payload.agent_orchestra_status?.current_step?.toLowerCase().trim() || "";

    if (step) {
      dynamic.add(STATUS_MESSAGE_BY_STEP[step] || `Processing ${step.replaceAll("_", " ")}...`);
    }

    (payload.comfort_messages || []).slice(0, 2).forEach((message) => {
      if (message.trim()) {
        dynamic.add(message.trim());
      }
    });

    (payload.portal_guidance || []).slice(0, 1).forEach((message) => {
      if (message.trim()) {
        dynamic.add(message.trim());
      }
    });

    const merged = [...dynamic, ...DEFAULT_LIVE_MESSAGES];
    return merged.slice(0, 8);
  };

  useEffect(() => {
    if (!analysisInProgress || !state.artistId) {
      return;
    }

    let active = true;
    let timer: number | undefined;

    const poll = async () => {
      try {
        const [statusResult, agentStatus] = await Promise.all([
          refreshStatus(state.artistId),
          fetchAgentStatus(state.artistId),
        ]);
        if (!active) {
          return;
        }

        setAnalysisMessages(mapAgentStatusToMessages(agentStatus));
        if (statusResult.firstClaimDrafted) {
          setAnalysisInProgress(false);
          setState((prev) => ({ ...prev, message: "Analysis complete. Opening your recovery dashboard." }));
          return;
        }

        timer = window.setTimeout(poll, 2000);
      } catch (error) {
        if (!active) {
          return;
        }
        setAnalysisInProgress(false);
        setState((prev) => ({ ...prev, message: `Analysis status unavailable: ${String(error)}` }));
      }
    };

    poll();

    return () => {
      active = false;
      if (timer) {
        window.clearTimeout(timer);
      }
    };
  }, [analysisInProgress, state.artistId]);

  const whiteLabelThemeVariant = (import.meta.env.VITE_WHITE_LABEL_THEME as AnalysisProgressThemeVariant | undefined) || "xr7";
  const whiteLabelTitle = import.meta.env.VITE_WHITE_LABEL_TITLE || "XR7 Forensic Analysis";
  const whiteLabelCaption = import.meta.env.VITE_WHITE_LABEL_CAPTION || "Validating cross-platform royalty evidence with precision.";
  const whiteLabelThemeOverrides = useMemo<Partial<AnalysisProgressThemeTokens>>(
    () => ({
      ...(import.meta.env.VITE_WHITE_LABEL_TEXT_COLOR
        ? { textColor: String(import.meta.env.VITE_WHITE_LABEL_TEXT_COLOR) }
        : {}),
      ...(import.meta.env.VITE_WHITE_LABEL_BG_PRIMARY
        ? { backgroundPrimary: String(import.meta.env.VITE_WHITE_LABEL_BG_PRIMARY) }
        : {}),
      ...(import.meta.env.VITE_WHITE_LABEL_BG_SECONDARY
        ? { backgroundSecondary: String(import.meta.env.VITE_WHITE_LABEL_BG_SECONDARY) }
        : {}),
      ...(import.meta.env.VITE_WHITE_LABEL_PANEL_BG
        ? { panelBackground: String(import.meta.env.VITE_WHITE_LABEL_PANEL_BG) }
        : {}),
      ...(import.meta.env.VITE_WHITE_LABEL_BORDER_COLOR
        ? { borderColor: String(import.meta.env.VITE_WHITE_LABEL_BORDER_COLOR) }
        : {}),
      ...(import.meta.env.VITE_WHITE_LABEL_GLOW_PRIMARY
        ? { glowColorPrimary: String(import.meta.env.VITE_WHITE_LABEL_GLOW_PRIMARY) }
        : {}),
      ...(import.meta.env.VITE_WHITE_LABEL_GLOW_SECONDARY
        ? { glowColorSecondary: String(import.meta.env.VITE_WHITE_LABEL_GLOW_SECONDARY) }
        : {}),
    }),
    [],
  );

  const createArtist = async () => {
    if (!canCreate) return;
    setLoading(true);
    try {
      const artist = await api.artists.createArtistArtistsPost({
        artistCreate: {
          name: name.trim(),
          email: email.trim(),
          firstName: name.trim().split(" ")[0],
          lastName: name.trim().split(" ").slice(1).join(" "),
          countryCode: "US",
          defaultAttorneyGracePeriodDays: 60,
          primaryJurisdiction: "USA",
          preferredContractType: "recording",
        },
      });
      await refreshStatus(artist.id);
    } catch (error) {
      setState((prev) => ({ ...prev, message: `Unable to create artist: ${String(error)}` }));
    } finally {
      setLoading(false);
    }
  };

  const acceptTerms = async () => {
    if (!canAcceptTerms) return;
    setLoading(true);
    try {
      const terms = await api.terms.getTermsTermsGet();
      await api.terms.acceptTermsArtistsArtistIdTermsAcceptPost({
        artistId: state.artistId,
        termsAcceptRequest: {
          termsVersion: String((terms as Record<string, unknown>).terms_version || "v1"),
          agreed: true,
        },
      });
      await refreshStatus(state.artistId);
    } catch (error) {
      setState((prev) => ({ ...prev, message: `Unable to accept terms: ${String(error)}` }));
    } finally {
      setLoading(false);
    }
  };

  const uploadStatement = async () => {
    if (!canUpload || !file) return;
    setLoading(true);
    try {
      await api.ingestion.uploadStatementArtistsArtistIdStatementsUploadPost({
        artistId: state.artistId,
        file: file as unknown as string,
      });
      await refreshStatus(state.artistId);
      setAnalysisInProgress(true);
      setAnalysisMessages(DEFAULT_LIVE_MESSAGES);
      setState((prev) => ({ ...prev, message: "Statement uploaded. XR7 forensic agents are processing your data." }));
    } catch (error) {
      setState((prev) => ({ ...prev, message: `Upload failed: ${String(error)}` }));
    } finally {
      setLoading(false);
    }
  };

  if (analysisInProgress) {
    return (
      <AnalysisProgressScreen
        messages={analysisMessages}
        animationSpeed={2050}
        title={whiteLabelTitle}
        caption={whiteLabelCaption}
        themeVariant={whiteLabelThemeVariant}
        themeOverrides={whiteLabelThemeOverrides}
      />
    );
  }

  return (
    <section className="panel onboarding-panel">
      <h1>Recover Missing Music Revenue in Minutes</h1>
      <p className="panel-lead">Three steps: create account, accept terms, upload statement. XR7 auto-detects anomalies and drafts your first claim.</p>

      <div className="flow-grid">
        <div className="step-card">
          <h2>1. Create artist account</h2>
          <label>
            Artist name
            <input value={name} onChange={(e) => setName(e.target.value)} placeholder="NOVA SKY" />
          </label>
          <label>
            Contact email
            <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="artist@example.com" />
          </label>
          <button disabled={!canCreate || loading} onClick={createArtist}>Create account</button>
        </div>

        <div className="step-card">
          <h2>2. Accept terms</h2>
          <p>Terms acceptance is recorded with an immutable audit trail.</p>
          <button disabled={!canAcceptTerms || loading} onClick={acceptTerms}>Accept terms</button>
        </div>

        <div className="step-card">
          <h2>3. Upload statement</h2>
          <label className="dropzone" htmlFor="statement-file">
            <input
              id="statement-file"
              type="file"
              accept=".csv,.tsv,.xlsx"
              onChange={onFileChange}
            />
            <span>{file ? file.name : "Tap or drag CSV/TSV/XLSX statement"}</span>
          </label>
          <button disabled={!canUpload || loading} onClick={uploadStatement}>Upload and analyze</button>
        </div>
      </div>

      <div className="status-strip">
        <span>{state.message}</span>
        <span>Terms: {state.termsAccepted ? "Accepted" : "Pending"}</span>
        <span>Statement: {state.statementUploaded ? "Uploaded" : "Pending"}</span>
        <span>First claim: {state.firstClaimDrafted ? "Drafted" : "Pending"}</span>
      </div>
    </section>
  );
}
