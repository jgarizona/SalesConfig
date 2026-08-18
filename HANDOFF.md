# JLT Inside-Sales Configurator — Handoff Brief

Written 2026-08-15 for handing this project to another agent/developer. Goal: everything
needed to understand, run, extend, or fully recreate this project without access to the
conversation that built it.

## 0a. Review checkpoint — read and act on this before anything else

**Last reviewed up to:** HEAD `76d76f5` — by Claude Code — 2026-08-17 10:47 -0500

This line is the answer to "has anyone else touched this repo since I was last here?" —
don't skip it because `CHANGELOG.md` looks like it covers everything; changelog entries can
be incomplete or written after the fact, the commit graph can't lie.

**Every agent, on starting work, must:**
1. `git fetch origin`, then compare the hash above to `git rev-parse origin/main`.
2. If they match, nothing has changed since the checkpoint — proceed normally.
3. If they differ, someone (a different agent, a different session of the same agent, or
   the user directly) changed the repo since. Run
   `git log --oneline <hash-above>..origin/main` to list what's new, then actually read each
   commit's diff (`git show <hash>`) — not just the subject lines — before starting new
   work. Cross-check the commits against `CHANGELOG.md` for the same range and flag any
   change that wasn't logged.
4. `git pull --ff-only origin main` to bring the local Box-backed worktree current.

**Every agent, before ending a session's work, must:** update the line above — your own
agent name (or "the user" if a human made the change directly), the current `git rev-parse
--short HEAD`, and the current local timestamp. This is the last edit of the session, not
an optional cleanup step; a stale checkpoint is what makes the next session's step 3 above
either miss something or re-review work it's already seen.

## 0. Required change-log and TODO workflow — read before changing anything

`CHANGELOG.md` is the **canonical source of truth** for both completed changes and
`Pending / TODO` work. `HANDOFF.md` explains architecture and context; it must not be used
as a substitute for checking the live changelog.

Before starting work:

1. Read `AGENTS.md` for mandatory repository instructions. **Claude Code reads `CLAUDE.md`
   automatically as its own entry point instead** — same role as `AGENTS.md`, agent-specific
   file. A human or a third agent picking this up cold should check both.
2. **If the acting agent is OpenAI Codex, read `CODEX.md` next and follow its complete
   Box-backed project, Windows identity, Git/GitHub, automatic-merge, and three-way
   verification procedure.** Codex must work from the Box repository project itself, not a
   projectless task under `Documents\Codex`.
3. Read `CHANGELOG.md`, especially `Pending / TODO`, before choosing or beginning work.
4. Check `main` and open pull requests so work already in progress is not duplicated.

For every repository change:

1. Add a dated `CHANGELOG.md` entry in the same branch or pull request.
2. Attribute the entry to the person or agent that made it. OpenAI Codex uses
   `**[Codex]**`; other contributors use their own clear attribution.
3. Describe the concrete code, configuration, data, documentation, or workflow affected.
4. If necessary work is identified but not completed, add it to `Pending / TODO` with its
   source, current status, and next action. This includes a pull request still awaiting
   merge into `main`.
5. When a TODO is completed, close or update it with another dated, attributed entry.
6. After the change is verified, automatically merge it into `main` without waiting for a separate merge instruction, unless the user explicitly requests a draft/unmerged branch or verification is blocked.
7. Read `main` back after the merge and confirm the expected commit and changelog entries are present.

**Standing automatic-merge instruction (added 2026-08-15 by Codex):** for this repository, a user request to update the repository authorizes Codex to merge the verified change into `main` automatically. A separate “merge it” instruction is not required. Codex must stop before merging only if the user asks to keep the work as a draft, verification fails, or an unresolved blocker requires user input.

**Standing post-merge Box synchronization instruction (added 2026-08-15 by Codex):** after every successful merge into `main`, confirm the Box worktree at `C:\Users\Admin\Box\My Libraries\JLT\temp\Jeff temp\claude code\configurator\Git` is clean, fast-forward it with `git pull --ff-only origin main`, verify its `HEAD` and expected files match GitHub `main`, and wait for Box Desktop to synchronize the changes to Box cloud. Never overwrite a dirty or diverged worktree or bypass Git by uploading over tracked files. If permissions, network access, Git state, or Box synchronization blocks the update, leave Box unchanged and record the exact blocker and next action in `CHANGELOG.md` → `Pending / TODO`.

**Project governance — lead developer (decided 2026-08-15 by the user):** Claude Code is
the lead developer on this project. Codex is used only as a fallback when a Claude Code
session runs out of budget, not as an independent co-equal decision-maker. Practically:

- Codex's standing automatic-merge-to-`main` policy (above) **stays in place** —
  requiring Claude's approval before every Codex merge was considered and explicitly
  rejected, because it would block Codex's work until a Claude session is available again,
  defeating the point of the fallback. This is a live tool with real quote/pricing data, not
  a repo where an unmerged PR can sit indefinitely.
- **In exchange, every time a Claude Code session resumes work on this project, its first
  action must be a real diff-level review of everything merged into `main` since it was
  last active** — not a skim of `CHANGELOG.md` entries taken at face value. This is the
  review checkpoint for changes made under this policy; it happens after merge instead of
  gating it. Flag or fix anything that doesn't meet standard before starting new work.
- Files that govern another agent's behavior on this repo (`AGENTS.md`, `CODEX.md`) are
  reviewed and endorsed or corrected by the lead developer, not treated as self-authored
  artifacts to leave unquestioned — including policies an agent adopted on its own
  initiative, like the automatic-merge policy originally was.

**Codex-specific operating guide (added 2026-08-15 by Codex):** `CODEX.md` is the
required detailed guide for OpenAI Codex. It records the exact Box project path, the
Windows execution context needed for Box Drive reparse points and Git Credential Manager,
startup checks, the rule against connector-based Git bypasses, the automatic branch/PR/
merge sequence, and the final GitHub/local Box/Box-cloud verification. `AGENTS.md` remains
the automatic discovery entry point and explicitly requires Codex to read `CODEX.md`.

**Current git status (updated 2026-08-15 by Codex):** the repository is committed and pushed
to GitHub. `main` is the official/default branch; active work may exist in pull-request
branches. The earlier warning that nothing had been committed is resolved. Always verify
the current GitHub branch and PR state rather than relying on the historical local state.

---

## 1. What this is and why

**Goal (from the original project brief):** replace a paper-based, error-prone process
where field sales reps hand-write system configurations and mail them in for pricing. Two
problems, one tool:
- **Sales:** let reps build a valid, correctly-priced configuration themselves.
- **Technical:** bake compatibility rules in so configs are valid *by construction*,
  cutting the repetitive technical review that currently eats headcount.

**The bigger goal:** this is not just a JLT configurator. It's meant to become a
configurator *engine* that also handles 3 other vendors JLT resells (Winmate, Getac,
CipherLab), none of which have a configurator of their own today. See §7 for how far that
part actually got.

**Long-term integration target (not built yet):** HubSpot is the front door. A sales
opportunity starts there; the configurator reads/writes back to it by deal ID. See §9 for
what currently stands in for that.

**Current status:** rough working prototype. All 4 screens (Technical, Sales, Purchasing,
Admin) are functional against real pricing data for all 4 brands (JLT/Winmate/Getac/
CipherLab, 3,551 parts total, see §7). No database, no auth, no HubSpot — all
noted below.

