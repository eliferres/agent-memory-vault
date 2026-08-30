# Operating contract

How an agent reads and writes this vault. These rules are what make
plain files work as memory; break them and the vault rots into a pile
of contradicting notes.

## Reading

1. At session start, read [[INDEX]] and nothing else.
2. Route: find the task's topic in the INDEX table, open that one home.
3. Read on demand. Never load the whole vault to "get context"; the
   router exists so that full recall costs almost no tokens.
4. Trust the newest line. If two notes disagree, the newer one is true
   and the older one is a bug to fix now.

## Writing

1. A durable fact gets written the moment it appears: to its owner file,
   plus a one-line receipt in today's note under `daily/`.
2. One home per topic. If no home exists yet, create one and add a row
   to [[INDEX]]. If a fact seems to belong in two places, it belongs in
   one, with a link from the other.
3. Corrections beat additions. When the user corrects something, update
   the owner file in place and note why in [[decisions]].
4. Dates are absolute. Write "2025-06-02", never "yesterday"; relative
   dates are meaningless to the next session.

## The session lifecycle

1. Boot: read [[INDEX]]. If resuming, read [[LATEST-SESSION]] in full
   before doing anything else.
2. Work: route, read on demand, write back as you learn.
3. Checkpoint: at the end of a session, or before hitting a context
   limit, rewrite [[LATEST-SESSION]] top to bottom. State beats prose:
   record decisions with their why, dead ends so they are not retried,
   and exact next steps. To keep history, copy the old checkpoint into
   `system/checkpoints/` with a date prefix before overwriting.

## Maintenance

Run the linter whenever structure changes:

```
python3 tools/vault_lint.py vault
```

It fails on unresolvable links, duplicate homes, untyped memory notes,
and an incomplete checkpoint. Structure it can enforce; keeping facts
true is the discipline above.
