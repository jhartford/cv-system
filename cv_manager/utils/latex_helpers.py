"""LaTeX-specific utility functions."""

import re
from typing import Any


def escape_latex(text: Any) -> str:
    """Escape special LaTeX characters in text.

    Args:
        text: Input text to escape (can be any type, will be converted to string)

    Returns:
        String with LaTeX special characters escaped
    """
    if text is None:
        return ""

    text = str(text)

    # Escape backslash FIRST, before other characters
    text = text.replace('\\', r'\textbackslash{}')

    # Dictionary of other LaTeX special characters and their escaped versions
    latex_chars = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '^': r'\textasciicircum{}',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
    }

    # Apply escaping for other characters
    for char, escape in latex_chars.items():
        text = text.replace(char, escape)

    return text


def escape_latex_filter(text: Any) -> str:
    """Jinja2 filter version of escape_latex."""
    return escape_latex(text)


# For backward compatibility
latex_escape = escape_latex