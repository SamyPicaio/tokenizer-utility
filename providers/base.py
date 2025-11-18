from abc import ABC, abstractmethod
from typing import List, Optional, Union
from models import TokenCountResult, DetailedTokenResult
from constants import DataFormat


class LLMProvider(ABC):
    """Abstract base class for LLM token counting providers"""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        Initialize the provider with API credentials
        
        :param api_key: API key for the provider
        :param kwargs: Additional provider-specific configuration
        """
        self.api_key = api_key
        self.config = kwargs
        self._validate_credentials()
    
    @abstractmethod
    def _validate_credentials(self):
        """Validate that required credentials are present"""
        pass
    
    @abstractmethod
    def count_tokens(self, model: str, content: str, format_type: Union[DataFormat, str]) -> TokenCountResult:
        """
        Count total tokens for given content
        
        :param model: Model name/identifier
        :param content: Text content to tokenize
        :param format_type: Format of content (DataFormat enum or string)
        :return: TokenCountResult with token count and metadata
        """
        pass
    
    @abstractmethod
    def compute_tokens_detailed(self, model: str, content: str, format_type: Union[DataFormat, str]) -> DetailedTokenResult:
        """
        Get detailed token breakdown including individual tokens
        
        :param model: Model name/identifier
        :param content: Text content to tokenize
        :param format_type: Format of content (DataFormat enum or string)
        :return: DetailedTokenResult with full token breakdown
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """
        Return list of supported models for this provider
        
        :return: List of model identifiers
        """
        pass
    
    def get_provider_name(self) -> str:
        """Return the name of this provider"""
        return self.__class__.__name__.replace('Provider', '').lower()
