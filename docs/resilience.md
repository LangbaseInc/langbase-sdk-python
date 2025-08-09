# Resilience and Retry Mechanisms

The Langbase SDK includes comprehensive resilience features to handle network failures, rate limits, and service outages gracefully. These features help ensure your applications remain robust in production environments.

## Overview

The resilience system provides:

- **Automatic Retries**: Configurable retry strategies with exponential backoff
- **Circuit Breakers**: Prevent cascading failures by temporarily blocking requests to failing services
- **Rate Limit Handling**: Respect `Retry-After` headers from API responses
- **Jitter**: Add randomness to retry delays to prevent thundering herd problems

## Quick Start

### Basic Usage with Default Settings

```python
from langbase import Langbase

# Resilience is enabled by default
langbase = Langbase(api_key="your-api-key")

# Requests will automatically retry on failures
pipes = langbase.pipes.list()
```

### Custom Retry Configuration

```python
from langbase import Langbase, RetryConfig, RetryStrategy

retry_config = RetryConfig(
    max_attempts=5,
    strategy=RetryStrategy.EXPONENTIAL,
    base_delay=1.0,
    max_delay=60.0,
    multiplier=2.0,
    jitter=True,
    respect_retry_after=True,
    retry_on_status_codes=[429, 500, 502, 503, 504],
)

langbase = Langbase(
    api_key="your-api-key",
    retry_config=retry_config
)
```

## Retry Strategies

### Exponential Backoff (Recommended)

```python
from langbase import RetryConfig, RetryStrategy

config = RetryConfig(
    strategy=RetryStrategy.EXPONENTIAL,
    base_delay=1.0,      # Start with 1 second
    multiplier=2.0,      # Double each time
    max_delay=60.0,      # Cap at 60 seconds
    jitter=True          # Add randomness
)
# Delays: ~1s, ~2s, ~4s, ~8s, ~16s, ~32s, ~60s
```

### Linear Backoff

```python
config = RetryConfig(
    strategy=RetryStrategy.LINEAR,
    base_delay=2.0,      # 2 seconds per attempt
    max_delay=30.0
)
# Delays: 2s, 4s, 6s, 8s, 10s...
```

### Fixed Delay

```python
config = RetryConfig(
    strategy=RetryStrategy.FIXED,
    base_delay=5.0       # Always 5 seconds
)
# Delays: 5s, 5s, 5s, 5s...
```

### Fibonacci Backoff

```python
config = RetryConfig(
    strategy=RetryStrategy.FIBONACCI,
    base_delay=1.0
)
# Delays: 1s, 1s, 2s, 3s, 5s, 8s, 13s...
```

## Circuit Breakers

Circuit breakers prevent your application from repeatedly calling a failing service:

```python
from langbase import Langbase, CircuitBreakerConfig, RetryConfig

circuit_config = CircuitBreakerConfig(
    failure_threshold=5,      # Open after 5 failures
    recovery_timeout=30.0,    # Try again after 30 seconds
    success_threshold=3,      # Close after 3 successes
)

retry_config = RetryConfig(max_attempts=2)  # Fewer retries with circuit breaker

langbase = Langbase(
    api_key="your-api-key",
    retry_config=retry_config,
    circuit_breaker_config=circuit_config
)
```

### Circuit States

- **CLOSED**: Normal operation, requests pass through
- **OPEN**: Service is failing, requests are blocked
- **HALF_OPEN**: Testing if service has recovered

## Rate Limit Handling

The SDK automatically respects `Retry-After` headers:

```python
config = RetryConfig(
    respect_retry_after=True,    # Honor Retry-After headers
    max_retry_after=300.0,       # Don't wait more than 5 minutes
    retry_on_status_codes=[429]  # Retry on rate limits
)

langbase = Langbase(
    api_key="your-api-key",
    retry_config=config
)
```

## Advanced Configuration

### Selective Retry Conditions

```python
from langbase.errors import APIConnectionError, RateLimitError

config = RetryConfig(
    # Only retry on specific exceptions
    retry_on_exceptions=[
        APIConnectionError,
        RateLimitError,
    ],
    # Only retry on specific status codes
    retry_on_status_codes=[429, 500, 502, 503, 504],
)
```

### Disabling Resilience

```python
# Disable all resilience features
langbase = Langbase(
    api_key="your-api-key",
    enable_resilience=False
)
```

## Best Practices

### Production Configuration

```python
from langbase import Langbase, RetryConfig, CircuitBreakerConfig, RetryStrategy

# Recommended production settings
retry_config = RetryConfig(
    max_attempts=3,
    strategy=RetryStrategy.EXPONENTIAL,
    base_delay=1.0,
    max_delay=30.0,
    multiplier=2.0,
    jitter=True,
    respect_retry_after=True,
)

circuit_config = CircuitBreakerConfig(
    failure_threshold=5,
    recovery_timeout=60.0,
    success_threshold=2,
)

langbase = Langbase(
    api_key="your-api-key",
    retry_config=retry_config,
    circuit_breaker_config=circuit_config
)
```

## Error Handling

```python
from langbase.errors import APIError, APIConnectionError

try:
    response = langbase.agent.run(
        model="openai:gpt-4o-mini",
        api_key="your-llm-key",
        input=[{"role": "user", "content": "Hello"}]
    )
except APIConnectionError as e:
    print(f"Connection failed after retries: {e}")
except APIError as e:
    if "Circuit breaker is open" in str(e):
        print("Service temporarily unavailable")
    else:
        print(f"API error: {e}")
```

## Streaming with Resilience

Resilience features work with streaming responses:

```python
from langbase import get_runner

response = langbase.agent.run(
    model="openai:gpt-4o-mini",
    api_key="your-llm-key",
    input=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)

# The initial request benefits from retry logic
runner = get_runner(response)
for content in runner.text_generator():
    print(content, end="", flush=True)
```

## Performance Considerations

- **Jitter**: Always enable jitter in production to prevent thundering herd
- **Max Delay**: Set reasonable maximum delays to avoid blocking too long
- **Circuit Breakers**: Use circuit breakers for external dependencies
- **Monitoring**: Monitor retry rates and circuit breaker trips in production

## 📊 Comparison with Competition

| Feature | Langbase (Before) | Langbase (After) | Pydantic AI | OpenAI SDK |
|---------|-------------------|------------------|-------------|------------|
| Basic Retries | ❌ | ✅ | ✅ | ✅ |
| Circuit Breakers | ❌ | ✅ | ❌ | ❌ |
| Multiple Strategies | ❌ | ✅ | ✅ | ❌ |
| Rate Limit Respect | ❌ | ✅ | ✅ | ✅ |
| Jitter Support | ❌ | ✅ | ✅ | ❌ |
| Easy Configuration | ❌ | ✅ | ✅ | ❌ |

## Migration Guide

If you're upgrading from an older version:

```python
# Old way (still works)
langbase = Langbase(api_key="your-api-key")

# New way with explicit configuration
langbase = Langbase(
    api_key="your-api-key",
    retry_config=RetryConfig(),  # Use defaults
    enable_resilience=True       # Explicitly enable
)
```
