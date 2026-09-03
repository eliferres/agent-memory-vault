# agent-memory-vault

Plain-file memory for an AI agent: a folder of Markdown notes the agent reads on demand, writes back to as it learns, and carries across context resets. One router note, one home per topic, newest wins. No database, no embeddings. A linter and CI check the structure. Works with Claude Code out of the box.

Portable to any harness that can read files.

![ci](https://github.com/eliferres/agent-memory-vault/actions/workflows/ci.yml/badge.svg)

![An agent session booting from the vault, routing a question to one note, writing back, and checkpointing](demo/flow.svg)

## Quick start

```bash
git clone https://github.com/eliferres/agent-memory-vault.git
cd agent-memory-vault
python3 tools/vault_lint.py vault    # zero dependencies, Python 3.9+
```

Open the folder in Claude Code and start working: the contract in
`CLAUDE.md` wires the vault in automatically. On any other harness,
paste `CLAUDE.md` into your system prompt and keep the vault layout.
Then replace the example notes with your own facts.

## The four ideas

**A small router, always loaded.** `vault/INDEX.md` is the only note
that is always in context. It maps topics to homes, so the agent finds
any fact without ever bulk-loading the vault. Full recall, near-zero
standing token cost. The router's size is the budget you protect.

**One home per topic.** Every fact lives in exactly one owner file;
other notes link to it instead of copying it. Mirrors are how file
memory rots: two copies drift, and the agent confidently quotes the
stale one.

**Newest wins.** When notes disagree, the newer line is true and the
older one is a bug to fix on sight. Conflicts get resolved, never
averaged.

**Checkpoint, then rehydrate.** Before a session ends or the context
fills, the agent rewrites `vault/system/LATEST-SESSION.md`: state,
decisions with their why, dead ends, next steps. The next session reads
it in full and continues as if nothing was lost.

## The contract, verbatim

This is the entire wiring, copied from `CLAUDE.md` (that file is the
source of truth):

```markdown
# Memory contract

You have a persistent file-based memory: the vault in `vault/`.

**Boot.** At session start, read `vault/INDEX.md` and nothing else. If
you are resuming earlier work, also read `vault/system/LATEST-SESSION.md`
in full before doing anything else.

**Read.** Route through the INDEX table to the one home for the topic,
and read only what the task needs. Never bulk-load the vault. If two
notes disagree, the newer line is true; fix or retire the older one.

**Write.** The moment you learn a durable fact, write it to its owner
file and add a one-line receipt to today's note in `vault/daily/`. Use
absolute dates. One home per topic: update the owner, never copy a fact
into a second note. When the user corrects you, update the owner in
place and record the ruling with its why in `vault/memory/decisions.md`.
New topic: create its home and add an INDEX row, same session.

**Checkpoint.** At session end, or before you hit a context limit,
rewrite `vault/system/LATEST-SESSION.md` following the section hints in
that file. Write it for a reader with zero context.

**Verify.** After structural changes, run
`python3 tools/vault_lint.py vault` and fix anything it reports.

The full rules live in `vault/system/OPERATING-CONTRACT.md`. Using this
skeleton outside Claude Code: paste this file into your harness's system
prompt and keep the same vault layout.
```

## What is in the box

| Path | Role |
|---|---|
| `vault/INDEX.md` | The router. Always loaded, deliberately small. |
| `vault/system/OPERATING-CONTRACT.md` | The full read/write/lifecycle rules. |
| `vault/system/LATEST-SESSION.md` | The checkpoint, with section-by-section hints. |
| `vault/memory/` `projects/` `people/` | Typed owner files, one worked example each. |
| `vault/daily/` | Daily receipt notes, the audit trail. |
| `CLAUDE.md` | The contract Claude Code auto-loads. |
| `tools/vault_lint.py` | Structural linter, stdlib only. |
| `tests/test_vault_lint.py` | Real-vault fixtures, no mocks. |

## What the linter enforces

Four invariants, each guarding a way file memory actually fails:

1. Every `[[wikilink]]` resolves. A broken link is a fact the router
   can no longer reach.
2. One home per topic: no two notes share a name. Duplicate names make
   links ambiguous and mirrors inevitable.
3. Notes in typed folders declare a `type:` in frontmatter, so tooling
   and the agent know what kind of fact they are holding.
4. The checkpoint carries every section a cold resume needs.

Unreachable notes get a warning, not a failure. CI runs the test suite
and then lints the shipped skeleton, so this repo always passes its own
bar.

## Why files, not a vector store

For one user's working memory, routing beats similarity search: facts
have homes, the reader knows where to look, and retrieval is exact
rather than probabilistic. Files are inspectable and diffable; when the
agent misremembers, you open the note, see the wrong line, and fix it.
Git gives history and blame for free. And the agent maintains its own
memory the way it maintains code, with the same review discipline.

## Limitations

- Single user, single machine by design. Sync and merge between
  machines are real problems this skeleton does not solve.
- The linter checks structure, not truth. Stale facts survive until
  the newest-wins discipline catches them; nothing enforces honesty.
- Retrieval quality equals router quality. A bloated INDEX quietly
  turns back into bulk-loading.
- Exercised with Claude Code. Other harnesses need the contract pasted
  manually, and their file-reading behavior may differ.

## License

MIT
