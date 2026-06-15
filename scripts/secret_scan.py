#!/usr/bin/env python3
"""Scan tracked files for secret-shaped values without printing the values."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


SECRET_PATTERNS = (
    re.compile(r"((?:ZYTE_API_KEY|BROWSERBASE_API_KEY|AWS_SECRET_ACCESS_KEY|AWS_SESSION_TOKEN|R2_SECRET|CRAWLERA_KEY)=)([^\\s]+)"),
    re.compile(r"(bm-verify=)[A-Za-z0-9_-]{12,}"),
    re.compile(r"(X-Amz-(?:Credential|Signature|Security-Token)=)([^\\s&]+)"),
    re.compile(r"(hcvalidate\\.perfdrive\\.com/\\?ssa=)([^\\s\"'<>]+)"),
)


def tracked_files(root: Path) -> list[Path]:
    output = subprocess.check_output(["git", "ls-files", "-z"], cwd=root)
    return [root / item.decode() for item in output.split(b"\0") if item]


def redact(line: str) -> str:
    redacted = line.rstrip("\\n")
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub(lambda match: match.group(1) + "REDACTED", redacted)
    return redacted


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    root = args.root.resolve()

    findings = 0
    for path in tracked_files(root):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except FileNotFoundError:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            if any(pattern.search(line) for pattern in SECRET_PATTERNS):
                findings += 1
                rel_path = path.relative_to(root)
                print(f"{rel_path}:{line_number}:{redact(line)}")

    if findings:
        print(f"secret scan found {findings} tracked-file finding(s)", file=sys.stderr)
        return 1
    print("secret scan clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
