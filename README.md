# CV Management System

A modern, programmatic approach to academic CV creation and management with comprehensive ORCID integration, BibTeX import, and multiple professional CV templates.

## ✨ Key Features

- **📄 Multiple CV Templates**: Academic US/UK, Promotion/Tenure formats
- **🔄 ORCID Integration**: Bidirectional sync with ORCID profiles
- **📚 BibTeX Import**: Automatic publication import with smart categorization
- **🎓 Advanced Supervision Tracking**: Students, industry interns, academic collaborators
- **🌐 Unicode Support**: Proper handling of international names and characters
- **📝 YAML-Based**: Human-readable, version-control friendly data storage
- **🖥️ Web Interface**: User-friendly editing and management
- **⚙️ CLI Tools**: Powerful command-line interface for automation

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
# Journal Articles
journal_papers:
  - title: "Your Journal Article"
    authors: ["You", "Collaborator"]
    journal: "Nature Machine Intelligence"
    year: 2024
    volume: "6"
    pages: "123-145"
    doi: "10.1038/s42256-024-00123-4"

# Conference Papers (flat list, sorted by year)
conference_papers:
  - title: "Conference Paper Title"
    authors: ["You", "Co-author"]
    venue: "International Conference on Machine Learning"
    year: 2025
    type: "oral"
    acceptance_rate: "22% acceptance rate"
    url: "https://proceedings.mlr.press/..."

# Preprints and Under Review
preprints:
  - title: "Preprint Title"
    authors: ["You"]
    year: 2025
    arxiv: "2501.12345"

under_review:
  - title: "Under Review Paper"
    authors: ["You"]
    venue: "Journal of Machine Learning Research"
    year: 2025
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

### 3. Complete Data Structure Reference

The CV system supports comprehensive academic career data through structured YAML files:

#### **Personal Information** (`personal.yaml`)
```yaml
personal:
  name: "Your Name"
  current_position: "Assistant Professor"
  current_position_start_date: "2023-09"
  current_position_end_date: null  # null if ongoing
  department: "Computer Science"
  institution: "University Name"
  email: "you@university.edu"
  website: "https://yourwebsite.com"
  phone: "+1-555-0123"
  orcid: "0000-0000-0000-0000"
  address: "Office 123, Building Name"

education:
  - year: 2023
    degree: "Ph.D. Computer Science"
    institution: "University of Excellence"
    supervisor: "Dr. Advisor Name"
    thesis: "Thesis Title"

# Career History
employment:
  - position: "Postdoctoral Researcher"
    institution: "Research Institute"
    department: "Department Name"
    start_date: "2021-09"
    end_date: "2023-08"

joint_appointments:
  - position: "Research Scientist"
    institution: "Company Name"
    location: "City, Country"
    start_date: "2023-01"
    end_date: null
    percentage: "20%"
    description: "Part-time research collaboration"

visiting_appointments:
  - position: "Visiting Scholar"
    institution: "Partner University"
    location: "City, Country"
    start_date: "2022-06"
    end_date: "2022-08"
    description: "Summer research collaboration"

memberships:
  - organization: "ACM"
    type: "Professional"
    start_date: "2020"
    status: "Active"
```

#### **Teaching & Supervision** (`teaching.yaml`)
```yaml
experience:
  - year: 2024
    role: "Instructor"
    course: "Machine Learning"
    level: "Graduate"
    institution: "University Name"
    students: "45 students"

supervision:
  # Formal degree students
  - start_date: "2023-09"
    end_date: "2027-09"
    student: "PhD Student Name"
    institution: "University Name"
    level: "PhD"
    status: "Full-time"
    role: "Primary Supervisor"
    funder: "NSF Fellowship"

  # Industry internships
  - start_date: "2024-06"
    end_date: "2024-08"
    student: "Intern Name"
    institution: "Google Research"
    level: "Industry Intern"
    collaborator: "Industry Mentor"

  # Academic internships
  - start_date: "2023-06"
    end_date: "2023-08"
    student: "Research Intern"
    institution: "Partner University"
    level: "Masters Intern"
```

