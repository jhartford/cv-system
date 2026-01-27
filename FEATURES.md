# CV Management System - Current Features Documentation

## Overview

The CV Management System is a standalone Python package that provides a modern, programmatic approach to CV creation and management. It converts traditional markdown/LaTeX-based CVs to a structured system using YAML data files, Jinja2 templates, and provides both web and command-line interfaces for editing and generation.

## Core Architecture

### Data Structure
- **YAML-based Data Storage**: All CV information stored in structured YAML files
- **Git-friendly**: Human-readable format that works well with version control
- **Modular Organization**: Separate files for different CV sections
- **Schema Validation**: Ensures data integrity and consistency

### Template System
- **Jinja2 Templates**: Flexible templating with LaTeX output
- **Multiple Formats**: Academic US, Academic UK, Promotion formats
- **Template Inheritance**: Shared components and customizable sections
- **Conditional Rendering**: Dynamic section inclusion based on configuration

### Build Pipeline
- **Multi-format Output**: YAML → Jinja2 → LaTeX → PDF
- **Automated Compilation**: LaTeX to PDF generation
- **Error Handling**: Comprehensive build error reporting

## Current Features

### 1. Publications Management

#### Data Structure
Publications are organized into categories in `publications.yaml`:
- **Preprints**: Unpublished manuscripts and working papers
- **Conference Papers**: Organized by year with venue information
- **Journal Papers**: Peer-reviewed journal articles
- **Under Review**: Papers currently in review process
- **Workshop Papers**: Workshop presentations and posters

#### Metadata Support
- Authors, titles, venues, years
- DOI, arXiv IDs, URLs
- Publication types (oral, poster)
- Acceptance rates and awards
- BibTeX keys for citation management

#### Web Interface Features
- **Statistics Dashboard**: Publication counts by category
- **Categorized Display**: Organized by publication type
- **Rich Metadata Display**: Awards, acceptance rates, links
- **Year-based Organization**: Conference papers grouped by year
- **Export Functionality**: YAML and BibTeX export

### 2. ORCID Integration

#### Import Capabilities
- **ORCID API v3.0**: Direct integration with ORCID public API
- **Automatic Categorization**: Maps ORCID work types to CV categories
- **Metadata Extraction**: Authors, titles, journals, DOIs, years
- **Duplicate Detection**: Prevents duplicate imports by title/DOI comparison
- **Merge Functionality**: Combines imported data with existing publications

#### OAuth 2.0 Export Capabilities ⭐ NEW
- **Member API Access**: Full read/write access to ORCID profiles
- **Publication Sync**: Post CV publications to ORCID profile
- **Bidirectional Sync**: Import from and export to ORCID
- **Secure Authentication**: OAuth 2.0 with CSRF protection
- **Token Management**: Secure access token storage and refresh

#### OAuth Features
- **Web Interface**: Complete OAuth flow in web browser
- **CLI Interface**: OAuth support for command-line operations
- **Multiple Profiles**: Connect and manage multiple ORCID profiles
- **Dry Run Mode**: Preview sync operations before execution
- **Error Recovery**: Robust error handling for API failures

#### Publication Export Features
- **Work Type Mapping**: CV categories mapped to ORCID work types
- **Metadata Conversion**: Convert CV data to ORCID work format
- **Duplicate Prevention**: Skip publications already in ORCID
- **Batch Operations**: Sync entire publication lists efficiently
- **Progress Tracking**: Detailed sync results and error reporting

#### Supported ORCID Work Types
- `journal-article` ← Journal Papers
- `conference-paper` ← Conference Papers
- `preprint` ← Preprints
- `working-paper` ← Under Review
- `conference-poster` ← Workshop Papers

#### API Features
- **SSL Error Handling**: Robust network error management
- **Sandbox Support**: Testing with ORCID sandbox environment
- **Rate Limiting**: Respectful API usage
- **Error Recovery**: Graceful handling of private/missing profiles

#### ORCID ID Validation
- **Format Normalization**: Accepts multiple ORCID ID formats
- **Pattern Validation**: Ensures proper ORCID ID structure
- **URL Handling**: Strips ORCID URLs to extract ID

### 3. Web Interface

