"""
Workflow execution engine for Langbase SDK.

This module provides a robust workflow execution system with support for:
- Step-based execution with retries and timeouts
- Configurable retry strategies (exponential, linear, fixed backoff)
- Debug logging and performance monitoring
- Context management for step outputs
"""

import asyncio
import time
from typing import Any, Awaitable, Callable, Dict, Generic, List, Optional, TypeVar

from typing_extensions import Literal, TypedDict

from .errors import APIError

T = TypeVar("T")


class WorkflowContext(TypedDict):
    """Context for workflow execution containing step outputs."""

    outputs: Dict[str, Any]


class RetryConfig(TypedDict):
    """Configuration for step retry behavior."""

    limit: int
    delay: int
    backoff: Literal["exponential", "linear", "fixed"]


class StepConfig(TypedDict, Generic[T]):
    """Configuration for a workflow step."""

    id: str
    timeout: Optional[int]
    retries: Optional[RetryConfig]
    run: Callable[[], Awaitable[T]]


class TimeoutError(APIError):
    """Raised when a workflow step times out."""

    def __init__(self, step_id: str, timeout: int):
        """
        Initialize a timeout error.

        Args:
            step_id: The ID of the step that timed out
            timeout: The timeout value in milliseconds
        """
        message = f'Step "{step_id}" timed out after {timeout}ms'
        super().__init__(message=message)
        self.step_id = step_id
        self.timeout = timeout


class Workflow:
    """
    A workflow execution engine that provides step-based execution with retry logic,
    timeouts, and debugging capabilities.
    """

    def __init__(self, debug: bool = False):
        """
        Initialize a new workflow instance.

        Args:
            debug: Whether to enable debug logging and performance monitoring
        """
        self._context: WorkflowContext = {"outputs": {}}
        self._debug = debug

    @property
    def context(self) -> WorkflowContext:
        """Get the current workflow context."""
        return self._context

    async def step(self, config: StepConfig[T]) -> T:
        """
        Execute a workflow step with retry logic and timeout handling.

        Args:
            config: Step configuration including ID, timeout, retries, and execution function

        Returns:
            The result of the step execution

        Raises:
            TimeoutError: If the step exceeds the specified timeout
            APIError: If the step fails after all retry attempts
        """
        if self._debug:
            print(f"\n🔄 Starting step: {config['id']}")
            start_time = time.time()
            if config.get("timeout"):
                print(f"⏳ Timeout: {config['timeout']}ms")
            if config.get("retries"):
                print(f"🔄 Retries: {config['retries']}")

        last_error: Optional[Exception] = None
        attempt = 1
        max_attempts = 1

        if config.get("retries"):
            max_attempts = config["retries"]["limit"] + 1

        while attempt <= max_attempts:
            try:
                step_task = config["run"]()

                if config.get("timeout"):
                    step_task = self._with_timeout(
                        promise=step_task,
                        timeout=config["timeout"],
                        step_id=config["id"],
                    )

                result = await step_task
                self._context["outputs"][config["id"]] = result

                if self._debug:
                    elapsed = (time.time() - start_time) * 1000
                    print(f"⏱️ Step {config['id']}: {elapsed:.2f}ms")
                    print(f"📤 Output: {result}")
                    print(f"✅ Completed step: {config['id']}\n")

                return result

            except Exception as error:
                last_error = error

                if attempt < max_attempts:
                    retry_config = config.get("retries")
                    delay = 0

                    if retry_config:
                        delay = self._calculate_delay(
                            retry_config["delay"], attempt, retry_config["backoff"]
                        )

                    if self._debug:
                        print(f"⚠️ Attempt {attempt} failed, retrying in {delay}ms...")
                        print(f"Error: {error}")

                    await self._sleep(delay / 1000.0)  # Convert to seconds
                    attempt += 1
                else:
                    if self._debug:
                        elapsed = (time.time() - start_time) * 1000
                        print(f"⏱️ Step {config['id']}: {elapsed:.2f}ms")
                        print(f"❌ Failed step: {config['id']}")
                        print(f"Error: {error}")

                    if isinstance(last_error, Exception):
                        raise last_error from None
                    raise APIError(message=str(last_error)) from None

        # This should never be reached, but just in case
        if last_error:
            raise last_error
        raise APIError(message="Unknown error occurred")

    async def _with_timeout(
        self, promise: Awaitable[T], timeout: int, step_id: str
    ) -> T:
        """
        Add timeout handling to a promise.

        Args:
            promise: The awaitable to add timeout to
            timeout: Timeout in milliseconds
            step_id: Step ID for error reporting

        Returns:
            The result of the promise

        Raises:
            TimeoutError: If the promise doesn't complete within the timeout
        """
        try:
            return await asyncio.wait_for(promise, timeout=timeout / 1000.0)
        except asyncio.TimeoutError as e:
            raise TimeoutError(step_id=step_id, timeout=timeout) from e

    def _calculate_delay(
        self,
        base_delay: int,
        attempt: int,
        strategy: Literal["exponential", "linear", "fixed"],
    ) -> int:
        """
        Calculate retry delay based on strategy.

        Args:
            base_delay: Base delay in milliseconds
            attempt: Current attempt number (1-based)
            strategy: Backoff strategy to use

        Returns:
            Calculated delay in milliseconds
        """
        if strategy == "exponential":
            return base_delay * (2 ** (attempt - 1))
        if strategy == "linear":
            return base_delay * attempt
        # fixed
        return base_delay

    async def _sleep(self, seconds: float) -> None:
        """
        Sleep for the specified duration.

        Args:
            seconds: Duration to sleep in seconds
        """
        await asyncio.sleep(seconds)

    def run(self, steps: List[StepConfig[Any]]) -> Dict[str, Any]:
        """
        Execute multiple workflow steps in sequence.

        Args:
            steps: List of step configurations to execute

        Returns:
            Dictionary containing outputs from all steps

        Raises:
            TimeoutError: If any step exceeds its timeout
            APIError: If any step fails after all retry attempts
        """

        async def _run_all():
            for step_config in steps:
                await self.step(step_config)
            return self._context["outputs"]

        return asyncio.run(_run_all())

    def reset(self) -> None:
        """Reset the workflow context, clearing all step outputs."""
        self._context = {"outputs": {}}
