# OpenAI Codex Operating Guide

This file contains the repository-specific operating procedure for OpenAI Codex.
`AGENTS.md` is the automatic instruction entry point and requires Codex to read this file
before doing any repository work.

## 1. Canonical development location

Use the Box Drive working copy as the development workspace:

```text
C:\Users\Admin\Box\My Libraries\JLT\temp\Jeff temp\claude code\configurator\Git
```

- Open that exact folder as the Codex project (`Ctrl+O` in the Windows app) and start the
  task inside that project.
- Do not develop from a projectless task under `Documents\Codex` and do not create a
  second working clone unless the user explicitly requests one.
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

If the task is rooted somewhere else, stop before writing and tell the user to open the
`Git` project. A task can read outside its project while still being unable to update
`.git/FETCH_HEAD`; read access is not proof that Git writes will work.

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
4. `HANDOFF.md`
5. Current GitHub `main` and open pull requests

Every repository change, including documentation and maintenance, must receive a dated
`**[Codex]**` entry in `CHANGELOG.md` in the same branch or pull request. Record necessary
unfinished work under `Pending / TODO` with its source, status, and exact next action.

## 5. Development and automatic-merge workflow

1. Confirm the Box worktree is clean and up to date:

   ```powershell
   git status --porcelain
   git pull --ff-only origin main
   ```

2. Create or use an intentional working branch. Do not make feature commits directly on
   `main` when a branch/PR workflow is available.
3. Make the requested changes inside this Box-backed working copy.
4. Update `CHANGELOG.md` in the same change and update `Pending / TODO` for anything left
   incomplete.
5. Review the exact diff and run checks proportional to the change.
6. Commit only the intended files, push the branch, and create a pull request.
7. Under the standing repository policy, merge the verified pull request into `main`
   automatically unless the user requested a draft or verification is blocked.
8. Read GitHub `main` back and verify the merge commit and expected changelog entry.
9. Return this Box working copy to `main` and fast-forward it:

   ```powershell
   git switch main
   git pull --ff-only origin main
   ```

10. Do not force, reset, or overwrite a dirty/diverged worktree. Record and report the
    blocker instead.

## 6. Final three-way verification

Do not report completion until all three layers agree:

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
- If the required identity, project root, network access, or clean Git state cannot be
  established, stop the mutation, preserve files, add a `Pending / TODO` entry when a
  repository change is already in progress, and report the exact blocker.
