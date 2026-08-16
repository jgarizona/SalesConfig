# Repository Agent Instructions

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
