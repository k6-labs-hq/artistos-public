import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import "./InviteWelcomeScreen.css";
export const InviteWelcomeScreen = ({ onProceed, }) => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const [recipientName, setRecipientName] = useState("");
    const [isValid, setIsValid] = useState(null);
    const [error, setError] = useState(null);
    const [isLoading, setIsLoading] = useState(true);
    const inviteToken = searchParams.get("token");
    useEffect(() => {
        if (!inviteToken) {
            setError("No invite token provided");
            setIsValid(false);
            setIsLoading(false);
            return;
        }
        // Validate invite token
        validateInvite(inviteToken);
    }, [inviteToken]);
    const validateInvite = async (token) => {
        try {
            const response = await fetch("/api/invites/validate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ invite_token: token }),
            });
            const data = await response.json();
            if (data.is_valid) {
                setRecipientName(data.recipient_name || "Creator");
                setIsValid(true);
                setError(null);
                // Record that invite was opened
                await fetch("/api/invites/open", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ invite_token: token }),
                }).catch(() => {
                    // Silent fail, just for tracking
                });
            }
            else {
                setIsValid(false);
                setError(data.error || "This invitation is no longer active. Please request a new private session.");
            }
        }
        catch (err) {
            setIsValid(false);
            setError("Failed to validate invitation");
            console.error(err);
        }
        finally {
            setIsLoading(false);
        }
    };
    const handleProceed = () => {
        if (onProceed) {
            onProceed(recipientName);
        }
        else {
            // Navigate to onboarding with token
            navigate(`/onboarding?invite_token=${inviteToken}`, { replace: true });
        }
    };
    if (isLoading) {
        return (_jsxs("div", { className: "invite-welcome-container loading", children: [_jsx("div", { className: "xr7-logo breathing", children: _jsx("svg", { width: "64", height: "64", viewBox: "0 0 64 64", fill: "none", children: _jsx("text", { x: "32", y: "40", fontSize: "32", fontWeight: "700", textAnchor: "middle", fill: "#00FF88", fontFamily: "monospace", children: "XR7" }) }) }), _jsx("p", { className: "status-text", children: "Verifying your invitation..." })] }));
    }
    if (!isValid || error) {
        return (_jsxs("div", { className: "invite-welcome-container error", children: [_jsx("div", { className: "xr7-logo", children: _jsxs("svg", { width: "64", height: "64", viewBox: "0 0 64 64", fill: "none", children: [_jsx("circle", { cx: "32", cy: "32", r: "30", stroke: "#FF4444", strokeWidth: "2" }), _jsx("text", { x: "32", y: "40", fontSize: "28", fontWeight: "700", textAnchor: "middle", fill: "#FF4444", fontFamily: "monospace", children: "\u2715" })] }) }), _jsx("h1", { children: "Invitation Expired" }), _jsx("p", { className: "error-message", children: error }), _jsx("button", { className: "premium-button secondary", onClick: () => navigate("/"), children: "Return to Home" })] }));
    }
    return (_jsxs("div", { className: "invite-welcome-container", children: [_jsx("div", { className: "background-animation" }), _jsxs("div", { className: "welcome-content", children: [_jsx("div", { className: "xr7-logo breathing", children: _jsxs("svg", { width: "80", height: "80", viewBox: "0 0 64 64", fill: "none", children: [_jsx("defs", { children: _jsxs("linearGradient", { id: "logoGradient", x1: "0%", y1: "0%", x2: "100%", y2: "100%", children: [_jsx("stop", { offset: "0%", stopColor: "#00FF88" }), _jsx("stop", { offset: "100%", stopColor: "#00FFFF" })] }) }), _jsx("text", { x: "32", y: "40", fontSize: "32", fontWeight: "700", textAnchor: "middle", fill: "url(#logoGradient)", fontFamily: "monospace", children: "XR7" }), _jsx("circle", { cx: "32", cy: "32", r: "30", stroke: "url(#logoGradient)", strokeWidth: "1.5", opacity: "0.3" })] }) }), _jsxs("h1", { className: "welcome-title", children: ["Welcome, ", _jsx("span", { className: "recipient-name", children: recipientName }), "."] }), _jsx("p", { className: "welcome-subtitle", children: "Your private XR7 analysis session is now unlocked." }), _jsxs("div", { className: "trust-messaging", children: [_jsxs("div", { className: "trust-item", children: [_jsx("svg", { className: "checkmark", width: "20", height: "20", viewBox: "0 0 20 20", fill: "none", children: _jsx("path", { d: "M7 10L9 12L13 8", stroke: "#00FF88", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round" }) }), _jsx("span", { children: "This private portal is available by invitation only." })] }), _jsxs("div", { className: "trust-item", children: [_jsx("svg", { className: "checkmark", width: "20", height: "20", viewBox: "0 0 20 20", fill: "none", children: _jsx("path", { d: "M7 10L9 12L13 8", stroke: "#00FF88", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round" }) }), _jsx("span", { children: "Your personalized analysis session is secured and confidential." })] }), _jsxs("div", { className: "trust-item", children: [_jsx("svg", { className: "checkmark", width: "20", height: "20", viewBox: "0 0 20 20", fill: "none", children: _jsx("path", { d: "M7 10L9 12L13 8", stroke: "#00FF88", strokeWidth: "2", strokeLinecap: "round", strokeLinejoin: "round" }) }), _jsx("span", { children: "Access is limited to select creators and industry professionals." })] })] }), _jsxs("button", { className: "premium-button primary", onClick: handleProceed, children: ["Begin Your Analysis", _jsx("span", { className: "button-arrow", children: "\u2192" })] }), _jsxs("p", { className: "fine-print", children: ["This invitation is exclusive to ", recipientName, " and cannot be shared."] })] })] }));
};
export default InviteWelcomeScreen;
