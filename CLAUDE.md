# Project instructions for Claude Code

## Before starting work

This repo is also worked on from a separate Codex session (the user switches to Codex when
a Claude Code session runs low on budget — see `AGENTS.md`/`CODEX.md`, which is Codex's own
equivalent of this file). Both agents use the existing Box-backed working copy; GitHub `main` can also advance
between sessions. Follow
[`HANDOFF.md` → Start or resume local testing](HANDOFF.md#start-or-resume-local-testing)
when asked to open or resume the local app. Before editing anything:

1. Check `git status -sb` and preserve all existing changes. Only with a clean worktree
   and the intended `main` checkout, use `git pull --ff-only origin main` to bring it
   current. If dirty or diverged, stop the update and report it; do not overwrite user
   changes merely to resume testing.
2. Skim `CHANGELOG.md`'s `Pending / TODO` section — it's the canonical list of open work
   across every agent, not just Claude sessions.

## Git

**User clarification, 2026-09-02:** write changes locally in the existing Box checkout,
verify them, and present the local diff for review. Wait for the user's approval before
pushing to GitHub, opening a PR, or merging. This replaces the earlier standing
authorization to push without asking. Record publication under `CHANGELOG.md`'s
`Pending / TODO` until approved. After approval, commit only intended files and follow
the verified branch/PR/merge workflow, preserving all unrelated user changes.

This does **not** extend to destructive operations (force-push, `reset --hard`, deleting
branches, rewriting history) — those still need to be confirmed in chat first, same as any
other project.

**Changelog attribution:** `CHANGELOG.md` requires every entry to identify its author (see
its "Entry attribution" section). Claude Code entries begin with `**[Claude]**`, the same
pattern Codex uses for `**[Codex]**` — this repo now has more than one agent writing to the
same changelog, so don't drop the tag.

## Giving the user's boss temporary access to the running app

When the user asks for this (phrasing varies — "turn on the temp site", "give my boss
access", "let him test it", etc.), it means: expose the locally-running Flask app via a
temporary public URL using a Cloudflare quick tunnel. No account/signup needed, and no
router/firewall changes are ever required — the tunnel is an outbound connection initiated
from this machine, not inbound port-forwarding.

`cloudflared` is already installed at `C:\Program Files (x86)\cloudflared\cloudflared.exe`
(installed via `winget install --id Cloudflare.cloudflared -e --source winget`, so no need
to reinstall — check `where.exe cloudflared` or that path first).

Steps:
1. **Stop any Flask server currently running in debug mode.** Find it (`netstat -ano | grep
   ":5000"` then match the PID against a running python process) and kill it. Debug mode's
   interactive debugger is a known remote-code-execution risk if the process becomes
   reachable from the internet — never tunnel a `debug=True` instance.
2. **Start Flask with the debugger off**, from the repo root:
   ```bash
   python -c "import app; app.app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)"
   ```
   Run this in the background (it blocks). Confirm it's up with a curl to
   `http://127.0.0.1:5000/sales` before proceeding.
3. **Start the tunnel**, also in the background:
   ```bash
   "/c/Program Files (x86)/cloudflared/cloudflared.exe" tunnel --url http://127.0.0.1:5000
   ```
   Read its output for a line like `https://some-random-words.trycloudflare.com` — that's
   the link to give the user. Verify it actually works with a curl before handing it over.
4. Tell the user plainly: the link is temporary and random (a new one every time), it dies
   the moment either process stops, it's tied to their machine staying on, and anyone with
   the link has full read/write access to the real running data (no separate demo/sandbox
   data exists) — so it shouldn't be posted anywhere public, just shared directly.

**To stop it later** ("stop the temp site" or similar): find and kill the `cloudflared`
process (`Get-Process cloudflared` in PowerShell), which immediately kills the public URL.
The Flask server can keep running locally after that — only the public link needs to go
down, not the whole app, unless the user asks for that too.

## Where things are documented

- `CHANGELOG.md` — dated history of what's shipped, plus a "Pending / TODO" section. Update
  this whenever you ship a user-facing change.
- `HANDOFF.md` — full architecture/data-model brief, written for someone with zero context
  picking this project up cold. Keep it in sync if you change the data model, add a screen,
  or change a core rule (quote lock/rev semantics, brand handling, etc).
