from typing import List, Optional, Union
from anthropic import Anthropic
from providers.base import LLMProvider
from models import TokenCountResult, DetailedTokenResult
from constants import DataFormat
from datetime import datetime


class AnthropicProvider(LLMProvider):
    """Anthropic (Claude) provider for token counting"""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize Anthropic provider
        
        :param api_key: Anthropic API key
        :param kwargs: Additional configuration
        """
        super().__init__(api_key, **kwargs)
        self.client = Anthropic(api_key=self.api_key)
    
    def _validate_credentials(self):
        """Validate Anthropic API key is available"""
        if not self.api_key:
            import os
            self.api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "Anthropic requires ANTHROPIC_API_KEY environment variable or api_key parameter"
            )
    
    def count_tokens(self, model: str, content: str, format_type: Union[DataFormat, str]) -> TokenCountResult:
        """
        Count tokens for given content using Anthropic's API
        
        :param model: Model name (e.g., "claude-3-5-sonnet-20241022")
        :param content: Text content to tokenize
        :param format_type: Format type (DataFormat enum or string)
        :return: TokenCountResult
        """
        # Anthropic's count_tokens method
        response = self.client.messages.count_tokens(
            model=model,
            messages=[{"role": "user", "content": content}]
        )
        
        content_bytes = len(content.encode('utf-8'))
        total_tokens = response.input_tokens
        tokens_per_byte = total_tokens / content_bytes if content_bytes > 0 else 0
        
        return TokenCountResult(
            total_tokens=total_tokens,
            model=model,
            provider=self.get_provider_name(),
            format_type=format_type,
            content_size_bytes=content_bytes,
            tokens_per_byte=tokens_per_byte,
            timestamp=datetime.now()
        )
    
    def compute_tokens_detailed(self, model: str, content: str, format_type: Union[DataFormat, str]) -> DetailedTokenResult:
        """
        Get token count (Anthropic doesn't provide detailed token breakdown via API)
        
        :param model: Model name (e.g., "claude-3-5-sonnet-20241022")
        :param content: Text content to tokenize
        :param format_type: Format type (DataFormat enum or string)
        :return: DetailedTokenResult (without individual tokens)
        """
        # Anthropic doesn't expose individual tokens, only count
        response = self.client.messages.count_tokens(
            model=model,
            messages=[{"role": "user", "content": content}]
        )
        
        content_bytes = len(content.encode('utf-8'))
        total_tokens = response.input_tokens
        tokens_per_byte = total_tokens / content_bytes if content_bytes > 0 else 0
        
        return DetailedTokenResult(
            total_tokens=total_tokens,
            model=model,
            provider=self.get_provider_name(),
            format_type=format_type,
            content_size_bytes=content_bytes,
            tokens_per_byte=tokens_per_byte,
            timestamp=datetime.now(),
            token_ids=[],  # Not available from Anthropic API
            tokens=[],     # Not available from Anthropic API
            overhead_tokens=None,
            content_tokens=None
        )
    
    def get_available_models(self) -> List[str]:
        """Return list of commonly used Anthropic models"""
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
