#!/usr/bin/env python3
"""
Backward-compatible alias for the docx extractor.

The tool now extracts BOTH comments and tracked changes. All logic lives in
extract_docx.py; this shim keeps the old command working:

    python extract_comments.py document.docx --format markdown -o out.md

For the full feature set (json output, --all), use extract_docx.py directly.
"""

from extract_docx import main

if __name__ == '__main__':
    main()
