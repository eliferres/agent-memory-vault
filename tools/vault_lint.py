#!/usr/bin/env python3
"""Structural linter for a file-based agent-memory vault.

Enforces the four invariants that keep plain-file memory trustworthy:
every [[wikilink]] resolves, every topic has exactly one home, notes that
assert durable facts carry typed frontmatter, and the session checkpoint
is complete enough to restore a session at full depth.

Stdlib only. Exit 0 when clean, 1 on any failure.

Usage:
    python3 tools/vault_lint.py [vault-dir]
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Matches [[target]], [[target#section]], and [[target|shown text]].
WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
FENCED_BLOCK = re.compile(r"^(```|~~~).*?^\1\s*$", re.M | re.S)

# Notes in these folders assert durable facts, so each must declare what
# kind of fact it holds (a `type:` line in frontmatter).
TYPED_DIRS = {"memory", "projects", "people"}

# A checkpoint missing any of these sections cannot restore a session
# at depth, which defeats the point of writing one.
CHECKPOINT = "system/LATEST-SESSION.md"
CHECKPOINT_SECTIONS = ("Objective", "State", "Decisions", "Open threads", "Gotchas")


def prose_only(text: str) -> str:
    # Fenced code blocks hold example syntax, not live claims.
    return FENCED_BLOCK.sub("", text)


def check_links(notes: dict[Path, str], homes: dict[str, Path]) -> list[str]:
    fails = []
    for path, text in notes.items():
        for raw in WIKILINK.findall(prose_only(text)):
            target = raw.strip()
            if target.lower() not in homes:
                fails.append(f"{path}: [[{target}]] resolves to nothing")
    return fails


def check_one_home(notes: dict[Path, str]) -> list[str]:
    # Two files with the same name make every [[link]] to that name
    # ambiguous - the seed of a mirror. One topic, one home.
    seen: dict[str, Path] = {}
    fails = []
    for path in notes:
        stem = path.stem.lower()
        if stem in seen:
            fails.append(f"{path}: duplicate home for '{path.stem}' (also {seen[stem]})")
        else:
            seen[stem] = path
    return fails


def check_frontmatter(notes: dict[Path, str], root: Path) -> list[str]:
    fails = []
    for path, text in notes.items():
        rel = path.relative_to(root)
        if rel.parts[0] not in TYPED_DIRS:
            continue
        lines = text.splitlines()
        if not lines or lines[0].strip() != "---":
            fails.append(f"{path}: missing frontmatter (typed folder '{rel.parts[0]}')")
            continue
        head = []
        for line in lines[1:]:
            if line.strip() == "---":
                break
            head.append(line)
        if not any(line.startswith("type:") for line in head):
            fails.append(f"{path}: frontmatter has no 'type:' line")
    return fails


def check_checkpoint(root: Path) -> list[str]:
    path = root / CHECKPOINT
    if not path.is_file():
        return [f"{path}: checkpoint missing"]
    text = path.read_text(encoding="utf-8")
    headers = {h.strip() for h in re.findall(r"^#+\s+(.+)$", text, re.M)}
    return [
        f"{path}: checkpoint missing section '{name}'"
        for name in CHECKPOINT_SECTIONS
        if name not in headers
    ]


def warn_orphans(notes: dict[Path, str], homes: dict[str, Path]) -> list[str]:
    # Advisory only: a note nothing links to is invisible to the router,
    # but daily notes and the entry points are reachable by convention.
    referenced = {
        raw.strip().lower()
        for text in notes.values()
        for raw in WIKILINK.findall(prose_only(text))
    }
    exempt = {"index", "latest-session"}
    return [
        f"{path}: no note links here (unreachable from the router?)"
        for stem, path in sorted(homes.items())
        if stem not in referenced and stem not in exempt and path.parent.name != "daily"
    ]


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else "vault")
    if not root.is_dir():
        print(f"vault-lint: no such directory: {root}")
        return 1

    notes = {
        p: p.read_text(encoding="utf-8")
        for p in sorted(root.rglob("*.md"))
    }
    homes = {p.stem.lower(): p for p in notes}

    fails = (
        check_links(notes, homes)
        + check_one_home(notes)
        + check_frontmatter(notes, root)
        + check_checkpoint(root)
    )
    for line in fails:
        print(f"FAIL {line}")
    for line in warn_orphans(notes, homes):
        print(f"WARN {line}")

    links = sum(len(WIKILINK.findall(prose_only(t))) for t in notes.values())
    verdict = "FAIL" if fails else "PASS"
    print(f"{verdict}: {len(notes)} notes, {links} links, {len(fails)} failures")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
