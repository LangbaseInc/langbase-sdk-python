"""
Tests for the Workflow execution engine.
"""

import asyncio
import time

import pytest

from langbase.errors import APIError
from langbase.workflow import (
    RetryConfig,
    StepConfig,
    TimeoutError,
    Workflow,
    WorkflowContext,
)


class TestWorkflow:
    """Test the Workflow execution engine."""

    def test_workflow_initialization(self):
        """Test workflow initialization with and without debug mode."""
        # Test default initialization
        workflow = Workflow()
        assert workflow._debug is False
        assert workflow.context == {"outputs": {}}

        # Test with debug enabled
        debug_workflow = Workflow(debug=True)
        assert debug_workflow._debug is True
        assert debug_workflow.context == {"outputs": {}}

    @pytest.mark.asyncio
    async def test_basic_step_execution(self):
        """Test basic step execution without retries or timeout."""
        workflow = Workflow()

        async def simple_task():
            return "success"

        config: StepConfig = {"id": "test_step", "run": simple_task}

        result = await workflow.step(config)

        assert result == "success"
        assert workflow.context["outputs"]["test_step"] == "success"

    @pytest.mark.asyncio
    async def test_step_with_timeout_success(self):
        """Test step execution with timeout that completes in time."""
        workflow = Workflow()

        async def quick_task():
            await asyncio.sleep(0.01)  # 10ms
            return "completed"

        config: StepConfig = {
            "id": "quick_step",
            "timeout": 100,  # 100ms timeout
            "run": quick_task,
        }

        result = await workflow.step(config)

        assert result == "completed"
        assert workflow.context["outputs"]["quick_step"] == "completed"

    @pytest.mark.asyncio
    async def test_step_with_timeout_failure(self):
        """Test step execution that times out."""
        workflow = Workflow()

        async def slow_task():
            await asyncio.sleep(0.2)  # 200ms
            return "should_not_complete"

        config: StepConfig = {
            "id": "slow_step",
            "timeout": 50,  # 50ms timeout
            "run": slow_task,
        }

        with pytest.raises(TimeoutError) as exc_info:
            await workflow.step(config)

        assert exc_info.value.step_id == "slow_step"
        assert exc_info.value.timeout == 50
        assert "slow_step" in str(exc_info.value)
        assert "50ms" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_step_with_retries_success_on_retry(self):
        """Test step that fails initially but succeeds on retry."""
        workflow = Workflow()

        call_count = 0

        async def flaky_task():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise APIError("Temporary failure")
            return "success_on_retry"

        config: StepConfig = {
            "id": "flaky_step",
            "retries": {"limit": 3, "delay": 10, "backoff": "fixed"},  # 10ms delay
            "run": flaky_task,
        }

        result = await workflow.step(config)

        assert result == "success_on_retry"
        assert call_count == 3
        assert workflow.context["outputs"]["flaky_step"] == "success_on_retry"

    @pytest.mark.asyncio
    async def test_step_with_retries_failure_after_all_attempts(self):
        """Test step that fails after all retry attempts."""
        workflow = Workflow()

        async def always_fail_task():
            raise APIError("Persistent failure")

        config: StepConfig = {
            "id": "failing_step",
            "retries": {"limit": 2, "delay": 10, "backoff": "fixed"},
            "run": always_fail_task,
        }

        with pytest.raises(APIError) as exc_info:
            await workflow.step(config)

        assert "Persistent failure" in str(exc_info.value)

    def test_exponential_backoff_calculation(self):
        """Test exponential backoff delay calculation."""
        workflow = Workflow()

        # Test exponential backoff: base_delay * (2 ** (attempt - 1))
        assert workflow._calculate_delay(100, 1, "exponential") == 100  # 100 * 2^0
        assert workflow._calculate_delay(100, 2, "exponential") == 200  # 100 * 2^1
        assert workflow._calculate_delay(100, 3, "exponential") == 400  # 100 * 2^2
        assert workflow._calculate_delay(100, 4, "exponential") == 800  # 100 * 2^3

    def test_linear_backoff_calculation(self):
        """Test linear backoff delay calculation."""
        workflow = Workflow()

        # Test linear backoff: base_delay * attempt
        assert workflow._calculate_delay(100, 1, "linear") == 100  # 100 * 1
        assert workflow._calculate_delay(100, 2, "linear") == 200  # 100 * 2
        assert workflow._calculate_delay(100, 3, "linear") == 300  # 100 * 3
        assert workflow._calculate_delay(50, 4, "linear") == 200  # 50 * 4

    def test_fixed_backoff_calculation(self):
        """Test fixed backoff delay calculation."""
        workflow = Workflow()

        # Test fixed backoff: always base_delay
        assert workflow._calculate_delay(100, 1, "fixed") == 100
        assert workflow._calculate_delay(100, 2, "fixed") == 100
        assert workflow._calculate_delay(100, 3, "fixed") == 100
        assert workflow._calculate_delay(100, 10, "fixed") == 100

    @pytest.mark.asyncio
    async def test_multiple_steps_context_accumulation(self):
        """Test that multiple steps accumulate results in context."""
        workflow = Workflow()

        async def step1():
            return "result1"

        async def step2():
            return "result2"

        async def step3():
            return {"data": "result3"}

        # Execute multiple steps
        result1 = await workflow.step({"id": "step1", "run": step1})
        result2 = await workflow.step({"id": "step2", "run": step2})
        result3 = await workflow.step({"id": "step3", "run": step3})

        assert result1 == "result1"
        assert result2 == "result2"
        assert result3 == {"data": "result3"}

        # Check context accumulation
        context = workflow.context
        assert context["outputs"]["step1"] == "result1"
        assert context["outputs"]["step2"] == "result2"
        assert context["outputs"]["step3"] == {"data": "result3"}
        assert len(context["outputs"]) == 3

    @pytest.mark.asyncio
    async def test_debug_mode_output(self, capsys):
        """Test debug mode logging output using pytest's capsys fixture."""
        workflow = Workflow(debug=True)

        async def test_task():
            await asyncio.sleep(0.01)
            return "debug_result"

        config: StepConfig = {"id": "debug_step", "timeout": 1000, "run": test_task}

        result = await workflow.step(config)

        # Capture the printed output
        captured = capsys.readouterr()
        output = captured.out

        assert result == "debug_result"
        assert "🔄 Starting step: debug_step" in output
        assert "⏳ Timeout: 1000ms" in output
        assert "⏱️ Step debug_step:" in output
        assert "📤 Output: debug_result" in output
        assert "✅ Completed step: debug_step" in output

    @pytest.mark.asyncio
    async def test_debug_mode_retry_output(self, capsys):
        """Test debug mode output during retries using pytest's capsys fixture."""
        workflow = Workflow(debug=True)

        call_count = 0

        async def retry_task():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise APIError("Debug retry test")
            return "retry_success"

        config: StepConfig = {
            "id": "retry_debug",
            "retries": {"limit": 2, "delay": 10, "backoff": "fixed"},
            "run": retry_task,
        }

        result = await workflow.step(config)

        # Capture the printed output
        captured = capsys.readouterr()
        output = captured.out

        assert result == "retry_success"
        assert "🔄 Retries:" in output
        assert "⚠️ Attempt 1 failed, retrying in 10ms..." in output
        assert "Error: Debug retry test" in output

    @pytest.mark.asyncio
    async def test_step_with_complex_return_type(self):
        """Test step with complex return types (dict, list, etc.)."""
        workflow = Workflow()

        async def complex_task():
            return {
                "status": "success",
                "data": [1, 2, 3],
                "metadata": {"timestamp": "2023-01-01"},
            }

        config: StepConfig = {"id": "complex_step", "run": complex_task}

        result = await workflow.step(config)

        expected = {
            "status": "success",
            "data": [1, 2, 3],
            "metadata": {"timestamp": "2023-01-01"},
        }

        assert result == expected
        assert workflow.context["outputs"]["complex_step"] == expected

    @pytest.mark.asyncio
    async def test_step_error_without_retries(self):
        """Test step that fails without retry configuration."""
        workflow = Workflow()

        async def failing_task():
            raise ValueError("Test error without retries")

        config: StepConfig = {"id": "no_retry_step", "run": failing_task}

        with pytest.raises(ValueError) as exc_info:
            await workflow.step(config)

        assert "Test error without retries" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_concurrent_step_execution(self):
        """Test that workflow steps can be executed concurrently."""
        workflow1 = Workflow()
        workflow2 = Workflow()

        async def task1():
            await asyncio.sleep(0.02)
            return "task1_result"

        async def task2():
            await asyncio.sleep(0.02)
            return "task2_result"

        config1: StepConfig = {"id": "concurrent1", "run": task1}
        config2: StepConfig = {"id": "concurrent2", "run": task2}

        # Execute concurrently
        start_time = time.time()
        results = await asyncio.gather(workflow1.step(config1), workflow2.step(config2))
        end_time = time.time()

        # Should complete in roughly the time of one task (not two)
        execution_time = end_time - start_time
        assert execution_time < 0.05  # Less than 50ms for both tasks

        assert results == ["task1_result", "task2_result"]
        assert workflow1.context["outputs"]["concurrent1"] == "task1_result"
        assert workflow2.context["outputs"]["concurrent2"] == "task2_result"


