from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class PartnerProviderConfig:
    provider: str
    env_prefix: str
    normalized_contract: str


SUPPORTED_PARTNER_PROVIDERS: dict[str, PartnerProviderConfig] = {
    "stripe_connect": PartnerProviderConfig("stripe_connect", "STRIPE_CONNECT", "payments.v1"),
    "chartmetric": PartnerProviderConfig("chartmetric", "CHARTMETRIC", "analytics.v1"),
    "songtrust": PartnerProviderConfig("songtrust", "SONGTRUST", "publishing.v1"),
    "tunecore": PartnerProviderConfig("tunecore", "TUNECORE", "distribution.v1"),
    "distrokid": PartnerProviderConfig("distrokid", "DISTROKID", "distribution.v1"),
    "soundcloud": PartnerProviderConfig("soundcloud", "SOUNDCLOUD", "social.v1"),
    "ascap": PartnerProviderConfig("ascap", "ASCAP", "pro.v1"),
    "bmi": PartnerProviderConfig("bmi", "BMI", "pro.v1"),
    "sesac": PartnerProviderConfig("sesac", "SESAC", "pro.v1"),
}


def normalize_provider(provider: str) -> str:
    key = provider.strip().lower().replace("-", "_").replace(" ", "_")
    if key == "stripe":
        key = "stripe_connect"
    return key


def provider_status(provider: str) -> dict:
    key = normalize_provider(provider)
    config = SUPPORTED_PARTNER_PROVIDERS.get(key)
    if not config:
        return {"provider": key, "supported": False, "status": "unsupported_provider"}

    token_set = bool(
        os.getenv(f"{config.env_prefix}_TOKEN") or os.getenv(f"{config.env_prefix}_API_KEY")
    )
    endpoint_set = bool(os.getenv(f"{config.env_prefix}_BASE_URL"))

    return {
        "provider": config.provider,
        "supported": True,
        "status": "ready" if token_set else "missing_credentials",
        "retry_queue": "xr7.connector.retry",
        "dead_letter_queue": "xr7.connector.dlq",
        "schema_contract": config.normalized_contract,
        "endpoint_configured": endpoint_set,
        "credentials_configured": token_set,
    }
