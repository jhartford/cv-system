"""
Citation management for CV Manager.

This module provides functionality to extract and update citation counts
from various sources like Google Scholar.
"""

import re
import html
import yaml
import bibtexparser
from difflib import SequenceMatcher
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class CitationExtractor:
    """Extract citation information from various sources."""

    @staticmethod
    def clean_title(title: str) -> str:
        """Clean and normalize title for matching."""
        # Remove common LaTeX commands and normalize
        title = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', title)  # Remove LaTeX commands
        title = re.sub(r'[{}\\\'""]', '', title)  # Remove braces, quotes, backslashes
        title = re.sub(r'\s+', ' ', title).strip().lower()  # Normalize whitespace and case
        return title

    @staticmethod
    def similarity(a: str, b: str) -> float:
        """Calculate similarity between two strings."""
        return SequenceMatcher(None, a, b).ratio()

    def extract_from_google_scholar_html(self, html_file: str) -> List[Dict[str, Any]]:
        """Extract paper titles and citation counts from Google Scholar HTML."""
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()

        papers = []

        # Google Scholar uses table rows with class gsc_a_tr for each paper
        row_pattern = r'<tr class="gsc_a_tr"[^>]*>(.*?)</tr>'
        rows = re.findall(row_pattern, content, re.DOTALL | re.IGNORECASE)

        logger.info(f"Found {len(rows)} potential paper rows in Google Scholar HTML")

        for row in rows:
            # Extract title from link with class gsc_a_at
            title_pattern = r'<a[^>]*class="gsc_a_at"[^>]*>(.*?)</a>'
            title_matches = re.findall(title_pattern, row, re.DOTALL | re.IGNORECASE)

            if not title_matches:
                continue

            title = html.unescape(re.sub(r'<[^>]+>', '', title_matches[0])).strip()
            if len(title) < 10:  # Skip very short titles
                continue

            # Extract citation count
            citations = 0
            citation_patterns = [
                r'<a[^>]*class="gsc_a_ac[^"]*"[^>]*>(\d+)</a>',
                r'<td[^>]*class="gsc_a_c[^"]*"[^>]*>.*?(\d+).*?</td>'
            ]

            for pattern in citation_patterns:
                citation_matches = re.findall(pattern, row, re.IGNORECASE)
                if citation_matches:
                    try:
                        citations = int(citation_matches[0])
                        break
                    except ValueError:
                        continue

            # Extract year
            year = None
            year_patterns = [
                r'<span[^>]*class="gsc_a_h[^"]*"[^>]*>.*?((?:19|20)\d{2}).*?</span>',
                r'<td[^>]*class="gsc_a_y[^"]*"[^>]*>((?:19|20)\d{2})</td>'
            ]

            for pattern in year_patterns:
                year_matches = re.findall(pattern, row, re.IGNORECASE)
                if year_matches:
                    try:
                        year = int(year_matches[0])
                        break
                    except ValueError:
                        continue

            papers.append({
                'title': title,
                'clean_title': self.clean_title(title),
                'citations': citations,
                'year': year,
                'source': 'google_scholar'
            })

        return papers


