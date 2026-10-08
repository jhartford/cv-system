#!/usr/bin/env python3

# Simple test to check Jinja2 template syntax
import re

# Read the template file
with open('/Users/jason.hartford/Developer/Research/cv-system/cv_manager/templates/promotion.j2', 'r') as f:
    template_content = f.read()

# Simple syntax checks
brace_count = template_content.count('{%') - template_content.count('%}')
if brace_count != 0:
    print(f"Unmatched template blocks: {brace_count}")
else:
    print("Template block syntax appears balanced")

# Check for problematic patterns
problematic_patterns = [
    r'\{{{[^}]*}}}',  # Triple braces
    r'{{[^}]*{{',     # Nested opening braces
    r'}}[^{]*}}',     # Nested closing braces
]

for pattern in problematic_patterns:
    matches = re.findall(pattern, template_content)
    if matches:
        print(f"Found potentially problematic pattern: {pattern}")
        for match in matches[:3]:  # Show first 3 matches
            print(f"  {match}")

print("Basic syntax check completed.")