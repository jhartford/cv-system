# CV Manager Examples - Promotion Template

This directory contains comprehensive example data files that demonstrate all features of the promotion template (`cv_manager/templates/promotion.j2`).

## Example Profile: Dr. Alexandra Chen

These files showcase a fictional Senior Lecturer in Computer Science at University of Manchester, demonstrating the complete range of academic achievements and activities suitable for a promotion application.

## Files and Features Demonstrated

### `personal.yaml`
- **Personal information**: Name, contact details, current position
- **Career progression**: Previous positions and career timeline
- **Education**: PhD and previous degrees with full details
- **Awards and recognition**: Academic and professional honors
- **Career breaks**: Demonstrates how to handle career interruptions

### `publications.yaml`
- **Journal papers**: High-impact publications with citations and impact factors
- **Conference papers**: Top-tier venue publications with acceptance rates
- **Preprints**: ArXiv submissions and early-stage work
- **Under review**: Work in progress with target venues
- **Full bibliometric data**: DOIs, citation counts, co-authors

### `grants.yaml`
- **Major fellowships**: UKRI Future Leaders Fellowship, RAEng Fellowship
- **Research grants**: Range of funding bodies (EPSRC, Wellcome, MRC, etc.)
- **Equipment grants**: Infrastructure and facility funding
- **Travel grants**: Conference and collaboration support
- **Grant status tracking**: Active, completed, pending applications
- **Role specification**: PI vs Co-I roles clearly indicated
- **Financial details**: Total amounts and UoM attributable amounts

### `teaching.yaml`
- **Current UoM teaching**: Module leadership, lecturing at UG/PG levels
- **External teaching**: Guest lectures, summer schools, tutorials
- **Curriculum innovation**: Educational development activities
- **Teaching assessments**: Student feedback and peer review
- **PhD examining**: Internal and external examiner roles
- **Student supervision**: PhD, Masters, and research interns
- **Supervision tracking**: Start/end dates, funding sources, thesis topics

### `service.yaml`
- **Department roles**: Leadership positions within institution
- **Conference reviewing**: Area chair and reviewer roles across venues
- **Journal reviewing**: Editorial service for major journals
- **Workshop organization**: Conference workshop leadership
- **Professional service**: Volunteer activities and committee membership
- **Editorial boards**: Associate editor and review editor roles
- **Funding panels**: Grant review and evaluation service
- **External committees**: National and international advisory roles

### `talks.yaml`
- **Invited talks**: Academic and professional conference presentations
- **Invited workshops**: Specialist workshop participation
- **Industry talks**: Corporate and commercial audience presentations
- **Seminars**: University and research institution visits
- **Conference presentations**: Contributed talks at major venues
- **Keynotes and panels**: High-profile speaking engagements

### `knowledge_transfer.yaml` (Section C: Academic Enterprise and Knowledge Transfer)
- **External lectures**: Professional and policy audience presentations
- **Executive education**: Business school and professional development
- **Consultancy**: Industry advisory and research collaboration
- **Policy advisory**: Government and regulatory body engagement
- **Intellectual property**: Patents, software licenses, and commercialization
- **Enterprise leadership**: Startup and innovation hub involvement
- **Capital raising**: Major funding initiatives and partnerships
- **Community engagement**: Public outreach and societal impact

### `public_engagement.yaml` (Section D: Service and Leadership - Public Engagement)
- **Blog posts**: Popular science writing across platforms
- **Social media**: Professional presence and science communication
- **Podcasts**: Technical and general audience appearances
- **Media interviews**: Television, radio, and print coverage
- **Public talks**: Science festivals and community presentations
- **Online courses**: MOOC development and delivery
- **Educational videos**: YouTube and social media content
- **School engagement**: STEM education and outreach programs

## University of Manchester Promotion Template Structure

The examples follow the correct UoM promotion format:

### A. Research and academic/professional standing
- Publications (journal, conference, preprints/under review)
- Details of grants awarded
- Details of fellowships awarded
- Lectures and conference activity (invited talks, workshops)
- Conference area chair service
- Conference reviewing
- Journal reviewing

