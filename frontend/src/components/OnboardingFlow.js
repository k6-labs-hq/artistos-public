import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useMemo, useState } from "react";
import { api } from "@/api";
const initialState = {
    artistId: "",
    termsAccepted: false,
    statementUploaded: false,
    firstClaimDrafted: false,
    message: "Create your account to begin automatic recovery.",
};
export function OnboardingFlow({ onReady }) {
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [file, setFile] = useState(null);
    const [state, setState] = useState(initialState);
    const [loading, setLoading] = useState(false);
    const canCreate = useMemo(() => name.trim().length >= 2 && email.trim().length >= 5, [name, email]);
    const canAcceptTerms = state.artistId.length > 0 && !state.termsAccepted;
    const canUpload = state.artistId.length > 0 && state.termsAccepted && file !== null;
    const onFileChange = (e) => {
        setFile(e.target.files?.item(0) || null);
    };
    const refreshStatus = async (artistId) => {
        const status = await api.onboarding.onboardingStatusArtistsArtistIdOnboardingStatusGet({ artistId });
        const gates = (status?.gates || {});
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
        if (!canCreate)
            return;
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
        }
        catch (error) {
            setState((prev) => ({ ...prev, message: `Unable to create artist: ${String(error)}` }));
        }
        finally {
            setLoading(false);
        }
    };
    const acceptTerms = async () => {
        if (!canAcceptTerms)
            return;
        setLoading(true);
        try {
            const terms = await api.terms.getTermsTermsGet();
            await api.terms.acceptTermsArtistsArtistIdTermsAcceptPost({
                artistId: state.artistId,
                termsAcceptRequest: {
                    termsVersion: String(terms.terms_version || "v1"),
                    agreed: true,
                },
            });
            await refreshStatus(state.artistId);
        }
        catch (error) {
            setState((prev) => ({ ...prev, message: `Unable to accept terms: ${String(error)}` }));
        }
        finally {
            setLoading(false);
        }
    };
    const uploadStatement = async () => {
        if (!canUpload || !file)
            return;
        setLoading(true);
        try {
            await api.ingestion.uploadStatementArtistsArtistIdStatementsUploadPost({
                artistId: state.artistId,
                file: file,
            });
            await refreshStatus(state.artistId);
            setState((prev) => ({ ...prev, message: "Statement uploaded. XR7 is drafting your first claim." }));
        }
        catch (error) {
            setState((prev) => ({ ...prev, message: `Upload failed: ${String(error)}` }));
        }
        finally {
            setLoading(false);
        }
    };
    return (_jsxs("section", { className: "panel onboarding-panel", children: [_jsx("h1", { children: "Recover Missing Music Revenue in Minutes" }), _jsx("p", { className: "panel-lead", children: "Three steps: create account, accept terms, upload statement. XR7 auto-detects anomalies and drafts your first claim." }), _jsxs("div", { className: "flow-grid", children: [_jsxs("div", { className: "step-card", children: [_jsx("h2", { children: "1. Create artist account" }), _jsxs("label", { children: ["Artist name", _jsx("input", { value: name, onChange: (e) => setName(e.target.value), placeholder: "NOVA SKY" })] }), _jsxs("label", { children: ["Contact email", _jsx("input", { value: email, onChange: (e) => setEmail(e.target.value), placeholder: "artist@example.com" })] }), _jsx("button", { disabled: !canCreate || loading, onClick: createArtist, children: "Create account" })] }), _jsxs("div", { className: "step-card", children: [_jsx("h2", { children: "2. Accept terms" }), _jsx("p", { children: "Terms acceptance is recorded with an immutable audit trail." }), _jsx("button", { disabled: !canAcceptTerms || loading, onClick: acceptTerms, children: "Accept terms" })] }), _jsxs("div", { className: "step-card", children: [_jsx("h2", { children: "3. Upload statement" }), _jsxs("label", { className: "dropzone", htmlFor: "statement-file", children: [_jsx("input", { id: "statement-file", type: "file", accept: ".csv,.tsv,.xlsx", onChange: onFileChange }), _jsx("span", { children: file ? file.name : "Tap or drag CSV/TSV/XLSX statement" })] }), _jsx("button", { disabled: !canUpload || loading, onClick: uploadStatement, children: "Upload and analyze" })] })] }), _jsxs("div", { className: "status-strip", children: [_jsx("span", { children: state.message }), _jsxs("span", { children: ["Terms: ", state.termsAccepted ? "Accepted" : "Pending"] }), _jsxs("span", { children: ["Statement: ", state.statementUploaded ? "Uploaded" : "Pending"] }), _jsxs("span", { children: ["First claim: ", state.firstClaimDrafted ? "Drafted" : "Pending"] })] })] }));
}
