---
name: du-advisee-transcript-manager
description: >-
  Automates advisee student list extraction and batch academic transcript PDF
  export from Dhofar University (DU) Oracle APEX Student Information System (web.du.edu.om).
---

# Dhofar University Advisee & Transcript Manager

## Overview
Automates the retrieval of academic advisee student rosters and batch downloading of official individual student transcripts as high-resolution PDF documents from Dhofar University's Oracle APEX SIS (`web.du.edu.om`).

## Key Capabilities
- **Automated Oracle APEX Authentication**: Handles staff ID login (e.g. `001097`), form tokens, and session handshake.
- **Signed URL Resolution**: Automatically extracts signed APEX checksum links (`f?p=2023:400:...&cs=...` / `six-advisor-stu-lst-new`) from active sessions.
- **Roster Scraping**: Extracts Student ID (`SAP_CODE`), Student Full Name, and Academic Standing from `#advisee_data_panel`.
- **Headless Transcript PDF Exporter**: Clicks each advisee's `Transcript` link and renders/prints high-fidelity PDF documents via Chrome DevTools Protocol (`Page.printToPDF`).
- **Archive Bundler**: Packages all downloaded student transcript PDFs into a single ZIP file (`advisee_transcripts_pdf.zip`).

---

## Utility Script CLI

The skill provides a standalone CLI tool at `scripts/du_sync_cli.py`:

### 1. Sync Advisees Roster
```bash
python scripts/du_sync_cli.py sync --username "001097" --password "YOUR_PASSWORD" --output "data/students.json"
```

### 2. Download All Student Transcripts as PDF
```bash
python scripts/du_sync_cli.py transcripts --username "001097" --password "YOUR_PASSWORD" --output-dir "data/transcripts"
```

### 3. Full Sync & Transcript Batch Export (All in One)
```bash
python scripts/du_sync_cli.py all --username "001097" --password "YOUR_PASSWORD" --output-dir "data/transcripts"
```

### 4. Bundle Transcripts to ZIP
```bash
python scripts/du_sync_cli.py zip --transcripts-dir "data/transcripts" --output-zip "data/advisee_transcripts.zip"
```

---

## Technical Selectors & DOM Map

| Element / Action | Selector / Pattern |
|---|---|
| Login Username | `#P101_USERNAME` |
| Login Password | `#P101_PASSWORD` |
| Sign In Button | `button.t-Button--hot, #B22523398111720799` |
| Hamburger Navigation | `#t_Button_navControl, .t-Header-navBtn` |
| Advisor Student List | `//span[contains(text(), 'Advisor Student List')]/ancestor::a` / `a[href*='six-advisor-stu-lst-new']` |
| Advisee Table Container | `#advisee_data_panel, table.a-IRR-table` |
| Student ID Cell | `td[headers='SAP_CODE']` |
| Student Name Cell | `td[headers*='C54540470'] div` |
| Transcript Link | `.//a[contains(text(), 'Transcript')]` |

---

## Academic Standing & Probation Standard (CRITICAL)

Dhofar University uses official term-by-term academic standings calculated at the end of each major semester (Fall and Spring). Standings must NEVER default to "Normal / Good Standing" when parsing transcripts.

### Standing Hierarchy & Precedence
1. **Second Strict Probation / Third Strict Probation / Strict Probation**: Student is under critical academic dismissal warning. Restricted course load mandatory.
2. **Second Probation**: Second consecutive semester on probation.
3. **First Probation**: Initial academic warning/probation.
4. **Academic Probation Removal**: Student was previously on probation and has successfully raised their cumulative GPA above minimum thresholds in the latest semester.
5. **Normal / Good Standing / Very Good Standing**: Satisfactory academic status with no active probation.

### Chronological Term Sorting Algorithm
PDF transcripts contain multi-column layouts across pages. Terms must be sorted in true chronological sequence:
* **Academic terms**: `Fall YY-(YY+1)` (Season order: 1), `Spring (YY-1)-YY` (Season order: 2), `Summer (YY-1)-YY` (Season order: 3).
* **Foundation terms**: `Term1`, `Term2`, `Term3`.
* **APEX navigation elements** (e.g., `Change Semester [Fall 26-27]`) must be strictly ignored.
* The student's current status is determined by the **latest regular semester term** that calculated an academic standing.

### Visual Badge & Alert Specifications
All user interfaces, tables, and student profile pages must maintain these exact visual standards:
* 🔴 **Strict Probation**: `badge bg-danger text-white` with `fa-exclamation-triangle` icon. Banner alert on student detail profile.
* 🟠 **Second Probation**: `badge text-white` (`#fd7e14` orange) with `fa-exclamation-circle` icon.
* 🟡 **First Probation**: `badge bg-warning text-dark` with `fa-exclamation-circle` icon.
* 🔵 **Academic Probation Removal**: `badge bg-info text-dark` with `fa-shield-alt` icon.
* 🟢 **Normal / Good Standing**: `badge bg-success text-white` with `fa-check-circle` icon.
* **Filter Pills**: Provide quick 1-click filter pills on rosters (`All`, `Strict Probation`, `All On Probation`, `Probation Removal`, `Good Standing`).

