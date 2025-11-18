from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Union

from constants import DataFormat


@dataclass
class TokenCountResult:
    """Result from a token counting operation"""
    total_tokens: int
    model: str
    provider: str
    format_type: Union[DataFormat, str]
    content_size_bytes: int
    tokens_per_byte: float
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self):
        return {
            'total_tokens': self.total_tokens,
            'model': self.model,
            'provider': self.provider,
            'format_type': str(self.format_type),
            'content_size_bytes': self.content_size_bytes,
            'tokens_per_byte': self.tokens_per_byte,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class DetailedTokenResult(TokenCountResult):
    """Detailed token breakdown including individual tokens"""
    token_ids: List[int] = field(default_factory=list)
    tokens: List[str] = field(default_factory=list)
    overhead_tokens: Optional[int] = None  # delimiters, structure tokens
    content_tokens: Optional[int] = None   # actual data tokens
    
    def to_dict(self):
        base = super().to_dict()
        base.update({
            'token_ids': self.token_ids,
            'tokens': self.tokens,
            'overhead_tokens': self.overhead_tokens,
            'content_tokens': self.content_tokens
        })
        return base
