"""
Format converters for test data
Converts between JSON, CSV, and TOON formats
"""

import json
import csv
from io import StringIO
from typing import List, Dict, Any


def dict_to_json(data: List[Dict[str, Any]]) -> str:
    """Convert list of dicts to JSON string"""
    return json.dumps(data, indent=2)


def dict_to_csv(data: List[Dict[str, Any]]) -> str:
    """Convert list of dicts to CSV string"""
    if not data:
        return ""
    
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    writer.writerows(data)
    return output.getvalue()


def dict_to_toon(data: List[Dict[str, Any]]) -> str:
    """
    Convert list of dicts to TOON format
    
    TOON format example:
    name: Jenil
    role: Developer
    skills: [C#, .NET, Angular]
    active: true
    experience: 4
    
    --------
    
    name: John
    role: Manager
    ...
    """
    
    def _format_value(value: Any, indent: int = 0) -> str:
        """Recursively format a value with proper indentation for nested objects"""
        space = "  " * indent
        
        if isinstance(value, list):
            # Format list as [item1, item2, item3]
            return "[" + ", ".join(str(v) for v in value) + "]"
        elif isinstance(value, dict):
            # Format nested object with indentation
            lines = []
            for k, v in value.items():
                if isinstance(v, dict):
                    lines.append(f"{space}  {k}:")
                    lines.append(_format_value(v, indent + 1))
                else:
                    formatted = _format_value(v, indent + 1)
                    lines.append(f"{space}  {k}: {formatted}")
            return "\n".join(lines)
        elif isinstance(value, bool):
            return str(value).lower()
        else:
            return str(value)
    
    toon_parts = []
    
    for record in data:
        lines = []
        for key, value in record.items():
            if isinstance(value, dict):
                # Nested object: key on its own line, then indented content
                lines.append(f"{key}:")
                lines.append(_format_value(value, indent=0))
            else:
                # Simple value: key: value on same line
                formatted = _format_value(value, indent=0)
                lines.append(f"{key}: {formatted}")
        toon_parts.append("\n".join(lines))
    
    return "\n\n--------\n\n".join(toon_parts)


def json_to_dict(json_str: str) -> List[Dict[str, Any]]:
    """Parse JSON string to list of dicts"""
    data = json.loads(json_str)
    if isinstance(data, dict):
        return [data]
    return data


def csv_to_dict(csv_str: str) -> List[Dict[str, Any]]:
    """Parse CSV string to list of dicts"""
    input_stream = StringIO(csv_str)
    reader = csv.DictReader(input_stream)
    return list(reader)


def toon_to_dict(toon_str: str) -> List[Dict[str, Any]]:
    """Parse TOON format to list of dicts (supports nested objects)"""
    
    def _parse_value(value: str) -> Any:
        """Parse a value string into appropriate Python type"""
        value = value.strip()
        
        if value.startswith("[") and value.endswith("]"):
            # List
            items = value[1:-1].split(", ")
            return [item.strip() for item in items if item.strip()]
        elif value.lower() in ("true", "false"):
            # Boolean
            return value.lower() == "true"
        elif value.isdigit():
            # Integer
            return int(value)
        else:
            # String
            return value
    
    def _parse_lines(lines: List[str], start_idx: int = 0) -> tuple[Dict[str, Any], int]:
        """
        Recursively parse lines with nested object support
        Returns (dict, next_line_index)
        """
        result = {}
        i = start_idx
        current_indent = len(lines[i]) - len(lines[i].lstrip()) if i < len(lines) else 0
        
        while i < len(lines):
            line = lines[i]
            
            # Skip empty lines
            if not line.strip():
                i += 1
                continue
            
            indent = len(line) - len(line.lstrip())
            
            # If indent decreased, we're done with this level
            if indent < current_indent:
                break
            
            # If indent increased, skip (handled by parent)
            if indent > current_indent:
                i += 1
                continue
            
            stripped = line.strip()
            
            # Key with value on same line
            if ": " in stripped:
                key, value = stripped.split(": ", 1)
                result[key] = _parse_value(value)
                i += 1
            # Key only (nested object follows)
            elif stripped.endswith(":"):
                key = stripped[:-1]
                # Parse nested object
                nested, next_i = _parse_lines(lines, i + 1)
                result[key] = nested
                i = next_i
            else:
                i += 1
        
        return result, i
    
    records = []
    
    # Split by record separator
    record_strs = toon_str.strip().split("\n\n--------\n\n")
    
    for record_str in record_strs:
        lines = record_str.strip().split("\n")
        if lines:
            record, _ = _parse_lines(lines, 0)
            if record:
                records.append(record)
    
    return records
