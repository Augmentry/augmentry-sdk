"""
Custom exceptions for the Augmentry SDK
"""


class AugmentryError(Exception):
    """Base exception for all Augmentry SDK errors"""
    pass


class AuthenticationError(AugmentryError):
    """Raised when authentication fails"""
    pass


class RateLimitError(AugmentryError):
    """Raised when rate limit is exceeded"""
    pass


class ValidationError(AugmentryError):
    """Raised when input validation fails"""
    pass


class APIError(AugmentryError):
    """Raised when API returns an error response"""
    def __init__(self, message: str, status_code: int = None, response_data=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data