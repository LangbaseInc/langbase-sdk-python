# Langbase Python SDK

The AI SDK for building declarative and composable AI-powered LLM products.

## Documentation

Check the [Langbase SDK documentation](https://langbase.com/docs/sdk) for more details.

The following examples are for reference only. Prefer docs for the latest information.

## Getting Started with `langbase` SDK

### Installation

First, install the `langbase` package using npm or yarn:

```bash
pip install langbase
```

### Usage

You can [`langbase.pipes.run()`](https://langbase.com/docs/sdk/pipe/run) to generate or stream from a Pipe.

Check our [SDK documentation](https://langbase.com/docs/sdk) for more details.

### Example projects

Check the following examples:

- [Python: Generate Text](https://github.com/LangbaseInc/langbase-python-sdk/blob/main/examples/python/pipes/pipe.run.py)
- [Python: Stream Text](https://github.com/LangbaseInc/langbase-python-sdk/blob/main/examples/python/pipes/pipe.run.stream.py)

### Python Example Code

## Python Examples

### Add a `.env` file with your LANGBASE API key

```bash
# Add your Langbase API key here: https://langbase.com/docs/api-reference/api-keys
LANGBASE_API_KEY="your-api-key"
```

---

### Generate text [`langbase.pipes.run()`](https://langbase.com/docs/sdk/pipe/run)

Set the `stream` to `false`. For more, check the API reference of [`langbase.pipes.run()`](https://langbase.com/docs/langbase-sdk/generate-text)

```py
import json
import os
from dotenv import load_dotenv
from langbase import Langbase

load_dotenv()

# Get API key from environment variable
langbase_api_key = os.getenv("LANGBASE_API_KEY")

# Initialize the client
lb = Langbase(api_key=langbase_api_key)

response = lb.pipes.run(
    name="summary-agent",
    messages=[{"role": "user", "content": "Who is an AI Engineer?"}],
    stream=False,
)

# Print the entire response as is
print(json.dumps(response, indent=2))

```

---

### Stream text [`langbase.pipes.run()`](https://langbase.com/docs/sdk/pipe/run)

Set the `stream` to `true`. For more, check the API reference of [`langbase.pipes.run()`](https://langbase.com/docs/langbase-sdk/generate-text)

```py
import json
import os
from dotenv import load_dotenv
from langbase.streaming import stream_text
from langbase import Langbase

load_dotenv()

# Get API key from environment variable
langbase_api_key = os.getenv("LANGBASE_API_KEY")

# Initialize the client
lb = Langbase(api_key=langbase_api_key)

stream_response = lb.pipes.run(
    name="summary-agent",
    messages=[{"role": "user", "content": "Who is an AI Engineer?"}],
    stream=True,
)

print("Stream started\n\n")

# Process each chunk as it arrives
for text in stream_text(stream_response["stream"]):
    print(text, end="", flush=True)

print("\n\nStream completed")

```

Check out [more examples in the docs](https://langbase.com/docs/sdk/examples) →