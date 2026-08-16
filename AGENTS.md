# Repository Agent Instructions

## Required Codex startup

OpenAI Codex must read `CODEX.md` immediately after this file and before reading,
reviewing, or changing the repository. `AGENTS.md` is the automatic Codex instruction
entry point; `CODEX.md` contains the required Windows, Box Drive, GitHub, development,
automatic-merge, and three-way verification procedure for this repository.

Codex must open and work from the Box-backed repository project at
`C:\Users\Admin\Box\My Libraries\JLT\temp\Jeff temp\claude code\configurator\Git`.
If the current task is rooted elsewhere, stop before making changes and direct the user to
open that folder as the Codex project. Read access to the Box path is not sufficient;
Codex must be able to write the worktree and Git metadata from the correctly rooted task.

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

## Automatic merge policy for this repository

When the user asks Codex to update this repository, Codex must automatically merge the verified change into `main` without waiting for a separate merge instruction.

A change is verified only when its scope and diff are confirmed, relevant available checks pass, required `CHANGELOG.md` and `Pending / TODO` updates are present, and no unresolved review, permission, conflict, or material uncertainty remains.

Do not auto-merge when the user explicitly requests a draft/unmerged branch, when verification fails, or when a blocker requires user input. After every automatic merge, read `main` back from GitHub and confirm the expected commit and changelog entries are present.

## Post-merge Box synchronization

After every successful merge into `main`, synchronize the Box-backed working copy at `C:\Users\Admin\Box\My Libraries\JLT\temp\Jeff temp\claude code\configurator\Git`.

1. Confirm the Box worktree is clean with `git status --porcelain`; do not overwrite uncommitted work.
2. Fast-forward it with `git pull --ff-only origin main`; do not reset or force a diverged worktree.
3. Verify its `HEAD` equals GitHub `main` and confirm the expected changed files are present.
4. Confirm Box Desktop has synchronized the updated files to Box cloud before reporting GitHub and Box as identical.

If the worktree is dirty or diverged, or a permission, network, Git, or Box synchronization error prevents completion, do not bypass Git by uploading over tracked files. Record the blocker in `CHANGELOG.md` under `Pending / TODO`, report it to the user, and leave the existing Box files unchanged.
