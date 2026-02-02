"""LaTeX-specific utility functions."""

import re
from typing import Any


def escape_latex(text: Any) -> str:
    """Escape special LaTeX characters in text.

    This function is smart about not double-escaping text that already contains
    LaTeX commands (like accented characters).

    Args:
        text: Input text to escape (can be any type, will be converted to string)

    Returns:
        String with LaTeX special characters escaped
    """
    if text is None:
        return ""

    text = str(text)

    # Check if text appears to already contain LaTeX commands
    # Common patterns: {\'e}, {\`a}, {\^o}, {\~n}, etc.
    if re.search(r'\\[`\'^~"]?[a-zA-Z]|\{\\[`\'^~"]?[a-zA-Z]\}', text):
        # Text likely already contains LaTeX accent commands, don't escape
        return text

    # Check for other common LaTeX commands that shouldn't be escaped
    latex_command_patterns = [
        r'\\[a-zA-Z]+\{[^}]*\}',  # \command{arg}
        r'\\[a-zA-Z]+',           # \command
        r'\$[^$]*\$',             # Math mode $...$
    ]

    for pattern in latex_command_patterns:
        if re.search(pattern, text):
            return text

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

    # Apply escaping for other characters (but preserve LaTeX command braces)
    for char, escape_seq in latex_chars.items():
        if char in ['{', '}']:
            # Don't escape braces that are part of LaTeX commands like \pounds{}
            # Only escape standalone braces
            if char == '{':
                # Replace { that are not preceded by a backslash and letter
                text = re.sub(r'(?<!\\[a-zA-Z])\{', r'\\{', text)
            elif char == '}':
                # Replace } that are not following a LaTeX command
                text = re.sub(r'(?<!\\[a-zA-Z]\{[^}]*)\}', r'\\}', text)
        else:
            text = text.replace(char, escape_seq)

    return text


def escape_latex_filter(text: Any) -> str:
    """Jinja2 filter version of escape_latex."""
    return escape_latex(text)


def unicode_to_latex(text: Any) -> str:
    """Convert Unicode characters to LaTeX equivalents.

    This handles common accented characters and converts them to LaTeX commands.
    """
    if text is None:
        return ""

    text = str(text)

    # Unicode to LaTeX accent mappings
    unicode_map = {
        # Acute accents
        'á': r'{\'a}', 'é': r'{\'e}', 'í': r'{\'i}', 'ó': r'{\'o}', 'ú': r'{\'u}', 'ý': r'{\'y}',
        'Á': r'{\'A}', 'É': r'{\'E}', 'Í': r'{\'I}', 'Ó': r'{\'O}', 'Ú': r'{\'U}', 'Ý': r'{\'Y}',

        # Grave accents
        'à': r'{\`a}', 'è': r'{\`e}', 'ì': r'{\`i}', 'ò': r'{\`o}', 'ù': r'{\`u}',
        'À': r'{\`A}', 'È': r'{\`E}', 'Ì': r'{\`I}', 'Ò': r'{\`O}', 'Ù': r'{\`U}',

        # Circumflex accents
        'â': r'{\^a}', 'ê': r'{\^e}', 'î': r'{\^i}', 'ô': r'{\^o}', 'û': r'{\^u}',
        'Â': r'{\^A}', 'Ê': r'{\^E}', 'Î': r'{\^I}', 'Ô': r'{\^O}', 'Û': r'{\^U}',

        # Tilde accents
        'ã': r'{\~a}', 'ñ': r'{\~n}', 'õ': r'{\~o}',
        'Ã': r'{\~A}', 'Ñ': r'{\~N}', 'Õ': r'{\~O}',

        # Diaeresis (umlaut)
        'ä': r'{\"a}', 'ë': r'{\"e}', 'ï': r'{\"i}', 'ö': r'{\"o}', 'ü': r'{\"u}', 'ÿ': r'{\"y}',
        'Ä': r'{\"A}', 'Ë': r'{\"E}', 'Ï': r'{\"I}', 'Ö': r'{\"O}', 'Ü': r'{\"U}', 'Ÿ': r'{\"Y}',

        # Cedilla
        'ç': r'{\c{c}}', 'Ç': r'{\c{C}}',

        # Scandinavian and other
        'å': r'{\aa}', 'Å': r'{\AA}', 'æ': r'{\ae}', 'Æ': r'{\AE}', 'ø': r'{\o}', 'Ø': r'{\O}',
        'ß': r'{\ss}',

        # Common symbols
        '–': '--', '—': '---', ''': '`', ''': "'", '"': '``', '"': "''",
        '£': r'\pounds{}',
    }

    for unicode_char, latex_cmd in unicode_map.items():
        text = text.replace(unicode_char, latex_cmd)

    return text


def smart_latex_escape(text: Any) -> str:
    """Smart LaTeX escaping that handles Unicode properly.

    Escapes LaTeX special characters first, then converts Unicode to LaTeX commands.
    """
    if text is None:
        return ""

    text = str(text)

    # Check if text appears to already contain LaTeX commands
    # Common patterns: {\'e}, {\`a}, {\^o}, {\~n}, etc.
    if re.search(r'\\[`\'^~"]?[a-zA-Z]|\{\\[`\'^~"]?[a-zA-Z]\}', text):
        # Text likely already contains LaTeX accent commands, don't escape
        return text

    # First escape LaTeX special characters (except those that will be handled by Unicode conversion)
    # Don't escape characters that are part of Unicode that will be converted

    # Store Unicode characters temporarily to avoid escaping chars within them
    unicode_chars = ['£', 'á', 'é', 'í', 'ó', 'ú', 'ý', 'Á', 'É', 'Í', 'Ó', 'Ú', 'Ý',
                    'à', 'è', 'ì', 'ò', 'ù', 'À', 'È', 'Ì', 'Ò', 'Ù',
                    'â', 'ê', 'î', 'ô', 'û', 'Â', 'Ê', 'Î', 'Ô', 'Û',
                    'ã', 'ñ', 'õ', 'Ã', 'Ñ', 'Õ',
                    'ä', 'ë', 'ï', 'ö', 'ü', 'ÿ', 'Ä', 'Ë', 'Ï', 'Ö', 'Ü', 'Ÿ',
                    'ç', 'Ç', 'å', 'Å', 'æ', 'Æ', 'ø', 'Ø', 'ß']

    # Standard LaTeX character escaping
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

    # Escape backslash FIRST, before other characters
    text = text.replace('\\', r'\textbackslash{}')

    # Apply escaping for other characters
    for char, escape_seq in latex_chars.items():
        text = text.replace(char, escape_seq)

    # Finally convert Unicode characters to LaTeX
    text = unicode_to_latex(text)

    return text


# For backward compatibility
latex_escape = escape_latex