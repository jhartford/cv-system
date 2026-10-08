#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, '/Users/jason.hartford/Developer/Research/cv-system')

from jinja2 import Environment, FileSystemLoader
import yaml

# Load template
env = Environment(loader=FileSystemLoader('/Users/jason.hartford/Developer/Research/cv-system/cv_manager/templates'))
template = env.get_template('promotion.j2')

# Load test data
with open('/Users/jason.hartford/Developer/Research/test-cv/data/personal.yaml', 'r') as f:
    personal_data = yaml.safe_load(f)

with open('/Users/jason.hartford/Developer/Research/test-cv/data/grants.yaml', 'r') as f:
    grants_data = yaml.safe_load(f)

# Mock data for required sections
data = {
    'personal': personal_data['personal'],
    'education': personal_data.get('education', []),
    'employment': personal_data.get('employment', []),
    'joint_appointments': personal_data.get('joint_appointments', []),
    'visiting_appointments': personal_data.get('visiting_appointments', []),
    'past_appointments': personal_data.get('past_appointments', []),
    'memberships': personal_data.get('memberships', []),
    'grants': grants_data,
    'publications': {
        'journal_papers': [],
        'conference_papers': []
    },
    'teaching': {'supervision': []},
    'service': {},
    'talks': {}
}

try:
    result = template.render(**data)
    print("Template rendered successfully!")
except Exception as e:
    print(f"Error rendering template: {e}")
    print(f"Error type: {type(e).__name__}")
    if hasattr(e, 'lineno'):
        print(f"Line number: {e.lineno}")