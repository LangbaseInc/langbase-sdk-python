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
   git clone https://github.com/LangbaseInc/langbase-python-sdk
   cd langbase-python-sdk
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
   pip install -r requirements-dev.txt
   ```

4. **Create a `.env` file**:
   ```bash
   cp .env.example .env
   ```

   Then edit the `.env` file to include your API keys.

5. Format the code:
   ```bash
   black .
   isort .
   ```

6. Run the tests:

```bash
# Run all tests
pytest

# Run specific tests
pytest tests/test_langbase.py

# Run with coverage
pytest --cov=langbase
```


## Running and Testing Examples Locally


```bash
# Install in development mode
pip install -e .
```

Then you can run examples:

```
python examples/pipes/pipes.run.py
```

## Project Structure

The project follows this structure:

```
langbase-python-sdk/
├── langbase/                 # Main package
│   ├── __init__.py           # Package initialization
│   ├── errors.py             # Error classes
│   ├── helper.py             # Helper functions
│   ├── langbase.py           # Main client implementation
│   ├── request.py            # HTTP request handling
│   ├── types.py              # Type definitions
│   ├── utils.py              # Utility functions
│   └── workflow.py           # Workflow implementation
├── tests/                      # Test package
│   ├── __init__.py             # Test package initialization
│   ├── conftest.py             # Test configuration
│   ├── test_errors.py          # Tests for error classes
│   ├── test_langbase_client.py # Tests for the client
│   ├── test_memories.py        # Tests for memory functionality
│   ├── test_pipes.py           # Tests for pipes
│   ├── test_threads.py         # Tests for threads
│   ├── test_tools.py           # Tests for tools
│   ├── test_utilities.py       # Tests for utility functions
│   └── test_workflow.py        # Tests for workflow
├── examples/                   # Example scripts
│   ├── agent/                  # Agent examples
│   ├── chunker/                # Chunker examples
│   ├── embed/                  # Embed examples
│   ├── memory/                 # Memory examples
│   ├── parser/                 # Parser examples
│   ├── pipes/                  # Pipe examples
│   ├── threads/                # Thread examples
│   ├── tools/                  # Tool examples
│   └── workflow/               # Workflow examples
├── pyproject.toml              # Project configuration
├── requirements.txt            # Package dependencies
├── requirements-dev.txt        # Development dependencies
├── LICENCE                     # MIT license
├── CONTRIBUTION.md             # Contribution guidelines
└── README.md                   # Main documentation
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
