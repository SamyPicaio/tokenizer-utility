# Token Usage Comparison Tool

Compare token counts across different LLM providers (Gemini, OpenAI, Anthropic) and data formats (JSON, CSV, TOON).

## Features

- **Multi-Provider Support**: Compare tokenization across Gemini, OpenAI (GPT), and Anthropic (Claude)
- **Format Comparison**: Test JSON, CSV, and TOON formats with equivalent data
- **JSON Strategy Options**: Test 4 different JSON formatting strategies (pretty, compact, stringified, minimal) - **compact saves ~40-45% tokens**
- **Nested Object Support**: TOON format handles nested objects with automatic indentation
- **File Input Support**: Use your own data files or built-in test datasets
- **Flexible Configuration**: JSON-based config file with environment variable fallback
- **Detailed Analysis**: Optional detailed token breakdown (provider-dependent)
- **Automated Testing**: Built-in test datasets (small, medium, large)
- **Smart Size Handling**: Clear messaging when input files override --size parameter

## Installation

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up API keys (choose one method):

# Method 1: Environment variables
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_CLOUD_PROJECT="your-project"
export GOOGLE_CLOUD_LOCATION="us-central1"

# Method 2: Create config.json (auto-generated on first run)
python tokenizer.py  # Creates config.json
# Then edit config.json with your API keys
```

## Usage

### Basic Comparison
```bash
# Run with default settings (medium dataset, all enabled providers)
python tokenizer.py

# Use small dataset
python tokenizer.py --size small

# Use large dataset
python tokenizer.py --size large
```

### JSON Formatting Strategies
```bash
# Compare with compact JSON (no whitespace) - saves ~40-45% tokens
python tokenizer.py --json-strategy compact

# Test with stringified JSON (as sent to LLM in prompts)
python tokenizer.py --json-strategy stringified

# Minimal representation (same as compact for most cases)
python tokenizer.py --json-strategy minimal

# Pretty (default) - standard indented JSON
python tokenizer.py --json-strategy pretty

# Works with both input files and hardcoded data
python tokenizer.py --input input/ --json-strategy compact
```

### Detailed Token Breakdown
```bash
# Get individual tokens (slower, shows exact tokenization)
python tokenizer.py --detailed
```

### Using Your Own Data
```bash
# Place your data files in input/ directory:
# - input/data.json
# - input/data.csv
# - input/data.toon

# Run with input files (auto-detects and uses them)
python tokenizer.py

# Use custom input directory
python tokenizer.py --input /path/to/data

# Works with partial files (e.g., only JSON and CSV)
# Missing formats will be skipped or auto-converted from JSON

# Combine with JSON strategies
python tokenizer.py --input mydata/ --json-strategy compact
```

### Custom Configuration
```bash
# Use custom config file
python tokenizer.py --config my_config.json