class TestTimeoutError:
    """Test the TimeoutError exception class."""

    def test_timeout_error_creation(self):
        """Test TimeoutError creation with step_id and timeout."""
        error = TimeoutError("test_step", 5000)

        assert error.step_id == "test_step"
        assert error.timeout == 5000
        assert 'Step "test_step" timed out after 5000ms' in str(error)

    def test_timeout_error_inheritance(self):
        """Test that TimeoutError inherits from APIError."""
        error = TimeoutError("step", 1000)

        assert isinstance(error, APIError)
        assert isinstance(error, Exception)


class TestWorkflowTypes:
    """Test the TypedDict definitions for workflow types."""

    def test_workflow_context_structure(self):
        """Test WorkflowContext type structure."""
        context: WorkflowContext = {"outputs": {"step1": "result1", "step2": 42}}

        assert "outputs" in context
        assert isinstance(context["outputs"], dict)
        assert context["outputs"]["step1"] == "result1"
        assert context["outputs"]["step2"] == 42

    def test_retry_config_structure(self):
        """Test RetryConfig type structure."""
        retry_config: RetryConfig = {
            "limit": 3,
            "delay": 1000,
            "backoff": "exponential",
        }

        assert retry_config["limit"] == 3
        assert retry_config["delay"] == 1000
        assert retry_config["backoff"] == "exponential"

        # Test other backoff types
        linear_config: RetryConfig = {"limit": 2, "delay": 500, "backoff": "linear"}
        assert linear_config["backoff"] == "linear"

        fixed_config: RetryConfig = {"limit": 1, "delay": 100, "backoff": "fixed"}
        assert fixed_config["backoff"] == "fixed"

    def test_step_config_structure(self):
        """Test StepConfig type structure."""

        async def dummy_task():
            return "test"

        # Minimal step config
        minimal_config: StepConfig = {"id": "test_step", "run": dummy_task}
        assert minimal_config["id"] == "test_step"
        assert callable(minimal_config["run"])

        # Full step config
        full_config: StepConfig = {
            "id": "full_step",
            "timeout": 5000,
            "retries": {"limit": 3, "delay": 1000, "backoff": "exponential"},
            "run": dummy_task,
        }
        assert full_config["id"] == "full_step"
        assert full_config["timeout"] == 5000
        assert full_config["retries"]["limit"] == 3
        assert callable(full_config["run"])
