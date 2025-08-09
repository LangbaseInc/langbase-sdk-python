"""
Advanced retry and resilience system for the Langbase SDK.

This module provides comprehensive retry mechanisms, circuit breakers,
and resilience patterns for robust API interactions.
"""

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type, Union
from typing_extensions import Literal

import requests

from .errors import (
    APIConnectionError,
    APIConnectionTimeoutError,
    APIError,
    RateLimitError,
)


class RetryStrategy(str, Enum):
    """Available retry strategies."""
    
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    FIXED = "fixed"
    FIBONACCI = "fibonacci"


class CircuitState(str, Enum):
    """Circuit breaker states."""
    
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, rejecting requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    
    max_attempts: int = 3
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    base_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    multiplier: float = 2.0
    jitter: bool = True
    
    # Retry conditions
    retry_on_status_codes: List[int] = field(default_factory=lambda: [429, 500, 502, 503, 504])
    retry_on_exceptions: List[Type[Exception]] = field(
        default_factory=lambda: [
            APIConnectionError,
            APIConnectionTimeoutError,
            RateLimitError,
        ]
    )
    
    # Rate limit handling
    respect_retry_after: bool = True
    max_retry_after: float = 300.0  # seconds

    def calculate_delay(self, attempt: int, retry_after: Optional[float] = None) -> float:
        """Calculate delay for the given attempt using this config."""
        return RetryCalculator.calculate_delay(attempt, self, retry_after)


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    
    failure_threshold: int = 5
    recovery_timeout: float = 60.0  # seconds
    success_threshold: int = 2  # successes needed to close circuit
    
    # What constitutes a failure
    failure_exceptions: List[Type[Exception]] = field(
        default_factory=lambda: [
            APIConnectionError,
            APIConnectionTimeoutError,
        ]
    )


class RetryCalculator:
    """Calculates retry delays based on strategy."""
    
    @staticmethod
    def calculate_delay(
        attempt: int,
        config: "RetryConfig",
        retry_after: Optional[float] = None
    ) -> float:
        """Calculate delay for the given attempt."""
        
        # Respect Retry-After header if present and enabled
        if retry_after is not None and config.respect_retry_after:
            return min(retry_after, config.max_retry_after)
        
        if config.strategy == RetryStrategy.FIXED:
            delay = config.base_delay
        elif config.strategy == RetryStrategy.LINEAR:
            delay = config.base_delay * attempt
        elif config.strategy == RetryStrategy.EXPONENTIAL:
            delay = config.base_delay * (config.multiplier ** (attempt - 1))
        elif config.strategy == RetryStrategy.FIBONACCI:
            delay = config.base_delay * RetryCalculator._fibonacci(attempt)
        else:
            delay = config.base_delay
        
        # Apply jitter to prevent thundering herd
        if config.jitter:
            import random
            delay *= (0.5 + random.random() * 0.5)
        
        return min(delay, config.max_delay)
    
    @staticmethod
    def _fibonacci(n: int) -> int:
        """Calculate nth Fibonacci number."""
        if n <= 2:
            return 1
        a, b = 1, 1
        for _ in range(3, n + 1):
            a, b = b, a + b
        return b


class CircuitBreaker:
    """Circuit breaker implementation for API resilience."""
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0.0
    
    def should_allow_request(self) -> bool:
        """Check if request should be allowed through."""
        current_time = time.time()
        
        if self.state == CircuitState.CLOSED:
            return True
        elif self.state == CircuitState.OPEN:
            if current_time - self.last_failure_time >= self.config.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                return True
            return False
        else:  # HALF_OPEN
            return True
    
    def record_success(self) -> None:
        """Record a successful operation."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0
    
    def record_failure(self, exception: Exception) -> None:
        """Record a failed operation."""
        if any(isinstance(exception, exc_type) for exc_type in self.config.failure_exceptions):
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.config.failure_threshold:
                self.state = CircuitState.OPEN


class ResilientRequest:
    """Enhanced request handler with retry and circuit breaker capabilities."""
    
    def __init__(
        self,
        retry_config: Optional[RetryConfig] = None,
        circuit_breaker_config: Optional[CircuitBreakerConfig] = None,
        enable_circuit_breaker: bool = True,
    ):
        self.retry_config = retry_config or RetryConfig()
        self.circuit_breaker = (
            CircuitBreaker(circuit_breaker_config or CircuitBreakerConfig())
            if enable_circuit_breaker
            else None
        )
    
    def should_retry(self, exception: Exception, response: Optional[requests.Response] = None) -> bool:
        """Determine if request should be retried."""
        # Check exception types
        if any(isinstance(exception, exc_type) for exc_type in self.retry_config.retry_on_exceptions):
            return True
        
        # Check status codes
        if response and response.status_code in self.retry_config.retry_on_status_codes:
            return True
        
        return False
    
    def get_retry_after(self, response: Optional[requests.Response]) -> Optional[float]:
        """Extract Retry-After header value."""
        if not response:
            return None
        
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                return float(retry_after)
            except ValueError:
                # Could be HTTP date format, but we'll skip that complexity for now
                pass
        
        return None


# Export main components
__all__ = [
    "RetryStrategy",
    "CircuitState", 
    "RetryConfig",
    "CircuitBreakerConfig",
    "RetryCalculator",
    "CircuitBreaker",
    "ResilientRequest",
]
