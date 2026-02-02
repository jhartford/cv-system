#!/usr/bin/env python3
"""CV Manager CLI interface."""

import os
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from .utils.helpers import load_yaml, save_yaml, ensure_directory

console = Console()


@click.group()
@click.version_option()
def main():
    """CV Manager - A modern academic CV management system.

    Import data from BibTeX, ORCID, and citation sources like Google Scholar.
    Generate professional CVs with multiple templates and automatic formatting.
    """
    pass


@main.command()
@click.argument('name')
@click.option('--template', default='academic-us', help='Template to use for initialization')
def init(name: str, template: str):
    """Initialize a new CV directory with template files."""
    cv_dir = Path(name)

    if cv_dir.exists():
        console.print(f"[red]Error: Directory '{name}' already exists[/red]")
        sys.exit(1)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
    ) as progress:
        task = progress.add_task("Creating CV directory structure...", total=None)

        # Create directory structure
        data_dir = cv_dir / "data"
        output_dir = cv_dir / "output"
        custom_dir = cv_dir / "custom" / "templates"

        ensure_directory(str(data_dir))
        ensure_directory(str(output_dir))
        ensure_directory(str(custom_dir))

        progress.update(task, description="Creating configuration files...")

        # Create basic configuration
        config = {
            "default_template": template,
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

        save_yaml(config, str(cv_dir / "config.yaml"))

        progress.update(task, description="Creating data template files...")

        # Create template data files
        personal_template = {
            "personal": {
                "name": "Your Name",
                "current_position": "Your Position",
                "department": "Your Department",
                "institution": "Your Institution",
                "email": "your.email@institution.edu",
                "website": "https://yourwebsite.com",
                "phone": None,
                "orcid": None,
                "address": None
            },
            "education": [
                {
                    "year": 2020,
                    "degree": "Ph.D. in Your Field",
                    "institution": "Your University",
                    "thesis": "Your Thesis Title",
                    "supervisor": "Your Advisor"
                }
            ]
        }

        publications_template = {
            "preprints": [],
            "conference_papers": {},
            "journal_papers": [],
            "under_review": [],
            "workshop_papers": []
        }

        grants_template = {
            "fellowships": [],
            "grants": [],
            "conference_awards": [],
            "university_awards": [],
            "research_awards": []
        }

        teaching_template = {
            "experience": [],
            "supervision": []
        }

        service_template = {
            "conference_reviews": [],
            "journal_reviews": [],
            "workshops": [],
            "volunteer": []
        }

        talks_template = {
            "keynotes": [],
            "conference": [],
            "invited": [],
            "industry": [],
            "seminars": []
        }

        # Save template files
        save_yaml(personal_template, str(data_dir / "personal.yaml"))
        save_yaml(publications_template, str(data_dir / "publications.yaml"))
        save_yaml(grants_template, str(data_dir / "grants.yaml"))
        save_yaml(teaching_template, str(data_dir / "teaching.yaml"))
        save_yaml(service_template, str(data_dir / "service.yaml"))
        save_yaml(talks_template, str(data_dir / "talks.yaml"))

        progress.update(task, description="Creating README...")

        # Create README
        readme_content = f"""# {name} CV

This directory contains your CV data and configuration files.

## Structure

- `data/` - YAML data files for your CV content
- `output/` - Generated CV files (PDF, LaTeX)
- `custom/` - Custom templates (optional)
- `config.yaml` - CV configuration settings

## Getting Started

1. Edit the YAML files in `data/` with your information
2. Run `cv-manager build` to generate your CV
3. Or use `cv-manager serve` for the web interface

## Commands

- `cv-manager build` - Generate all CV variants
- `cv-manager build --template {template}` - Generate specific template
- `cv-manager serve` - Start web interface for editing
- `cv-manager validate` - Check data integrity
"""

        with open(cv_dir / "README.md", "w") as f:
            f.write(readme_content)

    console.print(Panel.fit(
        f"[green]Successfully created CV directory: {name}[/green]\n\n"
        f"Next steps:\n"
        f"1. cd {name}\n"
        f"2. Edit YAML files in data/ directory\n"
        f"3. Run 'cv-manager build' to generate your CV",
        title="CV Initialized"
    ))


@main.command()
@click.option('--source', required=True, help='Source directory containing markdown CV files')
@click.option('--output', default='.', help='Output directory for converted YAML files')
def import_cv(source: str, output: str):
    """Import CV data from existing markdown files."""
    source_path = Path(source)
    output_path = Path(output)

    if not source_path.exists():
        console.print(f"[red]Error: Source directory '{source}' does not exist[/red]")
        sys.exit(1)

    # Import the script functionality
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from scripts.import_from_research import CVMarkdownImporter

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            task = progress.add_task("Importing CV data...", total=None)

            importer = CVMarkdownImporter(str(source_path), str(output_path))
            importer.import_all()

        console.print(f"[green]Successfully imported CV data from {source}[/green]")

    except ImportError as e:
        console.print(f"[red]Error importing CV data: {e}[/red]")
        sys.exit(1)


@main.command()
@click.option('--template', help='Template to build (promotion, academic-us, academic-uk)')
@click.option('--format', default='pdf', type=click.Choice(['pdf', 'latex']), help='Output format')
@click.option('--output-dir', default='output', help='Output directory')
def build(template: Optional[str], format: str, output_dir: str):
    """Build CV from YAML data."""
    # Check if we're in a CV directory
    if not Path("config.yaml").exists() or not Path("data").exists():
        console.print("[red]Error: Not in a CV directory. Run 'cv-manager init' first.[/red]")
        sys.exit(1)

    config = load_yaml("config.yaml")
    templates_to_build = [template] if template else ["promotion", "academic-us", "academic-uk"]

    success_count = 0
    total_count = len(templates_to_build)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
    ) as progress:
        for tmpl in templates_to_build:
            task = progress.add_task(f"Building {tmpl} template...", total=None)

            try:
                # Import the build system
                from .build.latex import build_cv

                # Build the CV
                result_path = build_cv(tmpl, ".", format, output_dir)

                if result_path:
                    progress.update(task, description=f"✓ Built {tmpl} template")
                    console.print(f"[green]✓ {tmpl}: {result_path}[/green]")
                    success_count += 1
                else:
                    progress.update(task, description=f"✗ Failed {tmpl} template")
                    console.print(f"[red]✗ Failed to build {tmpl} template[/red]")

            except Exception as e:
                progress.update(task, description=f"✗ Error {tmpl} template")
                console.print(f"[red]✗ Error building {tmpl}: {e}[/red]")

    if success_count == total_count:
        console.print(f"[green]All {total_count} CV variants built successfully in {output_dir}/[/green]")
    elif success_count > 0:
        console.print(f"[yellow]{success_count}/{total_count} CV variants built successfully in {output_dir}/[/yellow]")
    else:
        console.print(f"[red]No CV variants were built successfully[/red]")
        sys.exit(1)