#### Core Web Features
- **Dashboard**: CV overview with statistics
- **Section Management**: Individual pages for each CV section
- **Form-based Editing**: WTForms integration for data validation
- **File Management**: Upload, download, and backup functionality
- **Live Validation**: Real-time YAML data validation

#### Navigation and UX
- **Responsive Design**: Tailwind CSS styling
- **Intuitive Navigation**: Clear section organization
- **Flash Messages**: User feedback for actions
- **Error Handling**: Graceful error display and recovery

#### Security Features
- **CSRF Protection**: Form security with WTForms
- **File Upload Limits**: 16MB maximum file size
- **Input Validation**: Server-side form validation
- **Safe File Handling**: Secure temporary file management

### 4. Command Line Interface

#### Core CLI Commands
```bash
cv-manager init <name>              # Create new CV directory
cv-manager import-orcid <orcid-id>  # Import from ORCID profile
cv-manager import-bibtex <file>     # Import from BibTeX file
cv-manager build [options]          # Generate CV outputs
cv-manager serve [--port]           # Start web interface
cv-manager validate                 # Validate YAML data
```

#### OAuth CLI Commands ⭐ NEW
```bash
cv-manager orcid-connect <orcid-id> # Connect ORCID with OAuth 2.0
cv-manager orcid-sync <orcid-id>    # Sync publications to ORCID
cv-manager orcid-status             # Show connected ORCID profiles
```

#### CLI Features
- **Click Framework**: Modern CLI with help system
- **Progress Feedback**: Real-time operation status
- **Error Reporting**: Clear error messages and suggestions
- **Option Flexibility**: Comprehensive flag and argument support
- **OAuth Support**: Secure token management for CLI operations
- **Interactive Prompts**: User-friendly OAuth authorization flow

### 5. Import/Export System

#### BibTeX Integration
- **Import Support**: Parse BibTeX files into YAML structure
- **Export Generation**: Create BibTeX from YAML publications
- **Metadata Preservation**: Maintain all bibliographic information
- **Category Mapping**: Intelligent categorization of imported entries

#### ORCID Import
- **Profile Synchronization**: Import complete ORCID work list
- **Incremental Updates**: Merge new publications with existing data
- **Backup Creation**: Automatic backup before import operations
- **Error Recovery**: Continue import despite individual work failures

#### Data Export
- **YAML Export**: Download structured data files
- **PDF Generation**: Compiled CV in multiple formats
- **BibTeX Export**: Publication list for citation managers

### 6. Template System

#### Available Templates
- **Academic US**: Standard US academic format
- **Academic UK**: UK/European academic format
- **Promotion**: Specialized promotion/tenure format

#### Template Features
- **Conditional Sections**: Show/hide sections based on data
- **Custom Macros**: LaTeX macros for consistent formatting
- **Flexible Layout**: Configurable section ordering
- **Rich Formatting**: Support for special characters, math symbols

### 7. Data Validation and Quality

#### YAML Validation
- **Schema Checking**: Ensure required fields are present
- **Type Validation**: Verify data types and formats
- **Cross-reference Validation**: Check internal data consistency
- **Error Reporting**: Detailed validation error messages

#### Publication Quality Checks
- **Duplicate Detection**: Identify potential duplicate entries
- **Metadata Completeness**: Warn about missing important fields
- **Format Consistency**: Standardize author names, venues
- **Link Validation**: Check DOI and URL accessibility

### 8. File Management

#### Data Organization
```
cv-data/
├── personal.yaml      # Personal information and contact details
├── publications.yaml  # All publications organized by category
├── grants.yaml       # Grants, awards, and funding
├── teaching.yaml     # Teaching experience and supervision
├── service.yaml      # Editorial activities and service
└── talks.yaml        # Presentations and invited talks
```

#### Output Management
```
output/
├── cv-academic-us.tex    # Generated LaTeX files
├── cv-academic-us.pdf    # Compiled PDF outputs
├── publications.bib      # BibTeX bibliography
└── backups/             # Automatic backups
```

#### Backup System
- **Automatic Backups**: Before major operations (imports, updates)
- **Version Tracking**: Timestamped backup files
- **Recovery Support**: Easy restoration from backups

