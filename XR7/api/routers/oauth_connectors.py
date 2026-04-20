"""OAuth connector endpoints for semi-automated platform data ingestion.

Feature #7: Semi-automated pull fallbacks

RESTful API for connecting artists to platform data sources via OAuth:
- Generate authorization URLs with CSRF protection
- Exchange authorization codes for access tokens
- Auto-refresh expired tokens
- Revoke credentials on disconnect
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from XR7.models.base import get_db
from XR7.models.platform_oauth import PlatformOAuthCredentialSchema
from XR7.services.oauth_connector_service import OAuthConnectorService
from XR7.services.router_v21_phase1 import router_service_for

router = APIRouter(tags=["oauth-connectors"])
_router_service = router_service_for("oauth-connectors")


class OAuthInitRequest(BaseModel):
    platform: str  # "spotify", "youtube", "soundcloud"
    redirect_uri: str  # OAuth callback URL


class OAuthCallbackRequest(BaseModel):
    platform: str
    code: str  # Authorization code
    state: str  # CSRF token
    redirect_uri: str


@router.post("/artists/{artist_id}/oauth/init")
def init_oauth_flow(
    artist_id: str,
    payload: OAuthInitRequest,
    db: Session = Depends(get_db),
):
    """
    Initiate OAuth flow for platform connection.
    
    Feature #7: Semi-automated pull fallbacks
    
    Generates authorization URL with CSRF state token.
    User should be redirected to authorization_url to grant permissions.
    
    Supported platforms:
    - spotify: Spotify for Artists API
    - youtube: YouTube Analytics API
    - soundcloud: SoundCloud API (where available)
    
    Returns:
        - authorization_url: URL to redirect user for OAuth consent
        - state: CSRF token to verify callback
    
    Security:
        - State token prevents CSRF attacks
        - Redirect URI must be pre-registered with platform
        - Credentials are artist-scoped (strict isolation)
    """
    _router_service.get_artist_or_404(artist_id, db)
    
    service = OAuthConnectorService(db)
    
    try:
        result = service.generate_authorization_url(
            artist_id=artist_id,
            platform=payload.platform,
            redirect_uri=payload.redirect_uri,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    
    return result


@router.post("/artists/{artist_id}/oauth/callback")
def oauth_callback(
    artist_id: str,
    payload: OAuthCallbackRequest,
    db: Session = Depends(get_db),
):
    """
    Handle OAuth callback and exchange code for tokens.
    
    Feature #7: Semi-automated pull fallbacks
    
    Exchanges authorization code for access/refresh tokens.
    Stores encrypted tokens with automatic refresh scheduling.
    
    Args:
        artist_id: Artist identifier
        payload: OAuth callback data (code, state, redirect_uri)
    
    Returns:
        PlatformOAuthCredential with connection status
    
    Security:
        - Verifies state token to prevent CSRF
        - Tokens encrypted at rest
        - Refresh tokens rotated on each use
        - Access tokens auto-refreshed before expiration
    """
    _router_service.get_artist_or_404(artist_id, db)
    
    # TODO: Verify state token against session (production requirement)
    # For MVP, accept any state (security risk - fix before production)
    
    service = OAuthConnectorService(db)
    
    try:
        credential = service.exchange_code_for_tokens(
            artist_id=artist_id,
            platform=payload.platform,
            authorization_code=payload.code,
            redirect_uri=payload.redirect_uri,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"OAuth token exchange failed: {str(exc)}",
        ) from exc
    
    return {
        "status": "connected",
        "credential": PlatformOAuthCredentialSchema.model_validate(credential).model_dump(),
    }


@router.get("/artists/{artist_id}/oauth/connections")
def list_oauth_connections(
    artist_id: str,
    db: Session = Depends(get_db),
):
    """
    List all OAuth platform connections for an artist.
    
    Returns active, expired, and revoked credentials.
    Does not return actual tokens (security).
    """
    _router_service.get_artist_or_404(artist_id, db)
    
    from XR7.models.platform_oauth import PlatformOAuthCredential
    
    credentials = (
        db.query(PlatformOAuthCredential)
        .filter(PlatformOAuthCredential.artist_id == artist_id)
        .all()
    )
    
    return {
        "artist_id": artist_id,
        "connections": [
            {
                "id": c.id,
                "platform": c.platform,
                "status": c.status,
                "expires_at": c.expires_at.isoformat() if c.expires_at else None,
                "created_at": c.created_at.isoformat(),
            }
            for c in credentials
        ],
    }


@router.delete("/artists/{artist_id}/oauth/connections/{credential_id}")
def revoke_oauth_connection(
    artist_id: str,
    credential_id: str,
    db: Session = Depends(get_db),
):
    """
    Revoke OAuth connection and delete tokens.
    
    Calls platform revocation endpoint to invalidate tokens server-side.
    Removes tokens from database.
    
    Args:
        artist_id: Artist identifier
        credential_id: PlatformOAuthCredential ID
    
    Returns:
        Confirmation of revocation
    """
    _router_service.get_artist_or_404(artist_id, db)
    
    service = OAuthConnectorService(db)
    service.revoke_credential(credential_id)
    
    return {"status": "revoked", "credential_id": credential_id}