class CitationMatcher:
    """Match extracted citations with existing publication data."""

    def __init__(self, similarity_threshold: float = 0.7):
        self.similarity_threshold = similarity_threshold
        self.extractor = CitationExtractor()

    def load_bibtex_papers(self, bib_file: str) -> List[Dict[str, Any]]:
        """Load papers from BibTeX file."""
        with open(bib_file, 'r', encoding='utf-8') as f:
            bib_database = bibtexparser.load(f)

        papers = []
        for entry in bib_database.entries:
            title = entry.get('title', '')
            papers.append({
                'bibtex_key': entry['ID'],
                'title': title,
                'clean_title': self.extractor.clean_title(title),
                'year': entry.get('year'),
                'entry': entry
            })

        return papers

    def match_papers(self, citation_papers: List[Dict[str, Any]],
                    bibtex_papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Match papers between citation source and BibTeX based on titles."""
        matches = []

        for citation_paper in citation_papers:
            best_match = None
            best_score = 0

            for bib_paper in bibtex_papers:
                # Try exact title match first
                if citation_paper['clean_title'] == bib_paper['clean_title']:
                    best_match = bib_paper
                    best_score = 1.0
                    break

                # Try similarity matching
                score = self.extractor.similarity(
                    citation_paper['clean_title'],
                    bib_paper['clean_title']
                )
                if score > best_score and score > self.similarity_threshold:
                    best_match = bib_paper
                    best_score = score

            if best_match:
                matches.append({
                    'citation_title': citation_paper['title'],
                    'bibtex_title': best_match['title'],
                    'bibtex_key': best_match['bibtex_key'],
                    'citations': citation_paper['citations'],
                    'match_score': best_score,
                    'citation_year': citation_paper.get('year'),
                    'bibtex_year': best_match.get('year'),
                    'source': citation_paper.get('source', 'unknown')
                })

        return matches


class CitationUpdater:
    """Update publications with citation information."""

    def __init__(self):
        self.matcher = CitationMatcher()
        self.extractor = CitationExtractor()

    def update_from_google_scholar(self, html_file: str, bib_file: str,
                                 yaml_file: str, dry_run: bool = False) -> Dict[str, Any]:
        """
        Update citations from Google Scholar HTML file.

        Args:
            html_file: Path to Google Scholar HTML file
            bib_file: Path to BibTeX file with paper metadata
            yaml_file: Path to publications YAML file to update
            dry_run: If True, don't actually update the file

        Returns:
            Dictionary with update results and statistics
        """
        # Extract citations from Google Scholar
        logger.info("Extracting citations from Google Scholar HTML...")
        citation_papers = self.extractor.extract_from_google_scholar_html(html_file)

        # Load BibTeX papers for matching
        logger.info("Loading BibTeX papers...")
        bibtex_papers = self.matcher.load_bibtex_papers(bib_file)

        # Match papers
        logger.info("Matching papers...")
        matches = self.matcher.match_papers(citation_papers, bibtex_papers)

        # Load existing publications
        with open(yaml_file, 'r', encoding='utf-8') as f:
            publications = yaml.safe_load(f)

        # Update publications with citation counts
        citation_map = {match['bibtex_key']: match['citations'] for match in matches}
        updated_papers = []
        updated_count = 0

        # Update each section
        for section in ['journal_papers', 'conference_papers', 'preprints', 'under_review', 'workshop_papers']:
            if section in publications:
                for paper in publications[section]:
                    bibtex_key = paper.get('bibtex_key')
                    if bibtex_key and bibtex_key in citation_map:
                        old_citations = paper.get('citations', 0)
                        new_citations = citation_map[bibtex_key]
                        if old_citations != new_citations:
                            if not dry_run:
                                paper['citations'] = new_citations
                            updated_papers.append({
                                'bibtex_key': bibtex_key,
                                'title': paper.get('title', ''),
                                'old_citations': old_citations,
                                'new_citations': new_citations
                            })
                            updated_count += 1

        # Write updated YAML (unless dry run)
        if not dry_run and updated_count > 0:
            with open(yaml_file, 'w', encoding='utf-8') as f:
                yaml.dump(publications, f, default_flow_style=False,
                         allow_unicode=True, sort_keys=False)

        # Calculate statistics
        unmatched_citation_papers = [
            p for p in citation_papers
            if not any(match['citation_title'] == p['title'] for match in matches)
        ]

        total_citations = sum(p['citations'] for p in citation_papers)
        matched_citations = sum(match['citations'] for match in matches)

        return {
            'total_citation_papers': len(citation_papers),
            'total_bibtex_papers': len(bibtex_papers),
            'matched_papers': len(matches),
            'updated_papers': updated_papers,
            'updated_count': updated_count,
            'unmatched_papers': unmatched_citation_papers,
            'total_citations': total_citations,
            'matched_citations': matched_citations,
            'matches': matches,
            'dry_run': dry_run
        }

    def get_citation_summary(self, results: Dict[str, Any]) -> str:
        """Generate a summary string of citation update results."""
        lines = []

        lines.append(f"Citation Update Summary")
        lines.append(f"=" * 22)
        lines.append(f"Papers found in citation source: {results['total_citation_papers']}")
        lines.append(f"Papers in BibTeX database: {results['total_bibtex_papers']}")
        lines.append(f"Papers matched: {results['matched_papers']}")
        lines.append(f"Papers updated: {results['updated_count']}")
        lines.append(f"Total citations (all papers): {results['total_citations']}")
        lines.append(f"Total citations (matched): {results['matched_citations']}")

        if results['dry_run']:
            lines.append("\n[DRY RUN] No files were modified")

        if results['updated_papers']:
            lines.append(f"\nUpdated Papers:")
            for paper in results['updated_papers']:
                lines.append(f"  • {paper['bibtex_key']}: {paper['old_citations']} → {paper['new_citations']} citations")

        if results['unmatched_papers']:
            count = len(results['unmatched_papers'])
            lines.append(f"\nUnmatched papers from citation source: {count}")
            # Show first few unmatched papers
            for paper in results['unmatched_papers'][:5]:
                title_preview = paper['title'][:60] + "..." if len(paper['title']) > 60 else paper['title']
                lines.append(f"  • {title_preview} ({paper['citations']} citations)")
            if count > 5:
                lines.append(f"  ... and {count - 5} more")

        return "\n".join(lines)


def update_citations_from_source(source_file: str, source_type: str,
                                bib_file: str, yaml_file: str,
                                dry_run: bool = False,
                                similarity_threshold: float = 0.7) -> Dict[str, Any]:
    """
    Generic function to update citations from various sources.

    Args:
        source_file: Path to citation source file
        source_type: Type of source ('google_scholar_html')
        bib_file: Path to BibTeX file
        yaml_file: Path to publications YAML file
        dry_run: If True, don't modify files

    Returns:
        Dictionary with update results
    """
    updater = CitationUpdater()
    # Set similarity threshold for the matcher
    updater.matcher.similarity_threshold = similarity_threshold

    if source_type == 'google_scholar_html':
        return updater.update_from_google_scholar(source_file, bib_file, yaml_file, dry_run)
    else:
        raise ValueError(f"Unsupported citation source type: {source_type}")