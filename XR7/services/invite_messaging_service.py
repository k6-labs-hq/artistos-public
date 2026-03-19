"""Automated messaging templates for invites."""

from __future__ import annotations

from typing import Optional
from enum import Enum

from XR7.models.invite import InviteChannel, InviteRole


class MessageTemplate(Enum):
    """Message template types."""
    EMAIL_INVITATION = "email_invitation"
    EMAIL_INQUIRY_RESPONSE = "email_inquiry_response"
    INSTAGRAM_DM = "instagram_dm"
    SMS = "sms"


class InviteMessagingService:
    """Generate personalized invite messages for different channels."""

    @staticmethod
    def get_email_invitation(
        recipient_name: str,
        invite_link: str,
        custom_message: Optional[str] = None,
        sender_name: str = "XR7 Team",
    ) -> dict:
        """Generate personalized email invitation.

        Returns:
            Dict with subject, body_text, body_html
        """
        subject = f"{recipient_name}, Your Private XR7 Analysis Session Is Ready"

        body_text = f"""\
Hello {recipient_name},

Your private XR7 analysis session has been unlocked.

Access your personalized portal here:
{invite_link}

This link is exclusive to you and cannot be shared.

{f"Note: {custom_message}" if custom_message else ""}

If you have any questions, please reach out.

Best regards,
{sender_name}
XR7 Engine — Artist Earnings Accuracy Platform
"""

        body_html = f"""\
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .logo {{ font-size: 28px; font-weight: 700; color: #00ff88; font-family: monospace; }}
        .greeting {{ font-size: 20px; font-weight: 600; color: #1a1a3e; margin-bottom: 20px; }}
        .body {{ color: #666; line-height: 1.6; margin-bottom: 24px; }}
        .cta-button {{
            display: inline-block;
            background: linear-gradient(135deg, #00ff88 0%, #00ffff 100%);
            color: #0a0e27;
            padding: 14px 32px;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 700;
            margin: 24px 0;
        }}
        .link-text {{ font-family: monospace; background: #f5f5f5; padding: 12px; border-radius: 4px; word-break: break-all; }}
        .exclusivity {{ background: rgba(0, 255, 136, 0.05); padding: 16px; border-left: 4px solid #00ff88; border-radius: 4px; margin: 20px 0; font-size: 14px; color: #666; }}
        .footer {{ font-size: 12px; color: #999; margin-top: 40px; border-top: 1px solid #e0e0e0; padding-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">XR7</div>
        </div>

        <p class="greeting">Welcome, {recipient_name}.</p>

        <p class="body">
            Your private XR7 analysis session has been unlocked.
            Access your personalized portal here:
        </p>

        <a href="{invite_link}" class="cta-button">Begin Your Analysis</a>

        <p class="body">Or copy this link:</p>
        <div class="link-text">{invite_link}</div>

        <div class="exclusivity">
            <strong>Exclusivity Notice:</strong> This private portal is available by invitation only.
            Your personalized analysis session is secured and confidential.
            This link is exclusive to you and cannot be shared.
        </div>

        {f'<p class="body"><strong>Message:</strong> {custom_message}</p>' if custom_message else ''}

        <div class="footer">
            <p>
                XR7 Engine — Artist Earnings Accuracy Platform<br>
                Questions? Reply to this email or visit us at xr7.app
            </p>
        </div>
    </div>
</body>
</html>
"""

        return {
            "subject": subject,
            "body_text": body_text,
            "body_html": body_html,
        }

    @staticmethod
    def get_email_inquiry_response(
        recipient_name: str,
        invite_link: str,
        inquiry_context: Optional[str] = None,
    ) -> dict:
        """Generate auto-response email to inquiry.

        Used when someone emails inquiries about analysis/royalties.
        """
        subject = "Your Private XR7 Analysis Session Is Ready"

        context_text = ""
        if inquiry_context:
            context_mapping = {
                "royalties": "earnings analysis",
                "analysis": "royalty analysis",
                "help": "support with your earnings",
                "billing": "billing and payment information",
                "tv/film": "TV/Film earnings analysis",
            }
            context = context_mapping.get(inquiry_context.lower(), "information")
            context_text = f"We received your inquiry about {context}. We're excited to help.\n\n"

        body_text = f"""\
Hello {recipient_name},

{context_text}Your private XR7 analysis session has been created.

Access your personalized portal here:
{invite_link}

XR7 will give you complete visibility into your earnings,
compensation, and performance across all platforms and territories.

This link is exclusive to you and cannot be shared. It expires in 72 hours.

Ready to explore?

Best regards,
XR7 Team
"""

        body_html = f"""\
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .logo {{ font-size: 28px; font-weight: 700; color: #00ff88; font-family: monospace; }}
        .greeting {{ font-size: 18px; font-weight: 600; color: #1a1a3e; margin-bottom: 20px; }}
        .body {{ color: #666; line-height: 1.6; margin-bottom: 20px; }}
        .features {{ background: rgba(0, 255, 136, 0.05); padding: 16px; border-radius: 4px; margin: 20px 0; }}
        .features li {{ margin: 8px 0; color: #666; }}
        .cta-button {{
            display: inline-block;
            background: linear-gradient(135deg, #00ff88 0%, #00ffff 100%);
            color: #0a0e27;
            padding: 14px 32px;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 700;
            margin: 24px 0;
        }}
        .footer {{ font-size: 12px; color: #999; margin-top: 40px; border-top: 1px solid #e0e0e0; padding-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">XR7</div>
        </div>

        <p class="greeting">Hello {recipient_name},</p>

        {f'<p class="body">{context_text}</p>' if context_text else ''}

        <p class="body">
            Your private XR7 analysis session is ready.
            Get instant access to complete visibility of your earnings.
        </p>

        <a href="{invite_link}" class="cta-button">Access Your Analysis</a>

        <div class="features">
            <strong>What You'll See:</strong>
            <ul>
                <li>Complete earnings breakdown by platform</li>
                <li>Royalty and compensation details</li>
                <li>Performance analytics</li>
                <li>Territory-by-territory data</li>
            </ul>
        </div>

        <p class="body" style="font-size: 12px; color: #999;">
            This link is exclusive to you and cannot be shared.
            It expires in 72 hours.
        </p>

        <div class="footer">
            <p>
                Questions? We're here to help.<br>
                XR7 Engine — Artist Earnings Accuracy Platform
            </p>
        </div>
    </div>
</body>
</html>
"""

        return {
            "subject": subject,
            "body_text": body_text,
            "body_html": body_html,
        }

    @staticmethod
    def get_instagram_dm(recipient_name: str, invite_link: str) -> str:
        """Generate Instagram DM auto-response.

        Keep under 300 chars for DM limit (can be split if needed).
        """
        return (
            f"Your private XR7 analysis session is ready, {recipient_name}. "
            f"This link is exclusive to you: {invite_link}\n"
            f"Begin uploading your statements whenever you're ready."
        )

    @staticmethod
    def get_sms(recipient_name: str, invite_link: str) -> str:
        """Generate SMS message.

        Keep under 160 chars (standard SMS limit).
        """
        return (
            f"XR7: Your private analysis session is unlocked: {invite_link}"
        )

    @staticmethod
    def get_message_by_channel(
        channel: InviteChannel,
        recipient_name: str,
        invite_link: str,
        **kwargs,
    ) -> dict | str:
        """Get message template for the given channel.

        Args:
            channel: InviteChannel enum
            recipient_name: Invitee name
            invite_link: Full invite URL
            **kwargs: Additional template parameters

        Returns:
            Template dict (email) or string (SMS/IG)
        """
        if channel == InviteChannel.EMAIL:
            return InviteMessagingService.get_email_invitation(
                recipient_name,
                invite_link,
                custom_message=kwargs.get("custom_message"),
            )
        elif channel == InviteChannel.INSTAGRAM_DM:
            return InviteMessagingService.get_instagram_dm(recipient_name, invite_link)
        elif channel == InviteChannel.SMS:
            return InviteMessagingService.get_sms(recipient_name, invite_link)
        else:
            # Default to email
            return InviteMessagingService.get_email_invitation(
                recipient_name, invite_link
            )


# Singleton
messaging_service = InviteMessagingService()
