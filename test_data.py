"""
Test data management for format comparison
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
from formats.converters import (
    dict_to_csv, dict_to_toon,
    json_to_dict, csv_to_dict, toon_to_dict
)
from formats.json_strategies import format_json, JSONStrategy
from constants import DataFormat


# Sample test data sets
SAMPLE_SMALL = [
    {
        "name": "Jenil",
        "role": "Developer",
        "skills": ["C#", ".NET", "Angular"],
        "active": True,
        "experience": 4
    }
]

SAMPLE_MEDIUM = [
    {
        "name": "Jenil",
        "role": "Developer",
        "skills": ["C#", ".NET", "Angular"],
        "active": True,
        "experience": 4
    },
    {
        "name": "Sarah",
        "role": "Designer",
        "skills": ["Figma", "Sketch", "Photoshop"],
        "active": True,
        "experience": 6
    },
    {
        "name": "Marcus",
        "role": "Manager",
        "skills": ["Leadership", "Agile", "Communication"],
        "active": False,
        "experience": 10
    }
]

SAMPLE_LARGE = [
    {
        "name": f"Employee{i}",
        "role": ["Developer", "Designer", "Manager", "Analyst"][i % 4],
        "skills": [f"Skill{j}" for j in range(3 + (i % 5))],
        "active": i % 3 != 0,
        "experience": (i % 15) + 1
    }
    for i in range(50)
]


class TestDataGenerator:
    """Generate test data in different formats"""
    
    def __init__(self, input_dir: Optional[str] = None):
        """
        Initialize test data generator
        
        :param input_dir: Optional directory to load data files from (json, csv, toon)
        """
        self.datasets = {
            "small": SAMPLE_SMALL,
            "medium": SAMPLE_MEDIUM,
            "large": SAMPLE_LARGE
        }
        self.input_dir = Path(input_dir) if input_dir else Path("input")
        self.loaded_formats = self._load_input_files()
    
    def get_dataset(self, size: str = "medium") -> List[Dict[str, Any]]:
        """Get dataset by size"""
        return self.datasets.get(size, SAMPLE_MEDIUM)
    
    def _load_input_files(self) -> Dict[str, str]:
        """
        Load data from input directory if available
        Returns dict of format -> raw content for files that exist
        """
        loaded = {}
        
        if not self.input_dir.exists():
            return loaded
        
        # Try to load each format
        format_files = {
            DataFormat.JSON.value: "data.json",
            DataFormat.CSV.value: "data.csv",
            DataFormat.TOON.value: "data.toon"
        }
        
        for format_type, filename in format_files.items():
            file_path = self.input_dir / filename
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        loaded[format_type] = content
                        print(f"✓ Loaded {filename} from {self.input_dir}")
                except Exception as e:
                    print(f"✗ Failed to load {filename}: {e}")
        
        return loaded
    
    def has_input_files(self) -> bool:
        """Check if any input files were loaded"""
        return len(self.loaded_formats) > 0
    
    def generate_all_formats(
        self, 
        size: str = "medium",
        json_strategy: JSONStrategy = JSONStrategy.PRETTY
    ) -> Dict[str, str]:
        """
        Generate test data in all formats
        Uses input files if available, otherwise generates from hardcoded data
        
        :param size: Dataset size ('small', 'medium', 'large') - ignored if using input files
        :param json_strategy: JSON formatting strategy (applied to JSON output)
        :return: Dict with format names as keys and formatted strings as values
        """
        # If we have loaded input files, use those
        if self.has_input_files():
            print(f"Using input files from {self.input_dir}")
            result = {}
            
            # Use loaded formats directly (but reformat JSON based on strategy)
            for format_type, content in self.loaded_formats.items():
                if format_type == DataFormat.JSON.value and json_strategy != JSONStrategy.PRETTY:
                    # Reformat JSON based on strategy
                    try:
                        data = json_to_dict(content)
                        result[format_type] = format_json(data, json_strategy)
                        print(f"✓ Reformatted JSON with {json_strategy.value} strategy")
                    except Exception as e:
                        print(f"✗ Could not reformat JSON: {e}, using original")
                        result[format_type] = content
                else:
                    result[format_type] = content
            
            # Generate missing formats from loaded data if possible
            if DataFormat.JSON.value in self.loaded_formats and len(result) == 1:
                # We have JSON, can generate others
                try:
                    data = json_to_dict(self.loaded_formats[DataFormat.JSON.value])
                    if DataFormat.CSV.value not in result:
                        result[DataFormat.CSV.value] = dict_to_csv(data)
                    if DataFormat.TOON.value not in result:
                        result[DataFormat.TOON.value] = dict_to_toon(data)
                except Exception as e:
                    print(f"✗ Could not convert JSON to other formats: {e}")
            
            return result
        
        # Fallback to hardcoded data
        print(f"No input files found in {self.input_dir}, using hardcoded {size} dataset")
        data = self.get_dataset(size)
        
        return {
            DataFormat.JSON.value: format_json(data, json_strategy),
            DataFormat.CSV.value: dict_to_csv(data),
            DataFormat.TOON.value: dict_to_toon(data)
        }
    
    def get_custom_data(
        self, 
        data: List[Dict[str, Any]],
        json_strategy: JSONStrategy = JSONStrategy.PRETTY
    ) -> Dict[str, str]:
        """
        Convert custom data to all formats
        
        :param data: List of dicts to convert
        :param json_strategy: JSON formatting strategy
        :return: Dict with format names as keys and formatted strings as values
        """
        return {
            DataFormat.JSON.value: format_json(data, json_strategy),
            DataFormat.CSV.value: dict_to_csv(data),
            DataFormat.TOON.value: dict_to_toon(data)
        }
