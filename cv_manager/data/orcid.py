"""ORCID API integration for importing and exporting publications."""

import re
import requests
import json
import uuid
import base64
from typing import Dict, List, Any, Optional
from datetime import datetime
from urllib.parse import urlencode, parse_qs, urlparse

class ORCIDClient:
    """ORCID API client supporting both public API and OAuth Member API."""

    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize ORCID client.

        Args:
            client_id: ORCID OAuth client ID for Member API access
            client_secret: ORCID OAuth client secret for Member API access
        """
        # Public API endpoints
        self.public_api_url = "https://pub.orcid.org/v3.0"
        self.public_sandbox_url = "https://pub.sandbox.orcid.org/v3.0"

        # Member API endpoints (for OAuth authenticated requests)
        self.member_api_url = "https://api.orcid.org/v3.0"
        self.member_sandbox_url = "https://api.sandbox.orcid.org/v3.0"

        # OAuth endpoints
        self.oauth_url = "https://orcid.org/oauth"
        self.oauth_sandbox_url = "https://sandbox.orcid.org/oauth"

        # OAuth configuration
        self.client_id = client_id
        self.client_secret = client_secret

        # Default headers
        self.headers = {
            'Accept': 'application/vnd.orcid+json',
            'User-Agent': 'CV-Manager/1.0',
            'Content-Type': 'application/vnd.orcid+json'
        }

        # Token storage (in production, this should be secure storage)
        self._access_tokens: Dict[str, Dict[str, Any]] = {}

    def validate_orcid_id(self, orcid_id: str) -> str:
        """Validate and normalize ORCID ID format.

        Args:
            orcid_id: ORCID ID in various formats

        Returns:
            Normalized ORCID ID (0000-0000-0000-0000)

        Raises:
            ValueError: If ORCID ID is invalid
        """
        # Remove common prefixes and clean up
        orcid_id = orcid_id.strip()
        orcid_id = re.sub(r'^https?://orcid\.org/', '', orcid_id)
        orcid_id = re.sub(r'[^\d\-X]', '', orcid_id.upper())

        # Ensure proper format with dashes
        if len(orcid_id) == 16 and '-' not in orcid_id:
            # Add dashes: 0000000000000000 -> 0000-0000-0000-0000
            orcid_id = f"{orcid_id[:4]}-{orcid_id[4:8]}-{orcid_id[8:12]}-{orcid_id[12:16]}"

        # Validate format
        pattern = r'^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$'
        if not re.match(pattern, orcid_id):
            raise ValueError(f"Invalid ORCID ID format: {orcid_id}")

        return orcid_id

    # OAuth 2.0 Methods

    def get_oauth_authorize_url(self, redirect_uri: str, scopes: List[str] = None,
                               use_sandbox: bool = False, state: str = None) -> str:
        """Generate ORCID OAuth authorization URL.

        Args:
            redirect_uri: OAuth callback URL
            scopes: List of requested scopes (default: ['/activities/update', '/read-limited'])
            use_sandbox: Use sandbox environment
            state: Optional state parameter for CSRF protection

        Returns:
            Authorization URL for redirecting user to ORCID

        Raises:
            ValueError: If client_id is not configured
        """
        if not self.client_id:
            raise ValueError("OAuth client_id must be configured for authorization")

        if scopes is None:
            scopes = ['/activities/update', '/read-limited']

        oauth_base = self.oauth_sandbox_url if use_sandbox else self.oauth_url

        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            'scope': ' '.join(scopes),
            'redirect_uri': redirect_uri
        }

        if state is None:
            state = str(uuid.uuid4())
        params['state'] = state

        return f"{oauth_base}/authorize?{urlencode(params)}"

    def exchange_code_for_token(self, code: str, redirect_uri: str,
                               use_sandbox: bool = False) -> Dict[str, Any]:
        """Exchange OAuth authorization code for access token.

        Args:
            code: Authorization code from ORCID callback
            redirect_uri: OAuth callback URL (must match authorization request)
            use_sandbox: Use sandbox environment

        Returns:
            Token response containing access_token, token_type, refresh_token, etc.

        Raises:
            requests.RequestException: If token exchange fails
            ValueError: If client credentials are not configured
        """
        if not self.client_id or not self.client_secret:
            raise ValueError("OAuth client_id and client_secret must be configured")

        oauth_base = self.oauth_sandbox_url if use_sandbox else self.oauth_url
        token_url = f"{oauth_base}/token"

        # Prepare request data
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri
        }

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.post(token_url, data=data, headers=headers)
        response.raise_for_status()

        token_data = response.json()

        # Store token for this ORCID ID
        orcid_id = token_data.get('orcid')
        if orcid_id:
            self._access_tokens[orcid_id] = token_data

        return token_data

    def refresh_access_token(self, refresh_token: str, use_sandbox: bool = False) -> Dict[str, Any]:
        """Refresh an expired access token.

        Args:
            refresh_token: Refresh token from original authorization
            use_sandbox: Use sandbox environment

        Returns:
            New token response

        Raises:
            requests.RequestException: If token refresh fails
        """
        if not self.client_id or not self.client_secret:
            raise ValueError("OAuth client credentials must be configured")

        oauth_base = self.oauth_sandbox_url if use_sandbox else self.oauth_url
        token_url = f"{oauth_base}/token"

        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.post(token_url, data=data, headers=headers)
        response.raise_for_status()

        return response.json()

    def get_authenticated_headers(self, orcid_id: str) -> Dict[str, str]:
        """Get headers with OAuth access token for authenticated requests.

        Args:
            orcid_id: ORCID ID to get token for

        Returns:
            Headers dict with Authorization header

        Raises:
            ValueError: If no valid token is available
        """
        if orcid_id not in self._access_tokens:
            raise ValueError(f"No access token available for ORCID ID {orcid_id}")

        token_info = self._access_tokens[orcid_id]
        access_token = token_info.get('access_token')

        if not access_token:
            raise ValueError(f"Invalid token data for ORCID ID {orcid_id}")

        headers = self.headers.copy()
        headers['Authorization'] = f"Bearer {access_token}"
        return headers

    def store_token(self, orcid_id: str, token_data: Dict[str, Any]):
        """Store access token for an ORCID ID.

        Args:
            orcid_id: ORCID ID to store token for
            token_data: Token response from ORCID OAuth
        """
        self._access_tokens[orcid_id] = token_data

    def has_valid_token(self, orcid_id: str) -> bool:
        """Check if we have a valid access token for an ORCID ID.

        Args:
            orcid_id: ORCID ID to check

        Returns:
            True if valid token is available
        """
        if orcid_id not in self._access_tokens:
            return False

        token_info = self._access_tokens[orcid_id]
        # In production, you'd also check token expiration here
        return 'access_token' in token_info and token_info['access_token']

    # Public API Methods (unchanged functionality)

    def fetch_works_summary(self, orcid_id: str, use_sandbox: bool = False) -> Dict[str, Any]:
        """Fetch list of works from ORCID.

        Args:
            orcid_id: Validated ORCID ID
            use_sandbox: Use sandbox environment for testing

        Returns:
            ORCID works summary response

        Raises:
            requests.RequestException: If API request fails
        """
        orcid_id = self.validate_orcid_id(orcid_id)
        base_url = self.sandbox_url if use_sandbox else self.base_url
        url = f"{base_url}/{orcid_id}/works"

        # Handle SSL verification issues in some environments
        try:
            response = requests.get(url, headers=self.headers, timeout=30, verify=True)
        except requests.exceptions.SSLError:
            # Retry with SSL verification disabled (not recommended for production)
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            response = requests.get(url, headers=self.headers, timeout=30, verify=False)

        response.raise_for_status()

        return response.json()

    def fetch_work_details(self, orcid_id: str, put_code: str, use_sandbox: bool = False) -> Dict[str, Any]:
        """Fetch detailed information for a specific work.

        Args:
            orcid_id: Validated ORCID ID
            put_code: ORCID put-code for the specific work
            use_sandbox: Use sandbox environment for testing

        Returns:
            Detailed work information

        Raises:
            requests.RequestException: If API request fails
        """
        orcid_id = self.validate_orcid_id(orcid_id)
        base_url = self.sandbox_url if use_sandbox else self.base_url
        url = f"{base_url}/{orcid_id}/work/{put_code}"

        # Handle SSL verification issues in some environments
        try:
            response = requests.get(url, headers=self.headers, timeout=30, verify=True)
        except requests.exceptions.SSLError:
            # Retry with SSL verification disabled (not recommended for production)
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            response = requests.get(url, headers=self.headers, timeout=30, verify=False)

        response.raise_for_status()

        return response.json()

    def extract_work_info(self, work_detail: Dict[str, Any]) -> Dict[str, Any]:
        """Extract publication information from ORCID work detail.

        Args:
            work_detail: Full work detail from ORCID API

        Returns:
            Standardized publication data
        """
        if work_detail is None:
            return None
        pub = {
            'title': '',
            'authors': [],
            'year': None,
            'venue': '',
            'journal': '',
            'volume': '',
            'pages': '',
            'doi': '',
            'url': '',
            'work_type': '',
            'orcid_put_code': work_detail.get('put-code', '')
        }

        # Extract title
        title_info = work_detail.get('title')
        if title_info and title_info.get('title'):
            pub['title'] = title_info['title'].get('value', '')

        # Extract work type
        work_type = work_detail.get('type')
        if work_type:
            pub['work_type'] = work_type.lower().replace('_', '-')

        # Extract publication date
        pub_date = work_detail.get('publication-date')
        if pub_date:
            year = pub_date.get('year')
            if year and year.get('value'):
                pub['year'] = int(year['value'])

        # Extract journal title - can be in journal-title or subtitle
        journal_title = work_detail.get('journal-title')
        if journal_title and journal_title.get('value'):
            journal_name = journal_title['value']
            pub['journal'] = journal_name
            pub['venue'] = journal_name
        elif title_info and title_info.get('subtitle'):
            # Sometimes journal is in subtitle field
            subtitle = title_info['subtitle'].get('value', '')
            if subtitle:
                pub['journal'] = subtitle
                pub['venue'] = subtitle

        # Extract authors/contributors - handle case where contributors is None or has different structure
        authors = []
        contributors = work_detail.get('contributors')
        if contributors and isinstance(contributors, dict):
            contributor_list = contributors.get('contributor', [])
            if isinstance(contributor_list, list):
                for contributor in contributor_list:
                    if contributor.get('contributor-attributes', {}).get('contributor-role') in ['author', None]:
                        credit_name = contributor.get('credit-name')
                        if credit_name and credit_name.get('value'):
                            authors.append(credit_name['value'])

        # If no contributors found, try to extract from citation
        if not authors:
            citation = work_detail.get('citation')
            if citation and citation.get('citation-value'):
                citation_text = citation['citation-value']
                # Try to extract author from BibTeX citation
                if 'author=' in citation_text:
                    author_match = re.search(r'author\s*=\s*\{([^}]+)\}', citation_text)
                    if author_match:
                        authors.append(author_match.group(1))

        pub['authors'] = authors

        # Extract external identifiers (DOI, etc.)
        external_ids = work_detail.get('external-ids', {}).get('external-id', [])
        for ext_id in external_ids:
            id_type = ext_id.get('external-id-type', '').lower()
            id_value = ext_id.get('external-id-value', '')

            if id_type == 'doi':
                pub['doi'] = id_value.replace('https://doi.org/', '').replace('http://dx.doi.org/', '')
            elif id_type == 'url':
                pub['url'] = id_value

        # Extract citation information if available
        citation = work_detail.get('citation')
        if citation and citation.get('citation-value'):
            citation_text = citation['citation-value']

            # Try to extract volume and pages from citation
            volume_match = re.search(r'volume[:\s]*(\d+)', citation_text, re.IGNORECASE)
            if volume_match:
                pub['volume'] = volume_match.group(1)

            pages_match = re.search(r'pages?[:\s]*(\d+(?:-{1,2}\d+)?)', citation_text, re.IGNORECASE)
            if pages_match:
                pub['pages'] = pages_match.group(1)

        return pub

    def map_work_type_to_category(self, work_type: str) -> str:
        """Map ORCID work type to CV publication category.

        Args:
            work_type: ORCID work type (e.g., 'journal-article')

        Returns:
            CV category name
        """
        mapping = {
            'journal-article': 'journal_papers',
            'conference-paper': 'conference_papers',
            'conference-abstract': 'conference_papers',
            'conference-poster': 'conference_papers',
            'book': 'journal_papers',
            'book-chapter': 'journal_papers',
            'book-review': 'journal_papers',
            'dissertation-thesis': 'journal_papers',
            'working-paper': 'preprints',
            'preprint': 'preprints',
            'report': 'preprints',
            'manual': 'preprints',
            'other': 'preprints'
        }

        return mapping.get(work_type.lower(), 'preprints')

    def import_publications_from_orcid(self, orcid_id: str, use_sandbox: bool = False) -> Dict[str, List[Dict[str, Any]]]:
        """Import all publications from an ORCID profile.

        Args:
            orcid_id: ORCID ID to import from
            use_sandbox: Use sandbox environment for testing

        Returns:
            Publications organized by category

        Raises:
            requests.RequestException: If API requests fail
            ValueError: If ORCID ID is invalid
        """
        publications = {
            'journal_papers': [],
            'conference_papers': [],
            'preprints': [],
            'under_review': [],
            'workshop_papers': []
        }

        # Fetch works summary
        works_summary = self.fetch_works_summary(orcid_id, use_sandbox)

        # Process each work
        works_group = works_summary.get('group', [])
        for group in works_group:
            work_summaries = group.get('work-summary', [])

            # Get the most recent version of each work
            if work_summaries:
                latest_work = max(work_summaries, key=lambda w: w.get('last-modified-date', {}).get('value', 0))
                put_code = latest_work.get('put-code')

                if put_code:
                    try:
                        # Fetch detailed work information
                        work_detail = self.fetch_work_details(orcid_id, str(put_code), use_sandbox)

                        if work_detail is None:
                            print(f"Warning: No work detail returned for put-code {put_code}")
                            continue

                        pub = self.extract_work_info(work_detail)

                        if pub and pub.get('title'):  # Only include works with titles
                            category = self.map_work_type_to_category(pub.get('work_type', ''))

                            publications[category].append(pub)

                    except requests.RequestException as e:
                        print(f"Warning: Could not fetch details for work {put_code}: {e}")
                        continue
                    except Exception as e:
                        print(f"Warning: Error processing work {put_code}: {e}")
                        continue

        # Sort publications within categories by year (descending)
        for category in ['journal_papers', 'conference_papers', 'preprints', 'under_review', 'workshop_papers']:
            publications[category].sort(key=lambda x: x.get('year', 0), reverse=True)

        return publications

    def merge_with_existing(self, new_publications: Dict[str, Any], existing_publications: Dict[str, Any]) -> Dict[str, Any]:
        """Merge ORCID publications with existing publications data.

        Args:
            new_publications: Publications from ORCID
            existing_publications: Existing publications.yaml data

        Returns:
            Merged publications data
        """
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

                    # Check for duplicates by title and DOI
                    existing_items = merged['conference_papers'][year]
                    existing_titles = {pub.get('title', '').lower().strip() for pub in existing_items}
                    existing_dois = {pub.get('doi', '').lower().strip() for pub in existing_items if pub.get('doi')}

                    for paper in papers:
                        paper_title = paper.get('title', '').lower().strip()
                        paper_doi = paper.get('doi', '').lower().strip()

                        # Check if this publication already exists
                        is_duplicate = False
                        if paper_title and paper_title in existing_titles:
                            is_duplicate = True
                        elif paper_doi and paper_doi in existing_dois:
                            is_duplicate = True

                        if not is_duplicate:
                            merged['conference_papers'][year].append(paper)
            else:
                # Other categories are simple lists
                if category not in merged:
                    merged[category] = []

                # Check for duplicates by title and DOI
                existing_titles = {pub.get('title', '').lower().strip() for pub in merged[category]}
                existing_dois = {pub.get('doi', '').lower().strip() for pub in merged[category] if pub.get('doi')}

                for paper in new_pubs:
                    paper_title = paper.get('title', '').lower().strip()
                    paper_doi = paper.get('doi', '').lower().strip()

                    # Check if this publication already exists
                    is_duplicate = False
                    if paper_title and paper_title in existing_titles:
                        is_duplicate = True
                    elif paper_doi and paper_doi in existing_dois:
                        is_duplicate = True

                    if not is_duplicate:
                        merged[category].append(paper)

        return merged

    # Member API Methods (requires OAuth authentication)

    def convert_publication_to_orcid_work(self, publication: Dict[str, Any]) -> Dict[str, Any]:
        """Convert CV publication to ORCID work format.

        Args:
            publication: Publication data from CV system

        Returns:
            ORCID work data structure
        """
        # Map CV publication types to ORCID work types
        type_mapping = {
            'journal_papers': 'journal-article',
            'conference_papers': 'conference-paper',
            'preprints': 'preprint',
            'under_review': 'working-paper',
            'workshop_papers': 'conference-poster'
        }

        work_type = publication.get('work_type', 'journal-article')
        if 'category' in publication:
            work_type = type_mapping.get(publication['category'], work_type)

        orcid_work = {
            'title': {
                'title': {
                    'value': publication.get('title', '')
                }
            },
            'type': work_type,
            'external-ids': {
                'external-id': []
            }
        }

        # Add publication date if available
        if publication.get('year'):
            orcid_work['publication-date'] = {
                'year': {
                    'value': str(publication['year'])
                }
            }

        # Add journal title if available
        if publication.get('journal') or publication.get('venue'):
            journal_title = publication.get('journal') or publication.get('venue')
            orcid_work['journal-title'] = {
                'value': journal_title
            }

        # Add DOI as external identifier
        if publication.get('doi'):
            doi_id = {
                'external-id-type': 'doi',
                'external-id-value': publication['doi'],
                'external-id-relationship': 'self'
            }
            orcid_work['external-ids']['external-id'].append(doi_id)

        # Add URL as external identifier
        if publication.get('url'):
            url_id = {
                'external-id-type': 'uri',
                'external-id-value': publication['url'],
                'external-id-relationship': 'self'
            }
            orcid_work['external-ids']['external-id'].append(url_id)

        # Add contributors (authors)
        if publication.get('authors'):
            contributors = []
            for author in publication['authors']:
                contributor = {
                    'contributor-attributes': {
                        'contributor-role': 'author'
                    },
                    'credit-name': {
                        'value': author
                    }
                }
                contributors.append(contributor)

            orcid_work['contributors'] = {
                'contributor': contributors
            }

        return orcid_work

    def post_work_to_orcid(self, orcid_id: str, work_data: Dict[str, Any],
                          use_sandbox: bool = False) -> Dict[str, Any]:
        """Post a work to ORCID profile using Member API.

        Args:
            orcid_id: ORCID ID to post work to
            work_data: ORCID work data structure
            use_sandbox: Use sandbox environment

        Returns:
            ORCID API response

        Raises:
            ValueError: If no valid authentication token
            requests.RequestException: If API request fails
        """
        if not self.has_valid_token(orcid_id):
            raise ValueError(f"No valid authentication token for ORCID ID {orcid_id}")

        # Choose API base URL
        api_base = self.member_sandbox_url if use_sandbox else self.member_api_url
        works_url = f"{api_base}/{orcid_id}/work"

        # Get authenticated headers
        headers = self.get_authenticated_headers(orcid_id)

        # Make POST request to add work
        response = requests.post(works_url, json=work_data, headers=headers)
        response.raise_for_status()

        return response.json() if response.content else {'status': 'created'}

    def update_work_in_orcid(self, orcid_id: str, put_code: str, work_data: Dict[str, Any],
                           use_sandbox: bool = False) -> Dict[str, Any]:
        """Update an existing work in ORCID profile.

        Args:
            orcid_id: ORCID ID
            put_code: ORCID put-code of work to update
            work_data: Updated ORCID work data structure
            use_sandbox: Use sandbox environment

        Returns:
            ORCID API response

        Raises:
            ValueError: If no valid authentication token
            requests.RequestException: If API request fails
        """
        if not self.has_valid_token(orcid_id):
            raise ValueError(f"No valid authentication token for ORCID ID {orcid_id}")

        # Choose API base URL
        api_base = self.member_sandbox_url if use_sandbox else self.member_api_url
        work_url = f"{api_base}/{orcid_id}/work/{put_code}"

        # Get authenticated headers
        headers = self.get_authenticated_headers(orcid_id)

        # Make PUT request to update work
        response = requests.put(work_url, json=work_data, headers=headers)
        response.raise_for_status()

        return response.json() if response.content else {'status': 'updated'}

    def delete_work_from_orcid(self, orcid_id: str, put_code: str,
                             use_sandbox: bool = False) -> bool:
        """Delete a work from ORCID profile.

        Args:
            orcid_id: ORCID ID
            put_code: ORCID put-code of work to delete
            use_sandbox: Use sandbox environment

        Returns:
            True if deletion successful

        Raises:
            ValueError: If no valid authentication token
            requests.RequestException: If API request fails
        """
        if not self.has_valid_token(orcid_id):
            raise ValueError(f"No valid authentication token for ORCID ID {orcid_id}")

        # Choose API base URL
        api_base = self.member_sandbox_url if use_sandbox else self.member_api_url
        work_url = f"{api_base}/{orcid_id}/work/{put_code}"

        # Get authenticated headers
        headers = self.get_authenticated_headers(orcid_id)

        # Make DELETE request
        response = requests.delete(work_url, headers=headers)
        response.raise_for_status()

        return True

    def sync_publications_to_orcid(self, orcid_id: str, publications: Dict[str, Any],
                                 use_sandbox: bool = False, dry_run: bool = False) -> Dict[str, Any]:
        """Sync CV publications to ORCID profile.

        Args:
            orcid_id: ORCID ID to sync to
            publications: Publications data from CV system
            use_sandbox: Use sandbox environment
            dry_run: If True, don't actually post works

        Returns:
            Sync results with counts and any errors

        Raises:
            ValueError: If no valid authentication token
        """
        if not self.has_valid_token(orcid_id):
            raise ValueError(f"No valid authentication token for ORCID ID {orcid_id}")

        results = {
            'posted': 0,
            'skipped': 0,
            'errors': [],
            'posted_works': []
        }

        # Get existing ORCID works to avoid duplicates
        try:
            existing_works = self.fetch_works_summary(orcid_id, use_sandbox)
            existing_titles = set()
            existing_dois = set()

            for group in existing_works.get('group', []):
                for work_summary in group.get('work-summary', []):
                    title_info = work_summary.get('title')
                    if title_info and title_info.get('title'):
                        existing_titles.add(title_info['title'].get('value', '').lower().strip())

                    # Note: DOIs not available in work summary, would need detail fetch
                    # For now, rely on title matching

        except Exception as e:
            results['errors'].append(f"Error fetching existing works: {e}")
            existing_titles = set()
            existing_dois = set()

        # Process each publication category
        for category, pubs in publications.items():
            if category == 'conference_papers':
                # Handle conference papers organized by year
                for year, papers in pubs.items():
                    for pub in papers:
                        self._sync_single_publication(
                            orcid_id, pub, category, use_sandbox, dry_run,
                            existing_titles, existing_dois, results
                        )
            else:
                # Handle other categories as simple lists
                if isinstance(pubs, list):
                    for pub in pubs:
                        self._sync_single_publication(
                            orcid_id, pub, category, use_sandbox, dry_run,
                            existing_titles, existing_dois, results
                        )

        return results

    def _sync_single_publication(self, orcid_id: str, pub: Dict[str, Any], category: str,
                               use_sandbox: bool, dry_run: bool, existing_titles: set,
                               existing_dois: set, results: Dict[str, Any]):
        """Helper method to sync a single publication."""
        try:
            # Check for duplicates
            pub_title = pub.get('title', '').lower().strip()
            pub_doi = pub.get('doi', '').lower().strip()

            if pub_title in existing_titles:
                results['skipped'] += 1
                return

            if pub_doi and pub_doi in existing_dois:
                results['skipped'] += 1
                return

            # Convert to ORCID format
            pub_with_category = pub.copy()
            pub_with_category['category'] = category
            orcid_work = self.convert_publication_to_orcid_work(pub_with_category)

            if dry_run:
                results['posted'] += 1
                results['posted_works'].append({
                    'title': pub.get('title', ''),
                    'type': orcid_work.get('type', ''),
                    'dry_run': True
                })
            else:
                # Actually post to ORCID
                response = self.post_work_to_orcid(orcid_id, orcid_work, use_sandbox)
                results['posted'] += 1
                results['posted_works'].append({
                    'title': pub.get('title', ''),
                    'type': orcid_work.get('type', ''),
                    'response': response
                })

                # Track this title to avoid duplicates in same session
                existing_titles.add(pub_title)

        except Exception as e:
            results['errors'].append(f"Error posting '{pub.get('title', 'Unknown')}': {e}")


# Convenience Functions

def import_orcid_publications(orcid_id: str, merge: bool = True, output_yaml: Optional[str] = None, use_sandbox: bool = False) -> Dict[str, Any]:
    """Convenience function to import publications from ORCID.

    Args:
        orcid_id: ORCID ID to import from
        merge: Whether to merge with existing publications.yaml
        output_yaml: Optional path to save merged publications
        use_sandbox: Use ORCID sandbox for testing

    Returns:
        Publications data structure

    Raises:
        requests.RequestException: If API requests fail
        ValueError: If ORCID ID is invalid
    """
    client = ORCIDClient()
    new_publications = client.import_publications_from_orcid(orcid_id, use_sandbox)

    if merge and output_yaml:
        # Try to load existing publications
        from ..utils.helpers import load_yaml, save_yaml
        try:
            existing = load_yaml(output_yaml)
        except FileNotFoundError:
            existing = {}

        merged_publications = client.merge_with_existing(new_publications, existing)
        save_yaml(merged_publications, output_yaml)
        return merged_publications

    return new_publications


def sync_publications_to_orcid(orcid_id: str, publications: Dict[str, Any],
                              client_id: str, client_secret: str,
                              access_token: str = None,
                              use_sandbox: bool = False,
                              dry_run: bool = False) -> Dict[str, Any]:
    """Convenience function to sync publications to ORCID profile.

    Args:
        orcid_id: ORCID ID to sync to
        publications: Publications data structure
        client_id: ORCID OAuth client ID
        client_secret: ORCID OAuth client secret
        access_token: Optional pre-existing access token
        use_sandbox: Use sandbox environment
        dry_run: If True, simulate sync without posting

    Returns:
        Sync results with counts and errors

    Raises:
        ValueError: If authentication fails or ORCID ID is invalid
    """
    client = ORCIDClient(client_id, client_secret)

    if access_token:
        # Use provided access token
        client.store_token(orcid_id, {'access_token': access_token})
    else:
        raise ValueError("OAuth access token required for posting to ORCID")

    return client.sync_publications_to_orcid(orcid_id, publications, use_sandbox, dry_run)


# Legacy alias for backward compatibility
ORCIDImporter = ORCIDClient