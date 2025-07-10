# Contributing to Langbase Python SDK

Thank you for your interest in contributing to the Langbase Python SDK! We welcome contributions from the community.

## Getting Started

### Prerequisites

- Python 3.7 or higher
- pip package manager
- git

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/langbase/langbase-python-sdk
   cd langbase-python-sdk
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install the package in development mode**
   ```bash
   pip install -e .
   ```

4. **Install development dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

5. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

## Before You Commit

**IMPORTANT**: All code must pass quality checks before committing. Run these commands:

### 1. Format Your Code
```bash
# Auto-format with Black (required)
black langbase/ tests/ examples/

# Sort imports with isort (required)
isort langbase/ tests/ examples/
```

### 2. Run Linting Checks
```bash
# Run Ruff linter (auto-fixes many issues)
ruff check --fix langbase/ tests/

# Check without auto-fix to see what changed
ruff check langbase/ tests/
```

### 3. Type Checking
```bash
# Run mypy for type checking
mypy langbase/ --strict
```

### 4. Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=langbase

# Run specific test file
pytest tests/test_pipes.py

# Run in verbose mode
pytest -v
```

### 5. Run All Checks at Once
```bash
# This runs all pre-commit hooks (black, isort, ruff, mypy)
pre-commit run --all-files
```

## Quick Checklist

Before pushing your changes, ensure:

- [ ] ✅ Code is formatted with `black`
- [ ] ✅ Imports are sorted with `isort`
- [ ] ✅ No linting errors from `ruff`
- [ ] ✅ Type checking passes with `mypy`
- [ ] ✅ All tests pass with `pytest`
- [ ] ✅ New features have tests
- [ ] ✅ New features have type hints
- [ ] ✅ Documentation is updated if needed

## Making Changes

### 1. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes
- Write clean, readable code
- Add type hints to all functions
- Follow existing code patterns
- Add docstrings to public functions

### 3. Add Tests
- Write tests for new features
- Ensure existing tests still pass
- Aim for good test coverage

### 4. Update Documentation
- Update README.md if adding new features
- Update docstrings
- Add examples if applicable

### 5. Commit Your Changes
```bash
# Stage your changes
git add .

# Commit with a descriptive message
git commit -m "📖 DOC: Improved contribution docs"
```

Follow conventional commit format:
- `📦 NEW:` New feature
- `🐛 BUG:` Bug fix
- `📖 Docs:` Documentation changes
- `👌🏻 IMP:` Improvements

### 6. Push and Create PR
```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Code Style Guide

### Type Hints
All functions should have type hints:
```python
def process_data(input_text: str, max_length: int = 100) -> Dict[str, Any]:
    """Process input text and return results."""
    ...
```

### Docstrings
Use Google-style docstrings:
```python
def my_function(param1: str, param2: int) -> bool:
    """
    Brief description of function.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When invalid input provided
    """
    ...
```

### Error Handling
Use specific exceptions and helpful error messages:
```python
if not api_key:
    raise ValueError(
        "API key is required. Set LANGBASE_API_KEY environment variable "
        "or pass api_key parameter."
    )
```

## Testing Guidelines

### Writing Tests
- Use pytest for all tests
- Use descriptive test names
- Test both success and error cases
- Use fixtures for common setup

Example:
```python
def test_pipe_run_with_invalid_name_raises_error(langbase_client):
    """Test that running a pipe with invalid name raises appropriate error."""
    with pytest.raises(NotFoundError) as exc_info:
        langbase_client.pipes.run(name="non-existent-pipe")
    
    assert "404" in str(exc_info.value)
```

## Need Help?

- Check existing issues and PRs
- Read the [documentation](https://langbase.com/docs)
- Ask in our [Discord community](https://discord.gg/langbase)
- Open an issue for bugs or feature requests

## License

By contributing, you agree that your contributions will be licensed under the MIT License.