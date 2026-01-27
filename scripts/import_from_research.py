#!/usr/bin/env python3
"""
Import CV data from Research/cv/ markdown files and convert to YAML format.

This script reads the existing markdown files (papers.md, awards.md, teaching.md,
service.md, talks.md) and converts them to structured YAML files compatible
with the CV management system.
"""

import re
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add cv_manager to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from cv_manager.utils.helpers import (
    save_yaml, parse_author_list, extract_year_from_string,
    clean_title, parse_venue_info, normalize_name
)


class CVMarkdownImporter:
    """Import CV data from markdown files."""

    def __init__(self, source_dir: str, output_dir: str):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)

    def import_all(self) -> None:
        """Import all CV data files."""
        print("Importing CV data from Research/cv/...")

        # Create output directories
        data_dir = self.output_dir / "data"
        data_dir.mkdir(parents=True, exist_ok=True)

        # Import each section
        self.import_publications()
        self.import_grants()
        self.import_teaching()
        self.import_service()
        self.import_talks()
        self.create_personal_info()
        self.create_config()

        print("Import completed successfully!")

    def import_publications(self) -> None:
        """Import publications from papers.md."""
        papers_file = self.source_dir / "papers.md"
        if not papers_file.exists():
            print(f"Warning: {papers_file} not found")
            return

        print("Importing publications...")
        with open(papers_file, 'r', encoding='utf-8') as f:
            content = f.read()

        publications = {
            "preprints": [],
            "conference_papers": {},
            "journal_papers": [],
            "under_review": [],
            "workshop_papers": []
        }

        # Split content into sections
        sections = re.split(r'^## (.+)$', content, flags=re.MULTILINE)[1:]

        for i in range(0, len(sections), 2):
            section_name = sections[i].strip()
            section_content = sections[i+1].strip()

            if 'preprints' in section_name.lower():
                publications["preprints"] = self._parse_publications_section(section_content)

            elif 'conference papers' in section_name.lower():
                publications["conference_papers"] = self._parse_yearly_publications(section_content)

            elif 'journal' in section_name.lower():
                publications["journal_papers"] = self._parse_publications_section(section_content)

            elif 'under review' in section_name.lower():
                publications["under_review"] = self._parse_publications_section(section_content)

            elif 'workshop' in section_name.lower():
                publications["workshop_papers"] = self._parse_publications_section(section_content)

        output_file = self.output_dir / "data" / "publications.yaml"
        save_yaml(publications, str(output_file))
        print(f"Publications saved to {output_file}")

    def _parse_yearly_publications(self, content: str) -> Dict[str, List[Dict]]:
        """Parse publications organized by year."""
        yearly_pubs = {}
        current_year = None

        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue

            # Check if line is a year header (### YYYY)
            year_match = re.match(r'^###\s+(\d{4})$', line)
            if year_match:
                current_year = int(year_match.group(1))
                yearly_pubs[current_year] = []
                continue

            # Parse publication line
            if line.startswith('- ') and current_year:
                pub = self._parse_publication_line(line)
                if pub:
                    yearly_pubs[current_year].append(pub)

        return yearly_pubs

    def _parse_publications_section(self, content: str) -> List[Dict]:
        """Parse a simple publications section."""
        publications = []

        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('- '):
                pub = self._parse_publication_line(line)
                if pub:
                    publications.append(pub)

        return publications

    def _parse_publication_line(self, line: str) -> Optional[Dict]:
        """Parse a single publication line."""
        # Remove list marker
        line = re.sub(r'^\s*-\s*', '', line.strip())

        # Extract year from beginning
        year_match = re.match(r'^(\d{4}):\s*(.+)$', line)
        if year_match:
            year = int(year_match.group(1))
            content = year_match.group(2)
        else:
            # Try to extract year from content
            year = extract_year_from_string(line) or 2025
            content = line

        # Split by quotes to extract title and other info
        parts = re.split(r'"([^"]*)"', content)

        if len(parts) >= 3:
            authors_part = parts[0].strip(' ,')
            title = clean_title(parts[1])
            venue_part = parts[2].strip(' ,-')
        else:
            # Fallback: try to parse without quotes
            match = re.match(r'([^-]*)-\s*(.+)', content)
            if match:
                authors_part = match.group(1).strip()
                venue_part = match.group(2).strip()
                title = "Unknown Title"
            else:
                return None

        # Parse authors
        authors = parse_author_list(authors_part)

        # Parse venue information
        venue_info = parse_venue_info(venue_part)

        publication = {
            "title": title,
            "authors": authors,
            "year": year
        }

        # Add venue information if available
        if venue_info['venue']:
            publication["venue"] = venue_info['venue']

        if venue_info['type']:
            publication["type"] = venue_info['type']

        if venue_info['acceptance_rate']:
            publication["acceptance_rate"] = venue_info['acceptance_rate']

        if venue_info['award']:
            publication["award"] = venue_info['award']

        return publication

    def import_grants(self) -> None:
        """Import grants and awards from awards.md."""
        awards_file = self.source_dir / "awards.md"
        if not awards_file.exists():
            print(f"Warning: {awards_file} not found")
            return

        print("Importing grants and awards...")
        with open(awards_file, 'r', encoding='utf-8') as f:
            content = f.read()

        grants = {
            "fellowships": [],
            "grants": [],
            "conference_awards": [],
            "university_awards": [],
            "research_awards": []
        }

        # Split content into sections
        sections = re.split(r'^## (.+)$', content, flags=re.MULTILINE)[1:]

        for i in range(0, len(sections), 2):
            section_name = sections[i].strip()
            section_content = sections[i+1].strip()

            category = self._categorize_grant_section(section_name)
            grants[category] = self._parse_grants_section(section_content)

        output_file = self.output_dir / "data" / "grants.yaml"
        save_yaml(grants, str(output_file))
        print(f"Grants and awards saved to {output_file}")

    def _categorize_grant_section(self, section_name: str) -> str:
        """Categorize grant section based on name."""
        section_lower = section_name.lower()
        if 'fellowship' in section_lower:
            return "fellowships"
        elif 'grant' in section_lower:
            return "grants"
        elif 'conference' in section_lower:
            return "conference_awards"
        elif 'university' in section_lower:
            return "university_awards"
        else:
            return "research_awards"

    def _parse_grants_section(self, content: str) -> List[Dict]:
        """Parse grants section."""
        grants = []

        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('- '):
                grant = self._parse_grant_line(line)
                if grant:
                    grants.append(grant)

        return grants

    def _parse_grant_line(self, line: str) -> Optional[Dict]:
        """Parse a single grant line."""
        # Remove list marker
        line = re.sub(r'^\s*-\s*', '', line.strip())

        # Pattern: YEAR(-YEAR): TITLE - $AMOUNT (additional info)
        match = re.match(r'^(\d{4}(?:-\d{4})?):?\s*([^-]+?)(?:\s*-\s*\$?([\d,]+(?:\.\d+)?[^\(;]*))?\s*(?:\(([^)]+)\))?(?:;\s*(.+))?$', line)

        if match:
            year = match.group(1)
            title = match.group(2).strip()
            amount = match.group(3)
            extra_info = match.group(4)
            additional = match.group(5)

            grant = {
                "year": year,
                "title": title
            }

            if amount:
                grant["amount"] = f"${amount.strip()}"

            # Handle additional information
            if additional:
                if 'declined' in additional.lower():
                    grant["status"] = "declined"
                grant["description"] = additional

            if extra_info:
                grant["organization"] = extra_info

            return grant

        return None

    def import_teaching(self) -> None:
        """Import teaching data from teaching.md."""
        teaching_file = self.source_dir / "teaching.md"
        if not teaching_file.exists():
            print(f"Warning: {teaching_file} not found")
            return

        print("Importing teaching data...")
        with open(teaching_file, 'r', encoding='utf-8') as f:
            content = f.read()

        teaching_data = {
            "experience": [],
            "supervision": []
        }

        # Split content into sections
        sections = re.split(r'^## (.+)$', content, flags=re.MULTILINE)[1:]

        for i in range(0, len(sections), 2):
            if i + 1 >= len(sections):
                break

            section_name = sections[i].strip()
            section_content = sections[i+1].strip()

            if 'teaching experience' in section_name.lower():
                teaching_data["experience"] = self._parse_teaching_section(section_content)
            elif 'supervision' in section_name.lower() or 'mentoring' in section_name.lower():
                teaching_data["supervision"] = self._parse_supervision_section(section_content)

        output_file = self.output_dir / "data" / "teaching.yaml"
        save_yaml(teaching_data, str(output_file))
        print(f"Teaching data saved to {output_file}")

    def _parse_teaching_section(self, content: str) -> List[Dict]:
        """Parse teaching experience section."""
        experiences = []

        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('- '):
                exp = self._parse_teaching_line(line)
                if exp:
                    experiences.append(exp)

        return experiences

    def _parse_teaching_line(self, line: str) -> Optional[Dict]:
        """Parse a single teaching line."""
        # Remove list marker
        line = re.sub(r'^\s*-\s*', '', line.strip())

        # Pattern: YEAR: **ROLE** - INSTITUTION, COURSE - INSTRUCTOR
        match = re.match(r'^(\d{4}):\s*\*\*(.*?)\*\*\s*-\s*(.*?)(?:,\s*(.*?))?(?:\s*-\s*(.+))?$', line)

        if match:
            year = int(match.group(1))
            role = match.group(2)
            institution = match.group(3)
            course = match.group(4)
            instructor = match.group(5)

            teaching = {
                "year": year,
                "role": role,
                "institution": institution
            }

            if course:
                teaching["course"] = course

            if instructor:
                teaching["instructor"] = instructor

            return teaching

        return None

    def _parse_supervision_section(self, content: str) -> List[Dict]:
        """Parse student supervision section."""
        supervisions = []
        current_category = None

        for line in content.split('\n'):
            line = line.strip()

            # Check for subsection headers (### Category)
            if line.startswith('###'):
                current_category = line.replace('###', '').strip()
                continue

            if line.startswith('- '):
                supervision = self._parse_supervision_line(line, current_category)
                if supervision:
                    supervisions.append(supervision)

        return supervisions

    def _parse_supervision_line(self, line: str, category: Optional[str]) -> Optional[Dict]:
        """Parse a single supervision line."""
        # Remove list marker
        line = re.sub(r'^\s*-\s*', '', line.strip())

        # Pattern: YEAR: STUDENT (INSTITUTION); additional info
        match = re.match(r'^(\d{4}):\s*([^(]+?)(?:\s*\(([^)]+)\))?(?:;\s*(.+))?$', line)

        if match:
            year = int(match.group(1))
            student = match.group(2).strip()
            institution = match.group(3) or ""
            additional = match.group(4)

            supervision = {
                "year": year,
                "student": student,
                "institution": institution,
                "level": self._determine_supervision_level(category, additional)
            }

            if additional and 'with' in additional.lower():
                # Extract collaborator
                collab_match = re.search(r'with\s+([^;]+)', additional, re.IGNORECASE)
                if collab_match:
                    supervision["collaborator"] = collab_match.group(1).strip()

            if 'incoming' in line.lower():
                supervision["status"] = "incoming"

            return supervision

        return None

    def _determine_supervision_level(self, category: Optional[str], additional: Optional[str]) -> str:
        """Determine supervision level from category and additional info."""
        if not category:
            return "Unknown"

        category_lower = category.lower()
        if 'phd' in category_lower:
            return "PhD"
        elif 'intern' in category_lower:
            return "Intern"
        elif 'project' in category_lower:
            return "Project"
        else:
            return "Unknown"

    def import_service(self) -> None:
        """Import service data from service.md."""
        service_file = self.source_dir / "service.md"
        if not service_file.exists():
            print(f"Warning: {service_file} not found")
            return

        print("Importing service data...")
        with open(service_file, 'r', encoding='utf-8') as f:
            content = f.read()

        service_data = {
            "conference_reviews": [],
            "journal_reviews": [],
            "workshops": [],
            "volunteer": []
        }

        # Split content into sections
        sections = re.split(r'^## (.+)$', content, flags=re.MULTILINE)[1:]

        for i in range(0, len(sections), 2):
            if i + 1 >= len(sections):
                break

            section_name = sections[i].strip()
            section_content = sections[i+1].strip()

            category = self._categorize_service_section(section_name)
            service_data[category] = self._parse_service_section(section_content, category)

        output_file = self.output_dir / "data" / "service.yaml"
        save_yaml(service_data, str(output_file))
        print(f"Service data saved to {output_file}")

    def _categorize_service_section(self, section_name: str) -> str:
        """Categorize service section."""
        section_lower = section_name.lower()
        if 'conference review' in section_lower:
            return "conference_reviews"
        elif 'journal review' in section_lower:
            return "journal_reviews"
        elif 'workshop' in section_lower:
            return "workshops"
        else:
            return "volunteer"

    def _parse_service_section(self, content: str, category: str) -> List[Dict]:
        """Parse service section."""
        services = []

        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('- '):
                service = self._parse_service_line(line, category)
                if service:
                    services.append(service)

        return services

    def _parse_service_line(self, line: str, category: str) -> Optional[Dict]:
        """Parse a single service line."""
        # Remove list marker
        line = re.sub(r'^\s*-\s*', '', line.strip())

        if category == "conference_reviews":
            # Pattern: **VENUE**: year, year, year
            match = re.match(r'^\*\*(.*?)\*\*:\s*(.+)$', line)
            if match:
                venue = match.group(1)
                years_str = match.group(2)
                years = [int(y.strip()) for y in years_str.split(',') if y.strip().isdigit()]

                return {
                    "venue": venue,
                    "years": years,
                    "role": "Reviewer"
                }

        elif category == "journal_reviews":
            # Pattern: YEAR: Role VENUE
            match = re.match(r'^(\d{4}):\s*(.+)$', line)
            if match:
                year = int(match.group(1))
                rest = match.group(2)
                role = "Reviewer"
                venue = rest

                if rest.startswith("Reviewer "):
                    venue = rest.replace("Reviewer ", "", 1)

                return {
                    "year": year,
                    "venue": venue,
                    "role": role
                }

        else:
            # Generic parsing
            year_match = re.search(r'\b(\d{4})\b', line)
            year = int(year_match.group(1)) if year_match else None

            return {
                "year": year,
                "venue": line,
                "role": "Service"
            }

        return None

    def import_talks(self) -> None:
        """Import talks data from talks.md."""
        talks_file = self.source_dir / "talks.md"
        if not talks_file.exists():
            print(f"Warning: {talks_file} not found")
            return

        print("Importing talks data...")
        with open(talks_file, 'r', encoding='utf-8') as f:
            content = f.read()

        talks_data = {
            "keynotes": [],
            "conference": [],
            "invited": [],
            "industry": [],
            "seminars": []
        }

        # Split content into sections
        sections = re.split(r'^## (.+)$', content, flags=re.MULTILINE)[1:]

        for i in range(0, len(sections), 2):
            if i + 1 >= len(sections):
                break

            section_name = sections[i].strip()
            section_content = sections[i+1].strip()

            category = self._categorize_talks_section(section_name)
            talks_data[category] = self._parse_talks_section(section_content, category)

        output_file = self.output_dir / "data" / "talks.yaml"
        save_yaml(talks_data, str(output_file))
        print(f"Talks data saved to {output_file}")

    def _categorize_talks_section(self, section_name: str) -> str:
        """Categorize talks section."""
        section_lower = section_name.lower()
        if 'keynote' in section_lower:
            return "keynotes"
        elif 'conference' in section_lower:
            return "conference"
        elif 'invited' in section_lower:
            return "invited"
        elif 'industry' in section_lower:
            return "industry"
        elif 'seminar' in section_lower or 'academic' in section_lower:
            return "seminars"
        else:
            return "invited"

    def _parse_talks_section(self, content: str, category: str) -> List[Dict]:
        """Parse talks section."""
        talks = []

        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('- '):
                talk = self._parse_talk_line(line)
                if talk:
                    talk["type"] = category
                    talks.append(talk)

        return talks

    def _parse_talk_line(self, line: str) -> Optional[Dict]:
        """Parse a single talk line."""
        # Remove list marker
        line = re.sub(r'^\s*-\s*', '', line.strip())

        # Pattern: YEAR: "TITLE" - VENUE, LOCATION (with COLLABORATOR)
        match = re.match(r'^(\d{4}):\s*"([^"]*)"?\s*-\s*([^(]+?)(?:\s*\(([^)]+)\))?(?:\s*\(with\s+([^)]+)\))?$', line)

        if match:
            year = int(match.group(1))
            title = clean_title(match.group(2) or "")
            venue_location = match.group(3).strip()
            extra_info = match.group(4)
            collaborator = match.group(5)

            # Split venue and location
            venue_parts = venue_location.split(',')
            venue = venue_parts[0].strip()
            location = ', '.join(part.strip() for part in venue_parts[1:]) if len(venue_parts) > 1 else None

            talk = {
                "year": year,
                "title": title,
                "venue": venue
            }

            if location:
                talk["location"] = location

            if collaborator:
                talk["collaborator"] = collaborator

            if extra_info and not collaborator:
                talk["location"] = extra_info

            return talk

        return None

    def create_personal_info(self) -> None:
        """Create personal information YAML file."""
        print("Creating personal information...")

        # Default personal info based on the CV data
        personal = {
            "name": "Jason Hartford",
            "current_position": "Lecturer in Machine Learning",
            "department": "Department of Computer Science",
            "institution": "University of Manchester",
            "email": "jason.hartford@manchester.ac.uk",
            "website": "https://jhartford.github.io",
            "phone": "+44 (7396) 846418",
            "orcid": None,
            "address": None
        }

        # Add education information
        education = [
            {
                "year": 2020,
                "degree": "Ph.D. Computer Science",
                "institution": "University of British Columbia",
                "thesis": "Deep Models for Causal Inference"
            }
        ]

        personal_data = {
            "personal": personal,
            "education": education
        }

        output_file = self.output_dir / "data" / "personal.yaml"
        save_yaml(personal_data, str(output_file))
        print(f"Personal information saved to {output_file}")

    def create_config(self) -> None:
        """Create configuration file."""
        print("Creating configuration...")

        config = {
            "templates": {
                "promotion": {
                    "include_all": True,
                    "max_pages": 10,
                    "font_size": "10pt"
                },
                "academic_us": {
                    "exclude_sections": [],
                    "format": "standard"
                },
                "academic_uk": {
                    "exclude_sections": [],
                    "format": "manchester"
                }
            },
            "build": {
                "latex_engine": "pdflatex",
                "bibtex_style": "plain",
                "output_dir": "output"
            }
        }

        output_file = self.output_dir / "data" / "config.yaml"
        save_yaml(config, str(output_file))
        print(f"Configuration saved to {output_file}")


def main():
    """Main function to run the import."""
    import argparse

    parser = argparse.ArgumentParser(description="Import CV data from Research/cv/")
    parser.add_argument("--source", default="../cv", help="Source directory containing CV markdown files")
    parser.add_argument("--output", default="./examples/jason-hartford", help="Output directory for YAML files")

    args = parser.parse_args()

    # Resolve paths
    source_dir = Path(args.source).resolve()
    output_dir = Path(args.output).resolve()

    if not source_dir.exists():
        print(f"Error: Source directory {source_dir} does not exist")
        return 1

    print(f"Importing from: {source_dir}")
    print(f"Output to: {output_dir}")

    # Create importer and run
    importer = CVMarkdownImporter(str(source_dir), str(output_dir))
    importer.import_all()

    return 0


if __name__ == "__main__":
    sys.exit(main())