import type { ChangeEvent } from "react";
import { useMemo, useState } from "react";

import { api } from "@/api";

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

  const canCreate = useMemo(() => name.trim().length >= 2 && email.trim().length >= 5, [name, email]);
  const canAcceptTerms = state.artistId.length > 0 && !state.termsAccepted;
  const canUpload = state.artistId.length > 0 && state.termsAccepted && file !== null;

  const onFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    setFile(e.target.files?.item(0) || null);
  };

  const refreshStatus = async (artistId: string) => {
    const status = await api.onboarding.onboardingStatusArtistsArtistIdOnboardingStatusGet({ artistId });
    const gates = (status?.gates || {}) as Record<string, unknown>;
    setState((prev) => ({
      ...prev,
      artistId,
      termsAccepted: Boolean(gates.terms_accepted),
      statementUploaded: Boolean(gates.statement_uploaded),
      firstClaimDrafted: Boolean(gates.first_claim_drafted),
      message: `Status: ${String(status?.status || "NEW")}`,
    }));
    if (Boolean(gates.statement_uploaded)) {
      onReady(artistId);
    }
  };

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
      setState((prev) => ({ ...prev, message: "Statement uploaded. XR7 is drafting your first claim." }));
    } catch (error) {
      setState((prev) => ({ ...prev, message: `Upload failed: ${String(error)}` }));
    } finally {
      setLoading(false);
    }
  };

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
