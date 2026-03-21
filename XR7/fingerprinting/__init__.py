"""XR7 Audio Fingerprinting + Matching Engine subsystem.

Provider-agnostic fingerprinting with pluggable adapters and a full
reconciliation matching engine.

Phase 2: ACRCloud
Phase 3: Audible Magic
Phase 4: Gracenote
Optional: BMAT, Soundmouse, Pex
"""

from XR7.fingerprinting.interface import IFingerprintingProvider
from XR7.fingerprinting.schema import (
    AnomalyType,
    FingerprintSubmitRequest,
    MatchType,
    NormalizedMatchResult,
    ProviderHealthStatus,
    ProviderStatus,
    RoyaltyStatus,
)

__all__ = [
    "IFingerprintingProvider",
    "AnomalyType",
    "FingerprintSubmitRequest",
    "MatchType",
    "NormalizedMatchResult",
    "ProviderHealthStatus",
    "ProviderStatus",
    "RoyaltyStatus",
]
