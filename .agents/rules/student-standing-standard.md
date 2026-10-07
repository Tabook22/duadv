# Dhofar University Academic Standing & Transcript Rules

1. **Academic Standing Extraction Standard (Non-Negotiable)**:
   - When parsing Dhofar University student transcripts, NEVER default student status to 'Normal / Good Standing'.
   - Always extract the chronological semester history and determine the latest evaluated term's standing.
   - Precedence: Second Strict Probation > Second Probation > First Probation > Academic Probation Removal > Normal / Good Standing.

2. **Visual Consistency & Badge Hierarchy**:
   - Strict Probation / Second Strict Probation: Red badge with warning icon (bg-danger text-white) and alert banner on student profile.
   - Second Probation: Orange badge with icon (#fd7e14).
   - First Probation: Yellow badge with icon (bg-warning text-dark).
   - Academic Probation Removal: Cyan / Info badge with shield icon (bg-info text-dark).
   - Normal / Good Standing: Green badge with check icon (bg-success text-white).

3. **Dynamic Advisee List Management**:
   - The user frequently updates advisees by uploading a ZIP archive of PDF transcripts or pasting table HTML.
   - Both 'Merge' (add/update) and 'Replace' (clear and set new roster) modes must be preserved.
   - When new transcripts are added or existing ones replaced, all student profiles, study plans, dashboard metrics, and status badges must automatically reflect the updated records without manual schema changes.

4. **Students at Risk & Report Formatting Standard (PERMANENT RULE)**:
   - Advisees with active academic probation (Strict, Second, First) or Cumulative GPA < 65.0% are categorized as "Students at Risk".
   - Official reports in Excel (`.xlsx`), PDF, and HTML must adhere strictly to:
     - Header: Navy (`#1E3A8A`) DU / College / Department title banner + Slate (`#334155`) subtitle banner + Advisor metadata line.
     - Grouped tables with category-specific colors: Strict Probation (`#DC2626`), Second Probation (`#EA580C`), First Probation (`#D97706`), Pre-Probation Warning (`#475569`).
     - Footer: `OFFICIAL VERIFICATION & SIGNATURES` banner + `Academic Advisor: Dr. Nasser Tabook` + `Signature: ______________`.
     - Excel export must feature both Sheet 1 (Executive styled report) and Sheet 2 (Flat filterable dataset).
   - This standard is invariant across all future advisee roster changes, additions, and deletions.

