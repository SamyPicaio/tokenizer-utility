from typing import List, Optional, Union
from google import genai
from google.genai.types import HttpOptions, Part, Content
from providers.base import LLMProvider
from models import TokenCountResult, DetailedTokenResult
from constants import DataFormat
from datetime import datetime


class GeminiProvider(LLMProvider):
    """Google Gemini provider for token counting"""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize Gemini provider
        
        :param api_key: Not used for Gemini (uses GCP credentials)
        :param kwargs: Should include 'project' and 'location' for GCP
        """
        super().__init__(api_key, **kwargs)
        self.client = genai.Client(http_options=HttpOptions(api_version="v1"))
    
    def _validate_credentials(self):
        """Validate GCP credentials are available"""
        import os
        if 'project' not in self.config:
            self.config['project'] = os.getenv('GOOGLE_CLOUD_PROJECT')
        if 'location' not in self.config:
            self.config['location'] = os.getenv('GOOGLE_CLOUD_LOCATION')
        
        if not self.config.get('project') or not self.config.get('location'):
            raise ValueError(
                "Gemini requires GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION "
                "environment variables or config parameters"
            )
    
    def count_tokens(self, model: str, content: str, format_type: Union[DataFormat, str]) -> TokenCountResult:
        """
        Count tokens for given content using Gemini
        
        :param model: Model name (e.g., "gemini-2.5-flash")
        :param content: Text content to tokenize
        :param format_type: Format type (DataFormat enum or string)
        :return: TokenCountResult
        """
        contents = [Content(parts=[Part(text=content)])]
        
        response = self.client.models.count_tokens(
            model=model,
            contents=contents
        )
        
        content_bytes = len(content.encode('utf-8'))
        tokens_per_byte = response.total_tokens / content_bytes if content_bytes > 0 else 0
        
        return TokenCountResult(
            total_tokens=response.total_tokens,
            model=model,
            provider=self.get_provider_name(),
            format_type=format_type,
            content_size_bytes=content_bytes,
            tokens_per_byte=tokens_per_byte,
            timestamp=datetime.now()
        )
    
    def compute_tokens_detailed(self, model: str, content: str, format_type: Union[DataFormat, str]) -> DetailedTokenResult:
        """
        Get detailed token breakdown using Gemini
        
        :param model: Model name (e.g., "gemini-2.5-flash")
        :param content: Text content to tokenize
        :param format_type: Format type (DataFormat enum or string)
        :return: DetailedTokenResult
        """
        contents = [Content(parts=[Part(text=content)])]
        
        response = self.client.models.compute_tokens(
            model=model,
            contents=contents
        )
        
        # Extract token IDs and decoded tokens
        all_token_ids = []
        all_tokens = []
        
        for info in response.tokens_info:
            all_token_ids.extend(info.token_ids)
            # Decode tokens, handling potential decode errors
            for token_bytes in info.tokens:
                try:
                    decoded = token_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    decoded = token_bytes.decode("utf-8", errors="replace")
                all_tokens.append(decoded)
        
        content_bytes = len(content.encode('utf-8'))
        total_tokens = len(all_token_ids)
        tokens_per_byte = total_tokens / content_bytes if content_bytes > 0 else 0
        
        return DetailedTokenResult(
            total_tokens=total_tokens,
            model=model,
            provider=self.get_provider_name(),
            format_type=format_type,
            content_size_bytes=content_bytes,
            tokens_per_byte=tokens_per_byte,
            timestamp=datetime.now(),
            token_ids=all_token_ids,
            tokens=all_tokens,
            overhead_tokens=None,  # Will be calculated by analysis layer
            content_tokens=None
        )
    
    def get_available_models(self) -> List[str]:
        """Return list of commonly used Gemini models"""
        return [
            "gemini-2.5-flash",
            "gemini-2.0-flash-exp",
            "gemini-1.5-pro",
            "gemini-1.5-flash"
        ]
