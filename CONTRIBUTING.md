# Contributing

Welcome things:

- New linter invariants, with a test and a one-line why.
- Ports of the contract to other agent harnesses (a `ports/` doc, not a
  framework).
- Fixes to anything the README claims that turns out not to be true.

Ground rules: the linter stays stdlib-only, the vault stays plain
Markdown, and every change keeps `python -m unittest discover -s tests`
green. Structural proposals belong in an issue before a PR; the pattern
here is deliberately small, and most feature ideas are better as forks.
