"""
Tests for the resilience module.
"""

import time
from unittest.mock import Mock, patch

import pytest
import responses

from langbase.errors import APIConnectionError, APIError, RateLimitError
from langbase.resilience import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
    ResilientRequest,
    RetryCalculator,
    RetryConfig,
    RetryStrategy,
)


class TestRetryCalculator:
    """Test retry delay calculations."""

    def test_fixed_strategy(self):
        """Test fixed delay strategy."""
        config = RetryConfig(strategy=RetryStrategy.FIXED, base_delay=2.0, jitter=False)
        
        assert RetryCalculator.calculate_delay(1, config) == 2.0
        assert RetryCalculator.calculate_delay(3, config) == 2.0
        assert RetryCalculator.calculate_delay(5, config) == 2.0

    def test_linear_strategy(self):
        """Test linear delay strategy."""
        config = RetryConfig(strategy=RetryStrategy.LINEAR, base_delay=1.0, jitter=False)
        
        assert RetryCalculator.calculate_delay(1, config) == 1.0
        assert RetryCalculator.calculate_delay(2, config) == 2.0
        assert RetryCalculator.calculate_delay(3, config) == 3.0

    def test_exponential_strategy(self):
        """Test exponential delay strategy."""
        config = RetryConfig(
            strategy=RetryStrategy.EXPONENTIAL, 
            base_delay=1.0, 
            multiplier=2.0, 
            jitter=False
        )
        
        assert RetryCalculator.calculate_delay(1, config) == 1.0
        assert RetryCalculator.calculate_delay(2, config) == 2.0
        assert RetryCalculator.calculate_delay(3, config) == 4.0
        assert RetryCalculator.calculate_delay(4, config) == 8.0

    def test_fibonacci_strategy(self):
        """Test Fibonacci delay strategy."""
        config = RetryConfig(strategy=RetryStrategy.FIBONACCI, base_delay=1.0, jitter=False)
        
        assert RetryCalculator.calculate_delay(1, config) == 1.0
        assert RetryCalculator.calculate_delay(2, config) == 1.0
        assert RetryCalculator.calculate_delay(3, config) == 2.0
        assert RetryCalculator.calculate_delay(4, config) == 3.0
        assert RetryCalculator.calculate_delay(5, config) == 5.0

    def test_max_delay_limit(self):
        """Test that delays are capped at max_delay."""
        config = RetryConfig(
            strategy=RetryStrategy.EXPONENTIAL,
            base_delay=1.0,
            multiplier=2.0,
            max_delay=5.0,
            jitter=False
        )
        
        assert RetryCalculator.calculate_delay(10, config) == 5.0

    def test_retry_after_header(self):
        """Test that Retry-After header is respected."""
        config = RetryConfig(respect_retry_after=True, max_retry_after=300.0)
        
        # Should use retry_after value
        assert RetryCalculator.calculate_delay(1, config, retry_after=10.0) == 10.0
        
        # Should cap at max_retry_after
        assert RetryCalculator.calculate_delay(1, config, retry_after=500.0) == 300.0

    def test_jitter_adds_randomness(self):
        """Test that jitter adds randomness to delays."""
        config = RetryConfig(strategy=RetryStrategy.FIXED, base_delay=2.0, jitter=True)
        
        delays = [RetryCalculator.calculate_delay(1, config) for _ in range(10)]
        
        # All delays should be between 1.0 and 2.0 (50% to 100% of base)
        assert all(1.0 <= delay <= 2.0 for delay in delays)
        
        # Should have some variation (not all the same)
        assert len(set(delays)) > 1


class TestCircuitBreaker:
    """Test circuit breaker functionality."""

    def test_initial_state_closed(self):
        """Test circuit breaker starts in closed state."""
        config = CircuitBreakerConfig()
        breaker = CircuitBreaker(config)
        
        assert breaker.state == CircuitState.CLOSED
        assert breaker.should_allow_request() is True

    def test_failure_threshold_opens_circuit(self):
        """Test that reaching failure threshold opens circuit."""
        config = CircuitBreakerConfig(failure_threshold=3)
        breaker = CircuitBreaker(config)
        
        # Record failures up to threshold
        for _ in range(3):
            breaker.record_failure(APIConnectionError())
        
        assert breaker.state == CircuitState.OPEN
        assert breaker.should_allow_request() is False

    def test_recovery_timeout_allows_half_open(self):
        """Test that recovery timeout allows half-open state."""
        config = CircuitBreakerConfig(failure_threshold=1, recovery_timeout=0.1)
        breaker = CircuitBreaker(config)
        
        # Open the circuit
        breaker.record_failure(APIConnectionError())
        assert breaker.state == CircuitState.OPEN
        
        # Wait for recovery timeout
        time.sleep(0.2)
        
        # Should allow request and move to half-open
        assert breaker.should_allow_request() is True
        assert breaker.state == CircuitState.HALF_OPEN

    def test_success_in_half_open_closes_circuit(self):
        """Test that successes in half-open state close circuit."""
        config = CircuitBreakerConfig(failure_threshold=1, recovery_timeout=0.1, success_threshold=2)
        breaker = CircuitBreaker(config)
        
        # Open the circuit
        breaker.record_failure(APIConnectionError())
        time.sleep(0.2)
        breaker.should_allow_request()  # Move to half-open
        
        # Record successes
        breaker.record_success()
        assert breaker.state == CircuitState.HALF_OPEN
        
        breaker.record_success()
        assert breaker.state == CircuitState.CLOSED

    def test_only_configured_exceptions_trigger_failure(self):
        """Test that only configured exceptions trigger failures."""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            failure_exceptions=[APIConnectionError]
        )
        breaker = CircuitBreaker(config)
        
        # This should trigger failure
        breaker.record_failure(APIConnectionError())
        assert breaker.state == CircuitState.OPEN
        
        # Reset for next test
        breaker.state = CircuitState.CLOSED
        breaker.failure_count = 0
        
        # This should not trigger failure
        breaker.record_failure(ValueError("Not a connection error"))
        assert breaker.state == CircuitState.CLOSED


