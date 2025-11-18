# Copilot Instructions

## Project Overview
Multi-provider token comparison tool for analyzing token usage across LLM providers (Gemini, OpenAI, Anthropic) and data formats (JSON, CSV, TOON).

## Architecture

### Core Components
- **`tokenizer.py`**: CLI entry point with argparse for running comparisons
- **`config.py`**: Configuration manager (loads from `config.json` or environment variables)
- **`comparison.py`**: `ComparisonEngine` orchestrates tests and generates reports
- **`models.py`**: `TokenCountResult` and `DetailedTokenResult` dataclasses
- **`test_data.py`**: `TestDataGenerator` with SMALL/MEDIUM/LARGE datasets
- **`constants.py`**: `DataFormat` enum for format types (replaces magic strings)

### Provider Pattern
All providers in `providers/` extend `LLMProvider` abstract base class:
- **`base.py`**: Defines interface (`count_tokens`, `compute_tokens_detailed`, `get_available_models`)
- **`gemini.py`**: Google GenAI SDK wrapper (requires GCP credentials)
- **`openai.py`**: Uses `tiktoken` library (works without API for counting)
- **`anthropic.py`**: Anthropic SDK (doesn't expose individual tokens)

### Format Converters
`formats/converters.py` provides bidirectional conversion:
- `dict_to_{csv,toon}()` - Convert Python dicts to format strings
- `{json,csv,toon}_to_dict()` - Parse format strings back to dicts

`formats/json_strategies.py` provides multiple JSON formatting strategies:
- `PRETTY` - Standard indented JSON (baseline)
- `COMPACT` - No whitespace (~45% fewer tokens)
- `STRINGIFIED` - Escaped string format (as sent to LLM)
- `MINIMAL` - Absolute minimal representation

## Key Patterns

### DataFormat Enum
```python
from constants import DataFormat

# Use enum instead of strings
format_type = DataFormat.JSON  # not "json"
all_formats = DataFormat.all()  # ['json', 'csv', 'toon']
fmt = DataFormat.from_string("csv")  # case-insensitive parsing
```

### Provider Interface
```python
# All providers implement:
result = provider.count_tokens(model, content, format_type)
# Returns TokenCountResult with tokens, tokens_per_byte, size_bytes
# format_type accepts DataFormat enum or string

detailed = provider.compute_tokens_detailed(model, content, format_type)
# Returns DetailedTokenResult with token_ids and tokens list
```

### TOON Format Structure
```
key: value
list_key: [item1, item2, item3]
bool_key: true

--------

(next record)
```
Records separated by `\n\n--------\n\n`, booleans lowercase, lists in brackets.

### Configuration Priority
1. `config.json` file (auto-generated on first run)
2. Environment variables (fallback)
3. Providers validate credentials in `_validate_credentials()`

### Result Data Flow
`TestDataGenerator` → formats → `ComparisonEngine` → providers → `TokenCountResult` → JSON output + console summary

## Usage Patterns

```bash
# Basic run (uses config.json)
python tokenizer.py

# Dataset sizes: small (1 record), medium (3), large (50)
python tokenizer.py --size large

# JSON formatting strategies (test token efficiency)
python tokenizer.py --json-strategy compact  # ~45% fewer tokens
python tokenizer.py --json-strategy stringified

# Get token breakdown (where supported)
python tokenizer.py --detailed

# Custom config
python tokenizer.py --config prod_config.json --output prod_results.json
```

## Provider-Specific Notes

### Gemini (`providers/gemini.py`)
- Uses `google.genai.Client` with `HttpOptions(api_version="v1")`
- Content must be wrapped: `Content(parts=[Part(text=content)])`
- Tokens are byte arrays: decode with `token.decode("utf-8", errors="replace")`
- Requires `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION`

### OpenAI (`providers/openai.py`)
- Uses `tiktoken.encoding_for_model()` (local tokenization, no API needed)
- Falls back to `cl100k_base` encoding for unknown models
- To decode tokens: `encoding.decode([token_id])`

### Anthropic (`providers/anthropic.py`)
- Uses `anthropic.Anthropic(api_key=...)`
- API method: `client.messages.count_tokens(model, messages=[...])`
- **Limitation**: Does NOT provide individual token breakdown (returns empty lists)

## Adding New Providers

1. Create `providers/new_provider.py` extending `LLMProvider`
2. Implement abstract methods: `_validate_credentials`, `count_tokens`, `compute_tokens_detailed`, `get_available_models`
3. Add to `create_providers()` in `tokenizer.py`
4. Add config section to `config.py` defaults

## Dependencies
- `google-genai` - Gemini API access
- `tiktoken` - OpenAI tokenization
- `anthropic` - Claude API access
- No external deps for format conversion (uses stdlib `json`, `csv`)

## Common Issues
- **Import errors on providers**: Expected if SDK not installed; provider initialization wrapped in try/except
- **Anthropic token details**: `compute_tokens_detailed()` returns empty `token_ids`/`tokens` (API limitation)
- **Token decode errors**: Use `errors="replace"` parameter for UTF-8 decoding