---

## 2. Where everything lives

| What | Path |
|---|---|
| **This repo** | `C:\Users\Admin\Box\My Libraries\JLT\temp\Jeff temp\claude code\configurator\Git\` |
| **GitHub repository (main + PR branches)** | `https://github.com/jgarizona/SalesConfig.git` |
| **Source vendor spreadsheets (Box, human-edited)** | `C:\Users\Admin\Box\My Libraries\JLT\temp\Jeff temp\claude code\configurator\` (one level up from the repo) — contains `JLT VMT Q1 2026 Updated final 02192026 Release.xlsx`, `JLT Winmate Master Price Book 03062026.xlsx`, `GetacSelectMSRP_2026-01-20.xlsx`, `CipherLab Price Increase effective 4_10_2026 Product List.xlsx` |
| **Runtime data (JSON, working state)** | `Git\data\*.json` — see §6 |

Run it with:
```bash
cd "C:\Users\Admin\Box\My Libraries\JLT\temp\Jeff temp\claude code\configurator\Git"
pip install -r requirements.txt
python app.py
```
Flask dev server on `http://127.0.0.1:5000`, debug mode on (auto-reloads on file change).
**This is a dev server, not production-ready** — no WSGI server, no HTTPS, no auth beyond
the rep-code gimmick described in §8.

---

## 3. Tech stack

- **Backend:** Python 3.12, Flask. No ORM, no database — see `requirements.txt` (just
  `flask` and `openpyxl`).
- **Frontend:** server-rendered Jinja2 templates + vanilla JavaScript (no build step, no
  framework, no npm). All JS is inline `<script>` in each template.
- **Data storage:** flat JSON files under `data/`. Chosen deliberately (see brief's original
  rationale) — source data arrives as Excel, purchasing/technical reviewers already live in
  spreadsheets, and Box was the assumed eventual sync point. Migrate to a real DB only if
  this gets outgrown (concurrent multi-user editing is the likely trigger — see §10).
- **Excel I/O:** `openpyxl` for both reading vendor spreadsheets (`ingest/parse_vmt.py`) and
  writing exports (quote Excel export, Purchasing CSV/xlsx reports).

---

## 4. File structure

```
Git/
├── app.py                    # The entire Flask app — routes, data access, business logic (~1020 lines)
├── requirements.txt          # flask, openpyxl
├── CHANGELOG.md              # Dated changelog + "Pending / TODO" section — READ THIS TOO
├── HANDOFF.md                # This file
├── AGENTS.md                 # Mandatory repository instructions for AI/coding agents
├── .claude/
│   └── launch.json           # Dev-server launch config for the Claude Code browser preview tool
├── ingest/
│   ├── parse_vmt.py          # JLT parser - one sheet per platform, category/code/description
│   │                          # + a price-label header block. Also invoked live by Technical's
│   │                          # "Upload vendor spreadsheet" button, via the PARSERS registry
│   │                          # in app.py (one entry per brand).
│   ├── parse_winmate.py      # Winmate parser - same category/code/description shape as JLT,
│   │                          # but label-driven header/price-column detection (not position-
│   │                          # anchored) since header row and price-label spelling/order vary
│   │                          # sheet to sheet, plus handling for a second flat "Accessories"
│   │                          # section some sheets have below the main matrix.
│   ├── parse_getac.py        # Getac parser - flat, already-fixed SKU list (no per-category
│   │                          # options at all); each row becomes one Base Unit record. Pulls
│   │                          # best-effort cpu/os/ram/storage/display/wireless out of the
│   │                          # free-text description into `attributes` purely for search
│   │                          # (see §6) - 100% hit rate on all six, real 370-row catalog.
│   ├── parse_cipherlab.py    # CipherLab parser - same flat-SKU shape as Getac. Platform/
│   │                          # category come from splitting "Model Code" (e.g. "1000A
│   │                          # Product"); no CPU field exists anywhere in this vendor's data.
│   └── category_map.py       # Shared by the Winmate/CipherLab parsers: maps each vendor's raw
│                              # category label to app.py's canonical CATEGORY_ORDER vocabulary
│                              # so cross-brand sort/search line up. Deliberately does NOT
│                              # collapse categories whose raw codes aren't globally unique
│                              # within a platform (see §6/§7 - this caused real, once-silent
│                              # data loss during ingest before it was caught).
├── templates/                # Jinja2 templates, one per screen + shared partials
│   ├── base.html             #   Nav bar, page shell
│   ├── technical.html        #   Technical Review screen
│   ├── sales.html            #   Sales Configurator screen (by far the largest — ~955 lines,
│                              #     most of it inline JS driving the whole quote lifecycle)
│   ├── purchasing.html       #   Purchasing Review screen
│   ├── admin.html            #   Admin Overview screen
│   └── quote_print.html      #   Standalone printable quote view (not extended from base.html)
├── static/
│   └── style.css             # All styling, hand-written, no framework (~480 lines)
└── data/                     # Runtime state — see §6 for exact schemas
    ├── parts_vmt_q1_2026.json
    ├── approvals.json
    ├── quotes.json
    ├── customers.json
    ├── sales_reps.json
    ├── site_access.json      # Site PIN + Flask session secret key - GITIGNORED, never commit (repo is public)
    └── reports/              # Generated CSV reports land here (created on demand, gitignore candidate)
```

---

## 5. The four screens

All routes live in `app.py`. Nav bar (`templates/base.html`) links all four.

### `/technical` — Technical Review
- **Viewing brand** dropdown (added 2026-08-16, defaults to JLT, `?view=` query param) shows
  one brand's platforms/options at a time - the catalog is 119 platforms across 4 brands now,
  too much to usefully show at once. Independent of the upload form's own Brand field below
  (that one picks the upload *target*, not which brand is currently being viewed).
- Checkbox-approve which vendor options are valid/buildable, **grouped by Platform →
  Category** within the selected brand. Only checked options become selectable on Sales - but
  see §7/§8: this only matters for `requires_review: true` parts (a not-yet-built third-party
  add-on path); every part from all 4 brands today is auto-approved and shows a checkmark
  instead of a checkbox.
- **Upload vendor spreadsheet** form: pick a Brand, upload that vendor's `.xlsx`. `app.py`'s
  `PARSERS` dict routes it to the matching parser (see §4) and merges the result into
  `parts_vmt_q1_2026.json`. New platforms/options land already selectable, not pending
  approval - see §7/§8 for why.
- A sticky "Save Approvals" bar (the page has ~500 checkboxes per brand; the button used to be
  unreachable without scrolling — now always visible) and a jump-to-platform nav scoped to
  the currently-viewed brand. **The approvals-save handler only replaces the viewed brand's
  entries in `approvals.json`, not the whole file** — added 2026-08-16 alongside the brand
  filter, since replacing the whole file would have silently deleted every other brand's
  approvals the moment the page stopped rendering all brands at once. If you ever change how
  the approvals form is submitted, keep that scoping (`approvals_brand` hidden field) intact.

### `/sales` — Sales Configurator
The big one. Top-to-bottom:
1. **Sales Rep** dropdown + 4-digit code, verified against `sales_reps.json`. **The entire
   rest of the page is disabled until this succeeds** — see §8, this is explicitly *not*
   real security.
