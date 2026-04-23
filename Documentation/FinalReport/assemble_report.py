"""Assemble the iWear final report.

Concatenates the chapter markdown files in this directory into a single
combined markdown file and then generates a Word .docx using the existing
``Documentation/md_to_docx.py`` converter.

Run from the project root::

    python Documentation/FinalReport/assemble_report.py

The combined markdown is written to ``Documentation/FinalReport/iWear_Final_Report.md``
and the Word file to ``Documentation/FinalReport/iWear_Final_Report.docx``.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / "Documentation"))

from md_to_docx import md_to_docx  # noqa: E402

# Chapters in display order. Files that don't exist are skipped silently so
# the script remains useful while the report is still being drafted.
CHAPTERS = [
    HERE / "00_front_matter.md",
    HERE / "01_introduction.md",
    HERE / "02_background_and_lit_review.md",
    HERE / "03_requirements_analysis.md",
    HERE / "04_system_design.md",
    HERE / "05_implementation.md",
    HERE / "06_testing.md",
    HERE / "07_results_and_discussion.md",
    HERE / "08_conclusion_and_future_work.md",
    HERE / "09_references.md",
    HERE / "appendix_A_individual" / "member1.md",
    HERE / "appendix_A_individual" / "member2.md",
    HERE / "appendix_A_individual" / "member3.md",
    HERE / "appendix_A_individual" / "member4.md",
    HERE / "appendix_B_project_process.md",
    HERE / "appendix_C_code_snippets.md",
]

OUT_MD = HERE / "iWear_Final_Report.md"
OUT_DOCX = HERE / "iWear_Final_Report.docx"


def assemble() -> None:
    parts: list[str] = []
    for path in CHAPTERS:
        if not path.exists():
            print(f"  - skipping missing chapter: {path.name}")
            continue
        text = path.read_text(encoding="utf-8").rstrip()
        parts.append(text)
        parts.append("\n\n")
    combined = "\n".join(parts).strip() + "\n"
    OUT_MD.write_text(combined, encoding="utf-8")
    word_count = len(combined.split())
    print(f"Combined markdown: {OUT_MD}  ({word_count} words)")

    md_to_docx(OUT_MD, OUT_DOCX)
    print(f"Generated Word doc: {OUT_DOCX}")


if __name__ == "__main__":
    assemble()
