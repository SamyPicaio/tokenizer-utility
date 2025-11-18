import os
import json
from typing import Dict, Optional, Any
from pathlib import Path

from constants import DataFormat


class Config:
    """Configuration manager for LLM providers and API keys"""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration
        
        :param config_file: Path to JSON config file (optional)
        """
        self.config_file = config_file or "config.json"
        self.config_data: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file if it exists"""
        config_path = Path(self.config_file)
        if config_path.exists():
            with open(config_path, 'r') as f:
                self.config_data = json.load(f)
        else:
            # Create default config file
            self.config_data = self._get_default_config()
            self._save_config()
    
    def _save_config(self):
        """Save configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config_data, f, indent=2)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration structure"""
        return {
            "providers": {
                "gemini": {
                    "enabled": True,
                    "project": os.getenv("GOOGLE_CLOUD_PROJECT", ""),
                    "location": os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
                    "default_model": "gemini-2.5-flash"
                },
                "openai": {
                    "enabled": True,
                    "api_key": os.getenv("OPENAI_API_KEY", ""),
                    "default_model": "gpt-4o"
                },
                "anthropic": {
                    "enabled": True,
                    "api_key": os.getenv("ANTHROPIC_API_KEY", ""),
                    "default_model": "claude-3-5-sonnet-20241022"
                }
            },
            "test_data": {
                "formats": DataFormat.all(),
                "output_dir": "results"
            }
        }
    
    def get_provider_config(self, provider_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific provider
        
        :param provider_name: Name of provider ('gemini', 'openai', 'anthropic')
        :return: Provider configuration dict
        """
        return self.config_data.get("providers", {}).get(provider_name, {})
    
    def get_api_key(self, provider_name: str) -> Optional[str]:
        """
        Get API key for a provider (checks config file, then environment)
        
        :param provider_name: Name of provider
        :return: API key or None
        """
        provider_config = self.get_provider_config(provider_name)
        
        # Check config file first
        api_key = provider_config.get("api_key")
        if api_key:
            return api_key
        
        # Fall back to environment variables
        env_var_map = {
            "gemini": None,  # Uses GCP credentials
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY"
        }
        
        env_var = env_var_map.get(provider_name)
        if env_var:
            return os.getenv(env_var)
        
        return None
    
    def is_provider_enabled(self, provider_name: str) -> bool:
        """Check if a provider is enabled"""
        provider_config = self.get_provider_config(provider_name)
        return provider_config.get("enabled", False)
    
    def get_enabled_providers(self) -> list[str]:
        """Get list of enabled provider names"""
        return [
            name for name, config in self.config_data.get("providers", {}).items()
            if config.get("enabled", False)
        ]
    
    def get_output_dir(self) -> str:
        """Get output directory for results"""
        return self.config_data.get("test_data", {}).get("output_dir", "results")
    
    def get_test_formats(self) -> list[str]:
        """Get list of formats to test"""
        return self.config_data.get("test_data", {}).get("formats", DataFormat.all())
