class JengaError(Exception):
    """Base exception for package errors."""


class JengaConfigError(JengaError):
    """Raised when required configuration is missing."""


class JengaSignatureError(JengaError):
    """Raised when request signing fails."""


class JengaRequestError(JengaError):
    """Raised when an HTTP request fails or returns invalid data."""
