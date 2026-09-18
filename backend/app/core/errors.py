"""Custom exception hierarchy for AI Instagram Reels Autopilot."""

from typing import Optional, Any


class AutopilotError(Exception):
    """Base exception for all Autopilot errors."""
    pass


class InstagramPublishingError(AutopilotError):
    """Raised when Meta Graph API fails during Reels container creation, polling, or publishing."""
    def __init__(self, message: str, meta_code: Optional[int] = None, meta_subcode: Optional[int] = None, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.meta_code = meta_code
        self.meta_subcode = meta_subcode
        self.details = details


class QCScoreThresholdError(AutopilotError):
    """Raised when a rendered Reel fails the strict Quality Control gate (score < 90)."""
    def __init__(self, score: float, remediation_notes: str):
        message = f"Quality Control gate failed: Score {score:.1f}/100 is below the required 90 threshold. Notes: {remediation_notes}"
        super().__init__(message)
        self.score = score
        self.remediation_notes = remediation_notes


class DuplicateUploadPreventedError(AutopilotError):
    """Raised when a video hash matches an already published Reel."""
    def __init__(self, file_hash: str):
        message = f"Upload blocked: Video with SHA-256 hash {file_hash} has already been published to Instagram."
        super().__init__(message)
        self.file_hash = file_hash


class ResourceExhaustionError(AutopilotError):
    """Raised when system CPU, RAM, or Disk space violates safety thresholds."""
    pass
