"""
Data format constants and utilities
"""

from enum import Enum


class DataFormat(str, Enum):
    """Supported data format types"""
    JSON = "json"
    CSV = "csv"
    TOON = "toon"
    
    @classmethod
    def all(cls) -> list[str]:
        """Get list of all format values"""
        return [fmt.value for fmt in cls]
    
    @classmethod
    def from_string(cls, value: str) -> "DataFormat":
        """Parse format from string, case-insensitive"""
        value_lower = value.lower()
        for fmt in cls:
            if fmt.value == value_lower:
                return fmt
        raise ValueError(f"Invalid format: {value}. Must be one of: {cls.all()}")
    
    def __str__(self) -> str:
        return self.value
