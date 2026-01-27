# CV Management System

A modern, programmatic approach to academic CV creation and management with ORCID integration.

## 🚀 TLDR - Quick Start

### Installation & Basic Setup
```bash
# Clone and install
git clone <cv-system-repo>
cd cv-system
pip install -e .

# Create new CV
cv-manager init my-cv
cd my-cv

# Start web interface
cv-manager serve
# Visit: http://localhost:5000
```

### ORCID Integration (Optional)
```bash
# Set OAuth credentials (get from orcid.org/developer-tools)
export ORCID_CLIENT_ID="your-client-id"
export ORCID_CLIENT_SECRET="your-client-secret"

# Import publications FROM ORCID (no OAuth needed)
cv-manager import-orcid 0000-0000-0000-0000

# Sync publications TO ORCID (requires OAuth)
cv-manager orcid-connect 0000-0000-0000-0000  # One-time setup
cv-manager orcid-sync 0000-0000-0000-0000 --dry-run  # Preview
cv-manager orcid-sync 0000-0000-0000-0000     # Actual sync
```

### Generate CV
```bash
cv-manager build --template academic-us --format pdf
# Output: output/cv-academic-us.pdf
```

**That's it!** You now have a working CV system with optional ORCID bidirectional sync.

---

## 📖 Detailed Documentation

### Overview

This CV Management System provides:
- **YAML-based data storage** for all CV information (git-friendly)
- **Multiple LaTeX templates** (academic US/UK, promotion formats)
- **Web interface** for easy editing and management
- **ORCID integration** for importing and syncing publications
- **BibTeX import/export** for bibliography management
- **Command-line tools** for automation and scripting

### System Architecture

```
CV Data (YAML) → Jinja2 Templates → LaTeX → PDF
     ↕              ↕                ↕       ↕
ORCID Sync    Web Interface    CLI Tools  Output
```

## 📁 Project Structure

After running `cv-manager init my-cv`:

```
my-cv/
├── data/                           # YAML data files
│   ├── personal.yaml              # Personal info & contact
│   ├── publications.yaml          # All publications
│   ├── grants.yaml                # Grants & awards
│   ├── teaching.yaml              # Teaching experience
│   ├── service.yaml               # Editorial activities
│   └── talks.yaml                 # Presentations
├── config.yaml                    # CV configuration
└── output/                        # Generated files
    ├── cv-academic-us.pdf         # Generated CVs
    ├── cv-academic-us.tex         # LaTeX source
    └── publications.bib           # BibTeX export
```

## 🔧 Installation

### Requirements
- Python 3.8+
- LaTeX distribution (for PDF generation)
- Modern web browser
- Internet connection (for ORCID features)

### Install from Source
```bash
git clone <repository-url>
cd cv-system
pip install -e .

# Verify installation
cv-manager --help
```

### Dependencies
The system automatically installs:
- Flask (web interface)
- Jinja2 (templating)
- Click (CLI framework)
- PyYAML (data files)
- WTForms (form validation)
- Requests (ORCID API)

## 🎯 Core Features

### 1. Publications Management

**Data Structure** - Publications organized by category in `publications.yaml`:
```yaml
preprints:
  - title: "Your Preprint Title"
    authors: ["You", "Collaborator"]
    year: 2025

conference_papers:
  2025:
    - title: "Conference Paper"
      authors: ["You"]
      venue: "ICML 2025"
      year: 2025
      type: "oral"

journal_papers:
  - title: "Journal Article"
    authors: ["You"]
    journal: "Nature"
    year: 2024
    doi: "10.1000/example"
```

**Web Interface Features:**
- Statistics dashboard with publication counts
- Categorized display by publication type
- Rich metadata display (awards, DOI links, acceptance rates)
- Export functionality (YAML, BibTeX)

### 2. ORCID Integration

#### Import Publications (Public API - No Setup Required)
```bash
# Basic import
cv-manager import-orcid 0000-0000-0000-0000

# With options
cv-manager import-orcid 0000-0000-0000-0000 --merge --backup --sandbox
```

