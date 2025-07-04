"""
Tests for the Workflow module.

This module tests the workflow execution engine including:
- Basic step execution
- Retry logic with different backoff strategies
- Timeout handling
- Error handling and propagation
- Debug mode functionality
- Context management
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Any

from langbase.workflow import (
    Workflow, 
    TimeoutError, 
    WorkflowContext, 
    RetryConfig, 
    StepConfig
)
from langbase.errors import APIError


class TestWorkflow:
    """Test cases for the Workflow class."""
    
    def test_workflow_initialization(self):
        """Test workflow initialization with default and custom settings."""
        # Default initialization
        workflow = Workflow()
        assert workflow._debug is False
        assert workflow.context == {"outputs": {}}
        
        # Debug initialization
        debug_workflow = Workflow(debug=True)
        assert debug_workflow._debug is True
        assert debug_workflow.context == {"outputs": {}}
    
    @pytest.mark.asyncio
    async def test_basic_step_execution(self):
        """Test basic step execution without retries or timeouts."""
        workflow = Workflow()
        
        async def mock_operation():
            return "test_result"
        
        config: StepConfig = {
            "id": "test_step",
            "run": mock_operation
        }
        
        result = await workflow.step(config)
        
        assert result == "test_result"
        assert workflow.context["outputs"]["test_step"] == "test_result"
    
    @pytest.mark.asyncio
    async def test_step_with_timeout_success(self):
        """Test step execution with timeout that completes successfully."""
        workflow = Workflow()
        
        async def fast_operation():
            await asyncio.sleep(0.01)  # 10ms
            return "completed"
        
        config: StepConfig = {
            "id": "fast_step",
            "timeout": 100,  # 100ms timeout
            "run": fast_operation
        }
        
        result = await workflow.step(config)
        assert result == "completed"
    
    @pytest.mark.asyncio
    async def test_step_with_timeout_failure(self):
        """Test step execution that times out."""
        workflow = Workflow()
        
        async def slow_operation():
            await asyncio.sleep(0.2)  # 200ms
            return "should_not_complete"
        
        config: StepConfig = {
            "id": "slow_step",
            "timeout": 50,  # 50ms timeout
            "run": slow_operation
        }
        
        with pytest.raises(TimeoutError) as exc_info:
            await workflow.step(config)
        
        assert exc_info.value.step_id == "slow_step"
        assert exc_info.value.timeout == 50
    
    @pytest.mark.asyncio
    async def test_step_with_retries_success_on_retry(self):
        """Test step that fails initially but succeeds on retry."""
        workflow = Workflow()
        call_count = 0
        
        async def flaky_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success_on_retry"
        
        config: StepConfig = {
            "id": "flaky_step",
            "retries": {
                "limit": 3,
                "delay": 10,  # 10ms delay
                "backoff": "fixed"
            },
            "run": flaky_operation
        }
        
        result = await workflow.step(config)
        assert result == "success_on_retry"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_step_with_retries_failure_after_all_attempts(self):
        """Test step that fails even after all retry attempts."""
        workflow = Workflow()
        call_count = 0
        
        async def always_failing_operation():
            nonlocal call_count
            call_count += 1
            raise ValueError("Always fails")
        
        config: StepConfig = {
            "id": "failing_step",
            "retries": {
                "limit": 2,
                "delay": 10,
                "backoff": "fixed"
            },
            "run": always_failing_operation
        }
        
        with pytest.raises(ValueError, match="Always fails"):
            await workflow.step(config)
        
        assert call_count == 3  # 1 initial + 2 retries
    
    @pytest.mark.asyncio
    async def test_exponential_backoff_calculation(self):
        """Test exponential backoff delay calculation."""
        workflow = Workflow()
        
        # Test exponential backoff
        assert workflow._calculate_delay(100, 1, "exponential") == 100
        assert workflow._calculate_delay(100, 2, "exponential") == 200
        assert workflow._calculate_delay(100, 3, "exponential") == 400
        assert workflow._calculate_delay(100, 4, "exponential") == 800
    
    @pytest.mark.asyncio
    async def test_linear_backoff_calculation(self):
        """Test linear backoff delay calculation."""
        workflow = Workflow()
        
        # Test linear backoff
        assert workflow._calculate_delay(100, 1, "linear") == 100
        assert workflow._calculate_delay(100, 2, "linear") == 200
        assert workflow._calculate_delay(100, 3, "linear") == 300
        assert workflow._calculate_delay(100, 4, "linear") == 400
    
    @pytest.mark.asyncio
    async def test_fixed_backoff_calculation(self):
        """Test fixed backoff delay calculation."""
        workflow = Workflow()
        
        # Test fixed backoff
        assert workflow._calculate_delay(100, 1, "fixed") == 100
        assert workflow._calculate_delay(100, 2, "fixed") == 100
        assert workflow._calculate_delay(100, 3, "fixed") == 100
        assert workflow._calculate_delay(100, 4, "fixed") == 100
    
    @pytest.mark.asyncio
    async def test_multiple_steps_context_accumulation(self):
        """Test that multiple steps accumulate results in context."""
        workflow = Workflow()
        
        async def step1():
            return "result1"
        
        async def step2():
            return "result2"
        
        async def step3():
            return "result3"
        
        # Execute multiple steps
        result1 = await workflow.step({"id": "step1", "run": step1})
        result2 = await workflow.step({"id": "step2", "run": step2})
        result3 = await workflow.step({"id": "step3", "run": step3})
        
        # Check individual results
        assert result1 == "result1"
        assert result2 == "result2"
        assert result3 == "result3"
        
        # Check context accumulation
        assert workflow.context["outputs"]["step1"] == "result1"
        assert workflow.context["outputs"]["step2"] == "result2"
        assert workflow.context["outputs"]["step3"] == "result3"
        assert len(workflow.context["outputs"]) == 3
    
    @pytest.mark.asyncio
    async def test_debug_mode_output(self, capsys):
        """Test debug mode prints appropriate messages."""
        workflow = Workflow(debug=True)
        
        async def test_operation():
            await asyncio.sleep(0.01)
            return "debug_test"
        
        config: StepConfig = {
            "id": "debug_step",
            "timeout": 1000,
            "retries": {
                "limit": 2,
                "delay": 100,
                "backoff": "exponential"
            },
            "run": test_operation
        }
        
        result = await workflow.step(config)
        
        captured = capsys.readouterr()
        assert "🔄 Starting step: debug_step" in captured.out
        assert "⏳ Timeout: 1000ms" in captured.out
        assert "🔄 Retries:" in captured.out
        assert "✅ Completed step: debug_step" in captured.out
        assert result == "debug_test"
    
    @pytest.mark.asyncio
    async def test_debug_mode_retry_output(self, capsys):
        """Test debug mode prints retry messages."""
        workflow = Workflow(debug=True)
        call_count = 0
        
        async def flaky_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Retry test")
            return "success"
        
        config: StepConfig = {
            "id": "retry_debug_step",
            "retries": {
                "limit": 2,
                "delay": 10,
                "backoff": "fixed"
            },
            "run": flaky_operation
        }
        
        result = await workflow.step(config)
        
        captured = capsys.readouterr()
        assert "⚠️ Attempt 1 failed, retrying in 10ms..." in captured.out
        assert "Retry test" in captured.out
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_step_with_complex_return_type(self):
        """Test step execution with complex return types."""
        workflow = Workflow()
        
        async def complex_operation():
            return {
                "data": [1, 2, 3],
                "metadata": {"status": "success", "count": 3},
                "nested": {"inner": {"value": 42}}
            }
        
        config: StepConfig = {
            "id": "complex_step",
            "run": complex_operation
        }
        
        result = await workflow.step(config)
        
        expected = {
            "data": [1, 2, 3],
            "metadata": {"status": "success", "count": 3},
            "nested": {"inner": {"value": 42}}
        }
        
        assert result == expected
        assert workflow.context["outputs"]["complex_step"] == expected
    
    @pytest.mark.asyncio
    async def test_step_error_without_retries(self):
        """Test that errors are properly propagated without retries."""
        workflow = Workflow()
        
        async def error_operation():
            raise APIError(message="Custom API error")
        
        config: StepConfig = {
            "id": "error_step",
            "run": error_operation
        }
        
        with pytest.raises(APIError, match="Custom API error"):
            await workflow.step(config)
        
        # Ensure context is not updated on failure
        assert "error_step" not in workflow.context["outputs"]
    
    @pytest.mark.asyncio
    async def test_concurrent_step_execution(self):
        """Test that workflows can handle concurrent step execution safely."""
        workflow1 = Workflow()
        workflow2 = Workflow()
        
        async def operation1():
            await asyncio.sleep(0.01)
            return "workflow1_result"
        
        async def operation2():
            await asyncio.sleep(0.01)
            return "workflow2_result"
        
        # Execute steps concurrently on different workflow instances
        results = await asyncio.gather(
            workflow1.step({"id": "step1", "run": operation1}),
            workflow2.step({"id": "step2", "run": operation2})
        )
        
        assert results[0] == "workflow1_result"
        assert results[1] == "workflow2_result"
        
        # Check that contexts are separate
        assert workflow1.context["outputs"]["step1"] == "workflow1_result"
        assert workflow2.context["outputs"]["step2"] == "workflow2_result"
        assert "step2" not in workflow1.context["outputs"]
        assert "step1" not in workflow2.context["outputs"]


class TestTimeoutError:
    """Test cases for the TimeoutError class."""
    
    def test_timeout_error_creation(self):
        """Test TimeoutError creation and attributes."""
        error = TimeoutError("test_step", 5000)
        
        assert error.step_id == "test_step"
        assert error.timeout == 5000
        assert str(error) == 'Step "test_step" timed out after 5000ms'
    
    def test_timeout_error_inheritance(self):
        """Test that TimeoutError inherits from APIError."""
        error = TimeoutError("test_step", 1000)
        
        assert isinstance(error, APIError)
        assert isinstance(error, Exception)


class TestWorkflowTypes:
    """Test cases for workflow type definitions."""
    
    def test_workflow_context_structure(self):
        """Test WorkflowContext type structure."""
        context: WorkflowContext = {"outputs": {"step1": "result1", "step2": 42}}
        
        assert "outputs" in context
        assert context["outputs"]["step1"] == "result1"
        assert context["outputs"]["step2"] == 42
    
    def test_retry_config_structure(self):
        """Test RetryConfig type structure."""
        retry_config: RetryConfig = {
            "limit": 3,
            "delay": 1000,
            "backoff": "exponential"
        }
        
        assert retry_config["limit"] == 3
        assert retry_config["delay"] == 1000
        assert retry_config["backoff"] == "exponential"
    
    def test_step_config_structure(self):
        """Test StepConfig type structure."""
        async def test_func():
            return "test"
        
        step_config: StepConfig = {
            "id": "test_step",
            "timeout": 5000,
            "retries": {
                "limit": 2,
                "delay": 500,
                "backoff": "linear"
            },
            "run": test_func
        }
        
        assert step_config["id"] == "test_step"
        assert step_config["timeout"] == 5000
        assert step_config["retries"]["limit"] == 2
        assert callable(step_config["run"]) 