# Specify output filename
python tokenizer.py --output my_results.json
```

## Configuration

The tool creates a `config.json` file on first run. Edit it to:
- Enable/disable specific providers
- Set API keys (alternative to environment variables)
- Configure default models
- Set output directory

Example `config.json`:
```json
{
  "providers": {
    "gemini": {
      "enabled": true,
      "project": "your-gcp-project",
      "location": "us-central1",
      "default_model": "gemini-2.5-flash"
    },
    "openai": {
      "enabled": true,
      "api_key": "sk-...",
      "default_model": "gpt-4o"
    },
    "anthropic": {
      "enabled": true,
      "api_key": "sk-ant-...",
      "default_model": "claude-3-5-sonnet-20241022"
    }
  },
  "test_data": {
    "formats": ["json", "csv", "toon"],
    "output_dir": "results"
  }
}
```

## Data Formats

### JSON (4 Formatting Strategies)

Use `--json-strategy` to test different JSON formats and their token efficiency:

| Strategy | Description | Token Savings | Example Size |
|----------|-------------|---------------|--------------|
| **pretty** (default) | Standard indented JSON | baseline | 284 chars, 96 tokens |
| **compact** | No whitespace | ~40-45% | 206 chars, 56 tokens |
| **stringified** | Escaped string (as in prompts) | ~30-35% | 248 chars, 66 tokens |
| **minimal** | Absolute minimal | ~40-45% | 206 chars, 56 tokens |

**Example: Pretty Format**
```json
[
  {
    "name": "Jenil",
    "role": "Developer",
    "skills": ["C#", ".NET", "Angular"],
    "active": true,
    "experience": 4
  }
]
```

**Example: Compact Format**
```json
[{"name":"Jenil","role":"Developer","skills":["C#",".NET","Angular"],"active":true,"experience":4}]
```

**Example: Stringified Format**
```json
"[{\"name\":\"Jenil\",\"role\":\"Developer\",\"skills\":[\"C#\",\".NET\",\"Angular\"],\"active\":true,\"experience\":4}]"
```

### CSV
```csv
name,role,skills,active,experience
Jenil,Developer,"['C#', '.NET', 'Angular']",True,4
```

### TOON

TOON format supports nested objects with automatic indentation (2 spaces per level):

```
name: Jenil
role: Developer
skills: [C#, .NET, Angular]
active: true
experience: 4
```

**With nested objects:**
```
name: Jenil
role: Developer
skills: [C#, Angular]
active: true
contact:
  email: jenil@example.com
  address:
    city: New York
    country: USA
```

## Project Structure

```
.
├── tokenizer.py          # Main CLI entry point
├── config.py             # Configuration management
├── comparison.py         # Comparison engine
├── test_data.py          # Test data generation
├── models.py             # Data models
├── providers/
│   ├── base.py          # Abstract provider interface
│   ├── gemini.py        # Google Gemini provider
│   ├── openai.py        # OpenAI provider
│   └── anthropic.py     # Anthropic provider
├── formats/
│   ├── converters.py    # Format conversion utilities
│   └── json_strategies.py # JSON formatting strategies
├── input/
│   ├── README.md        # Input file documentation
│   └── data.json        # Your data files (optional)
├── results/             # Output directory for comparison results
├── requirements.txt
├── constants.py         # DataFormat and JSONStrategy enums
└── README.md
```

## Output

Results are saved in `results/` directory as JSON files with metrics including:
- Total token count
- Content size in bytes
- Tokens per byte ratio (efficiency metric)
- Provider and model used
- Format tested
- Timestamp

Console summary includes:
- Per-format comparison across providers
- Average tokens by format
- Efficiency metrics
- Token savings when using compact strategies

Example output:
```
JSON FORMAT:
----------------------------------------
  openai       gpt-4                              56 tokens  (0.272 tokens/byte, 206 bytes)

AVERAGES BY FORMAT:
----------------------------------------
  json         56.0 tokens  (0.272 tokens/byte)
  csv          50.0 tokens  (0.336 tokens/byte)
  toon         55.0 tokens  (0.297 tokens/byte)
```

## Input Data

The tool supports two modes:

### 1. File Input (Recommended for Real Data)
Place files in `input/` directory (or specify with `--input`):
- `data.json` - JSON array of objects
- `data.csv` - CSV with headers
- `data.toon` - TOON format records

**Behavior:**
- ✓ Auto-detects and uses available files from input directory
- ✓ Works with 1, 2, or all 3 formats (partial files supported)
- ✓ Applies `--json-strategy` to loaded JSON files (reformats on-the-fly)
- ✓ If only JSON exists, auto-converts to CSV and TOON
- ✓ Falls back to hardcoded samples if no files found
- ✓ Input files override `--size` parameter (with clear warning message)

**Example:**
```bash
# Create input files
echo '[{"name":"Alice","role":"Engineer"}]' > input/data.json

# Run comparison with your data
python tokenizer.py --json-strategy compact
# Output: ✓ Loaded data.json from input
#         ✓ Reformatted JSON with compact strategy
```

### 2. Hardcoded Samples (Automatic Fallback)
If no input files found, uses built-in datasets:
- **Small**: 1 employee record (Jenil - Developer)
- **Medium**: 3 employee records (Jenil, Sarah, Marcus)
- **Large**: 50 generated employee records

Controlled via `--size` flag: `python tokenizer.py --size large`

## Troubleshooting

**Import errors**: Ensure all dependencies are installed: `pip install -r requirements.txt`

**Authentication errors**: 
- Gemini: Ensure `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` are set
- OpenAI: Set `OPENAI_API_KEY` (optional - tiktoken works locally without it)
- Anthropic: Set `ANTHROPIC_API_KEY`

**Provider not available**: Check that provider is enabled in `config.json`

**Input file not detected**: 
- Ensure files are named exactly `data.json`, `data.csv`, `data.toon`
- Check they're in the `input/` directory or the path specified by `--input`
- Look for `✓ Loaded data.json from input` message in output

**JSON strategy not applied**: 
- Only works when no input files or when input contains JSON
- Look for `✓ Reformatted JSON with {strategy} strategy` message
- Pretty strategy is applied by default (no reformatting message shown)

**--size parameter ignored**:
- The `--size` parameter only works with hardcoded datasets
- If input files exist in `input/` directory, they take precedence
- Look for `→ Input files found - will use them instead of hardcoded data (--size large parameter will be ignored)` message
- To use `--size`, temporarily move/remove files from `input/` directory

## License

MIT