@main.command()
@click.option('--port', default=5000, help='Port to run the web server on')
@click.option('--host', default='127.0.0.1', help='Host to bind the web server to')
def serve(port: int, host: str):
    """Start the web interface for editing CV data."""
    # Check if we're in a CV directory
    if not Path("config.yaml").exists() or not Path("data").exists():
        console.print("[red]Error: Not in a CV directory. Run 'cv-manager init' first.[/red]")
        sys.exit(1)

    console.print(f"[blue]Starting CV Manager web interface...[/blue]")
    console.print(f"[blue]Open your browser to: http://{host}:{port}[/blue]")
    console.print(f"[yellow]Press Ctrl+C to stop the server[/yellow]")

    try:
        # Import and start Flask app
        from .web.app import create_app
        app = create_app()
        app.run(host=host, port=port, debug=True)
    except ImportError:
        console.print("[red]Web interface not available. Flask dependencies missing.[/red]")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[blue]Server stopped.[/blue]")


@main.command()
def validate():
    """Validate YAML data files for errors."""
    if not Path("data").exists():
        console.print("[red]Error: No data directory found. Run 'cv-manager init' first.[/red]")
        sys.exit(1)

    data_files = [
        "personal.yaml",
        "publications.yaml",
        "grants.yaml",
        "teaching.yaml",
        "service.yaml",
        "talks.yaml"
    ]

    errors = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
    ) as progress:
        task = progress.add_task("Validating data files...", total=len(data_files))

        for file in data_files:
            file_path = Path("data") / file

            try:
                if file_path.exists():
                    data = load_yaml(str(file_path))
                    # Basic validation could be added here
                    progress.update(task, description=f"Validated {file}")
                else:
                    errors.append(f"Missing file: {file}")
            except Exception as e:
                errors.append(f"Error in {file}: {e}")

            progress.advance(task)

    if errors:
        console.print("[red]Validation errors found:[/red]")
        for error in errors:
            console.print(f"  - {error}")
        sys.exit(1)
    else:
        console.print("[green]All data files are valid![/green]")


