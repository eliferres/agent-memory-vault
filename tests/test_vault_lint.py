"""Tests for vault_lint.

Every case builds a real vault on disk and runs the real checks on it,
including one differential test against the skeleton this repo ships:
the shipped vault must always pass its own linter. One further test
holds the README's quoted contract to CLAUDE.md.
"""

import difflib
import re
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
    homes = vault_lint.find_homes(notes)
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

    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(REPO / "tools" / "vault_lint.py"), *args],
            capture_output=True,
            text=True,
        )

    def test_shipped_skeleton_passes(self):
        # The real thing, end to end through the CLI: the vault this repo
        # ships must satisfy its own linter, exit code included.
        proc = self.run_cli(str(REPO / "vault"))
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("PASS", proc.stdout)

    def test_cli_exit_codes_clean_failure_and_usage(self):
        # 0 clean, 1 lint failures, 2 usage or input error, and the usage
        # error goes to stderr so a clean stdout still means a clean vault.
        build_vault(self.root, {})
        clean = self.run_cli(str(self.root))
        self.assertEqual(clean.returncode, 0, clean.stdout + clean.stderr)

        (self.root / "INDEX.md").write_text("See [[nowhere]].\n", encoding="utf-8")
        failing = self.run_cli(str(self.root))
        self.assertEqual(failing.returncode, 1, failing.stdout + failing.stderr)

        usage = self.run_cli(str(self.root / "not-a-vault"))
        self.assertEqual(usage.returncode, 2, usage.stdout + usage.stderr)
        self.assertEqual(usage.stdout, "")
        self.assertIn("no such directory", usage.stderr)

    def test_minimal_vault_passes(self):
        self.assertEqual(run_checks(build_vault(self.root, {})), [])

    def test_broken_link_fails(self):
        build_vault(self.root, {"INDEX.md": "See [[nowhere]].\n"})
        self.assertTrue(any("[[nowhere]]" in f for f in run_checks(self.root)))

    def test_duplicate_home_fails(self):
        build_vault(self.root, {"projects/prefs.md": "---\ntype: project\n---\nCopy.\n"})
        self.assertTrue(any("duplicate home" in f for f in run_checks(self.root)))

    def test_link_to_duplicated_name_fails_as_ambiguous(self):
        build_vault(self.root, {
            "memory/budget.md": "---\ntype: memory\n---\nOne.\n",
            "projects/budget.md": "---\ntype: project\n---\nTwo.\n",
            "INDEX.md": "See [[prefs]], [[OPERATING-CONTRACT]] and [[budget]].\n",
        })
        ambiguous = [f for f in run_checks(self.root) if "[[budget]]" in f]
        self.assertEqual(len(ambiguous), 1, ambiguous)
        self.assertIn("ambiguous", ambiguous[0])
        first = str(self.root / "memory" / "budget.md")
        second = str(self.root / "projects" / "budget.md")
        # Candidates are named in sorted order, whatever order the disk lists them.
        self.assertIn(f"{first}, {second}", ambiguous[0])

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
        homes = vault_lint.find_homes(notes)
        self.assertEqual(run_checks(self.root), [])
        self.assertTrue(any("lonely" in w for w in vault_lint.warn_orphans(notes, homes)))


class ContractBlockTest(unittest.TestCase):
    """The README quotes CLAUDE.md under a heading that says "verbatim"."""

    def test_readme_contract_block_matches_claude_md(self):
        readme = (REPO / "README.md").read_text(encoding="utf-8")
        contract = (REPO / "CLAUDE.md").read_text(encoding="utf-8")
        blocks = re.findall(r"^```markdown\n(.*?)^```$", readme, re.M | re.S)
        self.assertEqual(len(blocks), 1, "README should quote exactly one markdown block")
        if blocks[0] != contract:
            drift = "".join(
                difflib.unified_diff(
                    contract.splitlines(keepends=True),
                    blocks[0].splitlines(keepends=True),
                    fromfile="CLAUDE.md",
                    tofile="README.md contract block",
                )
            )
            self.fail("the README contract block has drifted from CLAUDE.md:\n" + drift)


if __name__ == "__main__":
    unittest.main()
