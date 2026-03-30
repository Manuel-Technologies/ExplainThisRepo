# `explain_this_repo/providers`

Provider implementations for ExplainThisRepo.

This module implements the **LLM provider architecture** used by the CLI.
It allows ExplainThisRepo to support multiple language model backends without coupling the core CLI to any specific vendor SDK.

The CLI is **provider-agnostic**. All model interaction happens through this provider layer.

Model selection is delegated to provider configuration.

# Overview

ExplainThisRepo previously relied on a **single hard-coded model provider (Gemini)**.

The provider system implements a **pluggable architecture** that separates:

```
CLI logic
prompt generation
repository analysis
```

from

```
model providers
vendor SDKs
API configuration
diagnostics
```

The result is a clean separation of concerns.

# Architecture

The provider system consists of the following components:

```
providers/
│
├── base.py        # Provider interface
├── registry.py    # Provider resolution
│
├── gemini.py      # Gemini implementation
├── openai.py      # OpenAI implementation
├── ollama.py      # Ollama implementation
├── anthropic.py   # Anthropic implementation
├── groq.py        # Groq implementation
└── openrouter.py  # OpenRouter implementation
```

Each provider implements the same interface defined in `base.py`.

# Provider Contract

All providers must implement the `LLMProvider` interface.

```python
class LLMProvider(ABC):

    name: str

    def validate_config(self) -> None:
        ...

    def generate(self, prompt: str) -> str:
        ...

    def doctor(self) -> list[str] | bool:
        ...
```

## Responsibilities

### `validate_config()`

Ensures required configuration values exist.

Examples:

* API keys
* model name
* server host

This method should fail early if configuration is invalid.

### `generate(prompt)`

Executes the model request and returns the generated text.

Providers are responsible for:

* constructing the API request
* handling vendor SDK behavior
* translating API errors
* ensuring text output exists

The CLI expects this method to return **a non-empty string**.

### `doctor()`

Runs provider diagnostics.

This method is used by:

```bash
explainthisrepo --doctor
```

Providers can implement checks such as:

* API key presence
* server connectivity
* model availability

Return value may be:

```
True
False
list[str]
```

# Provider Registry

Provider resolution is handled by `registry.py`.

The registry is responsible for:

* mapping provider names to implementations
* loading provider configuration
* selecting the configured provider

Example registry mapping:

```python
_PROVIDER_REGISTRY = {
    "gemini": "explain_this_repo.providers.gemini.GeminiProvider",
    "openai": "explain_this_repo.providers.openai.OpenAIProvider",
    "ollama": "explain_this_repo.providers.ollama.OllamaProvider",
    "anthropic": "explain_this_repo.providers.anthropic.AnthropicProvider",
    "groq": "explain_this_repo.providers.groq.GroqProvider",
    "openrouter": "explain_this_repo.providers.openrouter.OpenRouterProvider",
}
```

The active provider is determined by:

1. `--llm` runtime flag
2. configured provider from config.toml

Resolution flow:

```
CLI
  ↓
generate()
  ↓
registry.get_active_provider()
  ↓
provider.generate()
```

Only one provider is resolved per execution. No fallback or chaining is performed.

# Configuration

ExplainThisRepo supports multiple LLM providers, but only one active provider is used per run.

- Gemini
- OpenAI
- Ollama
- Anthropic
- Groq
- OpenRouter

Run `explainthisrepo init` to select a provider and write its configuration.

The configuration is single-provider.

Only one provider is stored and used unless overridden with `--llm`.

Provider configuration is stored in `config.toml`.

Example for Gemini:

```toml
[llm]
provider = "gemini"

[providers.gemini]
api_key = "..."
```
Example for OpenAI:

```toml
[llm]
provider = "openai"

[providers.openai]
api_key = "..."
```

Example for Ollama:

```toml
[llm]
provider = "ollama"

[providers.ollama]
model = "<user-selected>"
host = "http://localhost:11434"
```

Example for Anthropic:

```toml
[llm]
provider = "anthropic"

[providers.anthropic]
api_key = "..."
```

Example for Groq:

```toml
[llm]
provider = "groq"

[providers.groq]
api_key = "..."
model = "<user-selected>"
```

Example for OpenRouter:

```toml
[llm]
provider = "openrouter"

[providers.openrouter]
api_key = "..."
model = "<user-selected>"
```

Only the configured or overridden provider is used during execution.

If required fields (e.g. API key or model) are missing, the provider will fail during validation or execution.

## Provider Configuration Types

Providers fall into two categories:

### API-only providers
Require only an API key:
- Gemini
- OpenAI
- Anthropic

### Model-configured providers
Require user model selection:
- Ollama
- Groq
- OpenRouter

# Runtime Provider Selection

Only one provider is stored and used. Users can override the configured provider using `--llm`:

```
explainthisrepo owner/repo --llm gemini
explainthisrepo owner/repo --llm openai
explainthisrepo owner/repo --llm ollama
explainthisrepo owner/repo --llm anthropic
explainthisrepo owner/repo --llm groq
explainthisrepo owner/repo --llm openrouter
```

This override is resolved by the provider registry.

# Optional Dependencies

Some providers require additional SDK dependencies.

Example:

```
pip install explainthisrepo[gemini]
pip install explainthisrepo[openai]
pip install explainthisrepo[anthropic]
pip install explainthisrepo[groq]
```

Ollama uses HTTP and does not require additional Python dependencies.

# Adding a New Provider

To add a new provider:

### 1. Implement the provider

Create:

```
providers/myprovider.py
```

Example:

```python
from explain_this_repo.providers.base import LLMProvider


class MyProvider(LLMProvider):

    name = "myprovider"

    def validate_config(self):
        ...

    def generate(self, prompt: str) -> str:
        ...

    def doctor(self):
        ...
```

---

### 2. Register the provider

Add it to the registry:

```python
_PROVIDER_REGISTRY["myprovider"] = "explain_this_repo.providers.myprovider.MyProvider"
```

---

### 3. Update configuration

Add provider configuration support to `init.py`.

# Design Principles

The provider architecture follows several rules:

### CLI must remain vendor-agnostic

No vendor SDK logic should appear in:

```
cli.py
generate.py
prompt.py
repo_reader.py
```

All vendor interaction belongs inside providers.

### Providers own SDK logic

Providers are responsible for:

* initializing SDK clients
* formatting requests
* handling API errors
* running diagnostics

### Core modules remain stable

The core CLI should not change when new providers are added.

Only the provider layer expands.

# Why This Architecture Exists

This system enables:

• support for multiple LLM vendors
• runtime model selection
• isolated vendor integrations
• easier testing
• future provider expansion

The CLI can now evolve independently of any specific model provider.

# Summary

The provider system isolates model interaction from the rest of the application.

Only one provider is active per execution

This keeps the CLI:

```
stable
extensible
vendor-agnostic
```

All future model integrations should be implemented inside this module.

This module defines the integration boundary for LLM providers.

For more details about how initialization works, see also [INIT.md](https://github.com/calchiwo/ExplainThisRepo/blob/main/docs/INIT.md)