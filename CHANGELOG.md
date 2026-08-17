# Changelog

## Entry attribution

Every repository change must be recorded under the date it was made and identify its author or agent. Changes made by OpenAI Codex begin with `**[Codex]**`. Other contributors and agents use their own clear attribution; existing attribution must not be rewritten.

## Pending / TODO

- **Harden spreadsheet ingestion** — source: 2026-08-15 Codex review of the repository and the JLT, Winmate, Getac, and CipherLab workbooks in Box. Current status: ~~Technical always uses the JLT parser~~ resolved 2026-08-16 (`app.py`'s `PARSERS` dict now routes each brand to its own parser); Getac no longer risks a misleading zero-row success now that it's a real, tested parser. Still open: wrong-vendor uploads can still create unreliable data (no schema/brand validation rejects a mismatched file before parsing it), Purchasing still reads only the active sheet with exact headers, and uploads still have no preflight preview or size limit. Next action: reject unsupported layouts, validate schemas and brands before merging, treat zero parsed rows as an error, preview changes before saving, and enforce an upload-size limit.
- **Normalize and validate spreadsheet prices** — source: 2026-08-15 Codex review. Current status: currency strings containing symbols/special spaces and other unknown text can silently calculate as zero; several existing 1514N wireless prices are affected if those options are approved. Next action: normalize currency cells and explicit included/no-charge values, preserve meaningful statuses such as discontinued, and reject unknown price text instead of silently converting it to zero.
- **Define catalog refresh lifecycle rules** — source: 2026-08-15 Codex review. Current status: exact key changes can create duplicate logical records and rows removed from a workbook remain indefinitely. Next action: detect normalized-key collisions and present renamed, missing, and retired rows for explicit review without silently deleting approved parts.
- **Make JSON catalog writes recoverable and concurrency-safe** — source: 2026-08-15 Codex review. Current status: uploads rewrite the complete catalog JSON directly with no atomic replacement, backup, or write lock. Next action: use atomic writes plus locking/backups now, then migrate to a database when concurrent usage warrants it.
- **Add automated spreadsheet-ingestion tests** — source: 2026-08-15 Codex review and the handoff's known no-tests limitation. Current status: ingestion is verified manually. Next action: add representative JLT, Winmate, Getac, CipherLab, malformed-workbook, pricing-normalization, blank-preservation, and zero-row test fixtures.

- **HubSpot connector** — opportunity/customer lookup, reading deal info, writing quotes back to the deal, sending the customer-facing quote. Sales page currently uses a manually-typed Opportunity ID as a stand-in.
- **Jeeves connector** — cost/inventory reconciliation against JLT's accounting system. Purchasing currently fills in missing Cost/Current Cost by hand.
- ~~**Ingest Winmate, Getac, and CipherLab**~~ — resolved 2026-08-16: dedicated parsers built for all three (`ingest/parse_winmate.py`, `ingest/parse_getac.py`, `ingest/parse_cipherlab.py`), real data ingested (1,060 / 370 / 1,622 parts respectively), catalog now 3,551 parts across all 4 brands.
- **Third-party add-on ingestion path** — not built yet, and deliberately deferred (per the user, 2026-08-16: "addons will come later in this project"). Manufacturer-catalog parts are now auto-approved (`requires_review: false`, see the 2026-08-16 entry below), but a mount vendor's own catalog (RAM Mounts, Gamber-Johnson, etc.) doesn't self-certify fit with a specific host platform the way an OEM's own spec sheet does — that path needs `requires_review: true` and will go through the existing `approvals.json`/Technical-checkbox flow, which still exists specifically for this.
- **Real email sending** — the Email button on the Sales page downloads the Excel file and opens the printable view, but doesn't actually send anything (no SMTP/Outlook integration in the app).
- **Real HubSpot upload** — the Upload button is a stub that reports "not connected."
- ~~**Data drift risk**~~ — resolved 2026-08-14: both Technical's and Purchasing's Upload buttons now merge (never blindly overwrite), so a vendor refresh can't erase prices purchasing already filled in.
- **Quote revision history** — only the current revision of a quote is stored; prior revisions aren't kept anywhere once overwritten.
- ~~**Customer/opportunity lookup UI**~~ — resolved 2026-08-15: Customer and saved-quote lookup have real search-as-you-type panels; Manual Customer and Copy no longer use browser prompt() dialogs.
- **Architecture decision (§6 of the project brief)** — single-agent vs multi-agent, agents vs skills, still open.
- **Move off flat JSON files** if data volume/concurrent-editing needs outgrow it — currently `data/*.json`, no database.
- **Remove test data before go-live** — the 5 seeded test customers (Acme Manufacturing, Blue Ridge Industrial, Harborview Freight, Northwind Logistics, Sunrise Distribution) need to be cleared via Admin's "Remove All Test Customers" once the HubSpot connector replaces Customer Lookup. Also sanity-check `data/quotes.json`, `data/customers.json`, and `data/sales_reps.json` for any other leftover test entries (e.g. the "Test" sales rep) before real use.

## 2026-08-17

- **[Claude]** **"Lookup Saved Quote" now scopes results and supports copying an orphaned
  quote's configuration onto a real customer, per the user.** When the active customer was
  found via Customer Lookup (simulating a real HubSpot pull), results are limited to that
  customer's own quotes plus quotes belonging to customers not yet linked to HubSpot
  (`source: "manual"`) — a real HubSpot search wouldn't surface some other unrelated
  customer's quotes. Picking one of those "orphaned" results doesn't take over editing it —
  it copies the configuration onto a new, not-yet-saved quote for the currently active
  customer (`copyQuoteConfigToCurrentCustomer()`), leaving the Customer field, Opportunity
  ID, and — critically — **the original quote record completely untouched** (no save/update
  call ever references it). A manually-typed active customer sees every quote, unscoped,
  same as always. Server side: `/api/quotes/all` gained an optional `?customer=` filter.
  Verified live end-to-end: selected "Acme Manufacturing" via Customer Lookup, opened Lookup
  Saved Quote, confirmed only the one orphaned quote ("test-1-0", customer `source:"manual"`)
  appeared and was labeled "(copy config to Acme Manufacturing)"; selecting it correctly left
  Customer/Opportunity ID untouched, reset Quote#/Rev# to unsaved, populated the real saved
  configuration (not defaults); confirmed via MD5 checksum that `quotes.json` was **byte-
  identical** before and after — the original quote was genuinely never written to.
- **[Claude]** Also finally logged and documented (previously shipped live for the user's own
  testing, undocumented until now): **`/api/customers` excludes `source: "manual"` records
  from Customer Lookup results** — a manually-created customer is confirmed not to be in
  HubSpot, so a real HubSpot search wouldn't find them either. `source: "test"` stays
  included (that's what those exist for). Does not affect Admin's "pending HubSpot link"
  report or saving — both read/write `customers.json` directly, not through this endpoint.
- **[Claude]** Three Sales-page fixes per the user, tested together:
  - **Fixed: the "Lookup Saved Quote" dropdown reverted to the "Select a quote/revision…"
    placeholder immediately after selecting an entry**, instead of showing the loaded quote
    as selected. Root cause: `loadQuote()` calls `refreshExistingQuotes()` again right after
    loading (to refresh the list), which rebuilt the `<select>` from scratch with no memory
    of what had just been picked. Fixed by having the rebuild check `loadedQuote` and
    pre-select the matching option when it belongs to the same Opportunity ID. Verified via
    the dropdown's actual selected value/text after a full select→reload cycle, not just a
    screenshot.
  - Renamed the per-quote "Upload" button to **"Upload Hspt"** — clearer that it's pushing
    the quote back to the HubSpot deal (once connected), not attaching a generic file.
  - Added a **second "Accept Configuration" button near the top** (next to Save/Lock/Print/
    Upload Hspt/Email), mirroring the existing one at the bottom of the config panel - both
    now share one `updateConfigAcceptState()` so a rep doesn't have to scroll down every time
    after changing an option.

- **[Claude]** **Fixed: category/option dropdowns (Base Unit, Processor Options, etc. on
  Sales, and the Search by Requirements modal's fields) rendered invisible white-on-white
  text once the page became interactive** (Sales Rep verified). Root cause: `.wselect-trigger`
  (the custom dropdown widget's button - built to work around native `<select>` not wrapping
  long option text) never set its own `color` for the enabled state, only for `:disabled`. It
  fell through to the generic `button, .btn { color: white }` rule while its own `background:
  white` also applied - white text on a white background, DOM/JS state fully correct
  underneath (confirmed via computed-style inspection: text was present, just invisible).
  This is a pre-existing bug, not something introduced by tonight's other changes - it went
  unnoticed in this session's own testing because that testing never happened past Sales Rep
  verification, which is the only state where it's visible. Fixed by giving `.wselect-trigger`
  an explicit `color: #0b2545` matching the rest of the app's input text. Verified live by
  reproducing the exact failure (Sales Rep verified, type in Customer field) before and after
  the fix.

## 2026-08-16

- **[Claude]** Replaced the "Lookup Saved Quote" panel's growing row of buttons with a real
  `<select>` dropdown, per the user - the API already returned every quote_number and
  rev_number for an Opportunity ID, but the UI rendered each as its own button, which
  wouldn't scale or scroll cleanly with many revisions. A native `<select>` handles scrolling
  automatically once opened. Each option now also shows the last-updated timestamp, not just
  the display ID/lock icon/platform. Verified by injecting 5 test quotes under one
  Opportunity ID (removed after verifying) and confirming both the dropdown populates
  correctly and selecting an entry loads the right quote.
- **[Claude]** Flash Populate and Lookup Saved Quote once a customer is selected but no
  Opportunity ID exists yet - the "Select one →" hint badge already pointed at these two
  buttons, but the buttons themselves never actually flashed, only Accept-style buttons did.
  Added a `.qh-buttons .btn.flash` CSS rule (same pulsing-ring animation as
  `.accept-btn.flash`, blue instead of green so it reads as "click this" rather than "confirm
  this") since neither button uses the green accept-btn styling at rest. Populate only
  flashes when it's actually visible (manual customer path only); Lookup Saved Quote flashes
  for either customer path, since it's always a valid next step. Verified live via the
  buttons' actual class list, since a static screenshot can't show a CSS animation reliably.
- **[Claude]** Restyled the "not connected to HubSpot" Opportunity ID note as a pill badge
  matching the Customer badge's visual style (`source-badge manual` - amber), per the user's
  crude mockup: the earlier version was small muted inline text, not a bubble. Shortened the
  text to "Not connected to HubSpot" (was a full sentence) and moved it before the "Select
  one →" hint instead of after, matching the mockup's ordering.
- **[Claude]** Added a **Clear** button under the Customer row's button group on Sales,
  right below Manual Customer, per the user. Resets the Customer field, the source badge,
  Populate visibility, the Opportunity ID hint/note, and any leftover confirmation/error
  message back to "no customer selected" - deliberately leaves Sales Rep/code verification,
  Opportunity ID, and the Brand/Platform/option selections untouched. (First attempt at the
  layout broke the Customer row - a `flex-wrap` + `width:100%` combination on the button
  group pushed the Customer label/input below the buttons entirely. Fixed by giving Clear its
  own row instead of forcing a wrap inside the existing one.)
- **[Claude]** Reworked the Customer badge on Sales to simulate a HubSpot connection based on
  *how* a customer was selected this session, per the user - deliberately reintroducing the
  session-based distinction that a 2026-08-15 fix had replaced with the record's real `source`
  field. Rationale: there's no real HubSpot connector to test against yet, so Customer Lookup
  is standing in for "pull from HubSpot" - picking a customer that way now shows a green
  **"HubSpot Customer"** badge and hides Populate/the "not connected" note, as if a real
  connected lookup had found it. Typing via Manual Customer still shows **"Manual — not in
  HubSpot"** (amber) with Populate and the note, unchanged. Critically, `customers.json`'s real
  `source` field and Admin's "pending HubSpot link" report are **untouched** — this is a
  Sales-page-only display simulation using a separate session variable, not a change to what's
  actually stored or reported, so Admin can still be tested against genuinely
  manually-entered customers. Verified live both paths render correctly and independently.
- **[Claude]** Added a **"(Not connected to HubSpot...)" note** next to the Opportunity ID
  "Select one →" hint badge, per the user: once a customer is picked but no Opportunity ID
  exists yet, this is exactly the point where a real HubSpot connector would search for a
  matching open opportunity rather than pointing at Populate/Lookup Saved Quote as a manual
  stand-in. The note is conditioned on `customerSource !== "hubspot"` (always true today,
  since no connector exists) so it self-disables once a real `source:"hubspot"` customer
  exists and the real search replaces this step, rather than needing to be removed by hand
  later. Verified live: selecting an existing customer via Customer Lookup with no
  Opportunity ID shows both the hint badge and the note in the same row.
- **[Claude]** Ran the Flask dev server `threaded=True` after a report of intermittent hangs
  switching Technical brand views — 8 rapid alternating requests via curl (including the
  exact reported Getac↔CipherLab pattern) all returned correct and fast (20-36ms) responses,
  so no server-side data/logic bug was found. Most likely explanation: the debug reloader
  restarting mid-session from concurrent file edits. Threading removes one theoretical
  contributing factor regardless (a slow request no longer blocks the next one) at no cost.
- **[Claude]** Added a **Viewing brand** filter to Technical (previously all 4 brands' 119
  platforms rendered on one continuous scroll with one combined jump-nav — confusing and
  unwieldy now that all 4 brands have real data). Defaults to JLT, carried as `?view=` (kept
  separate from the upload form's own `brand` field, which picks the upload *target* and is
  independent of which brand is currently being viewed). Fixed a latent correctness bug this
  surfaced: the approvals-save handler previously replaced the *entire* `approvals.json` with
  whatever checkboxes were on the submitted page — harmless while every brand's checkboxes
  were always rendered together, but would have silently wiped out every other brand's
  approvals the moment the page only rendered one brand at a time. Now scopes the replace to
  only the submitted brand's entries via a hidden `approvals_brand` field, leaving every other
  brand's approvals untouched. Verified: switching the Viewing brand dropdown between JLT/
  Winmate/Getac shows only that brand's platforms in both the jump-nav and the options list,
  zero cross-brand leakage.
- **[Claude]** Added a small version tag (running git commit's short hash, e.g. `5efaab0`) to
  the nav bar, upper right, below the Admin link — useful given `main` can move independently
  of any given running process (see `HANDOFF.md`'s review-checkpoint section); lets you glance
  at a running instance and know exactly which commit it's on. Derived via `git rev-parse
  --short HEAD` at app startup (`app.py`'s `APP_VERSION`), falls back to `"dev"` if git isn't
  available. Not tied to any semver scheme — this is a live-updating build stamp, not a
  manually-bumped release number.

- **[Claude]** **Manufacturer-catalog options no longer need Technical approval** — decided
  by the user: an option from a vendor's own official price book is auto-selectable on Sales
  without a checkbox, since the vendor already publishes it as valid/sellable; Technical
  review stays required only for a not-yet-built third-party add-on path (RAM Mounts,
  Gamber-Johnson, etc. — explicitly deferred). Added `requires_review` to the part schema
  (`false` = auto-approved, `true`/missing = needs the existing `approvals.json` checkbox
  flow — safe default). New `is_selectable()` in `app.py` replaces the old
  `part_key(p) in approvals` check at all three call sites (`/sales`, `/api/search_options`,
  `/api/search_base_units`) plus `compute_unreviewed_base_models()`. `merge_parts()` now
  carries `requires_review` (and `attributes`, see below) through re-uploads the same way it
  already did for description/price. Migrated all 499 existing JLT parts to
  `requires_review: false`; `parse_vmt.py` sets it on every future ingest. Verified: Admin's
  reviewed count went from real approvals-based to 0 unreviewed platforms immediately after
  migration, with `approvals.json` untouched.

- **[Claude]** **Built dedicated parsers for Winmate, Getac, and CipherLab and ingested real
  data for all three** — catalog grew from 499 parts (JLT only) to 3,551 across all 4 brands
  (1,060 Winmate, 370 Getac, 1,622 CipherLab). Added `ingest/category_map.py` (shared raw→
  canonical category mapping), `ingest/parse_winmate.py`, `ingest/parse_getac.py`,
  `ingest/parse_cipherlab.py`, and a brand→parser `PARSERS` registry in `app.py` that
  Technical's upload form now routes through instead of always assuming JLT's parser. Full
  detail (why Getac/CipherLab are ingested as Base-Unit-only records instead of decomposed
  into fake per-category options, the Winmate header/section-detection specifics, and the
  data-loss bug found and fixed mid-ingest) is in `HANDOFF.md` §7 — not duplicated here.
  Headline points:
  - **CPU cataloging** (the original ask): JLT/Winmate already had a real `Processor Options`
    category, no extra work. Getac has no category but names a CPU in every description —
    extracted via regex into `attributes.cpu` (370/370 rows, 100% hit rate; also grabbed
    `attributes.os`). **CipherLab has no CPU data anywhere in the source file, including its
    Android mobile-computer families** — nothing was fabricated to fill that gap;
    `attributes.os`/`attributes.ram` are set where the description actually states them
    (~540/1,624 rows), `attributes.cpu` is simply absent.
  - **A real data-loss bug was caught and fixed before merging to the live catalog**: an
    early version of the category-mapping table collapsed distinct raw Winmate categories
    (e.g. "Camera" and "Data Collection:") onto one canonical bucket, and their reused short
    codes (`X`/`A`/`0`/`1`) collided once merged, silently overwriting one option with
    another. Caught by explicitly checking for `part_key()` collisions in parser output
    before trusting it, not by inspection — 12 Winmate options would otherwise have vanished
    silently. Fixed by not collapsing categories whose codes aren't provably unique, plus a
    same-category collision guard (`resolve_category()`) for a real source pattern
    (Winmate's MH4005 nests four independent choices under one inherited category label with
    no sub-headers). Verified zero `part_key()` collisions across the full merged catalog
    (3,551 parts) before shipping.
  - Extended `/api/search_options` and `/api/search_base_units` (`ATTRIBUTE_CATEGORY_MAP`)
    so Search by Requirements works for Getac/CipherLab's `attributes`-only data too — the
    search endpoints originally skipped `Base Unit:` rows entirely, which is correct for
    JLT/Winmate but left fixed-SKU brands with nothing searchable at all. Verified live:
    searching Processor Options = "Intel Core Ultra 5 225H Processor" correctly returns both
    Getac platforms that use it (B360G3, V120).
  - Updated `technical.html` to show a checkmark instead of a live checkbox for auto-approved
    options, and rewrote its intro copy — a checkbox that doesn't gate anything would have
    been actively misleading to a real reviewer.
  - Verified end-to-end via browser preview: Sales renders and prices correctly for all 4
    brands (Winmate/Getac/CipherLab spot-checked, not just JLT), Admin shows 119/119
    platforms reviewed (15 JLT + 33 Winmate + 10 Getac + 61 CipherLab), Purchasing/Technical
    both load without error against the 7x larger catalog, no errors in the server log.

## 2026-08-15

- **[Claude]** Added `.claude/settings.local.json` (gitignored — personal Claude Code tool
  permissions, not a shared team policy) allow-listing read-only git checks (`status`,
  `log`, `diff`, `fetch`, `show`, `rev-parse`, `remote`, `merge-base`) plus the non-destructive
  parts of the commit/push workflow `CLAUDE.md` already authorizes in prose (`add`, `commit`,
  `pull --ff-only`, `push origin main`) so the user isn't re-approving the same read-only
  checks every session. Deliberately excludes force-push, `reset`, `branch -D`, and other
  destructive commands — those stay gated, same carve-out `CLAUDE.md`'s Git section already
  states. Added the file to `.gitignore`.

- **[Claude]** Synced the review-checkpoint marker in `HANDOFF.md` §0a to this commit's own
  parent HEAD (`a31dc4f`) — the checkpoint necessarily lags by one commit right after it's
  first added, since the commit that writes the marker moves HEAD past whatever it records.
  This is the expected, harmless one-commit lag the checkpoint's own instructions describe,
  not a bug; not chasing it further. Session ends here.

- **[Claude]** Added a concrete "Review checkpoint" (`HANDOFF.md` §0a) implementing the
  review-on-resume policy from the governance entry below, which had stated the *requirement*
  but not the *mechanics*. A single line records the last HEAD hash, reviewing agent, and
  timestamp any agent caught up through; every agent must compare it to `origin/main` on
  start (differ → `git log`/`git show` the gap and cross-check against this changelog, not
  just skim commit subjects) and update it as the last action before ending a session. Fixes
  the actual gap: the prior entry said "review everything since last active" without any way
  to know what "since last active" meant. No code changed.

- **[Claude]** Documented the project's governance model in `HANDOFF.md` §0, per the user's
  explicit direction: Claude Code is lead developer; Codex is a fallback used only when a
  Claude Code session runs out of budget, not an independent co-equal decision-maker. Codex's
  standing auto-merge-to-`main` policy stays in place (requiring Claude's approval first was
  considered and rejected — it would block Codex's fallback role, and this is a live tool
  with real data, not one where an unmerged PR can sit indefinitely). In exchange, every
  Claude Code session must now open with a diff-level review of everything merged since it
  was last active, not a changelog skim — recorded as a standing instruction so this survives
  across sessions. No code changed.

- **[Claude]** Closed the Claude-side gap in the handoff docs that a Codex session had
  already found and partly fixed from its own end: `CLAUDE.md` had no equivalent of the
  "read this before starting, pull first" checklist that `AGENTS.md`/`CODEX.md` already
  require of Codex. Added a "Before starting work" section to `CLAUDE.md` — pull
  `origin/main` before editing (since Codex pushes directly to GitHub without ever touching
  this local Box-synced working copy, local `main` can silently fall behind with zero local
  activity — confirmed live during this session: local `main` advanced from `e6c7b4d` to
  `db5f71d` across three separate Codex-driven fast-forwards with no command run in this
  session), and skim `CHANGELOG.md`'s `Pending / TODO` first. Established `**[Claude]**` as
  this agent's changelog attribution tag, matching Codex's `**[Codex]**` convention now that
  more than one agent writes to this file. Added a one-line cross-reference in `HANDOFF.md`
  §0 noting Claude Code reads `CLAUDE.md` automatically, the same role `AGENTS.md` plays for
  Codex, so a human or third agent reading the handoff sees both entry points. No code
  changed; verified by re-reading `CLAUDE.md`/`HANDOFF.md` after editing.

- **[Codex]** Added `CODEX.md` as the detailed OpenAI Codex operating guide for using the Box-backed repository as the working and development area. Updated `AGENTS.md` to require Codex to read it from the automatically discovered instruction entry point, and updated `HANDOFF.md` to direct Codex to the guide explicitly. The guide records the exact Box project path, required Windows user/sandbox context, startup checks, Git-only tracked-file rule, changelog/TODO accountability, automatic branch/PR/merge workflow, post-merge fast-forward, and final GitHub/local Box/Box-cloud hash verification.

- **[Codex]** Verified the user-completed Box fast-forward: the clean Box-backed `main` worktree reached GitHub commit `85b3f63f33534db8a9177453833043522cfe3cc9`, and Box cloud file SHA-1 values for `AGENTS.md`, `HANDOFF.md`, and `CHANGELOG.md` matched the local synchronized files. Removed the completed Box synchronization item from `Pending / TODO`; the changelog-only merge containing this closure requires the routine final Box fast-forward.

- **[Codex]** Attempted a safe post-merge Box synchronization after confirming the Box-backed `main` worktree was clean. The fast-forward pull was blocked before checkout by Windows permission denial on `.git/FETCH_HEAD`, so no Box file was changed. Added the standing post-merge Box synchronization procedure to `AGENTS.md` and `HANDOFF.md`, and recorded this unresolved synchronization in `Pending / TODO` with the exact recovery action.

- **[Codex]** Squash-merged [PR #1](https://github.com/jgarizona/SalesConfig/pull/1) into `main` at commit `62b3fabad9373c72a404bb2dd15b72610f845768`, verified that `main` contains the CipherLab correction, attributed changelog/TODO rules, and automatic-merge policy, then removed the completed PR #1 merge item from `Pending / TODO` and updated the handoff's TODO summary.

- **[Codex]** Added the user's standing automatic-merge instruction to `AGENTS.md` and `HANDOFF.md`: after a repository update is scoped, verified, logged, and free of blockers, Codex must merge it into `main` automatically without waiting for a separate merge request, then read `main` back to verify the result.

- **[Codex]** Reworked the opening and TODO sections of `HANDOFF.md` to make `CHANGELOG.md` the canonical completed-change and `Pending / TODO` source, document the required read/log/attribute/capture/close workflow step by step, and replace the stale statement that the repository had never been committed with the current GitHub `main`/PR model.

- **[Codex]** Added a mandatory unresolved-work capture rule to `AGENTS.md` and `HANDOFF.md`, then expanded `CHANGELOG.md` → `Pending / TODO` with the outstanding PR #1 merge and every unresolved spreadsheet-ingestion risk identified during the Codex review.

- **[Codex]** Added `AGENTS.md` and a matching `HANDOFF.md` rule requiring every future repository change—including documentation and maintenance—to receive a dated, author-attributed `CHANGELOG.md` entry in the same branch or pull request.

- **[Codex]** Corrected the fourth vendor name to **CipherLab** across `app.py`, `ingest/parse_vmt.py`, `templates/sales.html`, `CHANGELOG.md`, and `HANDOFF.md`; also recorded the existing CipherLab source workbook in Box.

- Added a **site-wide access PIN** (4-8 digits) gating every page and API endpoint on the whole
  app, not just Sales — anyone loading any URL (local or via a temporary tunnel) hits a login
  page first. Auto-generated on first run into `data/site_access.json` (gitignored — this repo
  is public, so the PIN and Flask session secret key must never be committed) along with a
  random session secret key. Managed from Admin: view the current PIN, set a new one. Existing
  logged-in sessions stay valid after a PIN change; only new logins need the new one. A "Log
  out" link was added to the nav. Same **not real security** caveat as Sales Rep codes — short,
  no lockout, meant to keep a shared demo link from being casually poked at, not to be relied
  on as real access control. Verified: wrong PIN rejected, correct PIN redirects to the
  originally-requested page, static assets stay reachable (so the login page itself renders),
  both page routes and `/api/*` routes are gated, PIN change takes effect for new logins
  immediately, logout clears the session, and `data/site_access.json` is confirmed excluded
  from git via `git check-ignore`.

- **Fixed:** long option descriptions (the norm in this catalog) overflowed/got clipped in the category dropdowns and the Search modal's requirement dropdowns. Root cause: native `<select>` renders its open option list as OS-level browser chrome that page CSS cannot style or wrap on any browser — not something fixable with CSS alone. Replaced with a custom dropdown widget (`createWrappingSelect()` in `sales.html`) built from plain styled `<div>`s: a single-line truncated trigger button plus a panel of full-width rows that wrap normally, same visual pattern as the existing Customer/Quote Lookup panels. Applied to both the category-option dropdowns and the Search modal's requirement dropdowns. Verified: text wraps correctly, selecting an option updates price totals and the draft part number, opening one widget closes any other open one, clicking outside closes it, and — most importantly — loading a previously-saved quote correctly pre-selects the widget to its saved value (not the default option).
- **Major: Brand is now a first-class field across the whole system**, not just JLT. This was a real data-model change, not cosmetic:
  - Every part record, approval, and quote now carries a `brand` field. Existing JLT data was migrated in place (`brand: "JLT"` added to all 499 parts and 44 approvals).
  - `ingest/parse_vmt.py` takes a `--brand` argument (defaults to JLT) and tags every parsed row with it.
  - **Technical**: platforms are now grouped under a Brand heading (JLT, Winmate, Getac, CipherLab all show, even brands with zero data yet); the vendor-spreadsheet Upload form has a Brand selector.
  - **Sales**: new **Brand dropdown** ahead of Platform — picking a brand filters which platforms/options are available (only JLT is enabled today; the other three are visibly present but disabled with "no data ingested" until their spreadsheets are parsed). Quotes now record which brand they're for, shown on the quote status, the printable view, and the Excel export.
  - **Purchasing**: both tables (catalog pricing gaps, and the quotes action-item report) gained a Brand column; the inline price-edit row key and the upload/report CSV format are now brand-aware (`brand||platform||category||code`, with a missing brand column defaulting to JLT for backward compatibility).
  - **Admin**: the unreviewed-base-models table gained a Brand column.
  - Verified with a full round-trip: saved a quote through the new Brand dropdown, confirmed `brand:"JLT"` landed correctly in the saved record, the print view, and the Purchasing report; round-tripped all 44 existing Technical approvals through the new 4-part checkbox key with zero data loss; confirmed Winmate/Getac/CipherLab render as present-but-disabled with no data.
  - Removed an unused, dead `/api/parts/update` endpoint found while doing this (superseded by the Purchasing form-based save, never called from anywhere).
- **New: "Search by Requirements"** on the Sales page (button next to the Platform dropdown). A rep can optionally pick a desired spec per category (Processor, RAM, Storage, Display, ports, Add-Ons, IP Rating, Power Cable, Wireless, OS — none required, any subset), optionally narrow to one Brand, and Search returns every base unit (across brands, unless narrowed) whose **Technical-approved** options satisfy all of them, each with a radio button. Selecting one and clicking Select loads that Brand+Platform into the main configurator so the rep finishes the rest of the configuration and saves normally. Matches on option *description* text rather than code, since the same code can mean different things on different platforms. Verified end-to-end: searched for a specific storage size, got back two matching JLT platforms, selected one, confirmed it correctly populated Brand/Platform/category dropdowns and saved with the right brand attached.
- **Fixed:** the Customer badge/Populate button used "how was this customer selected this session" (typed vs picked from Lookup) instead of the customer record's real source. Picking an *existing* manually-created customer via Customer Lookup incorrectly showed the green "Existing customer" badge and hid Populate — even though it's not actually a HubSpot record. `/api/customers` now returns each customer's real `source`, and the badge/Populate logic uses that directly: anything that isn't `source:"hubspot"` gets the Manual treatment, regardless of how it was found.
- Added an **"Accept Configuration"** button at the bottom of the configuration panel (below the part number). Save stays disabled until it's clicked — deliberately reviewing the platform/option selections, not just leaving whatever the dropdowns defaulted to. It flashes when there's something to accept, same treatment as the other action buttons. Changing any option after accepting re-locks Save and re-flashes Accept; the same reset happens after every successful save too, so each save requires its own fresh Accept. Print/Upload/Email/Copy are unaffected — those already only need a clean saved quote (existing behavior).
- Added a **"Select one →" hint badge** next to the Opportunity ID label, same style as the Customer source badge — appears once a customer is chosen but no Opportunity ID exists yet, pointing at Populate/Lookup Saved Quote. Clears the moment Opportunity ID has a value, however it got there (Populate, Lookup, or typed directly).
- **Rep verification now gates the whole Sales page**, not just Save/Copy. Until a rep is selected and the 4-digit code verified, everything else — Customer field/buttons, Opportunity ID, Lookup Saved Quote, the platform picker, every option dropdown, and Save/Lock/Print/Upload/Email/Copy — is disabled. It re-locks instantly if you switch reps (since that invalidates the prior verification) and unlocks the moment the code matches. Server-side checks on Save/Copy remain in place as a backstop regardless.
- Added a **badge next to the Customer label** showing whether the current customer is manually typed ("Manual — not in HubSpot", amber) or an existing looked-up record ("Existing customer", green) — previously there was no visual difference between the two, even though the system already tracked it internally (it's the same state that drives the Populate button).
- **Fixed:** Customer Lookup had its own separate "Filter customers..." box, redundant with the Customer field right above it. The panel now filters live off the Customer field itself as you type — no second input to keep in sync.
- **Fixed:** the Accept button (Customer field) was fully hidden until there was a pending edit, which after a page refresh looked identical to "the button is missing" — confusing, not a bug, but bad UX. It's now always visible, just disabled/dim until there's something to accept, then enabled and flashing.
- Added a **Populate** button next to Opportunity ID, shown only right after accepting a manually-typed Customer (not one picked via Customer Lookup) — fills Opportunity ID with the customer name as a starting point, since there's no HubSpot deal to pull a real ID from yet.
- Added **5 test customers** for exercising Customer Lookup before HubSpot exists (Acme Manufacturing, Blue Ridge Industrial, Harborview Freight, Northwind Logistics, Sunrise Distribution), tagged `source: test` so they're excluded from the "pending a HubSpot link" report — that report is meant for real manually-entered customers, not demo data. Managed from Admin: **"Add 5 Test Customers"** / **"Remove All Test Customers"**, the latter a single click for when the real connector goes live.
- Reworked the Customer field: it's now always directly typeable (no more separate "Manual Customer" edit-mode). Typing anything different from the currently-accepted customer flashes a green **Accept** button next to it — nothing is saved until that's clicked (or Enter, as a shortcut). Escape reverts to the last accepted value. "Manual Customer" now just focuses/selects the field; "Customer Lookup" picks still commit immediately since selecting from a list is already explicit confirmation.
- **Fixed:** the Sales Rep dropdown only loaded its list once, when the page first loaded — a browser tab left open across an Admin-side rep add/remove kept showing the stale roster (this is what caused a removed test name to linger and block picking anyone else). It now re-fetches the rep list every time the dropdown is opened (mousedown/focus), so Admin changes show up without needing a page reload.
- **Fixed:** "Manual Customer" (and "Copy to New Opportunity") did nothing when clicked in some browsers. Both used `window.prompt()`, which browsers increasingly block or suppress outright — a blocked prompt returns nothing and the click silently does nothing. Replaced both with real inline UI: Manual Customer now makes the Customer field directly typeable (type a name, press Enter to save, Escape to cancel); Copy now opens an inline panel with real input fields instead of two chained popups.
- Added **Sales Rep** tracking, closing the "how do you know who made this quote" gap. A "Sales Rep" dropdown + 4-digit code field (last 4 of cell number) now sits at the top of the Sales page; the code is verified against the server before Save/Copy are allowed, and every quote records both `created_by` (set once) and `sales_rep` (updated on each save) — shown on the printable view, the Excel export, and stored in the quote record. Reps are managed on the Admin page (add/remove, name + 4-digit code). Seeded with Chad, Glenn, Eric, and Test.
  - **Explicitly not real security** — a 4-digit code is 10,000 guessable combinations with no lockout. It exists purely so a quote has an attributed rep, not to gate access to anything. Said plainly in the Admin UI itself.
- Renamed Sales page's "New Customer" button to **"Manual Customer"** (same behavior: prompts for a name, saves it permanently to the customer list, selects it for the current quote).
- Every customer created that way is now tagged `source: manual` with no `hubspot_id`. Added a new Admin section, **"Customers pending a HubSpot link"** (with its own stat card and CSV report), listing every manually-created customer that hasn't been tied to a real HubSpot record yet — so once the HubSpot connector exists, none of them get lost or left stranded.

## 2026-08-14

- Added an **Upload** button to both Technical and Purchasing:
  - **Technical** uploads a full vendor spreadsheet (same multi-tab format as the JLT VMT file) — new platforms/options are added unapproved, ready for review; existing ones are refreshed.
  - **Purchasing** uploads a flat pricing spreadsheet (same columns as its own "Generate Catalog Report") to bulk-fill Cost/Current Cost/etc. instead of typing each one in by hand. It can only update parts that already exist — it can't create new catalog entries.
  - Both share one merge rule: a blank cell in the upload never erases a value already on file, so a partial vendor refresh can't wipe out prices purchasing already found. Verified by re-uploading the original JLT VMT file after a Purchasing price edit and confirming the edit survived untouched.
- Added a **Customer** concept alongside Opportunity ID: "Customer Lookup" (search existing customers) and "New Customer" buttons on the Sales page, backed by `data/customers.json`. Quotes now store which customer they belong to, shown on the printable view and Excel export.
- Added a **"Lookup Saved Quote"** panel on the Sales page — searches *all* saved quotes by customer, opportunity, platform, or quote ID (not just quotes under whatever Opportunity ID happens to be typed in already).
- Moved the whole quote header — Customer, Opportunity ID, Quote #/Rev # (now shown as their own labeled boxes), and all the action buttons (Save/Lock/Print/Upload/Email/Copy) — to the **top** of the Sales page. Previously these were only reachable after scrolling past the entire configuration, which made them easy to miss.
- Added **Admin page** (`/admin`): total quotes created, purchasing action items pending, and technical base models not yet approved.
- Reworked **Purchasing page**: all 4 price fields (Floor, MSRP, Cost, Current Cost) shown and editable inline for any option missing data; added a second report — "what's been quoted to Sales" — that cross-references saved quotes against live pricing and flags exactly what purchasing still needs to resolve.
- Reworked **Sales page**: added a manual Opportunity ID field with existing-quote lookup, and a full quote lifecycle — Save / Lock / Unlock / Print (PDF) / Upload (stub) / Email (stub) / Copy-to-new-Opportunity. Quote IDs follow `OpportunityID-Quote#-Rev#`; locking (manual or via Print) fixes the quote, editing a previously-locked quote bumps the revision.
- Added a printable quote view and an Excel quote export — neither ever includes Cost, matching the rule that cost is purchasing-internal only.
- Fixed a real bug: editing an unlocked, previously-saved quote and re-saving was creating a brand-new quote instead of revising the original (the in-page reference to which quote was being edited was being dropped on every edit). Now it correctly bumps the revision number in place.
- Fixed Technical page usability: the Save Approvals button was only reachable after scrolling past all ~500 checkboxes. Added a sticky save bar (always visible) and a jump-to-platform nav at the top.

## 2026-08-13

- First ingest slice: `ingest/parse_vmt.py` parses the JLT VMT Q1 2026 spreadsheet into structured JSON — 499 options across all 15 platform tabs (1014P, 1214N, 1214P, 1514N, 6012/6012A/6015, and 8 Verso variants).
- Built first-draft **Technical**, **Sales**, and **Purchasing** screens against that data.
  - Technical: checkbox approval of which options are valid per platform.
  - Sales: platform + option dropdowns (only approved options selectable), live price totals, draft part number.
  - Purchasing: flagged options missing pricing, with a CSV export.
