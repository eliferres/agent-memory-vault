"""Tests for vault_lint.

Every case builds a real vault on disk and runs the real checks on it,
including one differential test against the skeleton this repo ships:
the shipped vault must always pass its own linter.
"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

import vault_lint  # noqa: E402


CHECKPOINT_OK = """# Checkpoint
## Objective
## State
## Decisions
## Open threads
## Gotchas
"""


def build_vault(root: Path, files: dict) -> Path:
    base = {
        "INDEX.md": "# Router\nSee [[prefs]] and [[OPERATING-CONTRACT]].\n",
        "system/OPERATING-CONTRACT.md": "Rules. Resume via [[LATEST-SESSION]].\n",
        "system/LATEST-SESSION.md": CHECKPOINT_OK,
        "memory/prefs.md": "---\ntype: memory\n---\nA fact.\n",
    }
    base.update(files)
    for rel, text in base.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return root


def run_checks(root: Path):
    notes = {p: p.read_text(encoding="utf-8") for p in sorted(root.rglob("*.md"))}
    homes = {p.stem.lower(): p for p in notes}
    return (
        vault_lint.check_links(notes, homes)
        + vault_lint.check_one_home(notes)
        + vault_lint.check_frontmatter(notes, root)
        + vault_lint.check_checkpoint(root)
    )


class VaultLintTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def test_shipped_skeleton_passes(self):
        # The real thing, end to end through the CLI: the vault this repo
        # ships must satisfy its own linter, exit code included.
        proc = subprocess.run(
            [sys.executable, str(REPO / "tools" / "vault_lint.py"), str(REPO / "vault")],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("PASS", proc.stdout)

    def test_minimal_vault_passes(self):
        self.assertEqual(run_checks(build_vault(self.root, {})), [])

    def test_broken_link_fails(self):
        build_vault(self.root, {"INDEX.md": "See [[nowhere]].\n"})
        self.assertTrue(any("[[nowhere]]" in f for f in run_checks(self.root)))

    def test_duplicate_home_fails(self):
        build_vault(self.root, {"projects/prefs.md": "---\ntype: project\n---\nCopy.\n"})
        self.assertTrue(any("duplicate home" in f for f in run_checks(self.root)))

    def test_missing_type_fails(self):
        build_vault(self.root, {"memory/untyped.md": "No frontmatter here.\n"})
        fails = run_checks(self.root)
        self.assertTrue(any("untyped" in f and "frontmatter" in f for f in fails))

    def test_checkpoint_missing_section_fails(self):
        broken = CHECKPOINT_OK.replace("## Gotchas\n", "")
        build_vault(self.root, {"system/LATEST-SESSION.md": broken})
        self.assertTrue(any("Gotchas" in f for f in run_checks(self.root)))

    def test_fenced_example_links_ignored(self):
        example = "Link syntax:\n```\n[[not-a-real-note]]\n```\n"
        build_vault(self.root, {"memory/prefs.md": "---\ntype: memory\n---\n" + example})
        self.assertEqual(run_checks(self.root), [])

    def test_orphan_warns_but_does_not_fail(self):
        build_vault(self.root, {"memory/lonely.md": "---\ntype: memory\n---\nUnlinked.\n"})
        notes = {p: p.read_text(encoding="utf-8") for p in sorted(self.root.rglob("*.md"))}
        homes = {p.stem.lower(): p for p in notes}
        self.assertEqual(run_checks(self.root), [])
        self.assertTrue(any("lonely" in w for w in vault_lint.warn_orphans(notes, homes)))


if __name__ == "__main__":
    unittest.main()
