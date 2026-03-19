import React, { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import "./InviteWelcomeScreen.css";

interface WelcomeScreenProps {
  onProceed?: (recipientName: string) => void;
}

export const InviteWelcomeScreen: React.FC<WelcomeScreenProps> = ({
  onProceed,
}) => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [recipientName, setRecipientName] = useState<string>("");
  const [isValid, setIsValid] = useState<boolean | null>(null);
  const [error, setError] = useState<string | null>(null);
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

  const validateInvite = async (token: string) => {
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
      } else {
        setIsValid(false);
        setError(
          data.error || "This invitation is no longer active. Please request a new private session."
        );
      }
    } catch (err) {
      setIsValid(false);
      setError("Failed to validate invitation");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleProceed = () => {
    if (onProceed) {
      onProceed(recipientName);
    } else {
      // Navigate to onboarding with token
      navigate(`/onboarding?invite_token=${inviteToken}`, { replace: true });
    }
  };

  if (isLoading) {
    return (
      <div className="invite-welcome-container loading">
        <div className="xr7-logo breathing">
          <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
            <text
              x="32"
              y="40"
              fontSize="32"
              fontWeight="700"
              textAnchor="middle"
              fill="#00FF88"
              fontFamily="monospace"
            >
              XR7
            </text>
          </svg>
        </div>
        <p className="status-text">Verifying your invitation...</p>
      </div>
    );
  }

  if (!isValid || error) {
    return (
      <div className="invite-welcome-container error">
        <div className="xr7-logo">
          <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
            <circle cx="32" cy="32" r="30" stroke="#FF4444" strokeWidth="2" />
            <text
              x="32"
              y="40"
              fontSize="28"
              fontWeight="700"
              textAnchor="middle"
              fill="#FF4444"
              fontFamily="monospace"
            >
              ✕
            </text>
          </svg>
        </div>
        <h1>Invitation Expired</h1>
        <p className="error-message">{error}</p>
        <button
          className="premium-button secondary"
          onClick={() => navigate("/")}
        >
          Return to Home
        </button>
      </div>
    );
  }

  return (
    <div className="invite-welcome-container">
      {/* Premium dark background with subtle gradient */}
      <div className="background-animation"></div>

      {/* Content */}
      <div className="welcome-content">
        {/* XR7 Logo with breathing animation */}
        <div className="xr7-logo breathing">
          <svg width="80" height="80" viewBox="0 0 64 64" fill="none">
            <defs>
              <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#00FF88" />
                <stop offset="100%" stopColor="#00FFFF" />
              </linearGradient>
            </defs>
            <text
              x="32"
              y="40"
              fontSize="32"
              fontWeight="700"
              textAnchor="middle"
              fill="url(#logoGradient)"
              fontFamily="monospace"
            >
              XR7
            </text>
            <circle
              cx="32"
              cy="32"
              r="30"
              stroke="url(#logoGradient)"
              strokeWidth="1.5"
              opacity="0.3"
            />
          </svg>
        </div>

        {/* Greeting */}
        <h1 className="welcome-title">
          Welcome, <span className="recipient-name">{recipientName}</span>.
        </h1>

        <p className="welcome-subtitle">
          Your private XR7 analysis session is now unlocked.
        </p>

        {/* Trust messaging */}
        <div className="trust-messaging">
          <div className="trust-item">
            <svg className="checkmark" width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path
                d="M7 10L9 12L13 8"
                stroke="#00FF88"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <span>This private portal is available by invitation only.</span>
          </div>
          <div className="trust-item">
            <svg className="checkmark" width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path
                d="M7 10L9 12L13 8"
                stroke="#00FF88"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <span>Your personalized analysis session is secured and confidential.</span>
          </div>
          <div className="trust-item">
            <svg className="checkmark" width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path
                d="M7 10L9 12L13 8"
                stroke="#00FF88"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <span>Access is limited to select creators and industry professionals.</span>
          </div>
        </div>

        {/* CTA Button */}
        <button className="premium-button primary" onClick={handleProceed}>
          Begin Your Analysis
          <span className="button-arrow">→</span>
        </button>

        {/* Fine print */}
        <p className="fine-print">
          This invitation is exclusive to {recipientName} and cannot be shared.
        </p>
      </div>
    </div>
  );
};

export default InviteWelcomeScreen;
