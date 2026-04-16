from __future__ import annotations

import os
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class XR7Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./XR7.db")
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    celery_broker_url: str = os.getenv(
        "CELERY_BROKER_URL", os.getenv("REDIS_URL", "redis://redis:6379/0")
    )
    celery_result_backend: str = os.getenv(
        "CELERY_RESULT_BACKEND", os.getenv("REDIS_URL", "redis://redis:6379/1")
    )
    s3_endpoint_url: str | None = os.getenv("S3_ENDPOINT_URL")
    s3_region: str = os.getenv("S3_REGION", "us-east-1")
    s3_bucket: str = os.getenv("S3_BUCKET", "xr7-artifacts")
    s3_access_key_id: str | None = os.getenv("S3_ACCESS_KEY_ID")
    s3_secret_access_key: str | None = os.getenv("S3_SECRET_ACCESS_KEY")
    s3_use_ssl: bool = os.getenv("S3_USE_SSL", "0").strip().lower() in {"1", "true", "yes"}
    sync_requeue_seconds: int = int(os.getenv("XR7_SYNC_REQUEUE_SECONDS", "60"))
    plugin_allowed_prefixes_raw: str = os.getenv(
        "XR7_PLUGIN_ALLOWED_PREFIXES", "XR7.plugins,tests.plugins"
    )
    plugin_blocked_prefixes_raw: str = os.getenv(
        "XR7_PLUGIN_BLOCKED_PREFIXES", "os,sys,subprocess,builtins,importlib"
    )
    plugin_signature_secret: str = os.getenv("XR7_PLUGIN_SIGNATURE_SECRET", "")
    jwt_secret: str = os.getenv(
        "XR7_JWT_SECRET", os.getenv("JWT_SECRET", "dev-only-change-me-xr7-default-32b")
    )
    hubspot_enabled: bool = os.getenv("HUBSPOT_ENABLED", "0").strip().lower() in {
        "1",
        "true",
        "yes",
    }
    hubspot_base_url: str = os.getenv("HUBSPOT_BASE_URL", "https://api.hubapi.com")
    hubspot_api_key: str | None = os.getenv("HUBSPOT_API_KEY")
    hubspot_private_app_token: str | None = os.getenv("HUBSPOT_PRIVATE_APP_TOKEN")
    white_label_enabled: bool = os.getenv("XR7_WHITE_LABEL_ENABLED", "0").strip().lower() in {
        "1",
        "true",
        "yes",
    }
    xr7_env: str = os.getenv("XR7_ENV", "development").lower()

    @property
    def plugin_allowed_prefixes(self) -> tuple[str, ...]:
        return tuple(p.strip() for p in self.plugin_allowed_prefixes_raw.split(",") if p.strip())

    @property
    def plugin_blocked_prefixes(self) -> tuple[str, ...]:
        return tuple(p.strip() for p in self.plugin_blocked_prefixes_raw.split(",") if p.strip())

    def validate_production_secrets(self) -> None:
        """
        Validate that required secrets are set when XR7_ENV=production.

        Prevents accidental deployment with dev defaults or missing credentials.
        Called automatically when settings module is imported.
        """
        if self.xr7_env != "production":
            return

        errors = []

        # JWT secret must not be a dev default
        dev_jwt_defaults = {
            "dev-only-change-me-xr7-default-32b",
            "change-me-in-production",
            "change-me",
        }
        if not self.jwt_secret or self.jwt_secret in dev_jwt_defaults:
            errors.append(
                "XR7_JWT_SECRET must be set to a secure random value in production. "
                'Generate with: python3 -c "import secrets; print(secrets.token_urlsafe(48))"'
            )

        # S3 credentials required
        if not self.s3_access_key_id or self.s3_access_key_id == "minioadmin":
            errors.append("S3_ACCESS_KEY_ID must be set (not 'minioadmin') in production")

        if not self.s3_secret_access_key or self.s3_secret_access_key == "minioadmin":
            errors.append("S3_SECRET_ACCESS_KEY must be set (not 'minioadmin') in production")

        # Database must not be SQLite
        if self.database_url.startswith("sqlite"):
            errors.append(
                "DATABASE_URL must be PostgreSQL in production. "
                "SQLite is not suitable for production workloads."
            )

        # SMTP required for email notifications
        smtp_host = os.getenv("SMTP_HOST")
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")

        if not smtp_host or not smtp_user or not smtp_password:
            errors.append(
                "SMTP_HOST, SMTP_USER, and SMTP_PASSWORD are required in production "
                "for email notifications"
            )

        # Twilio required for SMS
        twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
        twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
        twilio_from = os.getenv("TWILIO_FROM_NUMBER")

        if not twilio_sid or not twilio_token or not twilio_from:
            errors.append(
                "TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_FROM_NUMBER "
                "are required in production for SMS notifications"
            )

        # Widget CORS must not be wildcard
        widget_origins = os.getenv("WIDGET_ALLOWED_ORIGINS", "*")
        if widget_origins == "*":
            errors.append(
                "WIDGET_ALLOWED_ORIGINS must not be '*' in production. "
                "Set to comma-separated list of allowed origins."
            )

        if errors:
            print("\n❌ PRODUCTION SECRET VALIDATION FAILED\n", file=sys.stderr)
            print(
                "XR7_ENV is set to 'production' but required secrets are missing or unsafe:\n",
                file=sys.stderr,
            )
            for i, error in enumerate(errors, 1):
                print(f"  {i}. {error}", file=sys.stderr)
            print("\nRefer to .env.example for all required variables.", file=sys.stderr)
            print("See CONTRIBUTING.md § Secret Management for guidance.\n", file=sys.stderr)
            sys.exit(1)


settings = XR7Settings()

# Validate production secrets on module import
settings.validate_production_secrets()
