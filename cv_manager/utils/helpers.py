"""Utility functions for CV management."""

import os
import yaml
import re
from typing import Any, Dict, List, Optional
from pathlib import Path


def load_yaml(file_path: str) -> Dict[str, Any]:
    """Load YAML file and return data."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        return {}
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML file {file_path}: {e}")


def save_yaml(data: Dict[str, Any], file_path: str, create_dir: bool = True) -> None:
    """Save data to YAML file."""
    if create_dir:
        ensure_directory(os.path.dirname(file_path))

    with open(file_path, 'w', encoding='utf-8') as file:
        yaml.dump(data, file, default_flow_style=False, sort_keys=False,
                 allow_unicode=True, width=1000, indent=2)


def ensure_directory(directory: str) -> None:
    """Ensure directory exists, create if not."""
    if directory and not os.path.exists(directory):
        os.makedirs(directory)


def parse_author_list(author_string: str) -> List[str]:
    """Parse author string into list of individual authors."""
    # Handle bold markdown for names (remove **)
    author_string = re.sub(r'\*\*(.*?)\*\*', r'\1', author_string)

    # Split by comma and clean up
    authors = [author.strip() for author in author_string.split(',')]
    return [author for author in authors if author]


def extract_year_from_string(text: str) -> Optional[int]:
    """Extract year from string."""
    year_match = re.search(r'\b(20\d{2})\b', text)
    return int(year_match.group(1)) if year_match else None


def clean_title(title: str) -> str:
    """Clean publication title by removing quotes and extra whitespace."""
    # Remove surrounding quotes
    title = re.sub(r'^["\']|["\']$', '', title.strip())
    # Clean up whitespace
    title = ' '.join(title.split())
    return title


def parse_venue_info(venue_text: str) -> Dict[str, Optional[str]]:
    """Parse venue information from text."""
    venue_info = {
        'venue': None,
        'type': None,
        'acceptance_rate': None,
        'award': None
    }

    # Extract acceptance rate
    rate_match = re.search(r'(\d+(?:\.\d+)?%?\s*acceptance rate)', venue_text, re.IGNORECASE)
    if rate_match:
        venue_info['acceptance_rate'] = rate_match.group(1)
        venue_text = venue_text.replace(rate_match.group(0), '').strip()

    # Extract presentation type
    if 'oral presentation' in venue_text.lower() or 'oral' in venue_text.lower():
        venue_info['type'] = 'oral'
    elif 'poster' in venue_text.lower():
        venue_info['type'] = 'poster'

    # Extract awards
    award_patterns = [
        r'best\s+paper\s+award',
        r'best\s+poster\s+award',
        r'runner[- ]?up\s+best\s+paper',
        r'runner[- ]?up\s+best\s+poster'
    ]

    for pattern in award_patterns:
        if re.search(pattern, venue_text, re.IGNORECASE):
            venue_info['award'] = re.search(pattern, venue_text, re.IGNORECASE).group(0)
            break

    # Clean venue name
    venue_clean = re.sub(r'\*\*.*?\*\*', '', venue_text)  # Remove bold markdown
    venue_clean = re.sub(r'oral presentation.*', '', venue_clean, flags=re.IGNORECASE)
    venue_clean = re.sub(r'best\s+(paper|poster)\s+award.*', '', venue_clean, flags=re.IGNORECASE)
    venue_clean = venue_clean.strip(' -')

    venue_info['venue'] = venue_clean if venue_clean else None

    return venue_info


def normalize_name(name: str) -> str:
    """Normalize author name by handling bold formatting."""
    # Remove bold markdown and clean up spacing
    name = re.sub(r'\*\*(.*?)\*\*', r'\1', name)
    return ' '.join(name.split())


def parse_markdown_list_item(line: str) -> Optional[Dict[str, str]]:
    """Parse a markdown list item and extract structured information."""
    # Remove list marker
    line = re.sub(r'^\s*-\s*', '', line.strip())

    if not line:
        return None

    return {'text': line}