"""
Augmentry Python SDK
Official Python client for the Augmentry API
"""

from .client import AugmentryClient
from .exceptions import AugmentryError, AuthenticationError, RateLimitError

__version__ = "1.0.2"
__all__ = ["AugmentryClient", "AugmentryError", "AuthenticationError", "RateLimitError"]