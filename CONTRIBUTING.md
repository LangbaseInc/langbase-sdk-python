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
    ### Note:
    Check version of pip
    ```bash
    pip --version
    ```
    **If it's pip 21.3 or lower, you need to upgrade it.**
    ```bash
    pip install --upgrade pip
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

### Format Your Code
```bash
# Auto-format with Black (required)
black langbase/ tests/ examples/

# Sort imports with isort (required)
isort langbase/ tests/ examples/
```

### Run Tests
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

### Run All Checks at Once
```bash
# This runs all pre-commit hooks (black, isort)
pre-commit run --all-files
```

### Release a New Version

The release process is automated with an interactive script. **Only maintainers should create releases.**

```bash
python release.py
```

The script will guide you through:
- Choosing version bump type (patch/minor/major)
- Writing release notes
- Updating version files
- Committing and pushing changes
- Building and uploading to PyPI

See the [Release Process](#release-process) section below for detailed instructions.

## Quick Checklist

### Before Pushing Changes

Ensure your contribution meets these requirements:

- [ ] ✅ Code is formatted with `black`
- [ ] ✅ Imports are sorted with `isort`
- [ ] ✅ All tests pass with `pytest`
- [ ] ✅ New features have tests
- [ ] ✅ New features have type hints
- [ ] ✅ Documentation is updated if needed

### Before Creating a Release (Maintainers Only)

Before running `python release.py`, ensure:

- [ ] ✅ All tests pass: `pytest`
- [ ] ✅ Code is properly formatted: `pre-commit run --all-files`
- [ ] ✅ Working directory is clean: `git status`
- [ ] ✅ On main branch and up to date: `git pull origin main`
- [ ] ✅ Have PyPI credentials configured in `~/.pypirc` (see PyPI Configuration section)
- [ ] ✅ Have dev dependencies installed: `pip install -r requirements-dev.txt`
- [ ] ✅ Reviewed changes since last release
- [ ] ✅ Prepared release notes describing changes

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
- `📦 NEW:` New feature.
- `👌IMPROVE:` Improvements.
- `🐛 BUG:` Bug fix.
- `📖 Docs:` Documentation changes.
- `🚀 RELEASE`: Release new version.


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
    ...
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

## Release Process

**⚠️ Note: Only maintainers with PyPI access should perform releases.**

### Prerequisites for Releases

Before creating a release, ensure you have:

1. **PyPI Account & Access**
   - Account on [PyPI](https://pypi.org) and [Test PyPI](https://test.pypi.org)
   - Maintainer access to the `langbase` package
   - Configured `~/.pypirc` with credentials (see configuration below)

2. **Required Tools**

   These are already installed with dev dependencies:
   ```bash
   pip install -r requirements-dev.txt  # Includes build and twine
   ```

3. **Clean Working Directory**
   ```bash
   git status  # Should show no uncommitted changes
   git pull origin main  # Ensure you're up to date
   ```

### PyPI Configuration (~/.pypirc)

Create or update your `~/.pypirc` file with your PyPI credentials:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-test-api-token-here
```

**To get API tokens:**
1. **PyPI**: Go to [PyPI Account Settings](https://pypi.org/manage/account/) → API tokens → "Add API token"
2. **Test PyPI**: Go to [Test PyPI Account Settings](https://test.pypi.org/manage/account/) → API tokens → "Add API token"

**Security Notes:**
- Use API tokens instead of passwords (more secure)
- Set appropriate permissions (project-scoped tokens recommended)
- Keep your `~/.pypirc` file private (chmod 600)

### Release Types

Choose the appropriate version bump:

- **patch** (0.1.0 → 0.1.1): Bug fixes, documentation updates, small improvements
- **minor** (0.1.0 → 0.2.0): New features, backwards compatible changes
- **major** (0.1.0 → 1.0.0): Breaking changes, major API updates

### Step-by-Step Release Process

1. **Run the Release Script**
   ```bash
   python release.py
   ```

2. **Follow Interactive Prompts**

   The script will ask you to:
   - Choose release type (patch/minor/major)
   - Enter release message describing changes
   - Confirm version bump
   - Choose between Test PyPI or Production PyPI

3. **What the Script Does Automatically**

   - Updates version in `pyproject.toml` and `langbase/__init__.py`
   - Updates `CHANGELOG.md` with release notes
   - Commits changes with conventional commit message
   - Pushes to GitHub (optional)
   - Builds the package (`python -m build`)
   - Uploads to PyPI/Test PyPI (`twine upload`)

### Test Releases

For testing releases before production:

1. Run `python release.py`
2. Answer "y" when asked about Test PyPI
3. This uploads to https://test.pypi.org/project/langbase/
4. Test install: `pip install --index-url https://test.pypi.org/simple/ langbase`

**Note**: Test releases don't commit to git, so you can reset changes after testing.

### Production Releases

1. Run `python release.py`
2. Answer "n" when asked about Test PyPI
3. The package will be uploaded to https://pypi.org/project/langbase/
4. Changes are committed and pushed to GitHub

### Post-Release Checklist

After a successful release:

- [ ] ✅ Verify the new version appears on [PyPI](https://pypi.org/project/langbase/)
- [ ] ✅ Test install the new version: `pip install langbase=={version}`
- [ ] ✅ Check that GitHub has the release commit
- [ ] ✅ Update any dependent projects or documentation
- [ ] ✅ Announce the release (Discord, social media, etc.)

### Troubleshooting Releases

**Common Issues:**

1. **PyPI Upload Fails**
   - Check your `~/.pypirc` configuration
   - Ensure you have maintainer access
   - Version might already exist (can't overwrite)

2. **Pre-commit Hooks Fail**
   - The script retries automatically
   - Hooks may modify files (formatting, etc.)
   - Script will re-stage and retry up to 3 times

**Recovery:**

If a release fails partway through:
```bash
# Reset version changes (if not yet committed)
git checkout -- pyproject.toml langbase/__init__.py CHANGELOG.md

# Or if committed but not pushed, reset the last commit
git reset --soft HEAD~1
```

## Need Help?

- Check existing issues and PRs
- Read the [documentation](https://langbase.com/docs)
- Ask in our [Discord community](https://discord.gg/langbase)
- Open an issue for bugs or feature requests

## License

By contributing, you agree that your contributions will be licensed under the Apache 2.0 License.
