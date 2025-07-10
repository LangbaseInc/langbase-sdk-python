# Langbase Python SDK

[![PyPI version](https://badge.fury.io/py/langbase.svg)](https://badge.fury.io/py/langbase)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

The official Python SDK for [Langbase](https://langbase.com) - Build declarative and composable AI-powered LLM products with ease.

## Documentation

Check the [Langbase SDK documentation](https://langbase.com/docs/sdk) for more details.

The following examples are for reference only. Prefer docs for the latest information.

## Features

- 🚀 **Simple and intuitive API** - Get started in minutes
- 🔄 **Streaming support** - Real-time text generation with typed events
- 🛠️ **Type safety** - Full type hints for better IDE support
- 📦 **Minimal dependencies** - Only what you need
- 🐍 **Python 3.7+** - Support for modern Python versions
- 🔌 **Async ready** - Coming soon!

## Installation

```bash
pip install langbase
```

## Quick Start

### 1. Set up your API key

Create a `.env` file and add your [Langbase API Key](https://langbase.com/docs/api-reference/api-keys).
```bash
LANGBASE_API_KEY="your-api-key"
```

---

### 2. Initialize the client

```python
from langbase import Langbase
import os
from dotenv import load_dotenv

load_dotenv()

# Get API key from environment variable
langbase_api_key = os.getenv("LANGBASE_API_KEY")

# Initialize the client
lb = Langbase(api_key=langbase_api_key)
```

### 3. Generate text

```python
# Simple generation
response = lb.pipes.run(
    name="ai-agent",
    messages=[{"role": "user", "content": "Tell me about AI"}],
)

print(response["completion"])
```

---

### 4. Stream text (Simple)

```python
# Stream text as it's generated
response = lb.pipes.run(
    name="ai-agent",
    messages=[{"role": "user", "content": "Tell me about AI"}],
    stream=True,
)

for text in stream_text(response["stream"]):
    print(text, end="", flush=True)
```

### 5. Stream with typed events (Advanced) 🆕

```python
from langbase import StreamEventType, get_typed_runner

# Get streaming response
response = lb.pipes.run(
    name="ai-agent",
    messages=[{"role": "user", "content": "Tell me about AI"}],
    stream=True,
)

# Create typed stream processor
runner = get_typed_runner(response)

# Register event handlers
runner.on(StreamEventType.CONNECT, lambda e: 
    print(f"✓ Connected to thread: {e['threadId']}"))

runner.on(StreamEventType.CONTENT, lambda e: 
    print(e["content"], end="", flush=True))

runner.on(StreamEventType.TOOL_CALL, lambda e: 
    print(f"\n🔧 Tool: {e['toolCall']['function']['name']}"))

runner.on(StreamEventType.END, lambda e: 
    print(f"\n⏱️  Duration: {e['duration']:.2f}s"))

# Process the stream
runner.process()
```

## Core Features

### 🔄 Pipes - AI Pipeline Execution

```python
# List all pipes
pipes = lb.pipes.list()

# Run a pipe
response = lb.pipes.run(
    name="ai-agent",
    messages=[{"role": "user", "content": "Hello!"}],
    variables={"style": "friendly"},  # Optional variables
    stream=True,  # Enable streaming
)
```

### 🧠 Memory - Persistent Context Storage

```python
# Create a memory
memory = lb.memories.create(
    name="product-docs",
    description="Product documentation",
)

# Upload documents
lb.memories.documents.upload(
    memory_name="product-docs",
    document_name="guide.pdf",
    document=open("guide.pdf", "rb"),
    content_type="application/pdf",
)

# Retrieve relevant context
results = lb.memories.retrieve(
    query="How do I get started?",
    memory=[{"name": "product-docs"}],
    top_k=3,
)
```

### 🤖 Agent - LLM Agent Execution

```python
# Run an agent with tools
response = lb.agent_run(
    model="openai:gpt-4",
    messages=[{"role": "user", "content": "Search for AI news"}],
    tools=[{"type": "function", "function": {...}}],
    tool_choice="auto",
    api_key="your-llm-api-key",
    stream=True,
)
```

### 🔧 Tools - Built-in Utilities

```python
# Chunk text for processing
chunks = lb.chunker(
    content="Long text to split...",
    chunk_max_length=1024,
    chunk_overlap=256,
)

# Generate embeddings
embeddings = lb.embed(
    chunks=["Text 1", "Text 2"],
    embedding_model="openai:text-embedding-3-small",
)

# Parse documents
content = lb.parser(
    document=open("document.pdf", "rb"),
    document_name="document.pdf",
    content_type="application/pdf",
)
```

## Examples

Explore the [examples](./examples) directory for complete working examples:

- [Generate text](./examples/pipes/pipes.run.py)
- [Stream text with events](./examples/pipes/pipes.run.typed-stream.py)
- [Work with memory](./examples/memory/)
- [Agent with tools](./examples/agent/)
- [Document processing](./examples/parser/)
- [Workflow automation](./examples/workflow/)

## API Reference

For detailed API documentation, visit [langbase.com/docs/sdk](https://langbase.com/docs/sdk).

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## Support

- 📚 [Documentation](https://langbase.com/docs)
- 💬 [Discord Community](https://langbase.com/discord)
- 🐛 [Issue Tracker](https://github.com/LangbaseInc/langbase-python-sdk/issues)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
