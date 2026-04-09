"""Provider-agnostic interface for all audio fingerprinting adapters.

Every provider adapter must implement ``IFingerprintingProvider``.  The
interface is intentionally stable so callers never depend on provider
internals.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from XR7.fingerprinting.schema import (
    NormalizedMatchResult,
    ProviderHealthStatus,
)


class IFingerprintingProvider(ABC):
    """Abstract base class for all XR7 fingerprinting provider adapters.

    Implementations are expected to be async-first and handle their own
    HTTP client lifecycle (creation and cleanup via ``aclose()``).
    """

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Unique lowercase identifier for this provider (e.g. ``"acrcloud"``)."""

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------

    @abstractmethod
    async def submit_audio_fingerprint(
        self,
        audio_data: bytes,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Submit raw audio for fingerprinting.

        Returns a job/reference ID that can be used to poll results, or
        a sentinel like ``"no-match"`` when the provider resolves inline.
        """

    @abstractmethod
    async def submit_reference_file(
        self,
        audio_data: bytes,
        *,
        isrc: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Register a reference track in the provider's content library.

        Returns the provider-assigned reference ID.
        """

    @abstractmethod
    async def match_audio(
        self,
        audio_data: bytes,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> list[NormalizedMatchResult]:
        """Fingerprint audio and return normalized matches in a single call."""

    @abstractmethod
    async def detect_usage(
        self,
        reference_id: str,
        *,
        territory: str | None = None,
    ) -> list[NormalizedMatchResult]:
        """Detect where a registered reference track is currently being used.

        Used for ongoing monitoring (broadcast, UGC, live, etc.).
        """

    @abstractmethod
    async def get_match_results(self, job_id: str) -> list[NormalizedMatchResult]:
        """Retrieve results for a previously submitted asynchronous job.

        Return an empty list for providers that only support synchronous
        identification.
        """

    @abstractmethod
    async def get_provider_health(self) -> ProviderHealthStatus:
        """Return the provider's current operational health status."""

    @abstractmethod
    def normalize_provider_response(self, raw: dict[str, Any]) -> list[NormalizedMatchResult]:
        """Convert a provider-native response dict into the XR7 normalized schema.

        This must be callable synchronously (no I/O) so the orchestrator can
        post-process cached/stored raw payloads without network access.
        """

    # ------------------------------------------------------------------
    # Lifecycle helpers (optional override)
    # ------------------------------------------------------------------

    async def aclose(self) -> None:
        """Release any held resources (HTTP clients, connections, etc.)."""
