# Agent Examples

This directory contains examples demonstrating how to use the Langbase Python SDK's agent functionality.

## Prerequisites

Before running these examples, make sure you have:

1. **Langbase API Key**: Sign up at [Langbase](https://langbase.com) and get your API key
2. **LLM API Key**: Get an API key from your preferred LLM provider (OpenAI, Anthropic, etc.)
3. **Python Dependencies**: Install the required packages:
   ```bash
   pip install langbase requests
   ```

## Environment Variables

Set the following environment variables:

```bash
export LANGBASE_API_KEY="your_langbase_api_key"
export LLM_API_KEY="your_llm_api_key"  # OpenAI, Anthropic, etc.
```

For specific examples, you may need additional API keys:
- `RESEND_API_KEY` for the email tool example
- `OPENAI_API_KEY` for examples that specifically use OpenAI

## Examples

### 1. Basic Agent Run (`agent.run.py`)

Demonstrates how to run a basic agent with a user message.

```bash
python agent.run.py
```

**Features:**
- Simple agent execution
- Basic instructions
- Single user message

### 2. Agent Run with Streaming (`agent.run.stream.py`)

Shows how to run an agent with streaming response for real-time output.

```bash
python agent.run.stream.py
```

**Features:**
- Streaming response handling
- Real-time output processing
- Server-sent events parsing

### 3. Agent Run with Structured Output (`agent.run.structured.py`)

Demonstrates how to get structured JSON output from an agent using response schemas.

```bash
python agent.run.structured.py
```

**Features:**
- JSON schema definition
- Structured output validation
- Math problem solving example

### 4. Agent Run with Memory (`agent.run.memory.py`)

Shows how to retrieve and use memory in agent calls for context-aware responses.

```bash
python agent.run.memory.py
```

**Features:**
- Memory retrieval
- Context injection
- Career advice example

**Note:** You'll need to have a memory named "career-advisor-memory" created in your Langbase account.

### 5. Agent Run with Tools (`agent.run.tool.py`)

Demonstrates how to create and use tools with agents, including function calling and execution.

```bash
python agent.run.tool.py
```

**Features:**
- Tool schema definition
- Function calling
- Email sending example with Resend API
- Tool execution handling

**Additional Requirements:**
- `RESEND_API_KEY` environment variable
- Resend account for email functionality

### 6. Agent Run with MCP (`agent.run.mcp.py`)

Shows how to use Model Context Protocol (MCP) servers with agents.

```bash
python agent.run.mcp.py
```

**Features:**
- MCP server configuration
- External data source integration
- Technical documentation queries

## Common Patterns

### Error Handling

All examples include basic error handling and environment variable validation:

```python
if not os.environ.get("LANGBASE_API_KEY"):
    print("❌ Missing LANGBASE_API_KEY in environment variables.")
    exit(1)
```

### Client Initialization

Standard client initialization pattern:

```python
from langbase import Langbase

langbase = Langbase(api_key=os.environ.get("LANGBASE_API_KEY"))
```

### Agent Execution

Basic agent run pattern:

```python
response = langbase.agent.run(
    model="openai:gpt-4.1-mini",
    api_key=os.environ.get("LLM_API_KEY"),
    instructions="Your instructions here",
    input=[
        {
            "role": "user",
            "content": "Your message here"
        }
    ]
)
```

## Model Support

These examples work with various LLM providers:
- OpenAI (gpt-4.1, gpt-4.1-mini, gpt-3.5-turbo)
- Anthropic (claude-3-opus, claude-3-sonnet, claude-3-haiku)
- Google (gemini-pro, gemini-pro-vision)
- And many more

## Troubleshooting

### Common Issues

1. **Missing API Keys**: Ensure all required environment variables are set
2. **Network Issues**: Check your internet connection and API endpoint accessibility
3. **Rate Limits**: Some providers have rate limits; implement appropriate backoff strategies
4. **Response Format**: Ensure your response format schemas are valid JSON Schema

### Debug Mode

To enable debug mode, you can modify the examples to include additional logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Next Steps

- Explore the [Langbase Documentation](https://docs.langbase.com)
- Try creating your own custom tools
- Experiment with different models and parameters
- Build multi-agent workflows
