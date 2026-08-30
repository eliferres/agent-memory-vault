---
type: memory
topic: decisions
updated: 2025-06-02
---

# Decisions

Append-only log of rulings, each with its why. A decision recorded here
is settled: the agent applies it instead of re-asking. Reversals get a
new line pointing at the old one, never an edit that erases history.

- 2025-06-02 — Pricing page ships with three tiers, not four. Why: user
  tested both; the fourth tier pulled buyers down, not up.
- 2025-05-24 — All database migrations run through the staging copy
  first. Why: a schema change once took production down for an hour;
  see [[example-project]] for the incident.
