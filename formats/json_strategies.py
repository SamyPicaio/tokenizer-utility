"""
JSON formatting strategies for token efficiency comparison
"""

import json
from typing import List, Dict, Any
from enum import Enum


class JSONStrategy(str, Enum):
    """JSON formatting strategies"""
    PRETTY = "pretty"           # Standard formatted JSON with indentation
    COMPACT = "compact"         # No whitespace, minimal size
    STRINGIFIED = "stringified" # JSON as escaped string (as if sent to LLM)
    MINIMAL = "minimal"         # No spaces, no newlines, shortest possible
    
    @classmethod
    def all(cls) -> list[str]:
        """Get list of all strategy values"""
        return [strategy.value for strategy in cls]
    
    @classmethod
    def from_string(cls, value: str) -> "JSONStrategy":
        """Parse strategy from string, case-insensitive"""
        value_lower = value.lower()
        for strategy in cls:
            if strategy.value == value_lower:
                return strategy
        raise ValueError(f"Invalid JSON strategy: {value}. Must be one of: {cls.all()}")


def format_json_pretty(data: List[Dict[str, Any]]) -> str:
    """
    Pretty-printed JSON with indentation (default)
    Example: {\n  "name": "John"\n}
    """
    return json.dumps(data, indent=2)


def format_json_compact(data: List[Dict[str, Any]]) -> str:
    """
    Compact JSON with minimal whitespace
    Example: [{"name": "John","age": 30}]
    """
    return json.dumps(data, separators=(',', ':'))


def format_json_stringified(data: List[Dict[str, Any]]) -> str:
    """
    JSON as escaped string (simulating how it's sent to LLM in a prompt)
    Example: "{\"name\":\"John\",\"age\":30}"
    """
    compact = json.dumps(data, separators=(',', ':'))
    # Double-escape to show how it appears in a string
    return json.dumps(compact)


def format_json_minimal(data: List[Dict[str, Any]]) -> str:
    """
    Absolute minimal JSON - no spaces, no optional syntax
    Example: [{"name":"John","age":30}]
    """
    return json.dumps(data, separators=(',', ':'), ensure_ascii=False)


# Strategy mapping
JSON_FORMATTERS = {
    JSONStrategy.PRETTY: format_json_pretty,
    JSONStrategy.COMPACT: format_json_compact,
    JSONStrategy.STRINGIFIED: format_json_stringified,
    JSONStrategy.MINIMAL: format_json_minimal,
}


def format_json(data: List[Dict[str, Any]], strategy: JSONStrategy = JSONStrategy.PRETTY) -> str:
    """
    Format JSON data according to specified strategy
    
    :param data: List of dictionaries to format
    :param strategy: JSONStrategy enum value
    :return: Formatted JSON string
    """
    if isinstance(strategy, str):
        strategy = JSONStrategy.from_string(strategy)
    
    formatter = JSON_FORMATTERS.get(strategy)
    if not formatter:
        raise ValueError(f"Unknown JSON strategy: {strategy}")
    
    return formatter(data)