#### **Professional Service** (`service.yaml`)
```yaml
conference_reviews:
  - venue: "NeurIPS"
    years: [2022, 2023, 2024]
    role: "Area Chair"  # or "Reviewer"

journal_reviews:
  - venue: "Journal of Machine Learning Research"
    year: 2024
    role: "Reviewer"

workshops:
  - venue: "Workshop on Causal ML at NeurIPS"
    year: 2024
    role: "Organizer"
```

#### **Grants & Awards** (`grants.yaml`)
```yaml
fellowships:
  - title: "NSF CAREER Award"
    organization: "National Science Foundation"
    year: 2024
    amount: "$500,000"
    description: "5-year research program"

grants:
  - title: "AI Research Initiative"
    organization: "Industry Partner"
    year: 2023
    role: "Co-PI"
    amount: "$100,000"

conference_awards:
  - title: "Best Paper Award"
    venue: "ICML 2024"
    year: 2024

research_awards:
  - title: "Young Researcher Award"
    organization: "AI Society"
    year: 2023
```

#### **Talks & Presentations** (`talks.yaml`)
```yaml
invited:
  - title: "Keynote: Future of AI"
    venue: "AI Conference 2024"
    year: 2024
    location: "New York, NY"

industry:
  - title: "ML in Production"
    venue: "Tech Company"
    year: 2024

seminars:
  - title: "Research Seminar"
    venue: "University Department"
    year: 2024
```

### 4. Templates & CV Generation

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

### 5. Complete CLI Reference

#### Core Commands
```bash
# Initialize new CV
cv-manager init <directory>

# Build CV (all formats)
cv-manager build
cv-manager build --template promotion
cv-manager build --format latex --output-dir custom/

# Start web interface
cv-manager serve
cv-manager serve --port 8080 --host 0.0.0.0
```

#### Publication Import
```bash
# Import from BibTeX
cv-manager import-bibtex path/to/papers.bib

# Import from ORCID
cv-manager import-orcid 0000-0000-0000-0000
```

#### ORCID Integration
```bash
# Connect to ORCID (OAuth setup)
cv-manager orcid-connect 0000-0000-0000-0000

# Sync TO ORCID
cv-manager orcid-sync 0000-0000-0000-0000 --dry-run  # Preview
cv-manager orcid-sync 0000-0000-0000-0000           # Execute

# Check ORCID connection status
cv-manager orcid-status
```

#### Help & Documentation
```bash
# Get help for any command
cv-manager --help
cv-manager build --help
cv-manager import-bibtex --help
```

### 6. Advanced Features

#### Unicode & International Names
- **Smart LaTeX Escaping**: Automatically handles accented characters (é, ñ, ü, etc.)
- **Author Name Processing**: Proper formatting for international co-author names
- **Input Formats**: Supports Unicode in YAML files, converts to proper LaTeX

#### Supervision Organization
- **Students**: PhD and Masters degree supervision
- **Industry Interns**: Corporate/industry internship supervision
- **Academic Interns**: University/research institution interns
- **Date Ranges**: Full start/end date tracking with "present" for ongoing

#### Publication Categorization
- **Journal Articles**: Separate section with volume, pages, DOI
- **Conference Proceedings**: Independent numbering and formatting
- **Preprints**: arXiv and other preprint servers
- **Under Review**: Submissions in review process

#### Professional Service Organization
- **Area Chair vs Reviewer**: Separate sections for different service levels
- **Conference vs Journal**: Different formatting for different review types
- **Invited Talks**: Dedicated section separate from other service
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
- **This README** - Complete system overview with data structures and CLI reference
- **FEATURES.md** - Comprehensive feature documentation covering all capabilities
- **ORCID_OAUTH_SETUP.md** - Step-by-step ORCID OAuth setup guide

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