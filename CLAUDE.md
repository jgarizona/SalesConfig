# Project instructions for Claude Code

## Git

You have standing authorization to **commit and push to `origin/main` without asking for
confirmation first**, as part of normal iterative development on this project. Use your
judgment on when a change is "done enough" to commit (a working, tested slice — not every
single file edit). Write clear, specific commit messages describing what changed and why.

This does **not** extend to destructive operations (force-push, `reset --hard`, deleting
branches, rewriting history) — those still need to be confirmed in chat first, same as any
other project.

## Where things are documented

- `CHANGELOG.md` — dated history of what's shipped, plus a "Pending / TODO" section. Update
  this whenever you ship a user-facing change.
- `HANDOFF.md` — full architecture/data-model brief, written for someone with zero context
  picking this project up cold. Keep it in sync if you change the data model, add a screen,
  or change a core rule (quote lock/rev semantics, brand handling, etc).