### 9. Developer Features

#### Package Structure
- **Pip Installable**: Standard Python package with setup.py
- **Modular Design**: Separate modules for different functionality
- **Extension Points**: Plugin system for custom templates
- **Test Suite**: Comprehensive testing framework

#### API Design
- **Clear Interfaces**: Well-defined function signatures
- **Error Handling**: Consistent exception handling patterns
- **Documentation**: Comprehensive docstrings and comments
- **Type Hints**: Full type annotation for better IDE support

## Technical Specifications

### Dependencies
- **Flask**: Web framework for user interface
- **Jinja2**: Template engine for LaTeX generation
- **Click**: Command-line interface framework
- **PyYAML**: YAML file parsing and generation
- **WTForms**: Web form handling and validation
- **Requests**: HTTP client for ORCID API integration

### System Requirements
- Python 3.8+
- LaTeX distribution (for PDF generation)
- Modern web browser (for web interface)
- Internet connection (for ORCID imports)

### Performance Characteristics
- **Fast YAML Processing**: Efficient data loading and saving
- **Responsive Web Interface**: Quick page loads and form submissions
- **Scalable Publication Lists**: Handles hundreds of publications efficiently
- **Reliable PDF Generation**: Robust LaTeX compilation

## Current Limitations

### ORCID Integration
- **Read-only Access**: Can only import from ORCID, cannot publish to ORCID
- **Public API Only**: Limited to publicly visible ORCID works
- **No OAuth**: Currently uses public API without authentication

### Template System
- **LaTeX Only**: No support for other output formats (HTML, Word)
- **Limited Templates**: Only three academic templates available
- **Static Configuration**: No dynamic template customization

### Web Interface
- **Local Only**: No multi-user or cloud deployment support
- **Basic Editor**: No rich text editing for descriptions
- **Limited Preview**: No live PDF preview in web interface

## Upcoming Features (Based on Plan)

### OAuth 2.0 Integration
- **ORCID Member API**: Full read/write access to ORCID profiles
- **Publication Sync**: Two-way synchronization with ORCID
- **Secure Authentication**: OAuth 2.0 token management

### Enhanced Web Interface
- **Live Preview**: Real-time CV preview in web browser
- **Rich Editing**: WYSIWYG editors for text fields
- **Batch Operations**: Bulk import/export functionality

### Extended Template Support
- **More Formats**: Additional academic and industry templates
- **Template Editor**: Visual template customization
- **Custom Macros**: User-defined LaTeX macros

## Usage Examples

### Basic Workflow
```bash
# Initialize new CV
cv-manager init my-cv
cd my-cv

# Import publications from ORCID
cv-manager import-orcid 0000-0000-0000-0000

# Edit via web interface
cv-manager serve

# Generate CV
cv-manager build --template academic-us --format pdf
```

### OAuth Workflow ⭐ NEW
```bash
# Set OAuth credentials
export ORCID_CLIENT_ID="your-client-id"
export ORCID_CLIENT_SECRET="your-client-secret"

# Connect ORCID profile with OAuth
cv-manager orcid-connect 0000-0000-0000-0000

# Check connection status
cv-manager orcid-status

# Sync publications to ORCID (dry run first)
cv-manager orcid-sync 0000-0000-0000-0000 --dry-run
cv-manager orcid-sync 0000-0000-0000-0000
```

### Web Interface OAuth
```bash
# Start web server
cv-manager serve

# Navigate to OAuth pages:
# http://localhost:5000/orcid/connect   - Connect ORCID
# http://localhost:5000/orcid/sync     - Sync publications
# http://localhost:5000/publications   - View publications
```

### Advanced Import
```bash
# Import with specific options
cv-manager import-orcid 0000-0000-0000-0000 \
  --merge \
  --backup \
  --sandbox

# Import BibTeX file
cv-manager import-bibtex publications.bib --merge
```

### Validation and Export
```bash
# Validate all data
cv-manager validate

# Export publications as BibTeX
cv-manager export --format bibtex

# Download YAML data
curl http://localhost:5000/download/publications.yaml
```

This comprehensive system provides a modern, maintainable approach to CV management with strong integration capabilities and room for future enhancements.