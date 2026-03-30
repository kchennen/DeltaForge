"""Text diff engine supporting line, word, and character comparison.

Uses difflib.SequenceMatcher for line-level diffs and diff-match-patch for
word and character granularity.
"""

from __future__ import annotations

import difflib
from dataclasses import dataclass, field
from enum import Enum

import diff_match_patch as dmp_module


class DiffType(Enum):
    """Type of difference for a chunk of text."""

    EQUAL = "equal"
    INSERT = "insert"
    DELETE = "delete"
    REPLACE = "replace"


# Froze dataclass for immutability and hashability, which can be useful for caching results.
@dataclass(frozen=True)
class DiffChunk:
    """A contiguous block of diff output.

    Attributes:
        type: The kind of change (equal, insert, delete, replace).
        old_lines: Lines from the original (left) text. Empty for inserts.
        new_lines: Lines from the modified (right) text. Empty for deletes.
        old_start: 0-based starting line number in the original text.
        new_start: 0-based starting line number in the modified text.
    """

    type: DiffType
    old_lines: list[str] = field(default_factory=list)
    new_lines: list[str] = field(default_factory=list)
    old_start: int = 0  # 0-based to match Python difflib's indexing
    new_start: int = 0


def diff_text(
    text_a: str,
    text_b: str,
    *,
    granularity: str = "line",
) -> list[DiffChunk]:
    """Compute the diff between two text strings.

    Args:
        text_a: Original (left) text.
        text_b: Modified (right) text.
        granularity: Diff granularity — 'line', 'word', or 'char'.
            Note: diff_text always uses line-level comparison.
            Word/char granularity is validated here but handled by diff_inline()
            at the rendering layer (for sub-line highlighting in REPLACE chunks).

    Returns:
        A list of DiffChunk objects representing the differences.

    Raises:
        ValueError: If an unsupported granularity is specified.
    """
    valid = ("line", "word", "char")
    if granularity not in valid:
        msg = f"Unsupported granularity: {granularity!r}. Must be one of {valid}."
        raise ValueError(msg)

    return _diff_lines(text_a, text_b)


def _diff_lines(text_a: str, text_b: str) -> list[DiffChunk]:
    """Compute a line-level diff using difflib.SequenceMatcher."""
    lines_a = text_a.splitlines(keepends=True)
    lines_b = text_b.splitlines(keepends=True)

    matcher = difflib.SequenceMatcher(None, lines_a, lines_b)
    chunks: list[DiffChunk] = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            chunks.append(
                DiffChunk(
                    type=DiffType.EQUAL,
                    old_lines=lines_a[i1:i2],
                    new_lines=lines_b[j1:j2],
                    old_start=i1,
                    new_start=j1,
                )
            )
        elif tag == "replace":
            chunks.append(
                DiffChunk(
                    type=DiffType.REPLACE,
                    old_lines=lines_a[i1:i2],
                    new_lines=lines_b[j1:j2],
                    old_start=i1,
                    new_start=j1,
                )
            )
        elif tag == "insert":
            chunks.append(
                DiffChunk(
                    type=DiffType.INSERT,
                    old_lines=[],
                    new_lines=lines_b[j1:j2],
                    old_start=i1,
                    new_start=j1,
                )
            )
        elif tag == "delete":
            chunks.append(
                DiffChunk(
                    type=DiffType.DELETE,
                    old_lines=lines_a[i1:i2],
                    new_lines=[],
                    old_start=i1,
                    new_start=j1,
                )
            )

    return chunks


def diff_stats(chunks: list[DiffChunk]) -> dict[str, int]:
    """Compute summary statistics from a list of diff chunks.

    Returns:
        A dict with keys: lines_added, lines_removed, lines_unchanged.
    """
    added = 0
    removed = 0
    unchanged = 0

    for chunk in chunks:
        if chunk.type == DiffType.EQUAL:
            unchanged += len(chunk.old_lines)
        elif chunk.type == DiffType.INSERT:
            added += len(chunk.new_lines)
        elif chunk.type == DiffType.DELETE:
            removed += len(chunk.old_lines)
        elif chunk.type == DiffType.REPLACE:
            removed += len(chunk.old_lines)
            added += len(chunk.new_lines)

    return {
        "lines_added": added,
        "lines_removed": removed,
        "lines_unchanged": unchanged,
    }


@dataclass(frozen=True)
class InlineSegment:
    """A segment within a line for word/char-level highlighting.

    Used to mark sub-line changes when granularity is 'word' or 'char'.
    """

    text: str
    type: DiffType


def diff_inline(
    text_a: str,
    text_b: str,
    *,
    granularity: str = "word",
) -> list[InlineSegment]:
    """Compute a fine-grained inline diff using diff-match-patch.

    Returns a flat list of InlineSegment objects representing sub-line
    differences at word or character level.

    Args:
        text_a: Original text.
        text_b: Modified text.
        granularity: 'word' or 'char'.

    Returns:
        A list of InlineSegment objects.
    """
    dmp = dmp_module.diff_match_patch()
    diffs = dmp.diff_main(text_a, text_b)

    if granularity == "word":
        dmp.diff_cleanupSemantic(diffs)
    else:
        dmp.diff_cleanupEfficiency(diffs)

    segments: list[InlineSegment] = []
    type_map = {0: DiffType.EQUAL, -1: DiffType.DELETE, 1: DiffType.INSERT}

    for op, text in diffs:
        if text:
            segments.append(InlineSegment(text=text, type=type_map[op]))

    return segments


def get_line_inline_segments(
    old_line: str,
    new_line: str,
    *,
    granularity: str = "word",
) -> tuple[list[InlineSegment], list[InlineSegment]]:
    """Get inline diff segments for a single pair of lines.

    Returns two lists of segments: one for the old line (with DELETE highlights)
    and one for the new line (with INSERT highlights).
    """
    segments = diff_inline(old_line, new_line, granularity=granularity)

    old_segments: list[InlineSegment] = []
    new_segments: list[InlineSegment] = []

    for seg in segments:
        if seg.type == DiffType.EQUAL:
            old_segments.append(seg)
            new_segments.append(seg)
        elif seg.type == DiffType.DELETE:
            old_segments.append(seg)
        elif seg.type == DiffType.INSERT:
            new_segments.append(seg)

    return old_segments, new_segments
