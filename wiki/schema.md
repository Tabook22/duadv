---
title: Dhofar University Academic Advising Wiki Schema
type: schema
version: 1.0.0
last_updated: 2026-10-08
maintainer: LLM Agent & Dr. Nasser Tabook
---

# Dhofar University Academic Advising Wiki Schema

This document defines the constitution, naming conventions, directory structure,
and workflows for the Dhofar University Academic Advising LLM Wiki.
Inspired by the Andrej Karpathy LLM Wiki pattern, this wiki serves as a persistent,
compounding Second Brain for academic advising.

## 1. Directory Structure

- `schema.md`: This file. The constitution and operational rules.
- `index.md`: Content-oriented catalog of all pages with one-line summaries and wikilinks.
- `log.md`: Chronological append-only audit trail (`## [YYYY-MM-DD] action | Title`).
- `raw/`: Immutable source documents (regulations, study plans, student transcripts).
- `sources/`: Extracted summaries and key takeaways of raw sources.
- `concepts/`: University bylaws, grading policies, probation thresholds, and credit rules.
- `programs/`: Degree curricula, graduation requirements, and semester-by-semester roadmaps.
- `courses/`: Course entity pages with credit hours, category, prerequisites, and unlocks.
- `students/`: Individual student advising dossiers tracking term chronologies, deficiencies, and recovery schedules.
- `synthesis/`: Compounding cross-document analyses (e.g. Students at Risk, Prerequisite Graph).

## 2. Page Conventions

1. **Format**: Standard GitHub Flavored Markdown with YAML frontmatter.
2. **Wikilinks**: Use Obsidian-standard `[[Page_Name]]` or `[[Page_Name|Display Text]]`.
3. **Immutability of Raw**: The `raw/` directory is never modified; it is the ground truth.
4. **Compounding Artifact**: When a new source or transcript is ingested, existing entity pages are updated rather than creating duplicate fragments.

## 3. Workflows

- **Ingest**: Extract key data from a raw source, create/update entity pages in `sources/`, `students/`, `courses/`, update `index.md`, and append an entry to `log.md`.
- **Query**: Read directly from the compiled wiki pages; file significant answers back into `synthesis/`.
- **Lint**: Regularly check for broken wikilinks, orphan pages, or out-of-date standings.
