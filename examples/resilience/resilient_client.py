"""
Example demonstrating the resilience features of the Langbase SDK.

This example shows how to configure retry policies and circuit breakers
for robust API interactions.
"""

import os
import time
from dotenv import load_dotenv

from langbase import Langbase
from langbase.resilience import RetryConfig, CircuitBreakerConfig, RetryStrategy

# Load environment variables
load_dotenv()

def basic_resilience_example():
    """Basic example with default resilience settings."""
    print("=== Basic Resilience Example ===")
    
    # Initialize client with default resilience settings
    langbase = Langbase(
        api_key=os.getenv("LANGBASE_API_KEY"),
        base_url="https://api.langbase.com"
    )
    
    try:
        # This will automatically retry on failures
        pipes = langbase.pipes.list()
        print(f"✅ Successfully retrieved {len(pipes)} pipes")
    except Exception as e:
        print(f"❌ Failed after retries: {e}")


def custom_retry_configuration():
    """Example with custom retry configuration."""
    print("\n=== Custom Retry Configuration ===")
    
    # Configure custom retry behavior
    retry_config = RetryConfig(
        max_attempts=5,
        strategy=RetryStrategy.EXPONENTIAL,
        base_delay=0.5,  # Start with 500ms
        max_delay=30.0,  # Cap at 30 seconds
        multiplier=2.0,
        jitter=True,
        respect_retry_after=True,
        retry_on_status_codes=[429, 500, 502, 503, 504],
    )
    
    langbase = Langbase(
        api_key=os.getenv("LANGBASE_API_KEY"),
        base_url="https://api.langbase.com",
        retry_config=retry_config
    )
    
    try:
        # This will use the custom retry configuration
        response = langbase.agent.run(
            model="openai:gpt-4o-mini",
            api_key=os.getenv("LLM_API_KEY"),
            input=[{"role": "user", "content": "Hello, test resilience!"}],
        )
        print(f"✅ Agent response: {response.get('output', 'No output')[:100]}...")
    except Exception as e:
        print(f"❌ Failed after custom retries: {e}")


def circuit_breaker_example():
    """Example with circuit breaker configuration."""
    print("\n=== Circuit Breaker Example ===")
    
    # Configure circuit breaker
    circuit_breaker_config = CircuitBreakerConfig(
        failure_threshold=3,      # Open after 3 failures
        recovery_timeout=10.0,    # Try again after 10 seconds
        success_threshold=2,      # Close after 2 successes
    )
    
    retry_config = RetryConfig(
        max_attempts=2,  # Fewer retries when using circuit breaker
        strategy=RetryStrategy.FIXED,
        base_delay=1.0,
    )
    
    langbase = Langbase(
        api_key=os.getenv("LANGBASE_API_KEY"),
        base_url="https://api.langbase.com",
        retry_config=retry_config,
        circuit_breaker_config=circuit_breaker_config
    )
    
    # Simulate multiple requests to demonstrate circuit breaker
    for i in range(5):
        try:
            print(f"Request {i+1}...")
            pipes = langbase.pipes.list()
            print(f"✅ Success: {len(pipes)} pipes")
            time.sleep(1)
        except Exception as e:
            print(f"❌ Failed: {e}")
            time.sleep(1)


def rate_limit_handling():
    """Example showing rate limit handling with Retry-After."""
    print("\n=== Rate Limit Handling ===")
    
    retry_config = RetryConfig(
        max_attempts=3,
        strategy=RetryStrategy.EXPONENTIAL,
        base_delay=1.0,
        respect_retry_after=True,  # Respect Retry-After headers
        max_retry_after=60.0,      # Don't wait more than 1 minute
        retry_on_status_codes=[429],  # Specifically handle rate limits
    )
    
    langbase = Langbase(
        api_key=os.getenv("LANGBASE_API_KEY"),
        base_url="https://api.langbase.com",
        retry_config=retry_config
    )
    
    try:
        # Make multiple rapid requests to potentially trigger rate limiting
        for i in range(3):
            print(f"Rapid request {i+1}...")
            response = langbase.agent.run(
                model="openai:gpt-4o-mini",
                api_key=os.getenv("LLM_API_KEY"),
                input=[{"role": "user", "content": f"Quick test {i+1}"}],
            )
            print(f"✅ Response {i+1} received")
    except Exception as e:
        print(f"❌ Rate limit handling failed: {e}")


def disable_resilience():
    """Example showing how to disable resilience features."""
    print("\n=== Disabled Resilience ===")
    
    langbase = Langbase(
        api_key=os.getenv("LANGBASE_API_KEY"),
        base_url="https://api.langbase.com",
        enable_resilience=False  # Disable all resilience features
    )
    
    try:
        pipes = langbase.pipes.list()
        print(f"✅ Success without resilience: {len(pipes)} pipes")
    except Exception as e:
        print(f"❌ Failed without retries: {e}")


def streaming_with_resilience():
    """Example showing resilience with streaming responses."""
    print("\n=== Streaming with Resilience ===")
    
    retry_config = RetryConfig(
        max_attempts=3,
        strategy=RetryStrategy.EXPONENTIAL,
        base_delay=1.0,
    )
    
    langbase = Langbase(
        api_key=os.getenv("LANGBASE_API_KEY"),
        retry_config=retry_config
    )
    
    try:
        response = langbase.agent.run(
            model="openai:gpt-4o-mini",
            api_key=os.getenv("LLM_API_KEY"),
            input=[{"role": "user", "content": "Tell me a short story"}],
            stream=True
        )
        
        print("✅ Streaming response received")
        
        # Process the stream
        from langbase import get_runner
        runner = get_runner(response)
        
        print("📖 Story: ", end="")
        for content in runner.text_generator():
            print(content, end="", flush=True)
        print("\n")
        
    except Exception as e:
        print(f"❌ Streaming with resilience failed: {e}")


def main():
    """Run all resilience examples."""
    print("🔄 Langbase SDK Resilience Examples")
    print("=" * 50)
    
    # Check if API keys are available
    if not os.getenv("LANGBASE_API_KEY"):
        print("❌ LANGBASE_API_KEY not found in environment variables")
        return
    
    if not os.getenv("LLM_API_KEY"):
        print("⚠️  LLM_API_KEY not found - some examples may fail")
    
    try:
        basic_resilience_example()
        custom_retry_configuration()
        circuit_breaker_example()
        rate_limit_handling()
        disable_resilience()
        streaming_with_resilience()
        
        print("\n✅ All resilience examples completed!")
        
    except KeyboardInterrupt:
        print("\n⏹️  Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
