"""BibTeX parsing and conversion utilities."""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase


class BibTeXImporter:
    """Import and convert BibTeX files to CV data format."""

    def __init__(self):
        """Initialize BibTeX importer."""
        self.entry_type_mapping = {
            'article': 'journal_papers',
            'inproceedings': 'conference_papers',
            'incollection': 'conference_papers',
            'proceedings': 'conference_papers',
            'conference': 'conference_papers',
            'misc': 'preprints',
            'unpublished': 'under_review',
            'techreport': 'preprints',
            'phdthesis': 'journal_papers',  # Treat as journal paper
            'mastersthesis': 'journal_papers',
            'book': 'journal_papers',
            'inbook': 'journal_papers',
            'booklet': 'preprints',
        }

    def parse_bibtex_file(self, file_path: str) -> BibDatabase:
        """Parse a BibTeX file."""
        parser = BibTexParser()
        parser.interpolate_strings = False
        parser.common_strings = True

        with open(file_path, 'r', encoding='utf-8') as bibtex_file:
            bib_database = bibtexparser.load(bibtex_file, parser=parser)

        return bib_database

    def clean_text(self, text: str) -> str:
        """Clean text by removing LaTeX commands and extra whitespace."""
        if not text:
            return ""

        # Remove common LaTeX commands
        text = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', text)  # \command{text} -> text
        text = re.sub(r'\\[a-zA-Z]+', '', text)  # \command -> ""
        text = re.sub(r'[{}]', '', text)  # Remove braces
        text = re.sub(r'\s+', ' ', text)  # Multiple spaces -> single space
        text = text.strip()

        return text

    def extract_authors(self, authors_string: str) -> List[str]:
        """Extract and clean author names from BibTeX author field."""
        if not authors_string:
            return []

        # Split on 'and' (BibTeX author separator)
        authors = re.split(r'\s+and\s+', authors_string)

        cleaned_authors = []
        for author in authors:
            # Clean LaTeX commands
            author = self.clean_text(author)

            # Handle "Last, First" format
            if ',' in author:
                parts = author.split(',', 1)
                if len(parts) == 2:
                    last = parts[0].strip()
                    first = parts[1].strip()
                    author = f"{first} {last}"

            cleaned_authors.append(author.strip())

        return [author for author in cleaned_authors if author]

    def get_year(self, entry: Dict[str, str]) -> Optional[int]:
        """Extract year from BibTeX entry."""
        year_field = entry.get('year', '').strip()
        if not year_field:
            return None

        # Extract first 4 digits as year
        year_match = re.search(r'\d{4}', year_field)
        if year_match:
            return int(year_match.group())

        return None

    def convert_entry_to_publication(self, entry: Dict[str, str]) -> Dict[str, Any]:
        """Convert a single BibTeX entry to CV publication format."""
        pub = {
            'authors': self.extract_authors(entry.get('author', '')),
            'title': self.clean_text(entry.get('title', '')),
            'year': self.get_year(entry),
            'bibtex_key': entry.get('ID', ''),
        }

        entry_type = entry.get('ENTRYTYPE', '').lower()

        # Add venue information based on entry type
        if entry_type in ['article']:
            pub['journal'] = self.clean_text(entry.get('journal', ''))
            pub['volume'] = entry.get('volume', '')
            pub['number'] = entry.get('number', '')
            pub['pages'] = entry.get('pages', '')
            pub['doi'] = entry.get('doi', '')

        elif entry_type in ['inproceedings', 'incollection', 'conference']:
            pub['venue'] = self.clean_text(entry.get('booktitle', ''))
            pub['pages'] = entry.get('pages', '')

            # Try to extract acceptance rate or other info from note field
            note = entry.get('note', '')
            if note and ('accept' in note.lower() or '%' in note):
                pub['acceptance_rate'] = self.clean_text(note)

            # Check for presentation type
            if entry.get('note', '') and 'oral' in entry.get('note', '').lower():
                pub['type'] = 'oral'
            elif entry.get('note', '') and 'poster' in entry.get('note', '').lower():
                pub['type'] = 'poster'

        elif entry_type in ['misc', 'unpublished']:
            pub['venue'] = self.clean_text(entry.get('journal', '') or entry.get('booktitle', '') or entry.get('howpublished', ''))

            # Check for arXiv
            if 'arxiv' in str(entry).lower():
                arxiv_match = re.search(r'(\d{4}\.\d{4,5})', str(entry))
                if arxiv_match:
                    pub['arxiv'] = arxiv_match.group(1)

        # Add URL if available
        if entry.get('url'):
            pub['url'] = entry.get('url')

        return pub

    def categorize_publications(self, bib_database: BibDatabase) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize BibTeX entries into CV publication structure."""
        publications = {
            'journal_papers': [],
            'conference_papers': {},
            'preprints': [],
            'under_review': [],
            'workshop_papers': []
        }

        for entry in bib_database.entries:
            entry_type = entry.get('ENTRYTYPE', '').lower()
            category = self.entry_type_mapping.get(entry_type, 'preprints')

            pub = self.convert_entry_to_publication(entry)

            if category == 'conference_papers':
                # Group by year for conference papers
                year = pub.get('year')
                if year:
                    year_str = str(year)
                    if year_str not in publications['conference_papers']:
                        publications['conference_papers'][year_str] = []
                    publications['conference_papers'][year_str].append(pub)
                else:
                    # If no year, put in workshop papers
                    publications['workshop_papers'].append(pub)
            else:
                publications[category].append(pub)

        # Sort publications within categories
        for category in ['journal_papers', 'preprints', 'under_review', 'workshop_papers']:
            publications[category].sort(key=lambda x: x.get('year', 0), reverse=True)

        # Sort conference papers by year (descending)
        for year_papers in publications['conference_papers'].values():
            year_papers.sort(key=lambda x: x.get('title', ''))

        return publications

    def import_bibtex_file(self, file_path: str) -> Dict[str, List[Dict[str, Any]]]:
        """Import a BibTeX file and return CV publications structure."""
        bib_database = self.parse_bibtex_file(file_path)
        publications = self.categorize_publications(bib_database)
        return publications

    def merge_with_existing(self, new_publications: Dict[str, Any], existing_publications: Dict[str, Any]) -> Dict[str, Any]:
        """Merge new BibTeX publications with existing publications.yaml data."""
        merged = existing_publications.copy()

        # Merge each category
        for category, new_pubs in new_publications.items():
            if category == 'conference_papers':
                # Conference papers are organized by year
                if 'conference_papers' not in merged:
                    merged['conference_papers'] = {}

                for year, papers in new_pubs.items():
                    if year not in merged['conference_papers']:
                        merged['conference_papers'][year] = []

                    # Check for duplicates by title
                    existing_titles = {pub.get('title', '').lower() for pub in merged['conference_papers'][year]}
                    for paper in papers:
                        if paper.get('title', '').lower() not in existing_titles:
                            merged['conference_papers'][year].append(paper)
            else:
                # Other categories are simple lists
                if category not in merged:
                    merged[category] = []

                # Check for duplicates by title
                existing_titles = {pub.get('title', '').lower() for pub in merged[category]}
                for paper in new_pubs:
                    if paper.get('title', '').lower() not in existing_titles:
                        merged[category].append(paper)

        return merged

    def export_to_bibtex(self, publications: Dict[str, Any], output_path: str):
        """Export publications back to BibTeX format."""
        bib_database = BibDatabase()
        entries = []

        entry_counter = 1

        # Helper to create BibTeX key
        def create_bibtex_key(pub: Dict[str, Any]) -> str:
            if pub.get('bibtex_key'):
                return pub['bibtex_key']

            # Generate key from first author + year + title words
            authors = pub.get('authors', [])
            year = pub.get('year', '')
            title = pub.get('title', '')

            if authors:
                author_key = authors[0].split()[-1]  # Last name of first author
            else:
                author_key = 'unknown'

            # Take first few words of title
            title_words = re.findall(r'\w+', title.lower())[:2]
            title_key = ''.join(title_words[:2])

            return f"{author_key}{year}{title_key}"

        # Process each category
        categories_map = {
            'journal_papers': 'article',
            'preprints': 'misc',
            'under_review': 'unpublished',
            'workshop_papers': 'inproceedings'
        }

        for category, entry_type in categories_map.items():
            if category in publications:
                for pub in publications[category]:
                    entry = {
                        'ENTRYTYPE': entry_type,
                        'ID': create_bibtex_key(pub),
                        'title': pub.get('title', ''),
                        'author': ' and '.join(pub.get('authors', [])),
                        'year': str(pub.get('year', '')),
                    }

                    # Add category-specific fields
                    if category == 'journal_papers':
                        entry['journal'] = pub.get('journal', pub.get('venue', ''))
                        if pub.get('volume'):
                            entry['volume'] = pub.get('volume')
                        if pub.get('pages'):
                            entry['pages'] = pub.get('pages')
                        if pub.get('doi'):
                            entry['doi'] = pub.get('doi')
                    else:
                        if pub.get('venue'):
                            if entry_type == 'inproceedings':
                                entry['booktitle'] = pub.get('venue')
                            else:
                                entry['journal'] = pub.get('venue')
                        if pub.get('arxiv'):
                            entry['note'] = f"arXiv:{pub.get('arxiv')}"

                    if pub.get('url'):
                        entry['url'] = pub.get('url')

                    entries.append(entry)

        # Process conference papers
        if 'conference_papers' in publications:
            for year, papers in publications['conference_papers'].items():
                for pub in papers:
                    entry = {
                        'ENTRYTYPE': 'inproceedings',
                        'ID': create_bibtex_key(pub),
                        'title': pub.get('title', ''),
                        'author': ' and '.join(pub.get('authors', [])),
                        'booktitle': pub.get('venue', ''),
                        'year': str(pub.get('year', year)),
                    }

                    if pub.get('pages'):
                        entry['pages'] = pub.get('pages')
                    if pub.get('acceptance_rate'):
                        entry['note'] = pub.get('acceptance_rate')
                    if pub.get('url'):
                        entry['url'] = pub.get('url')

                    entries.append(entry)

        bib_database.entries = entries

        # Write to file
        writer = BibTexWriter()
        writer.indent = '  '
        with open(output_path, 'w', encoding='utf-8') as bibtex_file:
            bibtex_file.write(writer.write(bib_database))


def import_bibtex(file_path: str, merge: bool = True, output_yaml: Optional[str] = None) -> Dict[str, Any]:
    """Convenience function to import BibTeX file.

    Args:
        file_path: Path to BibTeX file
        merge: Whether to merge with existing publications.yaml
        output_yaml: Optional path to save merged publications

    Returns:
        Publications data structure
    """
    importer = BibTeXImporter()
    new_publications = importer.import_bibtex_file(file_path)

    if merge and output_yaml:
        # Try to load existing publications
        from ..utils.helpers import load_yaml, save_yaml
        try:
            existing = load_yaml(output_yaml)
        except FileNotFoundError:
            existing = {}

        merged_publications = importer.merge_with_existing(new_publications, existing)
        save_yaml(merged_publications, output_yaml)
        return merged_publications

    return new_publications