@main.command("templates")
def list_templates():
    """List available CV templates."""
    templates_info = {
        "promotion": "University of Manchester promotion format (includes citation counts)",
        "academic-us": "US academic CV format",
        "academic-uk": "UK academic CV format"
    }

    table = Table(title="Available CV Templates")
    table.add_column("Template", style="cyan")
    table.add_column("Description", style="white")

    for name, description in templates_info.items():
        table.add_row(name, description)

    console.print(table)

    console.print("\n[blue]Citation Features:[/blue]")
    console.print("• Import citation counts with 'cv-manager import-citations'")
    console.print("• Supports Google Scholar HTML files")
    console.print("• Citations displayed in italics when available")
    console.print("• Automatic matching with BibTeX entries")


@main.command('import-bibtex')
@click.argument('bibtex_file', type=click.Path(exists=True, path_type=Path))
@click.option('--merge/--no-merge', default=True, help='Merge with existing publications (default: yes)')
@click.option('--backup/--no-backup', default=True, help='Create backup of existing publications.yaml')
def import_bibtex(bibtex_file: Path, merge: bool, backup: bool):
    """Import publications from a BibTeX file.

    BIBTEX_FILE: Path to the .bib file to import
    """
    # Check if we're in a CV directory
    if not Path("data").exists():
        console.print("[red]Error: No data directory found. Run 'cv-manager init' first.[/red]")
        sys.exit(1)

    publications_file = Path("data/publications.yaml")

    try:
        from .data.bibtex import BibTeXImporter

        console.print(f"[blue]Importing BibTeX file: {bibtex_file}[/blue]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            # Parse BibTeX file
            task = progress.add_task("Parsing BibTeX file...", total=3)

            importer = BibTeXImporter()
            new_publications = importer.import_bibtex_file(str(bibtex_file))

            progress.update(task, advance=1, description="Processing publications...")

            # Count imported publications
            total_imported = 0
            for category, pubs in new_publications.items():
                total_imported += len(pubs) if isinstance(pubs, list) else 0

            if total_imported == 0:
                progress.update(task, description="No publications found")
                console.print("[yellow]No publications found in BibTeX file.[/yellow]")
                return

            # Handle existing publications
            existing_publications = {}
            if merge and publications_file.exists():
                # Create backup if requested
                if backup:
                    backup_file = publications_file.with_suffix('.yaml.backup')
                    import shutil
                    shutil.copy2(publications_file, backup_file)
                    console.print(f"[blue]Backup created: {backup_file}[/blue]")

                existing_publications = load_yaml(str(publications_file))
                merged_publications = importer.merge_with_existing(new_publications, existing_publications)
                progress.update(task, advance=1, description="Merging with existing publications...")
            else:
                merged_publications = new_publications
                progress.update(task, advance=1, description="Preparing publications...")

            # Save to file
            save_yaml(merged_publications, str(publications_file))
            progress.update(task, description="✓ Import completed")

        console.print(f"[green]Successfully imported {total_imported} publications![/green]")

        # Show summary by category
        console.print("\n[blue]Import Summary:[/blue]")
        for category, pubs in new_publications.items():
            count = len(pubs) if isinstance(pubs, list) else 0
            if count > 0:
                category_name = category.replace('_', ' ').title()
                console.print(f"  - {category_name}: {count}")

        console.print(f"\n[blue]Publications saved to: {publications_file}[/blue]")

    except Exception as e:
        console.print(f"[red]Error importing BibTeX file: {e}[/red]")
        sys.exit(1)


@main.command('import-orcid')
@click.argument('orcid_id', type=str)
@click.option('--merge/--no-merge', default=True, help='Merge with existing publications (default: yes)')
@click.option('--backup/--no-backup', default=True, help='Create backup of existing publications.yaml')
@click.option('--sandbox', is_flag=True, help='Use ORCID sandbox environment for testing')
def import_orcid(orcid_id: str, merge: bool, backup: bool, sandbox: bool):
    """Import publications from an ORCID profile.

    ORCID_ID: ORCID identifier (e.g., 0000-0000-0000-0000 or https://orcid.org/0000-0000-0000-0000)
    """
    # Check if we're in a CV directory
    if not Path("data").exists():
        console.print("[red]Error: No data directory found. Run 'cv-manager init' first.[/red]")
        sys.exit(1)

    publications_file = Path("data/publications.yaml")

    try:
        from .data.orcid import ORCIDImporter
        import requests

        console.print(f"[blue]Importing publications from ORCID: {orcid_id}[/blue]")
        if sandbox:
            console.print("[yellow]Using ORCID sandbox environment[/yellow]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            # Initialize importer and validate ORCID ID
            task = progress.add_task("Validating ORCID ID...", total=4)

            importer = ORCIDImporter()
            try:
                validated_orcid = importer.validate_orcid_id(orcid_id)
                console.print(f"[green]✓ Valid ORCID ID: {validated_orcid}[/green]")
            except ValueError as e:
                console.print(f"[red]Error: {e}[/red]")
                sys.exit(1)

            progress.update(task, advance=1, description="Fetching publications from ORCID...")

            try:
                new_publications = importer.import_publications_from_orcid(validated_orcid, sandbox)
            except requests.RequestException as e:
                console.print(f"[red]Error fetching ORCID data: {e}[/red]")
                if "404" in str(e):
                    console.print(f"[yellow]ORCID profile {validated_orcid} not found or has no public works.[/yellow]")
                elif "403" in str(e):
                    console.print("[yellow]Access denied. The ORCID profile may be private.[/yellow]")
                sys.exit(1)

            progress.update(task, advance=1, description="Processing publications...")

            # Count imported publications
            total_imported = 0
            for category, pubs in new_publications.items():
                total_imported += len(pubs) if isinstance(pubs, list) else 0

            if total_imported == 0:
                progress.update(task, description="No publications found")
                console.print("[yellow]No publications found in ORCID profile.[/yellow]")
                console.print("[blue]This could mean:[/blue]")
                console.print("  - The ORCID profile has no works added")
                console.print("  - All works are set to private visibility")
                console.print("  - You're using sandbox mode with a production ORCID ID")
                return

            # Handle existing publications
            existing_publications = {}
            if merge and publications_file.exists():
                # Create backup if requested
                if backup:
                    backup_file = publications_file.with_suffix('.yaml.backup')
                    import shutil
                    shutil.copy2(publications_file, backup_file)
                    console.print(f"[blue]Backup created: {backup_file}[/blue]")

                existing_publications = load_yaml(str(publications_file))
                merged_publications = importer.merge_with_existing(new_publications, existing_publications)
                progress.update(task, advance=1, description="Merging with existing publications...")
            else:
                merged_publications = new_publications
                progress.update(task, advance=1, description="Preparing publications...")

            # Save to file
            save_yaml(merged_publications, str(publications_file))
            progress.update(task, description="✓ Import completed")

        console.print(f"[green]Successfully imported {total_imported} publications from ORCID![/green]")

        # Show summary by category
        console.print(f"\n[blue]Import Summary for ORCID {validated_orcid}:[/blue]")
        for category, pubs in new_publications.items():
            count = len(pubs) if isinstance(pubs, list) else 0
            if count > 0:
                category_name = category.replace('_', ' ').title()
                console.print(f"  - {category_name}: {count}")

        console.print(f"\n[blue]Publications saved to: {publications_file}[/blue]")

    except Exception as e:
        console.print(f"[red]Error importing from ORCID: {e}[/red]")
        if "ModuleNotFoundError" in str(e) and "requests" in str(e):
            console.print("[yellow]Missing dependency. Please install requests: pip install requests[/yellow]")
        sys.exit(1)


@main.command()
@click.option('--format', default='bibtex', type=click.Choice(['bibtex', 'yaml']), help='Export format')
@click.option('--output', help='Output file (default: publications.bib or publications.yaml)')
def export(format: str, output: Optional[str]):
    """Export publications in various formats."""
    if not Path("data/publications.yaml").exists():
        console.print("[red]Error: No publications.yaml file found.[/red]")
        sys.exit(1)

    publications = load_yaml("data/publications.yaml")

    if not output:
        output = f"publications.{format}"

    if format == "bibtex":
        try:
            from .data.bibtex import BibTeXImporter
            importer = BibTeXImporter()
            importer.export_to_bibtex(publications, output)
            console.print(f"[green]Publications exported to {output}[/green]")
        except Exception as e:
            console.print(f"[red]Error exporting to BibTeX: {e}[/red]")
            sys.exit(1)
    elif format == "yaml":
        save_yaml(publications, output)
        console.print(f"[green]Publications exported to {output}[/green]")


@main.command('orcid-connect')
@click.argument('orcid_id', type=str)
@click.option('--client-id', envvar='ORCID_CLIENT_ID', help='ORCID OAuth client ID')
@click.option('--client-secret', envvar='ORCID_CLIENT_SECRET', help='ORCID OAuth client secret')
@click.option('--sandbox', is_flag=True, help='Use ORCID sandbox environment for testing')
def orcid_connect(orcid_id: str, client_id: str, client_secret: str, sandbox: bool):
    """Connect to ORCID using OAuth 2.0 for publication sync.

    This command initiates OAuth authentication with ORCID to obtain
    permissions for reading and writing publications.

    Args:
        orcid_id: ORCID ID to connect to (0000-0000-0000-0000)
    """
    from .data.orcid import ORCIDClient
    import webbrowser
    import urllib.parse as urlparse
    from rich.prompt import Prompt

    console = Console()

    if not client_id or not client_secret:
        console.print("[red]ORCID OAuth credentials required.[/red]")
        console.print("Set ORCID_CLIENT_ID and ORCID_CLIENT_SECRET environment variables")
        console.print("or use --client-id and --client-secret options.")
        sys.exit(1)

    try:
        # Initialize ORCID client
        client = ORCIDClient(client_id, client_secret)
        validated_orcid = client.validate_orcid_id(orcid_id)

        console.print(f"[blue]Connecting to ORCID profile: {validated_orcid}[/blue]")

        # For CLI, we need a simple redirect URI (localhost)
        redirect_uri = "http://localhost:8080/oauth/callback"
        scopes = ['/activities/update', '/read-limited']

        # Generate authorization URL
        auth_url = client.get_oauth_authorize_url(
            redirect_uri=redirect_uri,
            scopes=scopes,
            use_sandbox=sandbox
        )

        console.print("\n[yellow]OAuth Authorization Required[/yellow]")
        console.print("1. Your browser will open to ORCID's authorization page")
        console.print("2. Review and approve the requested permissions")
        console.print("3. Copy the authorization code from the callback URL")
        console.print("4. Paste it here when prompted")

        # Open browser
        if Prompt.ask("\nOpen browser now?", choices=["y", "n"], default="y") == "y":
            webbrowser.open(auth_url)
        else:
            console.print(f"\nManually visit: {auth_url}")

        # Get authorization code from user
        console.print(f"\n[cyan]Redirect URI: {redirect_uri}[/cyan]")
        auth_code = Prompt.ask("\nEnter the authorization code from the callback URL")

        if not auth_code:
            console.print("[red]No authorization code provided.[/red]")
            sys.exit(1)

        # Exchange code for token
        with console.status("Exchanging authorization code for access token..."):
            token_data = client.exchange_code_for_token(auth_code, redirect_uri, sandbox)

        # Store token securely (for CLI, use config file)
        config_dir = Path.home() / ".cv-manager"
        config_dir.mkdir(exist_ok=True)

        tokens_file = config_dir / "orcid_tokens.yaml"
        tokens = {}
        if tokens_file.exists():
            tokens = load_yaml(str(tokens_file))

        tokens[validated_orcid] = token_data
        save_yaml(tokens, str(tokens_file))

        # Set file permissions to be readable only by owner
        tokens_file.chmod(0o600)

        console.print(f"[green]✓ Successfully connected to ORCID {validated_orcid}[/green]")
        console.print(f"[dim]Token stored in {tokens_file}[/dim]")

    except Exception as e:
        console.print(f"[red]Error connecting to ORCID: {e}[/red]")
        sys.exit(1)


@main.command('orcid-sync')
@click.argument('orcid_id', type=str)
@click.option('--client-id', envvar='ORCID_CLIENT_ID', help='ORCID OAuth client ID')
@click.option('--client-secret', envvar='ORCID_CLIENT_SECRET', help='ORCID OAuth client secret')
@click.option('--sandbox', is_flag=True, help='Use ORCID sandbox environment')
@click.option('--dry-run', is_flag=True, help='Preview sync without posting to ORCID')
@click.option('--force', is_flag=True, help='Skip confirmation prompt')
def orcid_sync(orcid_id: str, client_id: str, client_secret: str, sandbox: bool, dry_run: bool, force: bool):
    """Sync publications to ORCID profile.

    Requires prior OAuth connection using 'orcid-connect' command.

    Args:
        orcid_id: ORCID ID to sync to (0000-0000-0000-0000)
    """
    from .data.orcid import ORCIDClient
    from rich.prompt import Confirm
    from rich.table import Table

    console = Console()

    if not client_id or not client_secret:
        console.print("[red]ORCID OAuth credentials required.[/red]")
        sys.exit(1)

    try:
        # Load stored token
        config_dir = Path.home() / ".cv-manager"
        tokens_file = config_dir / "orcid_tokens.yaml"

        if not tokens_file.exists():
            console.print("[red]No ORCID tokens found. Run 'orcid-connect' first.[/red]")
            sys.exit(1)

        tokens = load_yaml(str(tokens_file))
        if orcid_id not in tokens:
            console.print(f"[red]No token found for ORCID {orcid_id}. Run 'orcid-connect {orcid_id}' first.[/red]")
            sys.exit(1)

        # Load publications
        publications_file = Path.cwd() / "data" / "publications.yaml"
        if not publications_file.exists():
            console.print(f"[red]Publications file not found: {publications_file}[/red]")
            sys.exit(1)

        publications = load_yaml(str(publications_file))

        # Initialize client
        client = ORCIDClient(client_id, client_secret)
        client.store_token(orcid_id, tokens[orcid_id])

        # Count publications
        total_pubs = 0
        for category, pubs in publications.items():
            total_pubs += len(pubs) if isinstance(pubs, list) else 0

        console.print(f"[blue]Syncing {total_pubs} publications to ORCID {orcid_id}[/blue]")
        if dry_run:
            console.print("[yellow]DRY RUN: No changes will be made to ORCID[/yellow]")

        if not force and not dry_run:
            if not Confirm.ask("Proceed with sync to ORCID?"):
                console.print("[yellow]Sync cancelled.[/yellow]")
                return

        # Perform sync
        with console.status("Syncing publications to ORCID..." if not dry_run else "Checking publications..."):
            results = client.sync_publications_to_orcid(orcid_id, publications, sandbox, dry_run)

        # Display results
        if dry_run:
            console.print(f"\n[green]✓ Dry run completed[/green]")
            console.print(f"Would post: {results['posted']} publications")
        else:
            console.print(f"\n[green]✓ Sync completed[/green]")
            console.print(f"Posted: {results['posted']} publications")

        console.print(f"Skipped: {results['skipped']} (already exist)")
        console.print(f"Errors: {len(results['errors'])}")

        # Show posted works
        if results['posted_works']:
            table = Table(title="Posted Publications")
            table.add_column("Title", style="cyan")
            table.add_column("Type", style="magenta")
            table.add_column("Status", style="green")

            for work in results['posted_works']:
                status = "Would post" if work.get('dry_run') else "Posted"
                table.add_row(
                    work['title'][:50] + "..." if len(work['title']) > 50 else work['title'],
                    work['type'].replace('-', ' ').title(),
                    status
                )

            console.print(table)

        # Show errors
        if results['errors']:
            console.print("\n[red]Errors:[/red]")
            for error in results['errors']:
                console.print(f"  • {error}")

        if not dry_run and results['posted'] > 0:
            console.print(f"\n[cyan]View your ORCID profile: https://orcid.org/{orcid_id}[/cyan]")

    except Exception as e:
        console.print(f"[red]Error syncing to ORCID: {e}[/red]")
        sys.exit(1)


@main.command('orcid-status')
def orcid_status():
    """Show connected ORCID profiles and token status."""
    from rich.table import Table

    console = Console()

    config_dir = Path.home() / ".cv-manager"
    tokens_file = config_dir / "orcid_tokens.yaml"

    if not tokens_file.exists():
        console.print("[yellow]No ORCID connections found.[/yellow]")
        console.print("Use 'cv-manager orcid-connect <orcid-id>' to connect a profile.")
        return

    tokens = load_yaml(str(tokens_file))

    if not tokens:
        console.print("[yellow]No ORCID connections found.[/yellow]")
        return

    table = Table(title="Connected ORCID Profiles")
    table.add_column("ORCID ID", style="cyan")
    table.add_column("Access Token", style="green")
    table.add_column("Scopes", style="magenta")
    table.add_column("Expires", style="yellow")

    for orcid_id, token_data in tokens.items():
        access_token = token_data.get('access_token', '')
        scopes = token_data.get('scope', 'Unknown')
        expires_in = token_data.get('expires_in', 'Unknown')

        # Truncate token for display
        token_display = access_token[:8] + "..." if len(access_token) > 8 else access_token

        table.add_row(orcid_id, token_display, scopes, str(expires_in))

    console.print(table)
    console.print(f"\n[dim]Tokens stored in: {tokens_file}[/dim]")


@main.command('import-citations')
@click.argument('source_file', type=click.Path(exists=True, path_type=Path))
@click.option('--source-type', default='google_scholar_html',
              type=click.Choice(['google_scholar_html']),
              help='Type of citation source (default: google_scholar_html)')
@click.option('--bib', type=click.Path(exists=True, path_type=Path),
              help='Path to papers.bib file (default: data/papers.bib)')
@click.option('--merge/--no-merge', default=True, help='Merge with existing citations (default: yes)')
@click.option('--backup/--no-backup', default=True, help='Create backup of existing publications.yaml')
@click.option('--dry-run', is_flag=True, help='Preview changes without updating files')
@click.option('--similarity-threshold', default=0.7, type=float,
              help='Minimum similarity score for paper matching (0.0-1.0, default: 0.7)')
def import_citations(source_file: Path, source_type: str, bib: Path, merge: bool,
                    backup: bool, dry_run: bool, similarity_threshold: float):
    """Import citation counts from external sources.

    This command extracts citation numbers from various sources (Google Scholar, etc.)
    and updates your publications.yaml with the latest citation counts.

    SOURCE_FILE: Path to the citation source file (e.g., Google Scholar HTML)

    Workflow:
    1. Download citation data (e.g., Google Scholar profile as complete webpage)
    2. Run this command pointing to the downloaded file
    3. Publications are matched by title similarity with your BibTeX data
    4. Citation counts are merged into publications.yaml

    Examples:
        cv-manager import-citations scholar.html
        cv-manager import-citations --dry-run --source-type google_scholar_html scholar.html
        cv-manager import-citations --similarity-threshold 0.8 scholar.html
    """
    # Check if we're in a CV directory
    if not Path("data").exists():
        console.print("[red]Error: No data directory found. Run 'cv-manager init' first.[/red]")
        sys.exit(1)

    # Default paths if not provided
    if not bib:
        bib = Path("data/papers.bib")
    publications_file = Path("data/publications.yaml")

    # Check files exist
    for file_path, name in [(source_file, "Citation source"), (bib, "BibTeX"), (publications_file, "Publications YAML")]:
        if not Path(file_path).exists():
            console.print(f"[red]Error: {name} file not found: {file_path}[/red]")
            sys.exit(1)

    try:
        from .data.citations import update_citations_from_source

        # Will pass threshold to the updater

        console.print(f"[blue]Importing citations from: {source_file.name}[/blue]")
        console.print(f"[blue]Source type: {source_type}[/blue]")
        if dry_run:
            console.print("[yellow]DRY RUN: No files will be modified[/yellow]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
        ) as progress:
            task = progress.add_task("Processing citation data...", total=4)

            # Create backup if requested
            if backup and not dry_run and publications_file.exists():
                backup_file = publications_file.with_suffix('.yaml.backup')
                import shutil
                shutil.copy2(publications_file, backup_file)
                console.print(f"[blue]Backup created: {backup_file}[/blue]")

            progress.update(task, advance=1, description="Extracting citations...")

            # Update citations
            results = update_citations_from_source(
                str(source_file), source_type, str(bib),
                str(publications_file), dry_run, similarity_threshold
            )

            progress.update(task, advance=3, description="✓ Citation import completed")

        # Display results
        from .data.citations import CitationUpdater
        updater = CitationUpdater()
        summary = updater.get_citation_summary(results)
        console.print("\n" + summary)

        if not dry_run and results['updated_count'] > 0:
            console.print(f"\n[green]Successfully updated {results['updated_count']} publications![/green]")
            console.print(f"[blue]Publications saved to: {publications_file}[/blue]")

            # Suggest next steps
            console.print("\n[blue]Next steps:[/blue]")
            console.print("  - Run 'cv-manager build' to regenerate your CV with updated citations")
            console.print("  - Review the updates in your publications.yaml file")

        elif dry_run:
            console.print(f"\n[yellow]Dry run completed. Would update {results['updated_count']} publications.[/yellow]")
            console.print("[blue]Remove --dry-run to apply changes.[/blue]")

        else:
            console.print(f"\n[yellow]No publications were updated. All citation counts are current.[/yellow]")

    except Exception as e:
        console.print(f"[red]Error importing citations: {e}[/red]")
        import traceback
        if "--verbose" in sys.argv:
            console.print(f"[red]{traceback.format_exc()}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()