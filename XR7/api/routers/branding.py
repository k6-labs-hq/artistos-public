from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from XR7.models.base import get_db
from XR7.models.branding_profile import BrandingHelpArticle, BrandingProfile
from XR7.services.branding import (
    apply_brand_placeholders,
    branding_metadata,
    communication_templates,
    get_branding_profile,
    org_help_articles,
)

router = APIRouter(tags=["branding"])


class BrandingProfileUpsertRequest(BaseModel):
    display_name: str = "XR7"
    logo_url: str = "https://assets.xr7.ai/logo.svg"
    primary_color: str = "#1f7a5a"
    secondary_color: str = "#2f9c74"
    accent_color: str = "#f59e0b"
    dashboard_header_text: str = "Artist Recovery Dashboard"
    dashboard_footer_text: str = "Powered by XR7 Engine"
    support_email: str = "support@xr7.ai"
    support_phone: str = "+1-800-XR7-HELP"
    legal_disclaimer: str = (
        "Forecasts and recovery estimates are provided for operational guidance only. "
        "Actual outcomes may vary based on payer behavior, legal deadlines, and data quality."
    )
    custom_domain: str | None = None
    white_label_enabled: bool = False


class BrandingProfilePatchRequest(BaseModel):
    display_name: str | None = None
    logo_url: str | None = None
    primary_color: str | None = None
    secondary_color: str | None = None
    accent_color: str | None = None
    dashboard_header_text: str | None = None
    dashboard_footer_text: str | None = None
    support_email: str | None = None
    support_phone: str | None = None
    legal_disclaimer: str | None = None
    custom_domain: str | None = None
    white_label_enabled: bool | None = None


class HelpArticleCreateRequest(BaseModel):
    title: str
    body: str
    category: str = "faq"


@router.get("/branding/{org_id}")
def get_branding(org_id: str, db: Session = Depends(get_db)):
    brand = get_branding_profile(db, org_id)
    return {
        "org_id": org_id,
        "profile": brand,
        "branding": branding_metadata(brand),
    }