---

## Batch ZIP Transcripts Import & Roster Management

Whenever students are added, removed, or a batch of transcripts is provided in a ZIP archive:

### Web Upload
* **Endpoint**: `POST /api/upload-transcripts-zip`
* Accepts a `.zip` archive containing transcript PDFs.
* Parameter `replace_roster=true`: Clears the current advisee list and sets the roster strictly to the students in the uploaded ZIP.
* Parameter `replace_roster=false`: Merges new student records into the existing roster and updates academic standings.

### CLI Import Utility
```bash
# Merge transcripts from ZIP into advisee roster
python scripts/import_transcripts_zip.py --zip path/to/transcripts.zip

# Replace entire advisee roster from ZIP
python scripts/import_transcripts_zip.py --zip path/to/transcripts.zip --replace
```

---

## Students at Risk Suite & Official Report Standard (MANDATORY)

The application features a dedicated **Students at Risk** advising suite (`/students-at-risk`) and multi-format report generator (`/students-at-risk/report`, PDF, and Excel). This layout and styling standard must be preserved for any future advisee rosters:

### 1. Risk Categorization Hierarchy
* **Category 1: Strict Probation** (Second / Third Strict Probation) — Critical risk (`#DC2626`). Max 12 credit hours, immediate repeating of F/D courses.
* **Category 2: Second Academic Probation** — High risk (`#EA580C`). Max 12–14 credits, prioritize prerequisite courses.
* **Category 3: First Academic Probation** — Moderate risk (`#D97706`). Academic counseling intervention, balanced study plan.
* **Category 4: Pre-Probation Warning** (GPA < 65.0%) — Monitoring stage (`#475569`).

### 2. Official Excel Report Specification (`.xlsx`)
Exported via `/students-at-risk/report/excel` (`generate_students_at_risk_report_excel` in `app/utils.py`):
* **Sheet 1: 'Students at Risk Report'**:
  - **Header Row 1**: Navy Blue (`#1E3A8A`), White Bold 12pt, centered across A–G:
    `DHOFAR UNIVERSITY  •  COLLEGE OF ARTS AND APPLIED SCIENCES  •  COMPUTER SCIENCES DEPARTMENT`
  - **Header Row 2**: Dark Slate (`#334155`), White Bold 10pt, centered across A–G:
    `ACADEMIC ADVISING REPORT: STUDENTS AT ACADEMIC RISK`
  - **Header Row 3**: White/Italic 9.5pt, centered with bottom border across A–G:
    `Advisor: Dr. Nasser Tabook   |   Generated: [Month DD, YYYY - HH:MM]   |   Policy: Cumulative GPA < 65.0%`
  - **KPI Cards**: Summary tiles for Total Advisees, Total At-Risk, Strict, Second, and First Probation.
  - **Category Banners**: Color-coded banners (`#DC2626`, `#EA580C`, `#D97706`, `#475569`) with detailed advisee columns and advisory recommendations.
  - **Footer Block**:
    - Row 1: `OFFICIAL VERIFICATION & SIGNATURES` (Light Slate `#E2E8F0`, Bold `#1E293B`, Left-aligned with indent)
    - Row 2: `Academic Advisor: Dr. Nasser Tabook` (Bold, Calibri 11pt, Black, Left-aligned with indent)
    - Row 3: `Signature: __________________________________________________` (Left-aligned)
* **Sheet 2: 'All At-Risk Data (Filterable)'**:
  - Flat table formatted with headers for Excel native filtering, sorting, and pivot table analysis.

### 3. PDF & Printable HTML Report Standards
* Both the web report (`/students-at-risk/report`) and PDF generator (`generate_students_at_risk_report_pdf`) adhere to identical Dhofar University branding, categorized rosters, academic regulation summaries, and the single Academic Advisor verification block.

---

## Common Pitfalls & Solutions

1. **Staff ID Format**: DU Staff IDs must retain leading zeros (e.g. `001097`, not `1097`).
2. **APEX Session State Protection (`cs` checksum)**: Do not manually construct target URLs without session checksums. Always extract the rendered signed `href` from the active session page DOM.
3. **PDF Printing Options**: Ensure `printBackground=True` and `preferCSSPageSize=True` in Chrome DevTools Protocol to preserve university transcript layouts and styles.
4. **Standing Persistence**: Every sync, table paste, or ZIP upload must update both `data/transcripts/<student_id>_transcript.pdf` and `data/students.json` with the enriched fields (`id`, `name`, `status`, `gpa`, `credits`, `year`, `program`, `advisor`).
5. **Roster Independence**: Changing, adding, or deleting students must never degrade or alter the reporting styles, badge color-coding, or header/footer standards.

