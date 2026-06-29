#!/usr/bin/env python3
"""Validate a spec.yml against the required top-level keys. Exit non-zero on any gap."""
import sys, yaml

REQUIRED = ["journal","article_type","word_limits","abstract","references",
            "figures","tables","supplementary","sections","statements",
            "cover_letter","forms","file_formats","flagged"]

def main(path):
    with open(path) as f:
        spec = yaml.safe_load(f) or {}
    missing = [k for k in REQUIRED if k not in spec]
    if missing:
        print(f"INVALID: missing keys: {', '.join(missing)}")
        return 1
    flagged = spec.get("flagged") or []
    if flagged:
        print(f"VALID with {len(flagged)} flagged requirement(s) for user confirmation.")
    else:
        print("VALID")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