#### Export Publications (OAuth Required - Member API)
**Prerequisites:**
1. ORCID Member API access (contact your institution or apply at orcid.org)
2. OAuth application credentials

**Setup:**
```bash
# Set environment variables
export ORCID_CLIENT_ID="your-client-id"
export ORCID_CLIENT_SECRET="your-client-secret"

# Connect your ORCID profile (one-time)
cv-manager orcid-connect 0000-0000-0000-0000
```

**Sync Publications:**
```bash
# Preview changes (recommended)
cv-manager orcid-sync 0000-0000-0000-0000 --dry-run

# Actually sync to ORCID
cv-manager orcid-sync 0000-0000-0000-0000

# Check connection status
cv-manager orcid-status
```

**Web Interface:**
- Visit `http://localhost:5000/orcid/connect` for OAuth setup
- Visit `http://localhost:5000/orcid/sync` for publication management

### 3. Templates & CV Generation

**Available Templates:**
- `academic-us` - Standard US academic format
- `academic-uk` - UK/European academic format
- `promotion` - Promotion/tenure dossier format

**Generate CV:**
```bash
# Generate specific template
cv-manager build --template academic-us --format pdf

# Generate all templates
cv-manager build

# Custom output directory
cv-manager build --output-dir custom-output/
```

**Template Features:**
- Conditional sections (show/hide based on data)
- Automatic formatting and consistent styling
- Support for special characters and LaTeX math
- Flexible section ordering and customization

### 4. Web Interface

**Start Web Server:**
```bash
cv-manager serve                    # Default: http://localhost:5000
cv-manager serve --port 8080        # Custom port
cv-manager serve --host 0.0.0.0     # Allow external access
```

**Available Pages:**
- `/` - Dashboard with CV overview and statistics
- `/personal` - Edit personal information
- `/publications` - Manage publications with import/export
- `/grants` - Manage grants and awards
- `/teaching` - Teaching experience and supervision
- `/service` - Editorial activities and service
- `/talks` - Presentations and invited talks
- `/orcid/connect` - OAuth connection to ORCID
- `/orcid/sync` - Sync publications with ORCID

**Features:**
- Responsive design with Tailwind CSS
- Real-time form validation
- File upload/download
- CSRF protection
- Error handling and user feedback

### 5. Data Import/Export

#### BibTeX Integration
```bash
# Import BibTeX file
cv-manager import-bibtex publications.bib --merge --backup

# Export to BibTeX
cv-manager export --format bibtex --output my-publications.bib

# Web interface
# Upload: http://localhost:5000/import-bibtex
# Download: http://localhost:5000/download/publications.bib
```

#### YAML Export
```bash
# Export publications as YAML
cv-manager export --format yaml --output publications-backup.yaml
```

### 6. Validation & Quality Control

```bash
# Validate all YAML files
cv-manager validate

# Web validation
# Visit: http://localhost:5000/api/validate
```

**Validation Features:**
- YAML syntax and structure validation
- Required field checking
- Cross-reference validation
- Detailed error reporting

## 🌐 Web Interface Guide

### Dashboard
- **Overview statistics** for all CV sections
- **Recent activity** and file status
- **Quick actions** for common tasks
- **Validation status** of all data files

### Publications Management
- **Category-based organization** (journal, conference, preprints, etc.)
- **Rich metadata display** with DOI links and awards
- **Import/export functionality**
- **Statistics and counts** by publication type

### ORCID Integration Pages
- **Connect page** (`/orcid/connect`): OAuth authorization flow
- **Sync page** (`/orcid/sync`): Bidirectional publication synchronization
- **Results page**: Detailed sync results and error reporting

## 💻 Command Line Reference

### Core Commands
```bash
cv-manager init <name>              # Create new CV directory
cv-manager build [options]          # Generate CV outputs
cv-manager serve [options]          # Start web interface
cv-manager validate                 # Validate all data
cv-manager export --format bibtex  # Export publications
```

