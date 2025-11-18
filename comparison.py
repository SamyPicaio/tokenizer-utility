"""
Comparison engine for running token count tests across providers and formats
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime

from providers.base import LLMProvider
from models import TokenCountResult, DetailedTokenResult
from test_data import TestDataGenerator
from constants import DataFormat
from formats.json_strategies import JSONStrategy


class ComparisonEngine:
    """Run token comparison tests across providers and formats"""
    
    def __init__(
        self, 
        providers: List[LLMProvider], 
        output_dir: str = "results",
        input_dir: Optional[str] = None
    ):
        """
        Initialize comparison engine
        
        :param providers: List of LLMProvider instances to test
        :param output_dir: Directory to save results
        :param input_dir: Optional directory to load input files from
        """
        self.providers = providers
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.test_data_gen = TestDataGenerator(input_dir=input_dir)
    
    def run_comparison(
        self,
        dataset_size: str = "medium",
        models: Optional[Dict[str, str]] = None,
        detailed: bool = False,
        json_strategy: JSONStrategy = JSONStrategy.PRETTY
    ) -> List[Dict[str, Any]]:
        """
        Run token count comparison across all providers and formats
        
        :param dataset_size: Size of dataset ('small', 'medium', 'large')
        :param models: Dict mapping provider names to model names (optional)
        :param detailed: Whether to get detailed token breakdown
        :param json_strategy: JSON formatting strategy to use
        :return: List of result dictionaries
        """
        results = []
        
        # Generate test data in all formats
        test_data = self.test_data_gen.generate_all_formats(dataset_size, json_strategy)
        
        # Run tests for each provider
        for provider in self.providers:
            provider_name = provider.get_provider_name()
            
            # Get model to use
            if models and provider_name in models:
                model = models[provider_name]
            else:
                # Use first available model
                available_models = provider.get_available_models()
                model = available_models[0] if available_models else "unknown"
            
            # Test each format
            for format_type, content in test_data.items():
                try:
                    if detailed:
                        result = provider.compute_tokens_detailed(model, content, format_type)
                    else:
                        result = provider.count_tokens(model, content, format_type)
                    
                    results.append(result.to_dict())
                    print(f"✓ {provider_name} / {model} / {format_type}: {result.total_tokens} tokens")
                
                except Exception as e:
                    print(f"✗ {provider_name} / {model} / {format_type}: Error - {str(e)}")
                    results.append({
                        "provider": provider_name,
                        "model": model,
                        "format_type": format_type,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    })
        
        return results
    
    def save_results(self, results: List[Dict[str, Any]], filename: Optional[str] = None):
        """
        Save comparison results to JSON file
        
        :param results: List of result dictionaries
        :param filename: Output filename (auto-generated if not provided)
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"comparison_{timestamp}.json"
        
        output_path = self.output_dir / filename
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✓ Results saved to {output_path}")
    
    def generate_summary(self, results: List[Dict[str, Any]]) -> str:
        """
        Generate a human-readable summary of results
        
        :param results: List of result dictionaries
        :return: Formatted summary string
        """
        summary_lines = ["\n" + "="*80]
        summary_lines.append("TOKEN COMPARISON SUMMARY")
        summary_lines.append("="*80 + "\n")
        
        # Group by format
        by_format = {}
        for result in results:
            if "error" in result:
                continue
            
            format_type = result["format_type"]
            if format_type not in by_format:
                by_format[format_type] = []
            by_format[format_type].append(result)
        
        # Display results by format
        for format_type, format_results in sorted(by_format.items()):
            summary_lines.append(f"\n{format_type.upper()} FORMAT:")
            summary_lines.append("-" * 40)
            
            for result in format_results:
                provider = result["provider"]
                model = result["model"]
                tokens = result["total_tokens"]
                tpb = result["tokens_per_byte"]
                size = result["content_size_bytes"]
                
                summary_lines.append(
                    f"  {provider:12} {model:30} {tokens:6} tokens  "
                    f"({tpb:.3f} tokens/byte, {size} bytes)"
                )
        
        # Calculate averages
        summary_lines.append("\n" + "="*80)
        summary_lines.append("AVERAGES BY FORMAT:")
        summary_lines.append("-" * 40)
        
        for format_type, format_results in sorted(by_format.items()):
            avg_tokens = sum(r["total_tokens"] for r in format_results) / len(format_results)
            avg_tpb = sum(r["tokens_per_byte"] for r in format_results) / len(format_results)
            
            summary_lines.append(
                f"  {format_type:8} {avg_tokens:8.1f} tokens  ({avg_tpb:.3f} tokens/byte)"
            )
        
        summary_lines.append("="*80 + "\n")
        
        return "\n".join(summary_lines)