class TestResilientRequest:
    """Test resilient request functionality."""

    def test_should_retry_on_configured_exceptions(self):
        """Test retry logic for configured exceptions."""
        config = RetryConfig(retry_on_exceptions=[APIConnectionError, RateLimitError])
        resilient = ResilientRequest(retry_config=config)
        
        assert resilient.should_retry(APIConnectionError()) is True
        assert resilient.should_retry(RateLimitError()) is True
        assert resilient.should_retry(ValueError()) is False

    def test_should_retry_on_configured_status_codes(self):
        """Test retry logic for configured status codes."""
        config = RetryConfig(retry_on_status_codes=[429, 500, 502])
        resilient = ResilientRequest(retry_config=config)
        
        mock_response = Mock()
        mock_response.status_code = 429
        assert resilient.should_retry(APIError(), mock_response) is True
        
        mock_response.status_code = 404
        assert resilient.should_retry(APIError(), mock_response) is False

    def test_get_retry_after_header(self):
        """Test extraction of Retry-After header."""
        resilient = ResilientRequest()
        
        mock_response = Mock()
        mock_response.headers = {"Retry-After": "30"}
        assert resilient.get_retry_after(mock_response) == 30.0
        
        mock_response.headers = {}
        assert resilient.get_retry_after(mock_response) is None
        
        assert resilient.get_retry_after(None) is None


class TestRetryConfig:
    """Test RetryConfig functionality."""

    def test_calculate_delay_method(self):
        """Test that RetryConfig.calculate_delay works correctly."""
        config = RetryConfig(strategy=RetryStrategy.FIXED, base_delay=2.0, jitter=False)

        assert config.calculate_delay(1) == 2.0
        assert config.calculate_delay(3) == 2.0

    def test_calculate_delay_with_retry_after(self):
        """Test calculate_delay with retry_after parameter."""
        config = RetryConfig(respect_retry_after=True)

        # Should use retry_after when provided
        assert config.calculate_delay(1, retry_after=5.0) == 5.0


class TestRequestIntegration:
    """Test resilience integration with Request class."""

    @responses.activate
    def test_resilient_request_retries_on_failure(self):
        """Test that resilient requests retry on configured failures."""
        from langbase.request import Request
        from langbase.resilience import RetryConfig, RetryStrategy

        # Mock a failing then successful response
        responses.add(
            responses.GET,
            "https://api.langbase.com/test",
            status=500,
            json={"error": "Internal server error"}
        )
        responses.add(
            responses.GET,
            "https://api.langbase.com/test",
            status=200,
            json={"success": True}
        )

        retry_config = RetryConfig(
            max_attempts=3,
            strategy=RetryStrategy.FIXED,
            base_delay=0.01,  # Very short delay for testing
            jitter=False,
            retry_on_status_codes=[500]
        )

        request = Request({
            "api_key": "test-key",
            "base_url": "https://api.langbase.com",
            "retry_config": retry_config,
            "enable_resilience": True
        })

        # Should succeed after retry
        response = request.make_resilient_request(
            "https://api.langbase.com/test",
            "GET",
            {"Authorization": "Bearer test-key"}
        )

        assert response.status_code == 200
        assert len(responses.calls) == 2  # First failed, second succeeded

    @responses.activate
    def test_circuit_breaker_opens_after_failures(self):
        """Test that circuit breaker opens after configured failures."""
        from langbase.request import Request
        from langbase.resilience import RetryConfig, CircuitBreakerConfig
        from langbase.errors import APIError

        # Mock multiple failing responses
        for _ in range(5):
            responses.add(
                responses.GET,
                "https://api.langbase.com/test",
                status=500,
                json={"error": "Internal server error"}
            )

        retry_config = RetryConfig(max_attempts=1)  # No retries for this test
        circuit_config = CircuitBreakerConfig(
            failure_threshold=3,
            failure_exceptions=[APIError]  # Include APIError in circuit breaker triggers
        )

        request = Request({
            "api_key": "test-key",
            "base_url": "https://api.langbase.com",
            "retry_config": retry_config,
            "circuit_breaker_config": circuit_config,
            "enable_resilience": True
        })

        # Make requests until circuit opens
        for _ in range(3):
            with pytest.raises(APIError):
                request.make_resilient_request(
                    "https://api.langbase.com/test",
                    "GET",
                    {"Authorization": "Bearer test-key"}
                )

        # Circuit should now be open - next request should fail immediately
        with pytest.raises(APIError, match="Circuit breaker is open"):
            request.make_resilient_request(
                "https://api.langbase.com/test",
                "GET",
                {"Authorization": "Bearer test-key"}
            )

    def test_resilience_disabled(self):
        """Test that resilience can be disabled."""
        from langbase.request import Request

        request = Request({
            "api_key": "test-key",
            "base_url": "https://api.langbase.com",
            "enable_resilience": False
        })

        assert request.resilient_request is None
