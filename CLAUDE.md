# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Multi-provider token comparison tool for analyzing token usage across LLM providers (Gemini, OpenAI, Anthropic) and data formats (JSON, CSV, TOON).

## Commands

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Basic usage
python tokenizer.py                      # Default run with medium dataset
python tokenizer.py --size small|medium|large
python tokenizer.py --json-strategy compact  # ~45% fewer tokens
python tokenizer.py --detailed           # Token breakdown (provider-dependent)
python tokenizer.py --input /path/to/data
```

## Architecture

### Provider Pattern
All providers in `providers/` extend `LLMProvider` abstract base class (`providers/base.py`):
- `_validate_credentials()` - Check credentials on init
- `count_tokens(model, content, format_type)` → `TokenCountResult`
- `compute_tokens_detailed(model, content, format_type)` → `DetailedTokenResult`
- `get_available_models()` → List of model identifiers

### Core Components
- **`tokenizer.py`**: CLI entry point with argparse
- **`comparison.py`**: `ComparisonEngine` orchestrates tests and generates reports
- **`config.py`**: Configuration manager (config.json → env vars fallback)
- **`models.py`**: `TokenCountResult` and `DetailedTokenResult` dataclasses
- **`test_data.py`**: `TestDataGenerator` with SMALL/MEDIUM/LARGE datasets

### Format Converters (`formats/`)
- `converters.py`: Bidirectional conversion (dict ↔ csv/toon)
- `json_strategies.py`: PRETTY, COMPACT, STRINGIFIED, MINIMAL strategies

### Result Data Flow
`TestDataGenerator` → formats → `ComparisonEngine` → providers → `TokenCountResult` → JSON output + console summary

## Key Patterns

### DataFormat Enum
```python
from constants import DataFormat

format_type = DataFormat.JSON          # Not "json" strings
all_formats = DataFormat.all()         # ['json', 'csv', 'toon']
fmt = DataFormat.from_string("csv")    # Case-insensitive parsing
```

### TOON Format
```
key: value
list_key: [item1, item2, item3]
bool_key: true

--------

(next record)
```
Records separated by `\n\n--------\n\n`, booleans lowercase, lists in brackets.

## Provider-Specific Notes

### Gemini (`providers/gemini.py`)
- Uses `google.genai.Client` with `HttpOptions(api_version="v1")`
- Content wrapped: `Content(parts=[Part(text=content)])`
- Tokens are byte arrays: decode with `token.decode("utf-8", errors="replace")`
- Requires `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION`

### OpenAI (`providers/openai.py`)
- Uses `tiktoken.encoding_for_model()` (local tokenization, no API needed)
- Falls back to `cl100k_base` encoding for unknown models

### Anthropic (`providers/anthropic.py`)
- API method: `client.messages.count_tokens(model, messages=[...])`
- **Limitation**: Does NOT provide individual token breakdown (returns empty lists)

## Adding New Providers

1. Create `providers/new_provider.py` extending `LLMProvider`
2. Implement abstract methods: `_validate_credentials`, `count_tokens`, `compute_tokens_detailed`, `get_available_models`
3. Add to `create_providers()` in `tokenizer.py`
4. Add config section to `config.py` defaults
