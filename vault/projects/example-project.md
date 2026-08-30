---
type: project
topic: example-project
updated: 2025-06-02
---

# Example project

One home per ongoing effort. Everything an agent needs to pick this
work up cold: the goal, the live state, and what is next. Replace with
a real project and keep it current; a stale project note is worse than
none because it gets trusted.

## Goal

Ship the customer dashboard rebuild by end of June.

## State

- Auth and layout done, deployed to staging 2025-06-01.
- Migration script written, not yet run (see the ruling in [[decisions]]).

## Next

1. Run the migration on the staging copy.
2. Load-test the reports page before the switch.

## History

- 2025-05-24 — schema change caused a one-hour production outage; the
  staging-first rule in [[decisions]] came from this.
