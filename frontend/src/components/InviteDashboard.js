import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useState } from "react";
import "./InviteDashboard.css";
export const InviteDashboard = () => {
    const [recipientName, setRecipientName] = useState("");
    const [recipientEmail, setRecipientEmail] = useState("");
    const [role, setRole] = useState("artist");
    const [campaign, setCampaign] = useState("");
    const [isVip, setIsVip] = useState(false);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [invites, setInvites] = useState([]);
    const [invitesLoading, setInvitesLoading] = useState(false);
    const [activeTab, setActiveTab] = useState("generate");
    const [analytics, setAnalytics] = useState(null);
    useEffect(() => {
        loadInvites();
        loadAnalytics();
    }, []);
    const loadInvites = async () => {
        setInvitesLoading(true);
        try {
            const response = await fetch("/api/invites/?limit=50&offset=0");
            const data = await response.json();
            setInvites(data.invites);
        }
        catch (err) {
            console.error("Failed to load invites:", err);
        }
        finally {
            setInvitesLoading(false);
        }
    };
    const loadAnalytics = async () => {
        try {
            const response = await fetch("/api/invites/analytics/summary?days=30");
            const data = await response.json();
            setAnalytics(data);
        }
        catch (err) {
            console.error("Failed to load analytics:", err);
        }
    };
    const handleQuickGenerate = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setResult(null);
        try {
            const response = await fetch("/api/invites/dashboard/quick-generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    recipient_name: recipientName,
                    recipient_email: recipientEmail || null,
                    role,
                    campaign: campaign || "manual_generation",
                }),
            });
            const data = await response.json();
            if (!response.ok) {
                setError(data.detail || "Failed to generate invite");
            }
            else {
                setResult(data);
                // Reset form
                setRecipientName("");
                setRecipientEmail("");
                setRole("artist");
                setCampaign("");
                setIsVip(false);
                // Reload invites
                loadInvites();
            }
        }
        catch (err) {
            setError("Network error generating invite");
            console.error(err);
        }
        finally {
            setLoading(false);
        }
    };
    const copyToClipboard = (text) => {
        navigator.clipboard.writeText(text).then(() => {
            alert("Link copied to clipboard!");
        });
    };
    return (_jsxs("div", { className: "invite-dashboard", children: [_jsx("h1", { children: "Invite Management Dashboard" }), _jsx("p", { className: "subtitle", children: "Generate and manage private XR7 invites for selected creators." }), _jsxs("div", { className: "tabs", children: [_jsx("button", { className: `tab ${activeTab === "generate" ? "active" : ""}`, onClick: () => setActiveTab("generate"), children: "Generate Invite" }), _jsxs("button", { className: `tab ${activeTab === "list" ? "active" : ""}`, onClick: () => setActiveTab("list"), children: ["All Invites (", invites.length, ")"] }), _jsx("button", { className: `tab ${activeTab === "analytics" ? "active" : ""}`, onClick: () => setActiveTab("analytics"), children: "Analytics" })] }), activeTab === "generate" && (_jsxs("div", { className: "tab-content", children: [_jsxs("form", { onSubmit: handleQuickGenerate, className: "generate-form", children: [_jsxs("div", { className: "form-group", children: [_jsx("label", { children: "Recipient Name" }), _jsx("input", { type: "text", value: recipientName, onChange: (e) => setRecipientName(e.target.value), placeholder: "e.g., Jane Smith", required: true })] }), _jsxs("div", { className: "form-group", children: [_jsx("label", { children: "Email Address (optional)" }), _jsx("input", { type: "email", value: recipientEmail, onChange: (e) => setRecipientEmail(e.target.value), placeholder: "jane@example.com" })] }), _jsxs("div", { className: "form-row", children: [_jsxs("div", { className: "form-group", children: [_jsx("label", { children: "Role" }), _jsxs("select", { value: role, onChange: (e) => setRole(e.target.value), children: [_jsx("option", { value: "artist", children: "Artist" }), _jsx("option", { value: "writer", children: "Writer" }), _jsx("option", { value: "director", children: "Director" }), _jsx("option", { value: "actor", children: "Actor" }), _jsx("option", { value: "studio", children: "Studio" }), _jsx("option", { value: "manager", children: "Manager" }), _jsx("option", { value: "agent", children: "Agent" })] })] }), _jsxs("div", { className: "form-group", children: [_jsx("label", { children: "Campaign" }), _jsx("input", { type: "text", value: campaign, onChange: (e) => setCampaign(e.target.value), placeholder: "e.g., vip_kickoff" })] })] }), _jsx("div", { className: "form-group checkbox", children: _jsxs("label", { children: [_jsx("input", { type: "checkbox", checked: isVip, onChange: (e) => setIsVip(e.target.checked) }), "Grant VIP Status"] }) }), error && _jsx("div", { className: "error-message", children: error }), _jsx("button", { type: "submit", className: "submit-button", disabled: loading, children: loading ? "Generating..." : "Generate Invite Link" })] }), result && (_jsxs("div", { className: "result-card success", children: [_jsxs("div", { className: "result-header", children: [_jsx("h3", { children: "\u2713 Invite Generated Successfully" }), _jsxs("p", { className: "result-id", children: ["ID: ", result.invite_id] })] }), _jsxs("div", { className: "result-details", children: [_jsxs("p", { children: [_jsx("strong", { children: "Recipient:" }), " ", result.recipient_name] }), _jsxs("p", { children: [_jsx("strong", { children: "Expires:" }), " ", new Date(result.expires_at).toLocaleString()] })] }), _jsxs("div", { className: "result-link-section", children: [_jsx("label", { children: "Invite Link:" }), _jsxs("div", { className: "link-box", children: [_jsx("code", { children: result.invite_link }), _jsx("button", { className: "copy-button", onClick: () => copyToClipboard(result.invite_link), children: "Copy" })] })] }), _jsx("p", { className: "result-hint", children: "Share this link with the creator. It's exclusive to them and expires in 72 hours." })] }))] })), activeTab === "list" && (_jsx("div", { className: "tab-content", children: invitesLoading ? (_jsx("p", { className: "loading-text", children: "Loading invites..." })) : invites.length > 0 ? (_jsx("div", { className: "invites-table", children: _jsxs("table", { children: [_jsx("thead", { children: _jsxs("tr", { children: [_jsx("th", { children: "Recipient Name" }), _jsx("th", { children: "Email" }), _jsx("th", { children: "Status" }), _jsx("th", { children: "Created" }), _jsx("th", { children: "VIP" })] }) }), _jsx("tbody", { children: invites.map((invite) => (_jsxs("tr", { children: [_jsx("td", { children: invite.recipient_name }), _jsx("td", { children: invite.recipient_email || "—" }), _jsx("td", { children: _jsx("span", { className: `status-badge ${invite.status}`, children: invite.status }) }), _jsx("td", { children: new Date(invite.created_at).toLocaleDateString() }), _jsx("td", { children: invite.is_vip ? "✓" : "—" })] }, invite.id))) })] }) })) : (_jsx("p", { className: "loading-text", children: "No invites yet. Generate one above." })) })), activeTab === "analytics" && (_jsx("div", { className: "tab-content", children: analytics ? (_jsxs("div", { className: "analytics-grid", children: [_jsxs("div", { className: "stat-card", children: [_jsx("h4", { children: "Invites Created" }), _jsx("p", { className: "stat-value", children: analytics.invites_created })] }), _jsxs("div", { className: "stat-card", children: [_jsx("h4", { children: "Invites Sent" }), _jsx("p", { className: "stat-value", children: analytics.invites_sent })] }), _jsxs("div", { className: "stat-card", children: [_jsx("h4", { children: "Invites Opened" }), _jsx("p", { className: "stat-value", children: analytics.invites_opened })] }), _jsxs("div", { className: "stat-card", children: [_jsx("h4", { children: "Invites Redeemed" }), _jsx("p", { className: "stat-value", children: analytics.invites_redeemed })] }), _jsxs("div", { className: "stat-card", children: [_jsx("h4", { children: "Open Rate" }), _jsxs("p", { className: "stat-value", children: [analytics.open_rate_percent, "%"] })] }), _jsxs("div", { className: "stat-card", children: [_jsx("h4", { children: "Redemption Rate" }), _jsxs("p", { className: "stat-value", children: [analytics.redemption_rate_percent, "%"] })] })] })) : (_jsx("p", { className: "loading-text", children: "Loading analytics..." })) }))] }));
};
export default InviteDashboard;
