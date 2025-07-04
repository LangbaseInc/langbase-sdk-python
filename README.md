# Langbase Python SDK: Setup Guide

This document provides instructions for setting up the development environment, testing the SDK, and publishing it to PyPI.

## Local Development Setup

### Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- virtualenv (recommended)

### Setting Up the Development Environment

1. **Clone the repository**:
   ```bash
   git clone https://github.com/LangbaseInc/langbase-sdk-python
   cd langbase-sdk-python
   ```

2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv

   # On Unix/macOS
   source venv/bin/activate

   # On Windows
   venv\Scripts\activate
   ```

3. **Install development dependencies**:
   ```bash
   pip install -e ".[dev]"
   # Or
   pip install -r requirements-dev.txt
   ```

4. **Create a `.env` file**:
   ```bash
   cp .env.example .env
   ```

   Then edit the `.env` file to include your API keys.

## Running Tests

The SDK uses pytest for testing. To run the tests:

```bash
# Run all tests
pytest

# Run specific tests
pytest tests/test_langbase.py

# Run with coverage
pytest --cov=langbase
```

## Building the Package

To build the package:

```bash
python -m build
```

This will create both source distributions and wheel distributions in the `dist/` directory.

## Testing the Package Locally

You can test the package locally without publishing to PyPI:

```bash
# Install in development mode
pip install -e .
```

Then you can run examples:

```
./venv/bin/python examples/pipes/pipes.run.py
```

## Publishing to PyPI

### Prerequisites

- A PyPI account
- twine package (`pip install twine`)

### Steps to Publish

1. **Make sure your package version is updated**:
   - Update the version number in `langbase/__init__.py`

2. **Build the package**:
   ```bash
   python -m build
   ```

If it doesn't work, try installing the latest version of `build`:

```bash
pip install build
```

And then run:

```bash
./venv/bin/python -m build
```

3. **Check the package**:
   ```bash
   twine check dist/*
   ```

4. **Upload to TestPyPI (optional but recommended)**:
   ```bash
   twine upload --repository-url https://test.pypi.org/legacy/ dist/*
   ```

5. **Test the TestPyPI package**:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ langbase
   ```

6. **Upload to PyPI**:
   ```bash
   twine upload dist/*
   ```

## Automating Releases with GitHub Actions

For automated releases, you can use GitHub Actions. Create a workflow file at `.github/workflows/publish.yml` with the following content:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  build-and-publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install build twine
      - name: Build and publish
        env:
          TWINE_USERNAME: ${{ secrets.PYPI_USERNAME }}
          TWINE_PASSWORD: ${{ secrets.PYPI_PASSWORD }}
        run: |
          python -m build
          twine upload dist/*
```

## Project Structure

The project follows this structure:

```
langbase-python/
├── langbase/                   # Main package
│   ├── __init__.py             # Package initialization
│   ├── langbase.py             # Main client implementation
│   ├── request.py              # HTTP request handling
│   ├── errors.py               # Error classes
│   ├── types.py                # Type definitions (not used)
│   └── utils.py                # Utility functions
│   └── workflow.py             # Workflow implementation
├── tests/                      # Test package
│   ├── __init__.py             # Test package initialization
│   ├── test_client.py          # Tests for the client
│   ├── test_request.py         # Tests for request handling
│   ├── test_errors.py          # Tests for error classes
│   └── test_utils.py           # Tests for utility functions
│   └── test_workflow.py        # Tests for workflow
├── examples/                   # Example scripts
├── setup.py                    # Package setup script
├── pyproject.toml              # Project configuration
├── requirements.txt            # Package dependencies
├── requirements-dev.txt        # Development dependencies
├── LICENSE                     # MIT license
└── README.md                   # Main documentation
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Troubleshooting

### Common Issues

1. **Package not found after installation**:
   - Make sure your virtual environment is activated
   - Try running `pip list` to confirm installation

2. **Build errors**:
   - Make sure you have the latest `build` package: `pip install --upgrade build`
   - Check for syntax errors in your code

3. **Test failures**:
   - Run specific failing tests to get more details
   - Check for API key issues if integration tests are failing

### Getting Help

If you encounter issues not covered here, please open an issue on GitHub with detailed information about the problem, including:

- Your Python version
- Your operating system
- Any error messages
- Steps to reproduce the issue