### Import Commands
```bash
cv-manager import-orcid <orcid-id>  # Import from ORCID
cv-manager import-bibtex <file>     # Import BibTeX file
```

### ORCID OAuth Commands
```bash
cv-manager orcid-connect <orcid-id> # OAuth connection
cv-manager orcid-sync <orcid-id>    # Sync publications
cv-manager orcid-status             # Show connections
```

### Command Options
Most commands support these common options:
- `--help` - Show command help
- `--merge` - Merge with existing data (imports)
- `--backup` - Create backup before changes
- `--sandbox` - Use ORCID sandbox environment
- `--dry-run` - Preview changes without applying
- `--force` - Skip confirmation prompts

## 🔒 Security & Privacy

### OAuth Security
- **Standard OAuth 2.0** implementation with CSRF protection
- **State parameter validation** to prevent attacks
- **Secure token storage** with appropriate file permissions
- **Session-based tokens** in web interface (temporary)
- **File-based tokens** in CLI (persistent, user-only access)

### Data Privacy
- **Local storage only** - all data stays on your machine
- **No cloud dependencies** - works completely offline (except ORCID sync)
- **ORCID read scope** - only accesses publicly visible data
- **User-controlled sync** - you choose what to share with ORCID

### Token Management
- **Automatic expiration** handling
- **Refresh token support** (when available)
- **Revocation support** - disconnect anytime from ORCID settings
- **Multiple profiles** - separate tokens per ORCID ID

## 🛠️ Advanced Configuration

### Environment Variables
```bash
# ORCID OAuth (required for sync to ORCID)
export ORCID_CLIENT_ID="your-client-id"
export ORCID_CLIENT_SECRET="your-client-secret"

# Optional configuration
export CV_MANAGER_DEBUG=1           # Enable debug logging
export CV_MANAGER_BASE_URL="https://your-domain.com"  # Custom base URL
```

### Configuration File
Create `~/.cv-manager/config.yaml`:
```yaml
orcid:
  client_id: "your-client-id"
  client_secret: "your-client-secret"
  sandbox:
    client_id: "sandbox-client-id"
    client_secret: "sandbox-client-secret"

web:
  port: 5000
  host: "localhost"

templates:
  default: "academic-us"
  output_dir: "output"
```

## 📚 Examples & Workflows

### New User Setup
```bash
# 1. Install system
pip install -e cv-system

# 2. Create CV directory
cv-manager init jason-cv
cd jason-cv

# 3. Add personal information (edit data/personal.yaml or use web interface)
cv-manager serve  # Edit at http://localhost:5000/personal

# 4. Import publications from ORCID
cv-manager import-orcid 0000-0002-1825-0097

# 5. Generate CV
cv-manager build --template academic-us --format pdf
```

### ORCID Bidirectional Sync Setup
```bash
# 1. Get OAuth credentials from ORCID developer tools
# 2. Set environment variables
export ORCID_CLIENT_ID="your-client-id"
export ORCID_CLIENT_SECRET="your-client-secret"

# 3. Connect ORCID profile
cv-manager orcid-connect 0000-0002-1825-0097

# 4. Import existing publications from ORCID
cv-manager import-orcid 0000-0002-1825-0097 --merge

# 5. Add new publications to publications.yaml (manually or via web)

# 6. Sync new publications back to ORCID
cv-manager orcid-sync 0000-0002-1825-0097 --dry-run  # Preview
cv-manager orcid-sync 0000-0002-1825-0097            # Actually sync
```

### Regular Maintenance Workflow
```bash
# 1. Update publications in YAML files
# 2. Validate data integrity
cv-manager validate

# 3. Import any new publications from ORCID
cv-manager import-orcid 0000-0002-1825-0097 --merge --backup

# 4. Sync any new local publications to ORCID
cv-manager orcid-sync 0000-0002-1825-0097 --dry-run
cv-manager orcid-sync 0000-0002-1825-0097

# 5. Generate updated CV
cv-manager build --template academic-us --format pdf

# 6. Export BibTeX for reference managers
cv-manager export --format bibtex
```

