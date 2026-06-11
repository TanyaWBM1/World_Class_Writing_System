#!/usr/bin/env python3
"""
Validate research markdown files for locked World Class Writing System output contract.

Checks:
1. Required extraction block headings exist at end of file.
2. Blocks appear in locked order:
   RULESET_EXTRACT, OPERATOR_EXTRACT, FAILURE_MODE_EXTRACT, TEST_CASE_EXTRACT, LIBRARY_EXTRACT
3. RULESET / OPERATOR / FAILURE_MODE / TEST_CASE entries are atomic list items with stable IDs.
4. LIBRARY_EXTRACT contains at least one top-level library bullet.
5. File contains at least one H2 (##) or H3 (###) heading before extraction blocks.

Usage:
    python validate_research_file.py path/to/file.md [path/to/file2.md ...]
Exit code 0 if all files pass, 1 otherwise.
"""
from __future__ import annotations
import re
import sys
from pathlib import Path

BLOCKS = [
    "RULESET_EXTRACT",
    "OPERATOR_EXTRACT",
    "FAILURE_MODE_EXTRACT",
    "TEST_CASE_EXTRACT",
    "LIBRARY_EXTRACT",
]

ID_PATTERNS = {
    "RULESET_EXTRACT": re.compile(r"^- (RULE[-_A-Z0-9]+):\s+.+"),
    "OPERATOR_EXTRACT": re.compile(r"^- (OP[-_A-Z0-9]+):\s+.+"),
    "FAILURE_MODE_EXTRACT": re.compile(r"^- (FM[-_A-Z0-9]+):\s+.+"),
    "TEST_CASE_EXTRACT": re.compile(r"^- (TC[-_A-Z0-9]+):\s+.+"),
}

def extract_blocks(text: str) -> tuple[dict[str, str], list[str]]:
    found = {}
    errors = []
    positions = []
    for block in BLOCKS:
        m = re.search(rf"^## {re.escape(block)}\s*$", text, flags=re.M)
        if not m:
            errors.append(f"Missing block heading: ## {block}")
            continue
        positions.append((m.start(), block))
    if len(positions) != len(BLOCKS):
        return found, errors
    positions.sort()
    ordered = [b for _, b in positions]
    if ordered != BLOCKS:
        errors.append(f"Block order invalid: expected {BLOCKS}, found {ordered}")
    for i, (_, block) in enumerate(positions):
        start = positions[i][0]
        end = positions[i + 1][0] if i + 1 < len(positions) else len(text)
        found[block] = text[start:end].strip()
    return found, errors

def validate_atomic_block(block_name: str, content: str) -> list[str]:
    errors = []
    body_lines = [ln.rstrip() for ln in content.splitlines()[1:]]
    meaningful = [ln for ln in body_lines if ln.strip()]
    if not meaningful:
        return [f"{block_name} is empty"]
    if block_name == "LIBRARY_EXTRACT":
        top_level = [ln for ln in meaningful if re.match(r"^- [A-Za-z0-9_]+$", ln.strip())]
        if not top_level:
            errors.append("LIBRARY_EXTRACT needs at least one top-level library bullet like '- cadence_library'")
        return errors
    pattern = ID_PATTERNS[block_name]
    bad = [ln for ln in meaningful if ln.startswith("- ") and not pattern.match(ln)]
    if bad:
        errors.append(f"{block_name} contains non-atomic or non-ID entries: {bad[:5]}")
    ids = []
    for ln in meaningful:
        m = pattern.match(ln)
        if m:
            ids.append(m.group(1))
    if len(ids) != len(set(ids)):
        errors.append(f"{block_name} contains duplicate IDs")
    if not ids:
        errors.append(f"{block_name} has no valid ID-based entries")
    return errors

def validate_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    errors = []
    if "## " not in text and "### " not in text:
        errors.append("No H2/H3 headings found")
    blocks, block_errors = extract_blocks(text)
    errors.extend(block_errors)
    if blocks:
        # ensure extraction blocks are near file end
        last_heading = max(text.rfind(f"## {b}") for b in BLOCKS if f"## {b}" in text)
        tail = text[last_heading:]
        for heading in re.findall(r"^## .+$", tail, flags=re.M):
            if not any(heading == f"## {b}" for b in BLOCKS):
                errors.append(f"Unexpected H2 heading after extraction block start: {heading}")
        for name, content in blocks.items():
            errors.extend(validate_atomic_block(name, content))
    return errors

def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("Usage: python validate_research_file.py <file1.md> [file2.md ...]")
        return 1
    overall_errors = False
    for arg in argv[1:]:
        path = Path(arg)
        if not path.exists():
            overall_errors = True
            print(f"[FAIL] {path}: file not found")
            continue
        errors = validate_file(path)
        if errors:
            overall_errors = True
            print(f"[FAIL] {path}")
            for err in errors:
                print(f"  - {err}")
        else:
            print(f"[PASS] {path}")
    return 1 if overall_errors else 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