@router.post("/branding/{org_id}")
def create_branding(
    org_id: str, payload: BrandingProfileUpsertRequest, db: Session = Depends(get_db)
):
    existing = db.query(BrandingProfile).filter(BrandingProfile.org_id == org_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Branding profile already exists")

    row = BrandingProfile(org_id=org_id, **payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    merged = get_branding_profile(db, org_id)
    return {
        "org_id": org_id,
        "profile": merged,
        "branding": branding_metadata(merged),
    }


@router.patch("/branding/{org_id}")
def patch_branding(
    org_id: str, payload: BrandingProfilePatchRequest, db: Session = Depends(get_db)
):
    row = db.query(BrandingProfile).filter(BrandingProfile.org_id == org_id).first()
    if not row:
        row = BrandingProfile(org_id=org_id)
        db.add(row)

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(row, key, value)

    db.commit()
    db.refresh(row)
    merged = get_branding_profile(db, org_id)
    return {
        "org_id": org_id,
        "profile": merged,
        "branding": branding_metadata(merged),
    }


@router.get("/branding/{org_id}/help-articles")
def list_help_articles(org_id: str, db: Session = Depends(get_db)):
    brand = get_branding_profile(db, org_id)
    return {
        "org_id": org_id,
        "branding": branding_metadata(brand),
        "articles": org_help_articles(db, org_id),
    }


@router.post("/branding/{org_id}/help-articles")
def create_help_article(
    org_id: str, payload: HelpArticleCreateRequest, db: Session = Depends(get_db)
):
    brand = get_branding_profile(db, org_id)
    if not bool(brand.get("white_label_enabled")):
        raise HTTPException(
            status_code=403, detail="Help article uploads require white_label_enabled=true"
        )

    row = BrandingHelpArticle(
        org_id=org_id,
        title=payload.title,
        body=payload.body,
        category=payload.category,
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    return {
        "org_id": org_id,
        "branding": branding_metadata(brand),
        "article": {
            "id": row.id,
            "title": row.title,
            "body": row.body,
            "category": row.category,
        },
    }


@router.get("/ui/shell", response_class=HTMLResponse)
def ui_shell(org_id: str = Query(default="xr7-default"), db: Session = Depends(get_db)):
    brand = get_branding_profile(db, org_id)
    nav = [
        {"label": "Dashboard", "href": "/artists/{artist_id}/dashboard"},
        {"label": "Forecasting", "href": "/artists/{artist_id}/earnings/forecast"},
        {"label": "Evidence", "href": "/claims/{claim_id}/evidence/export"},
        {"label": "Uploads", "href": "/artists/{artist_id}/ingestion/upload-any"},
    ]
    nav_html = "".join(f'<a href="{item["href"]}">{item["label"]}</a>' for item in nav)
    shell = f"""
<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{{{{BRAND.NAME}}}} Shell</title>
  <style>
    :root {{
      --brand-primary: {{{{BRAND.PRIMARY_COLOR}}}};
      --brand-secondary: {brand.get('secondary_color')};
      --brand-accent: {brand.get('accent_color')};
    }}
    body {{ font-family: \"Avenir Next\", \"Trebuchet MS\", sans-serif; margin: 0; background: #f8fafc; }}
    header {{ background: linear-gradient(135deg, var(--brand-primary), var(--brand-secondary)); color: #fff; padding: 16px 20px; display:flex; justify-content:space-between; align-items:center; gap:10px; }}
    .logo {{ display:flex; align-items:center; gap:10px; font-weight:700; }}
    .logo img {{ width: 34px; height:34px; object-fit: contain; background: #fff; border-radius: 8px; }}
    nav {{ display:flex; gap: 12px; flex-wrap: wrap; }}
    nav a {{ color:#fff; text-decoration:none; font-size: 14px; border:1px solid rgba(255,255,255,.35); padding:6px 10px; border-radius: 999px; }}
    main {{ padding: 20px; }}
    .card {{ background:#fff; border:1px solid #dbe2ea; border-radius:14px; padding:16px; }}
    .splash {{ font-size: 24px; font-weight: 800; margin-bottom: 8px; }}
    footer {{ padding:14px 20px; color:#475569; font-size:13px; }}
  </style>
</head>
<body>
  <header>
    <div class=\"logo\"><img src=\"{{{{BRAND.LOGO}}}}\" alt=\"brand logo\" /><span>{{{{BRAND.NAME}}}}</span></div>
    <nav>{nav_html}</nav>
  </header>
  <main>
    <section class=\"card\">
      <div class=\"splash\">{{{{BRAND.NAME}}}} Dashboard</div>
      <p>{brand.get('dashboard_header_text')}</p>
      <p><strong>Support:</strong> {{{{BRAND.SUPPORT_EMAIL}}}}</p>
      <p><strong>Custom Domain:</strong> {brand.get('custom_domain') or 'not configured'}</p>
      <hr />
      <h3>UI Surfaces</h3>
      <ul>
        <li>Login / Onboarding UI</li>
        <li>Statement Upload UI</li>
        <li>Forecasting UI</li>
        <li>Evidence Packet UI</li>
        <li>Mobile splash + push sender branding</li>
      </ul>
      <p>{{{{BRAND.LEGAL_DISCLAIMER}}}}</p>
    </section>
  </main>
  <footer>{brand.get('dashboard_footer_text')}</footer>
</body>
</html>
"""
    rendered = apply_brand_placeholders(shell, brand)
    return HTMLResponse(content=rendered)


@router.get("/branding/{org_id}/templates")
def branding_templates(org_id: str, db: Session = Depends(get_db)):
    brand = get_branding_profile(db, org_id)
    templates = communication_templates()
    return {
        "org_id": org_id,
        "templates": templates,
        "rendered_templates": apply_brand_placeholders(templates, brand),
        "branding": branding_metadata(brand),
        "placeholders": {
            "name": "{{BRAND.NAME}}",
            "logo": "{{BRAND.LOGO}}",
            "primary_color": "{{BRAND.PRIMARY_COLOR}}",
            "support_email": "{{BRAND.SUPPORT_EMAIL}}",
            "legal_disclaimer": "{{BRAND.LEGAL_DISCLAIMER}}",
        },
    }