2. **Customer** field — always directly typeable. Typing something new flashes a green
   **Accept** button (nothing saves until clicked, or Enter). A badge next to the label shows
   "Manual — not in HubSpot" (amber, Populate button shown) or "HubSpot Customer" (green,
   Populate hidden) based on **how the customer was selected this session** — Manual
   Customer + Accept vs. Customer Lookup — a client-only `customerSource` variable in
   `sales.html`, **deliberately decoupled from the record's real `source` field in
   `customers.json`** (decided by the user, 2026-08-16). Reasoning: there's no real HubSpot
   connector yet, so Customer Lookup is standing in for "pull from HubSpot" - picking a
   customer that way is meant to *look* like a real connected pull found it, even though the
   record itself is still just local `customers.json` data.
   - **This was a deliberate reversal of an earlier fix**, not an oversight — a 2026-08-15
     entry describes fixing exactly this "session-based badge" behavior in favor of the real
     `source` field, because picking an existing manual customer via Lookup was wrongly
     showing the "existing/real" badge. That concern doesn't apply here: Admin's "pending
     HubSpot link" report and `customers.json`'s real `source` field are **untouched** by
     this — they still reflect genuine data, so Admin reporting can still be tested against
     real manually-entered customers regardless of what the Sales page badge shows. If you
     touch this again, keep those two decoupled: the *badge* may lie for simulation purposes,
     the *stored data* must not.
   - **Customer Lookup** button: opens a live-filtered panel using the Customer field itself
     as the filter (no separate search box). Selecting a result sets `customerSource =
     "lookup"` unconditionally (see above) and skips the Opportunity ID "not connected to
     HubSpot" note (below) — the note only shows for the Manual path. **`/api/customers`
     excludes `source: "manual"` records from these results** (added 2026-08-17) — a customer
     created via Manual Customer is confirmed not to be in HubSpot, so a real HubSpot search
     wouldn't find them either; `source: "test"` stays included since those exist to exercise
     this exact panel. Does not affect Admin's "pending HubSpot link" report, which reads
     `customers.json` directly server-side, not through this endpoint.
   - **Manual Customer** button: just focuses/selects the field for typing.
