#!/usr/bin/env python3
"""
Token Usage Test - Compare token counts across LLM providers and data formats
"""

import argparse
import sys
from typing import List, Optional
from pathlib import Path

from config import Config
from comparison import ComparisonEngine
from providers.base import LLMProvider
from formats.json_strategies import JSONStrategy


def _init_provider(name: str, config: Config, factory) -> Optional[LLMProvider]:
    """
    Initialize a single provider with error handling
    
    :param name: Provider name for display
    :param config: Config instance
    :param factory: Callable that creates the provider instance
    :return: Provider instance or None if initialization fails
    """
    if not config.is_provider_enabled(name.lower()):
        return None
    
    try:
        provider = factory(config)
        print(f"✓ {name} provider initialized")
        return provider
    except Exception as e:
        print(f"✗ Failed to initialize {name}: {e}")
        return None


def create_providers(config: Config) -> List[LLMProvider]:
    """
    Create provider instances based on configuration
    
    :param config: Config instance
    :return: List of initialized providers
    """
    provider_factories = {
        "Gemini": lambda cfg: _create_gemini_provider(cfg),
        "OpenAI": lambda cfg: _create_openai_provider(cfg),
        "Anthropic": lambda cfg: _create_anthropic_provider(cfg),
    }
    
    providers = []
    for name, factory in provider_factories.items():
        provider = _init_provider(name, config, factory)
        if provider:
            providers.append(provider)
    
    return providers


def _create_gemini_provider(config: Config) -> LLMProvider:
    """Create Gemini provider instance"""
    from providers.gemini import GeminiProvider
    gemini_config = config.get_provider_config("gemini")
    return GeminiProvider(
        project=gemini_config.get("project"),
        location=gemini_config.get("location")
    )


def _create_openai_provider(config: Config) -> LLMProvider:
    """Create OpenAI provider instance"""
    from providers.openai import OpenAIProvider
    api_key = config.get_api_key("openai")
    return OpenAIProvider(api_key=api_key)


def _create_anthropic_provider(config: Config) -> LLMProvider:
    """Create Anthropic provider instance"""
    from providers.anthropic import AnthropicProvider
    api_key = config.get_api_key("anthropic")
    return AnthropicProvider(api_key=api_key)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Compare token usage across LLM providers and data formats (JSON, CSV, TOON)",
        epilog="Example: python tokenizer.py --json-strategy compact --size large --output results.json"
    )
    parser.add_argument(
        "--config",
        default="config.json",
        help="Path to configuration file (default: config.json)"
    )
    parser.add_argument(
        "--size",
        choices=["small", "medium", "large"],
        default="medium",
        help="Dataset size for hardcoded test data: small=1 record, medium=3, large=50 (default: medium). Ignored if input files are found."
    )
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Get detailed token breakdown with individual token IDs (slower, provider-dependent)"
    )
    parser.add_argument(
        "--output",
        help="Output filename for results JSON file in results/ directory (auto-generated timestamp filename if not provided)"
    )
    parser.add_argument(
        "--json-strategy",
        choices=JSONStrategy.all(),
        default="pretty",
        help="JSON formatting strategy: pretty=indented (baseline), compact=no whitespace (~45%% savings), stringified=escaped string, minimal=absolute minimal (default: pretty)"
    )
    parser.add_argument(
        "--input",
        help="Input directory containing data files: data.json, data.csv, data.toon. Partial files supported. Falls back to hardcoded data if empty. (default: input/)"
    )
    
    args = parser.parse_args()
    
    # Load configuration
    print(f"\nLoading configuration from {args.config}...")
    config = Config(args.config)
    
    # Initialize providers
    print("\nInitializing providers...")
    providers = create_providers(config)
    
    if not providers:
        print("\n✗ No providers available. Please check your configuration and API keys.")
        sys.exit(1)
    
    print(f"\n✓ {len(providers)} provider(s) ready\n")
    
    # Run comparison
    json_strategy = JSONStrategy.from_string(args.json_strategy)
    input_dir = args.input or "input"
    
    print(f"\nChecking for input files in {input_dir}/...")
    
    # Check if input files exist to inform user
    from pathlib import Path
    input_path = Path(input_dir)
    has_input = False
    if input_path.exists():
        json_file = input_path / "data.json"
        csv_file = input_path / "data.csv"
        toon_file = input_path / "data.toon"
        has_input = json_file.exists() or csv_file.exists() or toon_file.exists()
    
    if has_input:
        print(f"→ Input files found - will use them instead of hardcoded data")
        print(f"  (--size {args.size} parameter will be ignored)")
    else:
        print(f"→ No input files found - will use hardcoded {args.size} dataset")
    
    print(f"JSON strategy: {json_strategy.value}")
    print("="*80)
    
    engine = ComparisonEngine(
        providers, 
        output_dir=config.get_output_dir(),
        input_dir=input_dir
    )
    results = engine.run_comparison(
        dataset_size=args.size,
        detailed=args.detailed,
        json_strategy=json_strategy
    )
    
    # Display summary
    summary = engine.generate_summary(results)
    print(summary)
    
    # Save results
    engine.save_results(results, filename=args.output)


if __name__ == "__main__":
    main()
