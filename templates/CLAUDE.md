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