### Multiple ORCID Profiles
```bash
# Connect multiple profiles (e.g., personal and institutional)
cv-manager orcid-connect 0000-0000-0000-0001  # Personal
cv-manager orcid-connect 0000-0000-0000-0002  # Institutional

# Check all connections
cv-manager orcid-status

# Sync to specific profile
cv-manager orcid-sync 0000-0000-0000-0001
```

## 🐛 Troubleshooting

### Common Issues

**"ORCID OAuth credentials not configured"**
```bash
# Solution: Set environment variables
export ORCID_CLIENT_ID="your-client-id"
export ORCID_CLIENT_SECRET="your-client-secret"

# Or check they're set correctly
echo $ORCID_CLIENT_ID
```

**"Invalid redirect URI"**
- Verify redirect URIs in ORCID application settings:
  - Web: `http://localhost:5000/orcid/callback`
  - CLI: `http://localhost:8080/oauth/callback`

**"No publications found in ORCID profile"**
- Check that works in your ORCID profile are set to "Public"
- Verify the ORCID ID is correct
- Try with `--sandbox` flag if using test data

**"LaTeX compilation failed"**
```bash
# Check LaTeX installation
which pdflatex

# Install LaTeX (macOS)
brew install --cask mactex

# Install LaTeX (Ubuntu)
sudo apt-get install texlive-full
```

### Debug Mode
```bash
export CV_MANAGER_DEBUG=1
cv-manager orcid-sync 0000-0000-0000-0000 --dry-run
```

### Getting Help
1. Check error messages carefully - they usually indicate the specific issue
2. Verify ORCID application configuration matches requirements
3. Test with sandbox environment first: `--sandbox`
4. Check file permissions on token storage: `~/.cv-manager/orcid_tokens.yaml`

## 🤝 Contributing

This system is designed to be:
- **Extensible** - Add new templates, data sources, or export formats
- **Maintainable** - Clean separation between data, templates, and logic
- **Shareable** - Colleagues can install and use for their own CVs

### Adding New Templates
1. Create new Jinja2 template in `cv_manager/templates/`
2. Add template metadata to configuration
3. Test with existing CV data

### Adding New Import Sources
1. Create new module in `cv_manager/data/`
2. Implement standardized data structure
3. Add CLI command and web interface

## 📋 System Requirements

### Minimum Requirements
- Python 3.8+
- 50MB disk space
- Internet connection (for ORCID features)

### Recommended Setup
- Python 3.9+
- LaTeX distribution (TeXLive, MacTeX, or MiKTeX)
- Modern web browser
- Git (for version control of CV data)

### Performance Notes
- Handles hundreds of publications efficiently
- Fast YAML processing and web interface
- LaTeX compilation time depends on CV complexity
- ORCID API calls are respectful of rate limits

## 🆘 Support

### Documentation
- **This README** - Complete system overview
- **FEATURES.md** - Detailed feature documentation
- **ORCID_OAUTH_SETUP.md** - ORCID OAuth setup guide

### Getting ORCID OAuth Access
1. **Individual researchers**: Contact your institution's library
2. **Institutions**: Apply at [orcid.org/developer-tools](https://orcid.org/developer-tools)
3. **Testing**: Use [sandbox.orcid.org](https://sandbox.orcid.org) for development

### File Issues
Report bugs or request features in the project repository.

---

## 🎉 You're All Set!

You now have a complete, modern CV management system with:
- ✅ **Structured data storage** (YAML files)
- ✅ **Professional templates** (LaTeX output)
- ✅ **Web interface** for easy editing
- ✅ **ORCID bidirectional sync** (OAuth 2.0)
- ✅ **Command-line tools** for automation
- ✅ **Import/export capabilities** (BibTeX, YAML)

Start with `cv-manager init my-cv` and build from there. The system grows with your needs!