#!/usr/bin/env python3
"""
CLI Utility: Batch Import Transcripts ZIP
Extracts student transcript PDFs, performs chronological academic standing extraction,
and updates or replaces the advisee roster in data/students.json.
"""

import argparse
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.utils import import_transcripts_from_zip

def main():
    parser = argparse.ArgumentParser(description="Import student transcript PDFs from a ZIP archive into DU Student Manager.")
    parser.add_argument("--zip", required=True, help="Path to the ZIP file containing student transcript PDFs.")
    parser.add_argument("--replace", action="store_true", help="Replace entire existing student roster instead of merging.")
    parser.add_argument("--output", default=os.path.join(PROJECT_ROOT, "data", "students.json"), help="Output path for students.json")
    parser.add_argument("--transcripts-dir", default=os.path.join(PROJECT_ROOT, "data", "transcripts"), help="Directory to save extracted transcript PDFs")

    args = parser.parse_args()

    if not os.path.exists(args.zip):
        print(f"Error: ZIP file not found: {args.zip}")
        sys.exit(1)

    print(f"Opening ZIP archive: {args.zip}")
    mode_str = "REPLACE ROSTER" if args.replace else "MERGE WITH EXISTING ROSTER"
    print(f"Mode: {mode_str}")
    
    res = import_transcripts_from_zip(
        zip_source=args.zip,
        replace_roster=args.replace,
        transcripts_dir=args.transcripts_dir,
        json_path=args.output
    )

    if res.get("status") == "success":
        print("\n=== IMPORT SUCCESSFUL ===")
        print(f"Imported Transcripts : {res['imported_count']}")
        print(f"Total Active Advisees: {res['total_count']}")
        print(f"Mode                 : {res['mode']}")
        print("\nAcademic Standing Breakdown:")
        print(f"  - Strict Probation : {res['stats']['strict']}")
        print(f"  - On Probation     : {res['stats']['probation']}")
        print(f"  - Probation Cleared: {res['stats']['cleared']}")
        print(f"  - Good Standing    : {res['stats']['good_standing']}")
        print(f"\nSaved records to: {args.output}")
    else:
        print(f"\nImport Failed: {res.get('message')}")
        sys.exit(1)

if __name__ == "__main__":
    main()
