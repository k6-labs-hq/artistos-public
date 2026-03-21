"""Fingerprinting provider adapters package.

Import adapters directly from their modules to avoid loading all providers
at startup — only enabled providers are instantiated by the orchestrator.
"""

from XR7.fingerprinting.adapters.acrcloud import ACRCloudAdapter
from XR7.fingerprinting.adapters.audible_magic import AudibleMagicAdapter
from XR7.fingerprinting.adapters.bmat import BMATAdapter
from XR7.fingerprinting.adapters.gracenote import GracenoteAdapter
from XR7.fingerprinting.adapters.pex import PexAdapter
from XR7.fingerprinting.adapters.soundmouse import SoundmouseAdapter

__all__ = [
    "ACRCloudAdapter",
    "AudibleMagicAdapter",
    "BMATAdapter",
    "GracenoteAdapter",
    "PexAdapter",
    "SoundmouseAdapter",
]
