from typing import List, Optional, Union
import tiktoken
from providers.base import LLMProvider
from models import TokenCountResult, DetailedTokenResult
from constants import DataFormat
from datetime import datetime


class OpenAIProvider(LLMProvider):
    """OpenAI provider for token counting using tiktoken"""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize OpenAI provider
        
        :param api_key: OpenAI API key (optional for token counting)
        :param kwargs: Additional configuration
        """
        super().__init__(api_key, **kwargs)
    
    def _validate_credentials(self):
        """API key not strictly required for token counting with tiktoken"""
        if not self.api_key:
            import os
            self.api_key = os.getenv('OPENAI_API_KEY')
        # Note: tiktoken works without API key, but we store it for potential future API calls
    
    def _get_encoding_for_model(self, model: str):
        """Get the appropriate tiktoken encoding for a model"""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            # Fallback to cl100k_base for newer models
            encoding = tiktoken.get_encoding("cl100k_base")
        return encoding
    
    def count_tokens(self, model: str, content: str, format_type: Union[DataFormat, str]) -> TokenCountResult:
        """
        Count tokens for given content using tiktoken
        
        :param model: Model name (e.g., "gpt-4", "gpt-3.5-turbo")
        :param content: Text content to tokenize
        :param format_type: Format type (DataFormat enum or string)
        :return: TokenCountResult
        """
        encoding = self._get_encoding_for_model(model)
        tokens = encoding.encode(content)
        
        content_bytes = len(content.encode('utf-8'))
        total_tokens = len(tokens)
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
        Get detailed token breakdown using tiktoken
        
        :param model: Model name (e.g., "gpt-4", "gpt-3.5-turbo")
        :param content: Text content to tokenize
        :param format_type: Format type (DataFormat enum or string)
        :return: DetailedTokenResult
        """
        encoding = self._get_encoding_for_model(model)
        token_ids = encoding.encode(content)
        
        # Decode each token to get string representation
        tokens = []
        for token_id in token_ids:
            try:
                token_str = encoding.decode([token_id])
                tokens.append(token_str)
            except Exception:
                tokens.append(f"<token_{token_id}>")
        
        content_bytes = len(content.encode('utf-8'))
        total_tokens = len(token_ids)
        tokens_per_byte = total_tokens / content_bytes if content_bytes > 0 else 0
        
        return DetailedTokenResult(
            total_tokens=total_tokens,
            model=model,
            provider=self.get_provider_name(),
            format_type=format_type,
            content_size_bytes=content_bytes,
            tokens_per_byte=tokens_per_byte,
            timestamp=datetime.now(),
            token_ids=token_ids,
            tokens=tokens,
            overhead_tokens=None,
            content_tokens=None
        )
    
    def get_available_models(self) -> List[str]:
        """Return list of commonly used OpenAI models"""
        return [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4o",
            "gpt-3.5-turbo",
            "o1-preview",
            "o1-mini"
        ]