### B. Teaching and learning
- Current and previous teaching duties (UoM only)
- Innovation; curriculum/assessment development
- External assessments of teaching ability
- Teaching/assessment outside UoM
- Internal/External PhD Examiner
- Supervision of research students

### C. Academic Enterprise and Knowledge Transfer
- External lectures and contributions to professional conferences
- Executive education
- Consultancy
- Policy advisory
- Creation and development of intellectual property
- Enterprise leadership
- Capital raising
- Community engagement

### D. Service and Leadership
- Industry engagement
- Department service
- Conference/workshop organization
- Professional service
- Academic seminars and departmental talks
- Engagement with the public and/or end-users of research

## Using These Examples

### Option 1: Test the Examples Directly

1. **Create a new CV project with the example data**:
   ```bash
   # Navigate to a directory where you want to create the test CV
   cd /path/to/your/workspace

   # Initialize a new CV project
   cv-manager init "Alexandra Chen Example"
   cd "Alexandra Chen Example"

   # Copy the example YAML files
   cp /path/to/cv-system/examples/*.yaml data/

   # Build the CV
   cv-manager build --template promotion
   ```

2. **View the generated CV**:
   ```bash
   # The CV will be generated as output/cv-promotion.pdf
   open output/cv-promotion.pdf  # macOS
   # or
   xdg-open output/cv-promotion.pdf  # Linux
   ```

### Option 2: Use Examples as Templates for Your Own CV

1. **Copy specific sections to your existing CV project**:
   ```bash
   # Navigate to your existing CV directory
   cd /path/to/your/cv/project

   # Copy individual files or sections as needed
   cp /path/to/cv-system/examples/public_engagement.yaml data/
   cp /path/to/cv-system/examples/knowledge_transfer.yaml data/

   # Or copy specific sections from example files to your existing files
   # Edit the YAML files to replace example data with your information
   ```

2. **Customize the content**: Replace all fictional details with your actual information

3. **Build your updated CV**:
   ```bash
   cv-manager build --template promotion
   ```

### Option 3: Use as Reference While Building Your Own

1. **Keep examples as reference**:
   ```bash
   # View example files while editing your own
   cat /path/to/cv-system/examples/grants.yaml
   cat /path/to/cv-system/examples/teaching.yaml
   ```

2. **Copy and adapt specific entries**: Use the example entries as templates for your own achievements

3. **Follow the same structure**: Ensure your YAML files follow the same field names and organization

### Quick Start Commands

```bash
# Clone or navigate to the cv-system repository
cd /Users/jason.hartford/Developer/Research/cv-system

# Create a test CV using the examples
cv-manager init "Test CV"
cd "Test CV"
cp ../examples/*.yaml data/
cv-manager build --template promotion

# View the result
open output/cv-promotion.pdf
```

### Troubleshooting

- **File not found errors**: Ensure you're in a properly initialized CV directory (`cv-manager init` creates the correct structure)
- **Template errors**: Check YAML syntax using `python -m yaml` or an online YAML validator
- **Missing sections**: Not all sections are required - the template will skip empty sections gracefully
- **Build failures**: Check that all referenced files exist and have valid YAML syntax

## Key Features Demonstrated

- **Complete coverage**: Every section and subsection of the promotion template
- **Realistic data**: Authentic-looking academic profiles and achievements
- **Proper formatting**: Correct YAML structure and field usage
- **Conditional sections**: Examples of both required and optional template sections
- **Data relationships**: Consistent cross-references between files (e.g., supervision entries matching teaching experience)
- **Progression narrative**: Realistic career development and growing responsibility
- **Impact demonstration**: Quantified outcomes and achievements
- **Diversity and inclusion**: Representation of modern academic career paths

## Notes for Adaptation

- **Dates and timelines**: Ensure consistency across all files
- **Institutional affiliations**: Update all University of Manchester references
- **Financial amounts**: Adjust currency and scale as appropriate
- **Venue names**: Use actual conference and journal names for your field
- **Collaboration details**: Include real co-author and partner names
- **Impact metrics**: Use realistic citation counts and download numbers

This comprehensive example set provides a template for creating compelling promotion applications that showcase the full breadth of modern academic careers.