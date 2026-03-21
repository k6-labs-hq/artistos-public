"""Configuration layer for the XR7 fingerprinting subsystem.

All provider credentials and routing rules are driven by environment
variables.  Never hard-code secrets.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


def _env_bool(key: str, default: str = "0") -> bool:
    return os.getenv(key, default).strip().lower() in {"1", "true", "yes"}


def _env_int(key: str, default: int) -> int:
    raw = os.getenv(key)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_float(key: str, default: float) -> float:
    raw = os.getenv(key)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


# ---------------------------------------------------------------------------
# Per-provider configs
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ACRCloudConfig:
    """ACRCloud Audio Recognition Service configuration.

    Phase 2 provider.  Set XR7_ACRCLOUD_ENABLED=1 to activate.
    """

    enabled: bool = field(default_factory=lambda: _env_bool("XR7_ACRCLOUD_ENABLED"))
    access_key: str = field(default_factory=lambda: os.getenv("ACRCLOUD_ACCESS_KEY", ""))
    access_secret: str = field(default_factory=lambda: os.getenv("ACRCLOUD_ACCESS_SECRET", ""))
    endpoint: str = field(
        default_factory=lambda: os.getenv(
            "ACRCLOUD_ENDPOINT", "https://identify-us-west-2.acrcloud.com"
        )
    )
    timeout_seconds: float = field(default_factory=lambda: _env_float("ACRCLOUD_TIMEOUT_SECONDS", 15.0))
    max_retries: int = field(default_factory=lambda: _env_int("ACRCLOUD_MAX_RETRIES", 3))
    rate_limit_per_minute: int = field(
        default_factory=lambda: _env_int("ACRCLOUD_RATE_LIMIT_PER_MINUTE", 100)
    )
    priority: int = field(default_factory=lambda: _env_int("ACRCLOUD_PRIORITY", 1))


@dataclass(frozen=True)
class AudibleMagicConfig:
    """Audible Magic enterprise API configuration.

    Phase 3 provider.  Set XR7_AUDIBLE_MAGIC_ENABLED=1 to activate.
    """

    enabled: bool = field(default_factory=lambda: _env_bool("XR7_AUDIBLE_MAGIC_ENABLED"))
    api_key: str = field(default_factory=lambda: os.getenv("AUDIBLE_MAGIC_API_KEY", ""))
    endpoint: str = field(
        default_factory=lambda: os.getenv(
            "AUDIBLE_MAGIC_ENDPOINT", "https://api.audiblemagic.com/v2"
        )
    )
    timeout_seconds: float = field(
        default_factory=lambda: _env_float("AUDIBLE_MAGIC_TIMEOUT_SECONDS", 20.0)
    )
    max_retries: int = field(default_factory=lambda: _env_int("AUDIBLE_MAGIC_MAX_RETRIES", 3))
    rate_limit_per_minute: int = field(
        default_factory=lambda: _env_int("AUDIBLE_MAGIC_RATE_LIMIT_PER_MINUTE", 60)
    )
    priority: int = field(default_factory=lambda: _env_int("AUDIBLE_MAGIC_PRIORITY", 2))


@dataclass(frozen=True)
class GracenoteConfig:
    """Gracenote MusicID / Media Recognition configuration.

    Phase 4 provider.  Set XR7_GRACENOTE_ENABLED=1 to activate.
    """

    enabled: bool = field(default_factory=lambda: _env_bool("XR7_GRACENOTE_ENABLED"))
    client_id: str = field(default_factory=lambda: os.getenv("GRACENOTE_CLIENT_ID", ""))
    user_id: str = field(default_factory=lambda: os.getenv("GRACENOTE_USER_ID", ""))
    api_key: str = field(default_factory=lambda: os.getenv("GRACENOTE_API_KEY", ""))
    endpoint: str = field(
        default_factory=lambda: os.getenv(
            "GRACENOTE_ENDPOINT", "https://c<CLIENTID>.web.cddbp.net/webapi/json/1.0"
        )
    )
    timeout_seconds: float = field(
        default_factory=lambda: _env_float("GRACENOTE_TIMEOUT_SECONDS", 20.0)
    )
    max_retries: int = field(default_factory=lambda: _env_int("GRACENOTE_MAX_RETRIES", 3))
    rate_limit_per_minute: int = field(
        default_factory=lambda: _env_int("GRACENOTE_RATE_LIMIT_PER_MINUTE", 60)
    )
    priority: int = field(default_factory=lambda: _env_int("GRACENOTE_PRIORITY", 3))


@dataclass(frozen=True)
class BMATConfig:
    """BMAT Musiio stub configuration (future provider)."""

    enabled: bool = field(default_factory=lambda: _env_bool("XR7_BMAT_ENABLED"))
    api_key: str = field(default_factory=lambda: os.getenv("BMAT_API_KEY", ""))
    endpoint: str = field(
        default_factory=lambda: os.getenv("BMAT_ENDPOINT", "https://api.bmat.com/v1")
    )
    timeout_seconds: float = field(default_factory=lambda: _env_float("BMAT_TIMEOUT_SECONDS", 20.0))
    max_retries: int = field(default_factory=lambda: _env_int("BMAT_MAX_RETRIES", 3))
    rate_limit_per_minute: int = field(
        default_factory=lambda: _env_int("BMAT_RATE_LIMIT_PER_MINUTE", 60)
    )
    priority: int = field(default_factory=lambda: _env_int("BMAT_PRIORITY", 4))


@dataclass(frozen=True)
class SoundmouseConfig:
    """Soundmouse stub configuration (future provider)."""

    enabled: bool = field(default_factory=lambda: _env_bool("XR7_SOUNDMOUSE_ENABLED"))
    api_key: str = field(default_factory=lambda: os.getenv("SOUNDMOUSE_API_KEY", ""))
    endpoint: str = field(
        default_factory=lambda: os.getenv(
            "SOUNDMOUSE_ENDPOINT", "https://api.soundmouse.com/v1"
        )
    )
    timeout_seconds: float = field(
        default_factory=lambda: _env_float("SOUNDMOUSE_TIMEOUT_SECONDS", 20.0)
    )
    max_retries: int = field(default_factory=lambda: _env_int("SOUNDMOUSE_MAX_RETRIES", 3))
    rate_limit_per_minute: int = field(
        default_factory=lambda: _env_int("SOUNDMOUSE_RATE_LIMIT_PER_MINUTE", 60)
    )
    priority: int = field(default_factory=lambda: _env_int("SOUNDMOUSE_PRIORITY", 5))


@dataclass(frozen=True)
class PexConfig:
    """Pex rights-management fingerprinting configuration."""

    enabled: bool = field(default_factory=lambda: _env_bool("XR7_PEX_ENABLED"))
    api_key: str = field(default_factory=lambda: os.getenv("PEX_API_KEY", ""))
    # Optional OAuth2 client_secret.  When set, the adapter exchanges
    # api_key + client_secret for a short-lived Bearer token.
    client_secret: str = field(default_factory=lambda: os.getenv("PEX_CLIENT_SECRET", ""))
    endpoint: str = field(
        default_factory=lambda: os.getenv("PEX_ENDPOINT", "https://api.pex.com/v1")
    )
    timeout_seconds: float = field(default_factory=lambda: _env_float("PEX_TIMEOUT_SECONDS", 20.0))
    max_retries: int = field(default_factory=lambda: _env_int("PEX_MAX_RETRIES", 3))
    rate_limit_per_minute: int = field(
        default_factory=lambda: _env_int("PEX_RATE_LIMIT_PER_MINUTE", 60)
    )
    priority: int = field(default_factory=lambda: _env_int("PEX_PRIORITY", 6))


# ---------------------------------------------------------------------------
# Orchestrator-level config
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FingerprintingOrchestratorConfig:
    """Global orchestrator settings."""

    # Confidence threshold below which a match is discarded
    min_confidence_threshold: float = field(
        default_factory=lambda: _env_float("XR7_FP_MIN_CONFIDENCE", 0.5)
    )
    # When True, aggregate results from all providers; when False, return
    # the first successful result.
    multi_provider_aggregation: bool = field(
        default_factory=lambda: _env_bool("XR7_FP_MULTI_PROVIDER", "1")
    )
    # Maximum number of providers to query in parallel
    max_parallel_providers: int = field(
        default_factory=lambda: _env_int("XR7_FP_MAX_PARALLEL_PROVIDERS", 3)
    )
    # Seconds to wait before marking a provider response as a timeout
    provider_timeout_seconds: float = field(
        default_factory=lambda: _env_float("XR7_FP_PROVIDER_TIMEOUT", 30.0)
    )
    # Per-tenant provider overrides: tenant_id → [provider_names in priority order]
    # Set via JSON env var: '{"tenant_abc": ["acrcloud", "gracenote"]}'
    tenant_provider_map_raw: str = field(
        default_factory=lambda: os.getenv("XR7_FP_TENANT_PROVIDER_MAP", "{}")
    )
    # Circuit-breaker: consecutive failures before a provider is opened
    cb_failure_threshold: int = field(
        default_factory=lambda: _env_int("XR7_FP_CB_FAILURE_THRESHOLD", 5)
    )
    # Circuit-breaker: seconds before a HALF-OPEN probe is allowed
    cb_recovery_timeout: float = field(
        default_factory=lambda: _env_float("XR7_FP_CB_RECOVERY_TIMEOUT", 60.0)
    )


# ---------------------------------------------------------------------------
# Aggregate config singleton
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FingerprintingConfig:
    """Top-level configuration aggregating all provider and orchestrator settings."""

    acrcloud: ACRCloudConfig = field(default_factory=ACRCloudConfig)
    audible_magic: AudibleMagicConfig = field(default_factory=AudibleMagicConfig)
    gracenote: GracenoteConfig = field(default_factory=GracenoteConfig)
    bmat: BMATConfig = field(default_factory=BMATConfig)
    soundmouse: SoundmouseConfig = field(default_factory=SoundmouseConfig)
    pex: PexConfig = field(default_factory=PexConfig)
    orchestrator: FingerprintingOrchestratorConfig = field(
        default_factory=FingerprintingOrchestratorConfig
    )


# Module-level singleton — importable directly
fingerprinting_config = FingerprintingConfig()
