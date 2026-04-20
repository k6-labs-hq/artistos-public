from enum import Enum
class FindingSeverity(str, Enum):
    LOW='LOW'
    MEDIUM='MEDIUM'
    HIGH='HIGH'
    CRITICAL='CRITICAL'
class Finding:
    def __init__(self, severity, message):
        self.severity=severity
        self.message=message
class PlatformState:
    pass
