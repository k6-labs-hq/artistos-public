# Backward-compatibility re-export.
# Functions have been merged into recovery_automation.py.
from XR7.recovery.recovery_automation import (  # noqa: F401
    automate_recovery,
    build_correction_packet,
)
