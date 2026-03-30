"""Text processing utilities for pre-processing before diff comparison."""

from __future__ import annotations

import re


def lowercase(text: str) -> str:
    """Convert text to lowercase."""
    return text.lower()


def sort_lines(text: str) -> str:
    """Sort lines alphabetically, preserving trailing newline."""
    lines = text.splitlines()
    lines.sort()
    if text.endswith("\n"):
        return "\n".join(lines) + "\n"
    return "\n".join(lines)


def trim_whitespace(text: str) -> str:
    """Trim trailing whitespace from each line."""
    lines = text.splitlines(keepends=True)
    result = []
    for line in lines:
        end = "\n" if line.endswith("\n") else ""
        result.append(line.rstrip() + end)
    return "".join(result)


def normalize_line_breaks(text: str) -> str:
    """Normalize all line breaks to Unix-style (LF)."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def remove_blank_lines(text: str) -> str:
    """Remove all blank lines from text."""
    lines = text.splitlines(keepends=True)
    result = [line for line in lines if line.strip()]
    return "".join(result)


def squeeze_whitespace(text: str) -> str:
    """Collapse multiple consecutive whitespace chars to a single space per line."""
    lines = text.splitlines(keepends=True)
    result = []
    for line in lines:
        end = "\n" if line.endswith("\n") else ""
        squeezed = re.sub(r"[ \t]+", " ", line.strip())
        result.append(squeezed + end)
    return "".join(result)
