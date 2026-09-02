# OpenAI Codex Operating Guide

This file contains the repository-specific operating procedure for OpenAI Codex.
`AGENTS.md` is the automatic instruction entry point and requires Codex to read this file
before doing any repository work.

## 1. Canonical development location

Use the Box Drive working copy as the development workspace:

```text
C:\Users\Admin\Box\My Libraries\JLT\temp\Jeff temp\claude code\configurator\Git
```

- Prefer opening that exact folder as the Codex project (`Ctrl+O` in the Windows app).
  Use this checkout as the working directory for all repository commands and local edits.
- If a task starts elsewhere, an explicit user instruction to edit this Box checkout
  authorizes local work through the permitted tools. It does not bypass filesystem or
  command approvals. Do not create a second working clone.
- Box Drive is the filesystem/synchronization layer. GitHub remains the Git remote and
  `main` remains the canonical branch.
- Use only one writing agent/application at a time. Before every edit, confirm the
  worktree is clean or identify all existing user changes and preserve them.

## 2. Required Windows execution context

This Box Drive checkout uses Windows Cloud Files reparse points, including files under
`.git`. On this machine, Codex must run in the logged-in Windows user's context so Box
Drive and Git Credential Manager can service those files.

The working Codex configuration is:

```toml
[windows]
sandbox = "unelevated"
```

`unelevated` is a weaker isolation mode than the preferred `elevated` sandbox. Keep normal
project boundaries and approval controls enabled. Do not switch to full access merely to
avoid a permission prompt. Never change this security setting silently; if it is not
already configured, explain the tradeoff and obtain the user's explicit approval.

At the start of a task, run these checks before editing:

```powershell
whoami
git rev-parse --show-toplevel
git status -sb
git remote -v
```

Expected results:

- Windows identity is the user's logged-in account (`RTG99\Admin` on the machine where
  this guide was written).
- Git top level is the exact Box path above.
- The active branch and any worktree changes are understood before work begins.
- `origin` is `https://github.com/jgarizona/SalesConfig.git`.

A task can read outside its project while still being unable to update the worktree or
`.git/FETCH_HEAD`; read access is not proof that writes will work. For user-authorized
local edits in this checkout, use the normal approval mechanism when required. If access
is denied, preserve the files and report the exact blocker; do not bypass the denial or
silently weaken sandbox settings.

## 3. How Box and GitHub are used

- Treat the Box Drive folder as an ordinary local filesystem workspace. A Box API or Box
  connector is not required for normal Git editing, commits, or pulls.
- Use the connected Box account only for cloud-side verification when helpful, such as
  checking changed-file IDs and SHA-1 values after Box Drive synchronizes.
- Use Git for every tracked-file update. Never upload a tracked file directly through the
  Box connector to bypass a Git, permission, or synchronization problem; that would leave
  the working tree and `.git` state inconsistent.
- Do not edit, replace, dehydrate, or manually upload `.git` files. Let Git, Windows Cloud
  Files, and Box Drive handle them.
- The vendor `.xlsx` source files live one directory above the repository. Treat them as
  source inputs and do not modify them unless the user explicitly requests it.

## 4. Required reading and change accounting

Before changing anything, read in this order:

1. `AGENTS.md`
2. `CODEX.md` (this file)
3. `CHANGELOG.md`, especially `Pending / TODO`
4. `HANDOFF.md`, including [Start or resume local testing](HANDOFF.md#start-or-resume-local-testing)
5. Current GitHub `main` and open pull requests

Every repository change, including documentation and maintenance, must receive a dated
`**[Codex]**` entry in `CHANGELOG.md` in the same branch or pull request. Record necessary
unfinished work under `Pending / TODO` with its source, status, and exact next action.

## 5. Local development, review, and approved publication

The user's 2026-09-02 instruction is to write changes locally in Box and push only
after approval. It supersedes the earlier unconditional automatic-publication policy.

1. Check the Box worktree with `git status --porcelain`. Identify and preserve existing
   changes. Pull only when clean and on the intended branch with a safe fast-forward;
   do not pull, stash, reset, or switch branches over unrelated user work.
2. Make the requested local changes in this checkout. Use an intentional working branch
   when safely available; existing dirty state may require leaving edits uncommitted on
   the current branch while preserving all user work.
3. Update `CHANGELOG.md` and `Pending / TODO`, review the exact diff, and run checks
   proportional to the change.
4. Present the concrete local result for review. Wait for the user's approval before
   pushing to GitHub, creating a PR, or merging. A local edit request alone is not that
   approval. Track publication as pending and make the local-only status explicit.
5. After approval, commit only the intended files on an appropriate working branch,
   push it, and create a PR. Never include unrelated runtime-data or credential files.
6. Complete the verified merge within the approved scope unless the user requests an
   unmerged draft or a blocker remains. Read GitHub `main` back to confirm the result.
7. Return the Box checkout to `main` and fast-forward only when its worktree is clean.
   If existing user edits prevent that, preserve them and record the blocker rather
   than forcing synchronization. Complete section 6 before claiming synchronization.

## 6. Final three-way verification

After approved publication, do not report GitHub/Box synchronization complete until
all three layers agree. Local work awaiting approval must be reported as local only:

1. **GitHub:** the pull request is merged and GitHub `main` is at the expected commit.
2. **Local Box checkout:** `HEAD` and `origin/main` equal the GitHub commit, the worktree is
   clean, and `git diff --exit-code origin/main` reports no differences.
3. **Box cloud:** Box Drive has synchronized the changed files. For each file changed by
   the merge, compare the local raw SHA-1 (`Get-FileHash -Algorithm SHA1`) with the Box
   cloud file's `sha1` when the Box connector is available. Record the Box file ID and
   acting Box identity in the verification result.

Suggested local verification:

```powershell
git rev-parse HEAD
git rev-parse refs/remotes/origin/main
git status --porcelain
git diff --exit-code origin/main
```

If network approval is required for GitHub, request it. If Box synchronization is still
pending, say so explicitly; do not claim that GitHub and Box match until cloud verification
passes.

## 7. Credentials and safety

- GitHub HTTPS authentication is provided by Git Credential Manager under the logged-in
  Windows account. Do not print, copy, or replace stored credentials.
- Box Drive is already authenticated as the user's Box account. Do not introduce a new
  Box API token merely to work with the local repository.
- Never disable TLS verification, force-push, hard-reset, or overwrite user changes to
  work around an access problem.
- If the required identity, authorized checkout access, or a safe Git operation cannot
  be established, stop that operation, preserve files, and record/report the blocker.
  Missing network access or unrelated user edits do not alone prevent authorized local
  documentation/code work; they can prevent publication or final synchronization.
