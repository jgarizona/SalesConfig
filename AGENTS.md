# Repository Agent Instructions

## Required Codex startup

OpenAI Codex must read `CODEX.md` immediately after this file and before reading,
reviewing, or changing the repository. `AGENTS.md` is the automatic Codex instruction
entry point; `CODEX.md` contains the required Windows, Box Drive, GitHub, development,
local-review, approved-publication, and three-way verification procedure for this repository.

Write requested local changes in the existing Box-backed checkout at
`C:\Users\Admin\Box\My Libraries\JLT\temp\Jeff temp\claude code\configurator\Git`.
Prefer opening that folder as the Codex project. If the task was opened elsewhere, an
explicit user instruction to edit this checkout authorizes local work there through the
permitted tools; all filesystem and command approvals still apply. Read access alone is
not proof of write access. Use this checkout as the working directory for repository
commands, preserve existing changes, and do not create another clone.

For starting or resuming local testing, follow
[`HANDOFF.md` → Start or resume local testing](HANDOFF.md#start-or-resume-local-testing)
after the required startup reading. This is the canonical checklist for preserving the
existing checkout/data, checking and reusing the server, conditional startup, sign-in,
and Windows/Box troubleshooting. A testing handoff ends by waiting for user feedback.

## Mandatory changelog attribution

Every repository change must update `CHANGELOG.md` in the same branch or pull request.

- Add a dated entry describing every code, configuration, data, or documentation change.
- Identify who made the change. Changes made by OpenAI Codex must begin with `**[Codex]**`.
- Other people or agents must use their own clear attribution; never relabel earlier work.
- Describe the concrete files, behavior, data, or workflow affected so a future human or AI can reconstruct what changed.
- Documentation-only and maintenance changes are still changes and must be logged.
- Do not consider work complete until the changelog entry is present and verified.
- When a review, investigation, or implementation identifies necessary work that is not completed immediately, add it to `CHANGELOG.md` under `Pending / TODO` before ending the task. Include the source, current status, and concrete next action.
- Repository workflow steps that remain outstanding, including an open pull request that still needs to be merged into `main`, must also be tracked in `Pending / TODO`.
- When a TODO is completed, mark or remove it through a dated, attributed changelog entry so the list does not become stale.

## Local review and approved publication

**User clarification, 2026-09-02:** write changes locally in the existing Box checkout,
verify them, and present the local diff for review. Wait for the user's approval before
pushing changes to GitHub, opening a pull request, or merging. A request to make a local
change is not approval to publish it. This supersedes the earlier unconditional
automatic-push/merge instruction.

After publication is approved, commit only intended files, push the working branch, and
complete the verified PR/merge workflow within that approved scope. Do not merge when
the user requests a draft/unmerged branch, checks fail, or a blocker remains. Verification
includes the exact scope/diff, relevant checks, and attributed changelog/TODO updates.
Read GitHub `main` back after a merge to confirm the expected commit and changelog.
Until approval, report the update as local and keep publishing in `Pending / TODO`.

## Post-merge Box synchronization

After every successful merge into `main`, synchronize the Box-backed working copy at `C:\Users\Admin\Box\My Libraries\JLT\temp\Jeff temp\claude code\configurator\Git`.

1. Confirm the Box worktree is clean with `git status --porcelain`; do not overwrite uncommitted work.
2. Fast-forward it with `git pull --ff-only origin main`; do not reset or force a diverged worktree.
3. Verify its `HEAD` equals GitHub `main` and confirm the expected changed files are present.
4. Confirm Box Desktop has synchronized the updated files to Box cloud before reporting GitHub and Box as identical.

If the worktree is dirty or diverged, or a permission, network, Git, or Box synchronization error prevents completion, do not bypass Git by uploading over tracked files. Record the blocker in `CHANGELOG.md` under `Pending / TODO`, report it to the user, and leave the existing Box files unchanged.