3. **Opportunity ID** — free-text, manually entered (HubSpot deal ID stand-in). Exact-match,
   case-sensitive, no normalization — a typo creates a whole new opportunity silently. A
   blue "Select one →" hint badge appears once a customer is chosen but this is still empty.
   Next to it, a muted **"(Not connected to HubSpot — once connected, this step will search
   HubSpot for a matching open opportunity instead)"** note (added 2026-08-16) shows only for
   a Manual-path customer — see point 2 above; a Lookup-path (simulated HubSpot) customer
   skips it, since that path is already pretending to be connected.
   - **Populate** button: fills this field with the customer name as a starting point.
     Visible for **both** customer paths (Manual and Customer-Lookup/simulated-HubSpot) as of
     2026-08-17 - originally Manual-only, but there's no real HubSpot connector for the
     "lookup" path either, so hiding it there left no way to get an Opportunity ID at all
     short of typing directly into the field (a real dead end the user hit in testing). Once
     a real connector exists and can supply a genuine deal ID for "lookup" customers, that's
     when this should go back to Manual-only.
   - **Lookup Saved Quote** button: searches saved quotes by customer/opportunity/platform/
     quote ID, not just ones under whatever's currently typed here. **Scoped when the active
     customer came from Customer Lookup** (added 2026-08-17, per the user): results are
     limited to that customer's own quotes plus quotes belonging to customers not yet linked
     to HubSpot (`source: "manual"`) - a real HubSpot search wouldn't surface some *other*
     unrelated customer's quotes. A manually-typed active customer sees everything,
     unscoped, same as before this existed. Picking one of the "orphaned" (foreign-customer)
     results doesn't load/take over that quote - it **copies its configuration onto a new,
     not-yet-saved quote for the currently active customer** (`copyQuoteConfigToCurrentCustomer()`
     in `sales.html`) and leaves the Customer field, Opportunity ID, and the original quote
     record completely untouched (no save/update call ever references the source quote). The
     rep still has to supply their own Opportunity ID and Accept before this new quote can be
     saved. Picking a result that already belongs to the active customer loads/edits it
     normally, same as always.
   - **Existing-quotes panel** (below Opportunity ID, auto-shown whenever it's non-blank):
     **read-only informational text as of 2026-08-18** ("N existing quotes for this Opportunity.
     Saving now will create Quote #X, Rev 0. To view or revise an existing one instead, use
     'Lookup Saved Quote' above" - or, if a quote for this Opportunity ID is already loaded,
     "Editing <display_id>... Saving now will revise this quote"). Used to be a clickable
     `<select>` that loaded whichever quote you picked - removed after a real dead end the user
     hit live: populating an Opportunity ID with existing quotes, picking the existing one out
     of this panel (a reasonable guess for what new on-screen UI here was for) loaded that
     locked quote instead of starting a new one, silently disabling Save with no visible
     explanation. Loading/revising an existing quote is Lookup Saved Quote's job specifically -
     this panel's only job now is telling a rep what clicking Save is about to do, correctly for
     either case (new quote vs. revising whatever's currently loaded).
4. **Quote # / Rev #** readout boxes (auto-assigned on Save, not user-entered) + **Copy to
   New Opportunity** (opens an inline panel — new Opportunity ID + optional new Customer —
   clones the current config to a fresh quote lineage starting at Rev 0).
5. **Save / Lock / Print (PDF) / Upload / Email** action row. See §8 for the exact
   lock/rev-increment rules and which buttons require what.
6. **Brand** dropdown, **Platform** dropdown (filtered to the selected brand), **Search by
   Requirements** button (opens the modal described below).
7. Category dropdowns (Processor, RAM, Storage, Display, ports, Add-Ons, IP Rating, Power
   Cable, Wireless, OS — order fixed by `CATEGORY_ORDER` in `app.py`), live price totals,
   draft part number.
8. **Accept Configuration** button — Save is disabled until this is clicked; changing any
   option after accepting re-locks Save; the same reset happens after every successful save
   too (each save needs its own fresh Accept).
9. **Search by Requirements modal**: pick zero or more desired specs per category (optional,
   independent), optionally narrow by Brand, hit Search → every base unit whose
   **Technical-approved** options satisfy all selected criteria, radio list, Select loads
   that Brand+Platform into the main form to finish configuring and save. Matches on option
   *description text*, not code (codes aren't consistent across platforms).

### `/purchasing` — Purchasing Review
Two independent sections:
1. **Catalog pricing gaps** — every option missing any of the 4 price fields (Floor Price,
   MSRP, Cost, Current Cost), editable inline, "Save Prices" writes back to
   `parts_vmt_q1_2026.json`. "Upload pricing spreadsheet" bulk-applies a flat `.xlsx`/`.csv`
   in the same shape as "Generate Catalog Report" — **can only update existing parts, never
   create new ones** (that's Technical's job). "Generate Catalog Report" exports the gaps
   as CSV.
2. **What's been quoted to Sales — action items** — every saved quote's line items
   cross-checked against *current* pricing (not the quote's frozen snapshot), flagging
   exactly what's still missing before purchasing can sign off. Own CSV export.

Shared upload rule (`merge_parts()` in `app.py`): **a blank cell in an upload never erases a
value already on file** — only non-blank incoming values overwrite. This is what stops a
partial vendor refresh from wiping purchasing's manual price entries.

### `/admin` — Admin Overview
Stat cards + detail tables:
- Quotes created (count).
- Purchasing action items pending (same computation Purchasing uses — one source of truth).
- Platforms with base model reviewed (X / Y) + table of which ones aren't.
- Customers pending a HubSpot link (manually-created customers with no `hubspot_id`) + CSV
  report + a "Test customers" sub-section (seed/remove 5 fake customers for testing Customer
  Lookup — tagged `source:"test"` so they're excluded from the pending-link report).
- **Sales Reps** management: add (name + 4-digit code) / remove. This is where
  `sales_reps.json` gets edited.

---

## 6. Data model — exact JSON shapes

All files are in `data/`. None are schema-validated; these shapes are enforced only by
`app.py`'s code, not by anything structural. **`brand` was retrofitted onto an
already-running system** (2026-08-15) — every read path that keys on a part/approval/quote
now expects `brand` to be present; if you ever hand-edit these files or write a new ingest
path, don't forget it. **`requires_review` was retrofitted the same way** (2026-08-16, see
§7/§8) — every part record needs it now too.

### `parts_vmt_q1_2026.json` — the catalog
List of option records (**despite the filename, this now holds all brands** — it was never
renamed after the brand retrofit; renaming it plus updating the two `PARTS_FILE` references
in `app.py` would be a reasonable cleanup):
```json
{
  "brand": "JLT",
  "platform": "1014P",
  "category": "Base Unit:",
  "code": "14P",
  "description": "Rugged Fixed Mount Computer, JLT1014P, ...",
  "requires_review": false,
  "Floor Price": 2660,
  "MSRP": 5320,
  "Cost": 1700,
  "Current Cost": 1669.71,
  "attributes": {}
}
```
`Floor Price`/`MSRP`/`Cost`/`Current Cost` are `None` when unknown, a number when known, or
occasionally the literal strings `"Incl"` / `"NC"` (included / no charge) carried straight
from the vendor spreadsheet — client and server both parse these specially (`moneyValue()`
in JS, `money_value()` in Python) treating them as 0 for totals.

`requires_review` (added 2026-08-16): `false` means the part is from a manufacturer's own
official catalog and is selectable on Sales automatically - see `is_selectable()` in
`app.py`. Every brand ingested today (JLT/Winmate/Getac/CipherLab) sets this `false` on every
row. `true` is reserved for a not-yet-built third-party add-on ingestion path (RAM Mounts,
Gamber-Johnson, etc.) that will still need the `approvals.json` checkbox flow, since a mount
vendor's catalog doesn't self-certify fit with a specific host platform the way an OEM's own
spec sheet does. A part missing this key entirely is treated as `true` (needs review) - the
safe default, so nothing slips through unreviewed by accident.

`attributes` (added 2026-08-16, optional - only Getac/CipherLab rows set it): a free-form
dict of search-only metadata pulled from free text, for brands whose data doesn't decompose
into real per-category options (see §7). Keys in use today: `cpu`, `os`, `ram`, `storage`,
`display`, `wireless` (all six Getac-only, extracted from its description column - not
present anywhere in CipherLab's source data). Not selectable fields, not shown on Sales -
`app.py`'s `ATTRIBUTE_CATEGORY_MAP` is what lets Search by Requirements match against them as
if they were real Processor/OS/RAM/Storage/Display/Wireless options.

Currently 3,551 rows: 499 JLT, 1,060 Winmate, 370 Getac, 1,622 CipherLab.

### `approvals.json` — Technical sign-off
List of 4-element arrays: `[brand, platform, category, code]`. Presence in this list is what
makes an option selectable on Sales. Order/uniqueness not enforced beyond what
`compute_*` functions assume (treated as a set via `part_key()` matching).

### `quotes.json` — saved quotes
Dict keyed by `"{opportunity_id}::{quote_number}"` (this is `lineage_key()` in `app.py` —
**note the key does not include brand**, only opportunity_id+quote_number, so quote
numbering is scoped per-opportunity across all brands, not per-brand). Each value:
```json
{
  "opportunity_id": "CW-APMPERU",
  "customer": "Acme Corp",
  "quote_number": 1,
  "rev_number": 0,
  "locked": false,
  "ever_locked": false,
  "brand": "JLT",
  "platform": "1014P",
  "selections": [
    {"category": "Base Unit:", "code": "14P", "description": "...", "Floor Price": 2660, "MSRP": 5320}
  ],
  "floor_total": 2970.0,
  "msrp_total": 5840.0,
  "part_number": "1014P-14P-D-G-4-P-99-X-1-P-KM-255",
  "created_by": "Chad",
  "sales_rep": "Chad",
  "copied_from": "CW-APMPERU-1-0",
  "created_at": "2026-08-15T14:43:56",
  "updated_at": "2026-08-15T14:43:56"
}
```
`selections` is a **frozen snapshot** taken at save time (never Cost/Current Cost — those
never leave Purchasing). `created_by` is set once and never changes; `sales_rep` updates on
every save. `copied_from` only exists on quotes created via the Copy button. Display ID
shown everywhere is `f"{opportunity_id}-{quote_number}-{rev_number}"`.

### `customers.json` — local customer stand-in (no CRM yet)
List of:
```json
{"name": "Acme Manufacturing", "source": "test", "hubspot_id": null, "created_at": "2026-08-15T09:27:48"}
```
`source` is one of `"manual"` (typed by a rep and Accepted), `"test"` (seeded demo data via
Admin), or — not implemented — `"hubspot"` for a future real synced record. **The
Manual-badge/Populate-button UI logic on Sales treats anything that isn't `"hubspot"` as
needing the manual treatment** — so `"test"` customers behave identically to `"manual"` ones
in the UI, which is intentional.

### `sales_reps.json` — rep roster
List of:
```json
{"name": "Chad", "code": "8845", "created_at": "2026-08-15T08:54:20"}
```
Currently seeded with Chad/Glenn/Eric/Test (codes are the last 4 digits of their real cell
numbers, per the actual user's instruction — only the 4-digit codes are stored, never full
phone numbers). **This is not authentication** — see §8.

---

## 7. Multi-brand: what's built and what's real data (all 4 ingested as of 2026-08-16)

`BRANDS = ["JLT", "Winmate", "Getac", "CipherLab"]` (constant in `app.py`) is the fixed
roster shown in every Brand dropdown. All four now have a real parser (`app.py`'s `PARSERS`
dict routes Technical's upload form to the right one per brand) and real ingested data - see
`ingest/` in §4 for what each parser does. Total catalog: 3,551 parts (breakdown in §6).

Two genuinely different *kinds* of vendor data turned up, not just different spreadsheet
layouts of the same kind:

- **JLT, Winmate — real configurator matrices.** One sheet per platform, category/code/
  description rows, a rep picks one option per category and the app builds a part number.
  Winmate's layout looks like JLT's but isn't uniform: header row position varies 3-5 sheet to
  sheet, price-label spelling/order varies ("Floor" vs "Floor Price", Cost sometimes before
  Floor Price, sometimes no Floor Price column at all), and some sheets have a second flat
  "Accessories" section below the main matrix with a different column layout entirely. See
  `ingest/parse_winmate.py`'s docstring for the specifics; it's label-driven header detection,
  not position-anchored, because of this.
- **Getac, CipherLab — flat catalogs of already-fixed SKUs, not configurators.** Getac: 371
  rows, 10 platforms, each row a complete pre-built unit with one SKU and one price - no
  category column at all. CipherLab: ~1,624 rows across 61 product families (mostly barcode
  scanners/readers, a few Android mobile computers), same flat shape. **Decomposing either
  into independent per-category options would be wrong**, not just extra work - their rows
  are the *only* combinations the vendor actually sells, not one of many valid combinations
  the way JLT/Winmate's category options are. Both are ingested as **Base Unit:-only
  records** instead: one option per SKU, nothing else to configure. On Sales this means
  picking a Getac or CipherLab platform shows just a Base Unit dropdown (pick the exact
  pre-built SKU) with no category dropdowns below it - working as intended, not a missing
  feature.

**A real data-loss bug was caught and fixed during this ingest** (2026-08-16): the first pass
at Winmate's category-mapping table collapsed distinct raw categories (e.g. "Camera" and
"Data Collection:") onto the same canonical bucket ("Add On Options:"). Both used small reused
codes (`X`/`A`/`0`/`1`) that were only unique *within* their own original category - merging
the categories collided their codes on `(brand, platform, category, code)` and silently
overwrote one option with another on merge. Caught by checking for collisions before trusting
the parser output, not by inspection. Fixed by (1) not collapsing categories whose codes
aren't provably unique once merged, and (2) a same-category collision guard in
`parse_winmate.py` (`resolve_category()`) that suffixes a repeat as `"Data Collection: (2)"`
instead of losing it - real source pattern found on Winmate's MH4005 sheet, which nests four
independent yes/no choices (Barcode/Smart Card/Fingerprint/NFC reader) under one inherited
"Data Collection:" label with no sub-labels, separated only by blank rows. **If you touch
`category_map.py` or write a new vendor parser, verify zero `part_key()` collisions in the
parsed output before merging it into the live catalog** - it's a silent failure mode
otherwise, not one that throws an error.

**CPU cataloging, brand by brand** (the original ask that drove this ingest):
- **JLT, Winmate**: real `"Processor Options"` category, one row per selectable CPU - no
  extra work needed, it's just a normal category like any other.
- **Getac**: no category, but every description packs its full spec inline - extracted via
  regex into `attributes` on the Base Unit record (100% hit rate, 370/370 rows, on all six):
  `cpu` (`"Intel Core Ultra 5 225H Processor"`, `"AMD Ryzen AI 5 340 Processor"`, `"Qualcomm
  QCS6490"`), `os` (Windows 11 Pro vs Android 15), `ram` (`"16GB"`), `storage` (`"256GB"` /
  `"1TB"`), `display` (`'13.3" Full HD Touchscreen'`), and `wireless` (`"WiFi + BT"`, `"WiFi +
  BT + 4G LTE"`). See `ingest/parse_getac.py`'s `extract_*` functions.
- **CipherLab**: **no CPU data exists anywhere in the source file**, including the
  Android-based RK/RS mobile-computer families - they mention Android version + RAM, never a
  chipset. Nothing was fabricated to fill this gap; `attributes.cpu` is simply absent for
  CipherLab. `attributes.os`/`attributes.ram` are set where the description states them
  (~540 of 1,624 rows).

**Search by Requirements works across all 4 brands**, including the `attributes`-only ones -
this needed explicit wiring (`app.py`'s `ATTRIBUTE_CATEGORY_MAP`), since the search endpoints
originally skipped `Base Unit:` rows entirely (correct for JLT/Winmate, where Base Unit isn't
a "requirement" - but wrong for Getac/CipherLab, where the Base Unit *is* the only row that
has anything to search). A criterion on "Processor Options" or "Operating System:" now
matches either a real option description (JLT/Winmate) or a Base Unit's `attributes` value
(Getac/CipherLab).

**Matching granularity matters here and previously had a real bug (found and fixed
2026-08-17):** a Getac/CipherLab platform can have *several* `Base Unit:` rows - one per
sellable SKU, each with its own `attributes` - unlike JLT/Winmate, which have exactly one
Base Unit per platform. `api_search_base_units` originally grouped a platform's rows together
and checked attribute criteria against only the first row found, so a criterion only ever
matched whichever SKU happened to be first in file order for that platform - 14 of Getac's 22
distinct CPU values returned zero results as a result, despite coming straight from the same
search dropdown. Fixed by checking each Base Unit row individually per platform, requiring all
attribute criteria to be satisfied by the *same* row (checking each criterion independently
across different rows would wrongly match spec combinations no real SKU offers). The frontend
also now receives the matched row's `code` and passes it as `presetSelections` so "Select"
loads the exact SKU found, not the platform's default. See `ingest/parse_getac.py`'s docstring
and the 2026-08-17 CHANGELOG entry for the full writeup, including a related data bug (one CPU
silently split across two dropdown entries by a non-breaking-space artifact in the source file,
fixed by normalizing whitespace before extraction).

Verified live: searching "Processor Options" = "Intel Core Ultra 5 225H Processor" correctly
returns both Getac platforms that use it (B360G3, V120); searching a CPU that previously
returned zero results now returns real matches, and Select loads the exact matching SKU.

**Full audit across all 4 brands (2026-08-17, requested by the user after the Getac bug above):**
scripted every dropdown value from `/api/search_options` (1,362 brand-scoped values, the exact
same values a rep sees) through `/api/search_base_units` and confirmed each returns >=1 match
with a real part `code`. JLT (113 values), Winmate (502), and Getac (45, post-fix) came back
completely clean - 0 issues. **CipherLab had 160 dead-end values** (51 "Add On Options:", 109
"Operating System:") that always returned zero results no matter what, root-caused to the
source file itself: `CipherLab Price Increase effective 4_10_2026 Product List.xlsx` is a price
*increase* list, not a full catalog, so a product family whose base price didn't change (8600,
HERA51, and a batch of Wavelink/Ivanti software-license SKUs numbered 901/903/904/etc.) shows up
with only its accessories/warranties/licenses and **no `Base Unit:` row at all** - there's no
system in this file for those options to ever attach to. Fixed in `api_search_options` (`app.py`):
the dropdown now only pools option values from a (brand, platform) that has at least one
`Base Unit:` row among approved parts, so a search term that can never resolve to a system is
no longer offered as one. CipherLab's dropdown count dropped from 702 to 542 values (exactly the
160 dead-end ones removed); re-running the full audit afterward (1,202 brand-scoped values, plus
1,190 more via the unscoped "Any brand" pooling) came back at 0 issues everywhere.

**CipherLab is currently excluded from Search by Requirements entirely (per the user,
2026-08-17), on top of the per-value fix above** - until a fuller catalog replaces the current
price-increase-only source file, there's no point letting a rep search a brand where most
product families are known to be incompletely represented. `app.py`'s `SEARCH_EXCLUDED_BRANDS`
set (currently just `{"CipherLab"}`) is checked in both `/api/search_options` and
`/api/search_base_units`, so CipherLab can't surface via any path - a direct `brand=CipherLab`
request, or the unscoped "Any brand" pool. The same set is passed to `sales.html` as
`search_excluded_brands` so the search modal's Brand dropdown renders CipherLab as a disabled,
greyed-out option ("CipherLab (search unavailable)") instead of silently returning nothing if
picked. This is search-only - CipherLab still works normally on the main Brand/Platform/Base
Unit dropdowns for direct configuration. Meant to be temporary: remove the set (both usages) and
the template's `disabled` branch once a fuller CipherLab catalog is sourced and re-ingested.

Everything downstream of ingestion — Sales dropdowns, Purchasing pricing, quote records — was
already brand-agnostic and needed no changes.

**"Storage Drive Options:" search was split into two independent facets, "Storage Capacity"
and "Storage Technology" (per the user, 2026-08-17).** The real category still exists unchanged
on Sales/Technical (JLT/Winmate's actual selectable storage options are untouched) - this only
changes what a rep searches *on*. Reasoning, straight from the user: searching by capacity
shouldn't require caring about the underlying technology (SSD vs CFAST vs eMMC vs M.2, etc.),
and searching by technology (e.g. "M.2") should surface every drive of that type regardless of
capacity - a single flat dropdown of 48 distinct full descriptions (JLT+Winmate combined) could
do neither, since "64GB eMMC" and "64GB M.2 SSD" and "60 GB CFAST" were three unrelated exact-
match strings a rep had to already know to pick between.

New shared module `ingest/storage_facets.py` (`extract_storage_capacity`/
`extract_storage_technology`) does the splitting, used two different ways:
- **Getac** precomputes both as `attributes.storage`/`attributes.storage_tech` at ingest time
  (`ingest/parse_getac.py`), the same way it already does cpu/os/ram/display/wireless - the
  existing `_storage_clause()` isolates just the storage-related snippet of the description
  first (e.g. "256GB PCIe SSD" out of the full sentence) before classifying it, since the
  description also states RAM as a GB quantity earlier in the same string and a generic
  whole-description classifier would risk grabbing the wrong number.
- **JLT/Winmate** have no precomputed attributes on their real "Storage Drive Options:" rows,
  so `app.py` derives both facets from each option's description on the fly, at both dropdown-
  build time (`api_search_options`) and match time (`api_search_base_units`'s
  `real_category_met`, via the new `STORAGE_FACET_CATEGORIES` map) - kept in sync by construction
  since both call the same extractor functions.

Capacity normalization collapses the industry's "same tier, different rounding convention"
pairs into one canonical label - 60GB/64GB, 120GB/128GB, 240GB/256GB, 480GB/512GB, 960GB/1TB
are different vendors' marketing numbers for what's functionally the same capacity class, so a
search on either number now finds both (confirmed against the real data: 8 canonical tiers
covering all 48 distinct JLT/Winmate descriptions, `Storage Capacity` dropdown shows
16/32/64/128/256/512GB/1TB/2TB). Technology classification checks for M.2/mSATA/CFAST/eMMC/
Micro SD/NVMe/SSD (in that priority order - "M.2" wins even on a description that also says
"SSD"/"NVMe"/"SATA", since a rep filtering by M.2 wants every M.2 drive regardless of which of
those it also mentions); a description with no technology keyword at all (e.g. plain "128 GB")
is only findable via Capacity, which is intentional - nothing to search wrongly if the source
never said what it was made of.

Verified live and via direct API calls against the real catalog: searching Storage Technology =
"M.2" returns 14 matches spanning both JLT and Winmate platforms at every capacity from 64GB to
512GB (not narrowed to one capacity); searching Storage Capacity = "64GB" returns 27 matches
spanning SSD/eMMC/CFAST/M.2/unspecified technology (not narrowed to one technology).

**"Operating System:" search got the same treatment immediately after, for the same reason
(per the user, 2026-08-18): split into "OS Version" and "OS Edition".** The real data was
worse than storage's - 31 distinct "Any brand" OS descriptions mixed version, licensing/
servicing channel (Pro/IoT Enterprise/LTSC/LTSB/GAC/SAC), bit-width, and even a leftover CPU
model in a few rows (`"Windows 11 IoT Enterprise LTSC  i7-1185GRE"`) into one exact-match
string. New `ingest/os_facets.py` (mirrors `storage_facets.py`'s structure) extracts:
- **OS Version**: `Android 9/11/12/13/15`, `Windows 7/10/11`, `Linux Ubuntu 20.04` - dedupes
  cosmetic variants too (`Android 11` and `Android 11.0` become one value). CPU mentions
  elsewhere in the text are simply never matched by these patterns, so they're silently
  ignored rather than corrupting the version - that's Processor Options' job, a real field of
  its own.
- **OS Edition**: `GAC`, `SAC`, `LTSC`, `LTSB`, `IoT Enterprise`, `Pro`, checked in that
  priority order. Order matters for a real row: `"Windows 11 IoT Enterprise GAC (64-bit) -
  Microsoft has not released Win 11 IoT Enterprise LTSC yet"` mentions LTSC only to say it's
  *not* what this SKU is - checking LTSC before GAC/SAC would misclassify it. Confirmed correct
  against the real data (that specific row's platform shows under OS Edition = GAC, not LTSC).

Getac precomputes both via the same shared functions (`attributes.os_version`/`os_edition`,
fed its already-isolated `os` attribute rather than the raw description). JLT/Winmate derive
both on the fly from their real "Operating System:" option rows, same pattern as storage -
`FACET_CATEGORIES` (generalized from the old storage-only `STORAGE_FACET_CATEGORIES`) now maps
each synthetic search category to *both* which real category its options live under and which
extractor to use, since storage and OS pull from two different real categories.

OS Version sorts by family then numeric version ascending (`_os_version_sort_key`) rather than
plain string sort, which would put "Windows 7" after "Windows 10"/"Windows 11" and "Android 11"
before "Android 9" (character-by-character '1' < '9'). Verified live and via direct API calls:
`OS Version` dropdown shows `Android 9, 11, 12, 13, 15, Linux Ubuntu 20.04, Windows 7, 10, 11`
in that exact order; `OS Edition = GAC` returns exactly the 2 platforms that should have it,
correctly excluding the negated-LTSC-mention row from LTSC's results; full audit re-run at 0
issues across 618 brand-scoped values.

**"Processor Options" got a cleanup too (2026-08-18), but a different kind from storage/OS -
deduping near-duplicate spellings of the same real chip, not splitting into facets.** CPU model
names have no predictable structure to regex-extract from the way capacity/version do, so a
blind fuzzy-match risked merging two genuinely *different* chips - a real near-miss found while
auditing: "Qualcomm 660"/"Snapdragon 660" is a different, older SoC than "Qualcomm QCS6490",
despite both being "Qualcomm." `ingest/cpu_facets.py` does this in two tiers: a mechanical pass
that's always safe (strip ®/™, collapse whitespace, drop a trailing "(Optional)"/"No Longer
available" annotation) merges purely cosmetic duplicates on its own; a small hand-curated alias
table (8 groups, built by manually reviewing all 55 distinct real values and confirmed with the
user before merging any of them) handles the ones where only a human can safely confirm it's the
same chip - e.g. "Intel 6413E" and "Intel 6413E Elkhart Lake" (Elkhart Lake is Intel's codename
for the Atom x6413E). One pair deliberately left unmerged despite looking similar: "ARM 2 x A78
2.0GHz + 4 x A55 2.0GHz" and "ARM Genio 510 2 x A78 2.0GHz + 4 x A55 2.0GH" have identical core
configs (probably the same MediaTek Genio 510) but that core layout isn't unique to one SoC, so
it wasn't safe to assume. Per the user, the dropdown sorts the 8 curated/deduped labels first,
then everything else alphabetically after (`cpu_sort_key`). 55 raw values collapsed to 40
distinct search values (Any-brand pool, spanning all 4 brands); full audit re-run at 0 issues
across 607 brand-scoped values. Getac's own `attributes.cpu` values are untouched by this - they
were already clean (verified during the earlier Getac audit) - this only affects JLT/Winmate's
real per-SKU "Processor Options" rows, matched via the same `FACET_CATEGORIES` mechanism as
storage/OS (mapped to itself: `"Processor Options": ("Processor Options", normalize_cpu_label)`,
since this is a dedup, not a split into two categories). Verified live: the search dropdown
shows the 8 canonical labels first (e.g. "Intel Atom x6413E (Elkhart Lake)"), searching one
returns real matches spanning every platform whose raw description used to be a different
near-duplicate spelling (7 matches across 1014P/1214N/1214P/1514N/6012/6015/VM1007E FM07E for
the x6413E group, previously split across up to 5 separate unmergeable search terms).

**"Internal Wireless" got a WWAN Generation/WWAN Carrier split too (2026-08-18), but ADDED
alongside the original flat field rather than replacing it - a real design difference from
storage/OS/CPU.** Per the user: WWAN/cellular info is jumbled together with WiFi/Bluetooth/GPS
in the same free-text description (109 distinct real values), and the carrier/module should be
searchable separately from WWAN generally, the same pattern as Storage Capacity/Technology. The
key difference from storage/OS: a single "Internal Wireless" description can simultaneously
encode WiFi standard (802.11ac/ax/etc), Bluetooth version, GPS, *and* cellular all at once (e.g.
`"WLAN (802.11 a/b/g/n/ac) + BT 5.0 + GPS 4G Sierra EM7455"`) - removing the flat field the way
storage/OS's raw categories were removed would have lost real search capability (a rep searching
by WiFi standard or Bluetooth version alone). So `ingest/wwan_facets.py`'s two new facets are
*added* alongside "Internal Wireless," which still lists all 109 raw descriptions unchanged.
New `_KEEP_RAW_ALONGSIDE_FACETS` set in `app.py` (currently just `{"Internal Wireless"}`) marks
which real categories get this "facets plus the original" treatment instead of full replacement
- everything else in `FACET_CATEGORIES` still fully replaces its real category as before.

- **WWAN Generation**: 3G/4G/5G, extracted by simple priority-ordered substring match
  (LTE counts as 4G).
- **WWAN Carrier**: named US carriers (AT&T/T-Mobile/Verizon, present on Intel Wireless
  8265/AX210 module SKUs) or a specific cellular module part number (Telit LN920/FN990, Sierra
  EM7455/EM7411/EM9291/EM7595, Sierra MC7455/MC7411, Quectel RedCap, MediaTek, HUAWEI).
  Deliberately does NOT merge EM7455/MC7455 or EM7411/MC7411 - different Sierra Wireless part
  numbers (M.2 vs mini-PCIe form factor), and nothing in the source text confirms they're
  interchangeable for search the way "Elkhart Lake" confirmed two CPU spellings were the same
  chip. A row with a generation but no named carrier/module (common - many just say "4G" or "5G
  WWAN" with nothing more specific) is only findable via Generation, same pattern as an untagged
  storage/OS description.

Getac's own `attributes.wireless` values are untouched by this - already simple/clean (a handful
of values like `"WiFi + BT + 5G Sub-6"`), and this only affects JLT/Winmate's real per-SKU
"Internal Wireless" rows. Full audit re-run after the change: 0 issues across 628 brand-scoped
values (Internal Wireless itself still has all 109 original values - nothing was lost). Verified
live and via direct API calls: `WWAN Generation` dropdown shows `3G, 4G, 5G`; searching
`WWAN Generation = "5G"` alone returns 6 real matches across platforms with different exact raw
wording; searching `WWAN Carrier = "AT&T"` returns 12 matches; the original exact-match
`Internal Wireless` search still works unchanged (verified against a real Getac value).

---

## 8. Non-obvious rules worth knowing before you touch this

- **Manufacturer-catalog options don't need Technical approval; third-party add-ons will.**
  Decided by the user 2026-08-16: an option from a vendor's own official price book
  (`requires_review: false` - every part from all 4 brands today) is auto-selectable on Sales,
  no checkbox needed - the vendor already publishes it as valid and sellable. This is
  `is_selectable()` in `app.py`, not the plain `part_key(p) in approvals` check the Technical
  checkbox flow used to be the *only* gate for. `approvals.json` / the Technical checkbox UI
  still exist and still matter, but only for `requires_review: true` parts - reserved for a
  not-yet-built third-party add-on ingestion path (RAM Mounts, Gamber-Johnson, etc.), since a
  mount vendor's catalog doesn't self-certify fit with a specific host platform the way an
  OEM's own spec sheet does. A part missing `requires_review` entirely defaults to `true`
  (safe default). If you add a new ingestion path, decide deliberately which value it needs -
  don't just copy whichever existing parser is closest without checking.
- **Every change must be logged with author attribution.** Read `AGENTS.md` before making
  changes. Update `CHANGELOG.md` in the same branch or pull request for every code,
  configuration, data, or documentation modification. Changes made by OpenAI Codex use
  `**[Codex]**`; other people or agents must use their own clear attribution.
  Any necessary work identified but not completed—including an open PR still awaiting merge—must also be added to `CHANGELOG.md` under `Pending / TODO` and cleared with a dated, attributed entry when completed.
- **Sales Rep verification is bookkeeping, not security.** A 4-digit code with no lockout,
  no hashing (stored plaintext in `sales_reps.json`), 10,000 possible combinations. It exists
  purely so a quote records who touched it. Don't let anyone mistake it for access control.
- **Site Access PIN is a soft gate, also not real security.** A single shared 4-8 digit PIN
  (`before_request` hook in `app.py`, checked against `data/site_access.json`) protects every
  page and every `/api/*` route from casual access — meant for "don't let a random person who
  finds a shared tunnel link poke around," not real auth. `data/site_access.json` holds both
  the PIN and the Flask session secret key, is auto-generated on first run, and is **gitignored
  on purpose — this repo is public on GitHub, so that file must never be committed.** If you
  ever regenerate `.gitignore` or restructure `data/`, keep that entry.
- **Quote lock/rev rules:** a quote gets its Quote# the first time it's saved (Rev 0).
  **Every successful Save locks the quote** (added 2026-08-17, per the user — was previously
  a separate manual toggle/Print-only) — a saved quote is treated as "this is what I'm
  proposing right now," protected from accidental further edits. This applies to the very
  first save too, not just revisions. Category dropdowns are disabled while locked (existing
  behavior, unchanged). To make another change: click **Unlock** (enabled immediately after
  a fresh save, since `dirty` is false at that point — no extra step needed to make it
  clickable), edit, Accept, Save — which locks it again. **Saving an already-saved quote
  bumps Rev by 1 whenever the configuration actually changed** (`selections`/`brand`/
  `platform` differ from what's stored), independent of the lock state at save time (the
  quote is always locked going into a save now, so the old "only bump if ever locked" rule
  became meaningless the moment auto-lock shipped — replaced with a real content-diff
  check). A no-op re-save (nothing actually different) does not bump Rev, so clicking
  Accept+Save twice with no real edit in between is harmless. **Only the current state of
  each quote is stored — there is no revision history.** Rev 0's content is gone the moment
  Rev 1 is saved over it. This is called out as a known gap in CHANGELOG's Pending list.
  Verified live end-to-end 2026-08-17: load quote → locked:false → change option → Accept →
  Save → locked:true, rev bumped, Unlock button immediately clickable → Unlock → dropdowns
  re-enabled → change again → Accept → Save → locked again, rev bumped again.
- **Accept Configuration** (Sales) is a *separate* gate from rep verification — Save needs
  both. It resets on any option change AND after every successful save (so *every* save,
  first or fifth, needs a fresh click). This was an explicit request, not an assumption.
- **Cost / Current Cost never leave Purchasing.** Not in quote snapshots, not in the printable
  view, not in the Excel export, not sent to the Sales-page JS at all
  (`CUSTOMER_FACING_PRICE_FIELDS = ["Floor Price", "MSRP"]` in `app.py` is the enforcement
  point — grep for it before adding any new customer-facing price display).
- **Uploads never erase with blanks** — re-read §5's Purchasing section. This is the fix for
  a real, previously-flagged data-loss risk; don't regress it if you touch `merge_parts()`.
- **Opportunity ID matching is exact-string, case-sensitive, not normalized.** A rep who
  types the same opportunity two different ways silently gets two different quote lineages.
  Flagged, not fixed.
- **`window.prompt()` is banned in this codebase** — it was used originally for
  Manual-Customer and Copy, and both broke silently in some browsers (prompt dialogs are
  increasingly blocked/suppressed with no error). Both were rebuilt as real inline UI. If
  you're tempted to reach for `prompt()`/`alert()`/`confirm()` anywhere in `sales.html`,
  don't — build an inline field or panel instead, same pattern as Customer/Copy/Search.
- **Any custom button-styled widget needs an explicit `color`, not just `background`.**
  `button, .btn` sets a global `color: white`; a widget that only overrides `background:
  white` (like `.wselect-trigger` did, fixed 2026-08-17) silently inherits white text on a
  white background - invisible, not broken in any way the DOM/console shows (text is present,
  computed style just matches the background). **This bug was specifically invisible to
  casual testing**: `.wselect-trigger` only renders this way once Sales Rep is verified
  (before that it's `:disabled`, which has its own correct color) - testing that never
  verifies a rep won't catch it. If you add a new custom form control anywhere in this app,
  check its computed `color` in the *enabled* state, not just that it renders at all.

---

## 9. HubSpot / Jeeves — what stands in for them today

Nothing is connected. Every place a real integration will eventually plug in has an explicit
placeholder, not a silent gap:
- **Opportunity ID**: manually typed (§5/§8).
- **Customer**: local `customers.json` with a `source`/`hubspot_id` field ready for real data
  once a connector exists (§6) — `hubspot_id` is never set by anything today.
- **Upload button** (Sales, per-quote): calls a real endpoint
  (`/api/quotes/.../upload`) that always returns
  `{"status": "not_connected", "message": "HubSpot isn't connected yet..."}`. The button and
  wiring exist; there's nothing on the other end.
- **Email button** (Sales): downloads the real Excel export and opens the real printable
  view, but does not send anything — there's no SMTP/Outlook integration in the app itself.
- **Jeeves** (JLT's accounting/inventory system — exact product name still unconfirmed per
  the original brief): Purchasing's manual price-fill workflow is the stand-in. No connector
  research has happened in this codebase at all.

---

## 10. Known limitations / risks

- **No database, no concurrency control.** Two people editing `data/*.json` at the same
  time (e.g. two Purchasing users saving prices simultaneously) will silently last-write-wins
  clobber each other. Fine for one Box-synced folder used by a handful of people today; will
  need real locking or a DB if usage grows.
- **Flask dev server**, not production WSGI (`app.run(debug=True)` in `app.py`'s `__main__`
  block). Fine for internal prototype use, not for anything internet-facing.
- **No automated tests.** Everything in this project has been verified by hand (curl,
  browser automation, direct JSON inspection) during development, not via a test suite.
  There is no `tests/` directory.
- **`.claude/launch.json`** is specific to the Claude Code tool's browser-preview feature —
  irrelevant to running the app normally, safe to ignore or delete if not using that tool.
- **No `.gitignore`** exists yet — worth adding one for `__pycache__/`, `data/reports/`, and
  possibly the `data/*.json` runtime files themselves (open question: should real
  quote/customer/pricing data be committed to git at all, or should `data/` be seeded once
  and then gitignored so it doesn't pollute history with every price edit? Not decided —
  flagging for whoever picks this up).

---

## 11. Pending / TODO — canonical location and handling

The live, complete task list is the `## Pending / TODO` section at the top of
`CHANGELOG.md`. **Read that section directly before beginning work.** Do not assume a TODO
mentioned elsewhere in this handoff is still open, and do not maintain an independent
"complete" list here because duplicate lists drift.

At the time of this update, the changelog tracks integration work (HubSpot, Jeeves, email,
and vendor ingestion), quote revision history, storage/concurrency and production-readiness
work, test-data cleanup, and the spreadsheet-ingestion risks identified by Codex. The changelog contains the authoritative status and next action for
each item.

When new work is discovered, update `CHANGELOG.md` → `Pending / TODO` immediately if it
will not be completed in the same change. When work is completed, record the result under
the current date with author/agent attribution and close or revise the corresponding TODO.

---

## 12. If you're recreating this from zero

Order that actually worked, in case the file tree above isn't enough context on its own:

1. Parse one vendor spreadsheet into normalized JSON (`ingest/parse_vmt.py`) — prove the
   ingest step works standalone before building any UI on top of it.
2. Build Technical (approve options), Sales (pick approved options, see live price), and
   Purchasing (flag missing prices) as three thin screens against that JSON — no quote
   persistence yet, just live calculation.
3. Add quote persistence (save/load), then lock/rev semantics, then Print/Email/Upload
   stubs, then Copy — each as its own testable slice.
4. Add Customer and Sales Rep concepts, including the "not real security" rep-gate and the
   Manual-vs-Lookup customer source tracking (get the *source of truth* right here — the
   Populate-button bug in this build happened because client-side "how was this selected"
   and server-side "what is this record's real source" were conflated for a while; use the
   server's `source` field as ground truth from the start).
5. Retrofit Brand as a first-class field last, once the single-vendor version is solid — it
   touches every data file and nearly every function, so validate the single-brand version
   thoroughly first (this build did it in that order and the migration was mechanical once
   the JLT-only version worked).
6. Search by Requirements was the last major feature — it's a pure read-side feature
   (matches Technical-approved data, writes nothing) and slotted in cleanly on top of
   everything else.
