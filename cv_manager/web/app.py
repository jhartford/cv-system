"""Main Flask application for CV Manager web interface."""

import os
from pathlib import Path
from typing import Dict, Any

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_wtf.csrf import CSRFProtect

from ..utils.helpers import load_yaml, save_yaml
from ..build.latex import CVBuilder


def create_app(config: Dict[str, Any] = None) -> Flask:
    """Create and configure Flask application."""
    app = Flask(__name__)

    # Configuration
    app.config.update({
        'SECRET_KEY': os.environ.get('SECRET_KEY', 'dev-key-change-in-production'),
        'WTF_CSRF_ENABLED': True,
        'MAX_CONTENT_LENGTH': 16 * 1024 * 1024,  # 16MB max upload
    })

    if config:
        app.config.update(config)

    # Enable CSRF protection
    csrf = CSRFProtect(app)

    # CV directory - assume we're running from a CV directory
    cv_dir = Path.cwd()

    @app.route('/')
    def dashboard():
        """Main dashboard showing CV overview."""
        try:
            # Load CV data
            personal = load_yaml(str(cv_dir / "data" / "personal.yaml"))
            publications = load_yaml(str(cv_dir / "data" / "publications.yaml"))
            grants = load_yaml(str(cv_dir / "data" / "grants.yaml"))

            # Calculate statistics
            stats = {
                'journal_papers': len(publications.get('journal_papers', [])),
                'conference_papers': sum(len(papers) for papers in publications.get('conference_papers', {}).values()),
                'preprints': len(publications.get('preprints', [])),
                'grants': len(grants.get('fellowships', [])) + len(grants.get('grants', [])),
                'awards': len(grants.get('conference_awards', [])) + len(grants.get('university_awards', []))
            }

            return render_template('dashboard.html', personal=personal, stats=stats)

        except Exception as e:
            flash(f'Error loading CV data: {e}', 'error')
            return render_template('dashboard.html', personal={}, stats={})

    @app.route('/personal', methods=['GET', 'POST'])
    def personal():
        """Edit personal information."""
        data_file = cv_dir / "data" / "personal.yaml"

        if request.method == 'POST':
            try:
                # Get form data
                personal_data = {
                    'personal': {
                        'name': request.form.get('name', ''),
                        'current_position': request.form.get('current_position', ''),
                        'department': request.form.get('department', ''),
                        'institution': request.form.get('institution', ''),
                        'email': request.form.get('email', ''),
                        'website': request.form.get('website', ''),
                        'phone': request.form.get('phone', ''),
                        'orcid': request.form.get('orcid', ''),
                        'address': request.form.get('address', '')
                    }
                }

                # Clean empty fields
                for key, value in list(personal_data['personal'].items()):
                    if not value:
                        personal_data['personal'][key] = None

                # Save data
                save_yaml(personal_data, str(data_file))
                flash('Personal information updated successfully!', 'success')

                return redirect(url_for('personal'))

            except Exception as e:
                flash(f'Error saving data: {e}', 'error')

        # Load existing data
        try:
            data = load_yaml(str(data_file))
            personal_info = data.get('personal', {})
        except:
            personal_info = {}

        return render_template('personal.html', personal=personal_info)

    @app.route('/publications')
    def publications():
        """View and manage publications."""
        try:
            data = load_yaml(str(cv_dir / "data" / "publications.yaml"))
            return render_template('publications.html', publications=data)
        except Exception as e:
            flash(f'Error loading publications: {e}', 'error')
            return render_template('publications.html', publications={})

    @app.route('/grants')
    def grants():
        """View and manage grants and awards."""
        try:
            data = load_yaml(str(cv_dir / "data" / "grants.yaml"))
            return render_template('grants.html', grants=data)
        except Exception as e:
            flash(f'Error loading grants: {e}', 'error')
            return render_template('grants.html', grants={})

    @app.route('/teaching')
    def teaching():
        """View and manage teaching information."""
        try:
            data = load_yaml(str(cv_dir / "data" / "teaching.yaml"))
            return render_template('teaching.html', teaching=data)
        except Exception as e:
            flash(f'Error loading teaching data: {e}', 'error')
            return render_template('teaching.html', teaching={})

    @app.route('/service')
    def service():
        """View and manage service activities."""
        try:
            data = load_yaml(str(cv_dir / "data" / "service.yaml"))
            return render_template('service.html', service=data)
        except Exception as e:
            flash(f'Error loading service data: {e}', 'error')
            return render_template('service.html', service={})

    @app.route('/talks')
    def talks():
        """View and manage talks and presentations."""
        try:
            data = load_yaml(str(cv_dir / "data" / "talks.yaml"))
            return render_template('talks.html', talks=data)
        except Exception as e:
            flash(f'Error loading talks data: {e}', 'error')
            return render_template('talks.html', talks={})

    @app.route('/build/<template>')
    def build_cv(template):
        """Build CV with specified template."""
        try:
            builder = CVBuilder(str(cv_dir))

            # Build LaTeX first
            latex_file = builder.build_cv(template, "latex")
            if not latex_file:
                return jsonify({'error': 'Failed to generate LaTeX'}), 500

            # Try to build PDF
            pdf_file = builder.build_cv(template, "pdf")

            result = {
                'latex_file': latex_file,
                'pdf_file': pdf_file,
                'template': template
            }

            flash(f'CV built successfully: {template}', 'success')
            return jsonify(result)

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/download/<path:filename>')
    def download_file(filename):
        """Download generated files."""
        try:
            file_path = cv_dir / "output" / filename
            if file_path.exists():
                return send_file(str(file_path), as_attachment=True)
            else:
                flash('File not found', 'error')
                return redirect(url_for('dashboard'))
        except Exception as e:
            flash(f'Error downloading file: {e}', 'error')
            return redirect(url_for('dashboard'))

    @app.route('/api/validate')
    def validate_data():
        """Validate all YAML data files."""
        errors = []

        data_files = [
            "personal.yaml", "publications.yaml", "grants.yaml",
            "teaching.yaml", "service.yaml", "talks.yaml"
        ]

        for file in data_files:
            file_path = cv_dir / "data" / file
            try:
                if file_path.exists():
                    load_yaml(str(file_path))
                else:
                    errors.append(f"Missing file: {file}")
            except Exception as e:
                errors.append(f"Error in {file}: {str(e)}")

        return jsonify({
            'valid': len(errors) == 0,
            'errors': errors
        })

    @app.route('/import-bibtex', methods=['GET', 'POST'])
    def import_bibtex():
        """Import publications from BibTeX file."""
        if request.method == 'POST':
            try:
                # Check if file was uploaded
                if 'bibtex_file' not in request.files:
                    flash('No file selected', 'error')
                    return redirect(request.url)

                file = request.files['bibtex_file']
                if file.filename == '':
                    flash('No file selected', 'error')
                    return redirect(request.url)

                if not file.filename.lower().endswith('.bib'):
                    flash('Please upload a .bib file', 'error')
                    return redirect(request.url)

                # Get form options
                merge = request.form.get('merge', 'on') == 'on'
                backup = request.form.get('backup', 'on') == 'on'

                # Save uploaded file temporarily
                import tempfile
                import os
                with tempfile.NamedTemporaryFile(mode='w+b', suffix='.bib', delete=False) as tmp_file:
                    file.save(tmp_file.name)
                    tmp_file_path = tmp_file.name

                try:
                    # Import BibTeX
                    from ..data.bibtex import BibTeXImporter

                    importer = BibTeXImporter()
                    new_publications = importer.import_bibtex_file(tmp_file_path)

                    # Count imported publications
                    total_imported = 0
                    for category, pubs in new_publications.items():
                        if category == 'conference_papers':
                            total_imported += sum(len(papers) for papers in pubs.values())
                        else:
                            total_imported += len(pubs)

                    if total_imported == 0:
                        flash('No publications found in BibTeX file', 'warning')
                        return redirect(url_for('import_bibtex'))

                    publications_file = cv_dir / "data" / "publications.yaml"

                    # Handle existing publications
                    if merge and publications_file.exists():
                        # Create backup if requested
                        if backup:
                            backup_file = publications_file.with_suffix('.yaml.backup')
                            import shutil
                            shutil.copy2(publications_file, backup_file)

                        existing_publications = load_yaml(str(publications_file))
                        merged_publications = importer.merge_with_existing(new_publications, existing_publications)
                    else:
                        merged_publications = new_publications

                    # Save publications
                    save_yaml(merged_publications, str(publications_file))

                    flash(f'Successfully imported {total_imported} publications!', 'success')
                    return redirect(url_for('publications'))

                finally:
                    # Clean up temp file
                    os.unlink(tmp_file_path)

            except Exception as e:
                flash(f'Error importing BibTeX file: {e}', 'error')

        return render_template('import_bibtex.html')

    @app.route('/import-orcid', methods=['GET', 'POST'])
    def import_orcid():
        """Import publications from ORCID profile."""
        if request.method == 'POST':
            try:
                # Get ORCID ID from form
                orcid_id = request.form.get('orcid_id', '').strip()
                if not orcid_id:
                    flash('Please enter an ORCID ID', 'error')
                    return redirect(request.url)

                # Get form options
                merge = request.form.get('merge', 'on') == 'on'
                backup = request.form.get('backup', 'on') == 'on'
                sandbox = request.form.get('sandbox', 'off') == 'on'

                # Import from ORCID
                from ..data.orcid import ORCIDImporter
                import requests

                importer = ORCIDImporter()

                try:
                    # Validate ORCID ID
                    validated_orcid = importer.validate_orcid_id(orcid_id)
                except ValueError as e:
                    flash(f'Invalid ORCID ID: {e}', 'error')
                    return redirect(request.url)

                try:
                    # Import publications
                    new_publications = importer.import_publications_from_orcid(validated_orcid, sandbox)
                except requests.RequestException as e:
                    if "404" in str(e):
                        flash(f'ORCID profile {validated_orcid} not found or has no public works', 'error')
                    elif "403" in str(e):
                        flash('Access denied. The ORCID profile may be private', 'error')
                    else:
                        flash(f'Error fetching ORCID data: {e}', 'error')
                    return redirect(request.url)

                # Count imported publications
                total_imported = 0
                for category, pubs in new_publications.items():
                    if category == 'conference_papers':
                        total_imported += sum(len(papers) for papers in pubs.values())
                    else:
                        total_imported += len(pubs)

                if total_imported == 0:
                    flash('No publications found in ORCID profile. This could mean the profile has no works added or all works are set to private.', 'warning')
                    return redirect(request.url)

                publications_file = cv_dir / "data" / "publications.yaml"

                # Handle existing publications
                if merge and publications_file.exists():
                    # Create backup if requested
                    if backup:
                        backup_file = publications_file.with_suffix('.yaml.backup')
                        import shutil
                        shutil.copy2(publications_file, backup_file)

                    existing_publications = load_yaml(str(publications_file))
                    merged_publications = importer.merge_with_existing(new_publications, existing_publications)
                else:
                    merged_publications = new_publications

                # Save publications
                save_yaml(merged_publications, str(publications_file))

                flash(f'Successfully imported {total_imported} publications from ORCID {validated_orcid}!', 'success')
                return redirect(url_for('publications'))

            except Exception as e:
                flash(f'Error importing from ORCID: {e}', 'error')

        return render_template('import_orcid.html')

    @app.route('/orcid/connect', methods=['GET', 'POST'])
    def orcid_connect():
        """Connect to ORCID using OAuth 2.0."""
        if request.method == 'POST':
            try:
                # Get ORCID OAuth configuration from environment
                client_id = os.environ.get('ORCID_CLIENT_ID')
                client_secret = os.environ.get('ORCID_CLIENT_SECRET')

                if not client_id or not client_secret:
                    flash('ORCID OAuth credentials not configured. Please set ORCID_CLIENT_ID and ORCID_CLIENT_SECRET environment variables.', 'error')
                    return redirect(request.url)

                # Get form data
                orcid_id = request.form.get('orcid_id', '').strip()
                use_sandbox = request.form.get('sandbox', 'off') == 'on'

                if not orcid_id:
                    flash('Please enter an ORCID ID', 'error')
                    return redirect(request.url)

                # Initialize ORCID client
                from ..data.orcid import ORCIDClient
                client = ORCIDClient(client_id, client_secret)

                try:
                    validated_orcid = client.validate_orcid_id(orcid_id)
                except ValueError as e:
                    flash(f'Invalid ORCID ID: {e}', 'error')
                    return redirect(request.url)

                # Generate OAuth authorization URL
                redirect_uri = url_for('orcid_callback', _external=True)
                scopes = ['/activities/update', '/read-limited']  # Required scopes for read/write

                # Store state in session for security
                import secrets
                state = secrets.token_urlsafe(32)

                # Store OAuth state and ORCID ID in session
                from flask import session
                session['oauth_state'] = state
                session['oauth_orcid_id'] = validated_orcid
                session['oauth_sandbox'] = use_sandbox

                auth_url = client.get_oauth_authorize_url(
                    redirect_uri=redirect_uri,
                    scopes=scopes,
                    use_sandbox=use_sandbox,
                    state=state
                )

                # Redirect user to ORCID for authorization
                return redirect(auth_url)

            except Exception as e:
                flash(f'Error initiating ORCID connection: {e}', 'error')

        return render_template('orcid_connect.html')

    @app.route('/orcid/callback')
    def orcid_callback():
        """Handle OAuth callback from ORCID."""
        try:
            # Get OAuth parameters from callback
            code = request.args.get('code')
            state = request.args.get('state')
            error = request.args.get('error')

            if error:
                flash(f'ORCID authorization failed: {error}', 'error')
                return redirect(url_for('orcid_connect'))

            if not code:
                flash('No authorization code received from ORCID', 'error')
                return redirect(url_for('orcid_connect'))

            # Verify state parameter to prevent CSRF attacks
            from flask import session
            stored_state = session.get('oauth_state')
            if not stored_state or stored_state != state:
                flash('Invalid OAuth state parameter. Possible CSRF attack.', 'error')
                return redirect(url_for('orcid_connect'))

            # Get stored OAuth info from session
            orcid_id = session.get('oauth_orcid_id')
            use_sandbox = session.get('oauth_sandbox', False)

            if not orcid_id:
                flash('OAuth session expired. Please try again.', 'error')
                return redirect(url_for('orcid_connect'))

            # Get OAuth credentials
            client_id = os.environ.get('ORCID_CLIENT_ID')
            client_secret = os.environ.get('ORCID_CLIENT_SECRET')

            if not client_id or not client_secret:
                flash('ORCID OAuth credentials not configured', 'error')
                return redirect(url_for('orcid_connect'))

            # Exchange code for access token
            from ..data.orcid import ORCIDClient
            client = ORCIDClient(client_id, client_secret)

            redirect_uri = url_for('orcid_callback', _external=True)
            token_data = client.exchange_code_for_token(code, redirect_uri, use_sandbox)

            # Store token data (in production, use secure storage)
            # For now, store in session temporarily
            session['orcid_tokens'] = session.get('orcid_tokens', {})
            session['orcid_tokens'][orcid_id] = token_data

            # Clear OAuth state
            session.pop('oauth_state', None)
            session.pop('oauth_orcid_id', None)
            session.pop('oauth_sandbox', None)

            flash(f'Successfully connected to ORCID profile {orcid_id}!', 'success')
            return redirect(url_for('orcid_sync'))

        except Exception as e:
            flash(f'Error processing ORCID authorization: {e}', 'error')
            return redirect(url_for('orcid_connect'))

    @app.route('/orcid/sync', methods=['GET', 'POST'])
    def orcid_sync():
        """Sync publications to ORCID profile."""
        if request.method == 'POST':
            try:
                # Get form data
                orcid_id = request.form.get('orcid_id', '').strip()
                dry_run = request.form.get('dry_run', 'off') == 'on'
                use_sandbox = request.form.get('sandbox', 'off') == 'on'

                if not orcid_id:
                    flash('Please enter an ORCID ID', 'error')
                    return redirect(request.url)

                # Check if we have access token for this ORCID ID
                from flask import session
                tokens = session.get('orcid_tokens', {})

                if orcid_id not in tokens:
                    flash(f'No OAuth token found for ORCID ID {orcid_id}. Please connect first.', 'error')
                    return redirect(url_for('orcid_connect'))

                # Load publications
                try:
                    publications = load_yaml(str(cv_dir / "data" / "publications.yaml"))
                except Exception as e:
                    flash(f'Error loading publications: {e}', 'error')
                    return redirect(request.url)

                # Initialize ORCID client
                client_id = os.environ.get('ORCID_CLIENT_ID')
                client_secret = os.environ.get('ORCID_CLIENT_SECRET')

                if not client_id or not client_secret:
                    flash('ORCID OAuth credentials not configured', 'error')
                    return redirect(request.url)

                from ..data.orcid import ORCIDClient
                client = ORCIDClient(client_id, client_secret)
                client.store_token(orcid_id, tokens[orcid_id])

                # Perform sync
                results = client.sync_publications_to_orcid(
                    orcid_id=orcid_id,
                    publications=publications,
                    use_sandbox=use_sandbox,
                    dry_run=dry_run
                )

                # Display results
                if dry_run:
                    flash(f'Dry run completed: {results["posted"]} publications would be posted, {results["skipped"]} skipped', 'info')
                else:
                    flash(f'Sync completed: {results["posted"]} publications posted, {results["skipped"]} skipped', 'success')

                if results['errors']:
                    for error in results['errors']:
                        flash(f'Error: {error}', 'warning')

                return render_template('orcid_sync_results.html', results=results, orcid_id=orcid_id)

            except Exception as e:
                flash(f'Error syncing to ORCID: {e}', 'error')

        # Get connected ORCID profiles
        from flask import session
        connected_profiles = list(session.get('orcid_tokens', {}).keys())

        return render_template('orcid_sync.html', connected_profiles=connected_profiles)

    @app.route('/orcid/disconnect/<orcid_id>')
    def orcid_disconnect(orcid_id):
        """Disconnect an ORCID profile."""
        from flask import session

        tokens = session.get('orcid_tokens', {})
        if orcid_id in tokens:
            del tokens[orcid_id]
            session['orcid_tokens'] = tokens
            flash(f'Disconnected from ORCID profile {orcid_id}', 'success')
        else:
            flash(f'ORCID profile {orcid_id} was not connected', 'warning')

        return redirect(url_for('orcid_sync'))

    return app