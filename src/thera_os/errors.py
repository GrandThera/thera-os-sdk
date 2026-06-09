from __future__ import annotations


class TheraOSError(Exception):
    """Base exception for thera-os client errors."""


class TheraOSAPIError(TheraOSError):
    """Raised when the API returns an error response."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        code: str | None = None,
        response_body: object | None = None,
    ) -> None:
        self.status_code = status_code
        self.code = code
        self.message = message
        self.response_body = response_body
        super().__init__(message)
