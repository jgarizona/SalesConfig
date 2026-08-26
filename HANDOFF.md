# JLT Inside-Sales Configurator — Handoff Brief

Written 2026-08-15 for handing this project to another agent/developer. Goal: everything
needed to understand, run, extend, or fully recreate this project without access to the
conversation that built it.

## 0a. Review checkpoint — read and act on this before anything else

**Last reviewed up to:** HEAD `671f354` — by Claude Code — 2026-08-25 20:40 -0500

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
CipherLab, 2,536 parts total as of 2026-08-25, see §7). No database, no auth, no HubSpot — all
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
│   ├── parse_cipherlab.py    # CipherLab parser - rewritten 2026-08-25 for the new source
│   │                          # workbook's shape (one sheet per device platform, a real
│   │                          # per-position option "legend" decoded into `attributes`, a
│   │                          # "Terminal Kit" table of real released SKUs, flat accessory
│   │                          # sections below it - see the file's own docstring for the full
│   │                          # row-classification rules). Still Base-Unit-only per SKU, same
│   │                          # reasoning as Getac - the Terminal Kit table lists only the
│   │                          # combinations CipherLab actually released, not a pick-your-own
│   │                          # matrix.
│   └── category_map.py       # Shared by the Winmate parser (only): maps each vendor's raw
│                              # category label to app.py's canonical CATEGORY_ORDER vocabulary
│                              # so cross-brand sort/search line up. Deliberately does NOT
│                              # collapse categories whose raw codes aren't globally unique
│                              # within a platform (see §6/§7 - this caused real, once-silent
│                              # data loss during ingest before it was caught). Those
│                              # deliberately-uncollapsed categories (CANBUS/DIDO/LAN/Camera/
│                              # Data Collection:/Data Collection: (2), plus JLT's own Dock)
│                              # are left to "just sort last" per this file's own docstring,
│                              # unsearchable via Search by Requirements (which only offers
│                              # categories listed in CATEGORY_ORDER) - and per the user
│                              # (2026-08-19), that's intentional: these narrow, collision-prone
│                              # categories should stay out of both Search and Technical's "Add
│                              # a new option" dropdown (see §5), not get added to
│                              # CATEGORY_ORDER. An earlier same-day attempt did add them to
│                              # CATEGORY_ORDER, which wrongly changed Search too - reverted.
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
- **"Add a new option" form** (added 2026-08-18, reworked 2026-08-19 after live user feedback)
  - a technician can add one new option by hand for a valid vendor-qualified configuration
  that isn't in the current vendor spreadsheet snapshot (e.g. a WWAN Card add-on for a
  platform whose price book doesn't list one). `action=add_option` in `technical()`. Always
  `requires_review: true` and create-only per platform (an existing `(brand, platform,
  category, code)` is skipped and reported, not overwritten - unlike the bulk upload path
  above, which does merge/overwrite on purpose).
  - **Vendor** is a real `<select>` (`add_brand`); **Platform** is a checkbox list
    (`add_platforms`, `request.form.getlist`) scoped to whichever Vendor is selected via a
    small JS toggle (`onAddVendorChange()` in `technical.html` - one platform-checkbox group
    per brand is always rendered server-side, only the matching one is `display:flex`, the
    rest `display:none`) - lets a technician add the same option to several platforms in one
    submission, and creates one part row per checked platform, partial-success-safe (a
    platform that already has that exact code is skipped and reported separately, the rest
    still get created). **Category** is a `<select>` populated from `all_categories` in
    `app.py` - **`CATEGORY_ORDER` itself (minus its search-only pseudo-categories), not every
    real category name used anywhere in the catalog.** An earlier same-day version drew this
    list from raw catalog data instead, which pulled in Winmate's narrow, deliberately-
    uncollapsed pass-through categories (CANBUS/DIDO/LAN/Camera/Data Collection:/Data
    Collection: (2), JLT's Dock - see `ingest/category_map.py`'s note in §4) as choices for a
    *new* option, which the user flagged as wrong - those stay out of both this dropdown and
    Search by Requirements on purpose.
  - **No price fields at all** (removed 2026-08-19, per the user - "Technical people should
    never do anything with price") - `add_option` always creates Floor Price/MSRP/Cost/Current
    Cost as `None`/blank unconditionally, doesn't even read them from the request.
  - No template changes were needed to make a new row show up in the right category box - the
    page already groups by real `category` via a stable sort on `CATEGORY_ORDER` position
    (`plist.sort(key=lambda p: (category_sort_key(p["category"]), p["code"] or ""))`), so any
    row that exists with the right `(brand, platform, category)` renders correctly
    automatically. The new `jeeves_part_number` field (see §6) stays optional - the point is
    exactly that a technician can add something before Purchasing has priced it or assigned it
    a real part number, and Purchasing's Dashboard/warnings (see below) are what surface that
    gap once the option actually gets quoted.
  - **Watch for this CSS trap if you touch this template again**: a `style` attribute with two
    declarations for the *same* property (e.g. a conditional `display:none;` followed by an
    unconditional `display:flex;`) always resolves to the *last* one, regardless of the
    condition - this silently broke the Vendor→Platform-group toggle once already (every
    vendor's platforms showed at once). Make the whole property value conditional in one
    declaration instead of stacking two.

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
Top of page: **Export Pricing Sheet**, **View Report**, **Part # Compare**, **$ Jeeves
Compare** buttons and a **Jump to §2** anchor link, all reachable with zero scrolling
regardless of how big the catalog gets. Every button has a `title` hover tooltip explaining
what it does (same convention already used elsewhere - Sales' HubSpot badge, the disabled
search-brand option - not a new pattern).

**Dashboard** (added 2026-08-18, above the button row): 5 stat cards - Missing Jeeves Part #/
Floor Price/MSRP/Cost/Current Cost. Deliberately scoped to **quoted line items only**
(`compute_quote_action_items()`/`compute_quote_action_item_counts()` in `app.py`, shared with
§2 below so the numbers can never drift apart), not the whole 3,551+-part catalog - the user
confirmed that scope explicitly, since §1 below already covers whole-catalog price gaps and
this dashboard exists to answer a different question ("what have we actually promised a
customer that isn't fully priced/numbered yet," not "what's incomplete in the catalog at
large"). A part missing `jeeves_part_number` shows up here the moment it's quoted, which as of
2026-08-18 is *every* quoted line (the field is brand new, nothing has one yet) - that's
accurate, not a bug, and the count will fall as Purchasing assigns real ones.

Two independent sections below that:
1. **Catalog pricing gaps** — every option missing any of the 4 price fields (Floor Price,
   MSRP, Cost, Current Cost). **No inline editing** (removed 2026-08-18 - see history below) -
   the only ways to see or change these are:
   - **View Report** (`GET /purchasing/pricing_gaps`,
     `templates/purchasing_pricing_gaps.html`) - read-only table, no form, no inputs.
   - **Export Pricing Sheet** / **Generate Catalog Report** (same action, appears at top of
     page and top of §1) - downloads a CSV in upload-ready format.
   - **Upload pricing spreadsheet** - now a **two-step preview-then-confirm** flow (added
     2026-08-18), not immediate-apply. Uploading parses the file and dry-runs
     `merge_parts()` against a `copy.deepcopy(parts)` to show real "N will update, M will
     skip" counts *before* anything is saved - nothing touches `parts_vmt_q1_2026.json` at
     this point. The already-parsed rows are stashed as JSON in
     `data/pending_imports/<token>.json` (gitignored, mirrors `data/reports/`). **Continue**
     (`action=confirm_import`) re-loads that JSON, runs the real merge against the live
     `parts` list, saves, and deletes the temp file. **Cancel** (`action=cancel_import`)
     just deletes it - nothing applied. No expiry/cleanup job for an abandoned preview
     (same as `data/reports/*.csv` already has none) - an ignored preview just leaves a
     small orphaned JSON file. **Can only update existing parts, never create new ones**
     (that's Technical's job) - unchanged from before.
   - **Part # Compare** / **$ Jeeves Compare** - stubs (see `/purchasing`'s Jeeves section
     in CHANGELOG.md's Pending/TODO for what they'll do once Jeeves access exists).
2. **What's been quoted to Sales — action items** — every saved quote's line items
   cross-checked against *current* pricing (not the quote's frozen snapshot), flagging
   exactly what's still missing before purchasing can sign off. Own CSV export, "Generate
   Report" button lives above the table.

Generated reports (`report_generated`/`quotes_report_generated`) are real downloads via
`/purchasing/download/<filename>` — previously the filename was shown as plain text with no
way to actually get the file from a browser. Path is validated against `REPORTS_DIR` to
block `../` traversal.

**History worth knowing before touching this page again - why it's built this way, not
just "how":** §1 used to be an inline-editable table (one `<form>`, one row per flagged
part x 4 price-field inputs - ~17,000 fields against the real 3,421-row catalog).
2026-08-18, in order: (1) that form had a hidden `action=save_prices` default competing
with a same-named "Generate Catalog Report" button - Flask resolves duplicate form keys to
whichever comes first in *document order*, not whichever control was clicked, so the report
button silently ran `save_prices` instead of generating anything, for as long as the page
had existed; (2) fixing that (every button needs its own explicit
`name="action" value="..."`, no shared hidden default) surfaced a live 413 - the ~17,000-field
form exceeds Werkzeug 3.x's default `max_form_parts=1000` safety limit, meaning **Save
Prices itself, not just the report button, had been completely broken for the full table**;
raised via `app.config["MAX_FORM_PARTS"]`/`["MAX_FORM_MEMORY_SIZE"]` (still set, harmless to
leave even though nothing needs them now) as a same-day fix; (3) rather than keep raising
limits as the catalog grows, the whole inline-editing model was replaced with the
export/view/import-with-preview design described above, which has no giant form at all.
Also during this: a test payload submitted directly against the live `save_prices` route
(checking whether the 413 fix worked) actually overwrote real Floor Price/MSRP/Cost across
all 3,421 rows with `null` before being caught via `git diff` and reverted - **when testing
any of this page's POST routes directly (test client, curl, etc.), always diff
`data/parts_vmt_q1_2026.json` before and after**, since none of these actions have a
confirmation step except the import flow's Continue/Cancel built specifically to solve that.

Shared upload rule (`merge_parts()` in `app.py`): **a blank cell in an upload never erases a
value already on file** — only non-blank incoming values overwrite. This is what stops a
partial vendor refresh from wiping purchasing's manual price entries. `merge_parts()` never
calls `save_parts()` itself - the caller does - which is exactly what makes it safe to
dry-run for the import preview (call it against a deep copy first, discard the result).

### `/admin` — Admin Overview
Stat cards + detail tables:
- Quotes created (count).
- Purchasing action items pending (same computation Purchasing uses — one source of truth).
- Platforms with base model reviewed (X / Y) + table of which ones aren't.
- Customers pending a HubSpot link (manually-created customers with no `hubspot_id`) + CSV
  report + a "Test customers" sub-section (seed/remove 5 fake customers for testing Customer
  Lookup — tagged `source:"test"` so they're excluded from the pending-link report).
- **Sales Reps** management: add (name + 4-digit code) / remove / **Lock-Unlock** / **Reset
  PIN** (the last two added 2026-08-18 - see §8). This is where `sales_reps.json` gets edited.
- **The Purchasing PIN** (added 2026-08-18): view/change the second PIN gating Purchasing -
  see §8 for the full mechanism.

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
  "attributes": {},
  "jeeves_part_number": null
}
```
`Floor Price`/`MSRP`/`Cost`/`Current Cost` are `None` when unknown, a number when known, or
occasionally the literal strings `"Incl"` / `"NC"` (included / no charge) carried straight
from the vendor spreadsheet — client and server both parse these specially (`moneyValue()`
in JS, `money_value()` in Python) treating them as 0 for totals.

`jeeves_part_number` (added 2026-08-18) is `None`/absent on every part ingested from a vendor
spreadsheet - no automated mapping to Jeeves exists (checked directly against a real Jeeves
export: zero overlap between JLT's option `code` and Jeeves' `USItem#`, only 3/125 exact
description matches - Jeeves tracks much more granular internal BOM/component part numbers
than JLT's price-book codes, see CHANGELOG.md's 2026-08-18 entry for the full finding). It's
only ever set today via Technical's "Add a new option" form (see §5), and is what Purchasing's
Dashboard counts as "missing" for quoted line items - existing parts don't need a migration
to add this key, every read path uses `.get("jeeves_part_number")`.

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

Currently 2,536 rows (2026-08-25): 719 JLT (499 from the original vendor ingest + 220 added
by hand via Technical's "Add a new option" - 60 accessory add-ons + 160 WWAN Card entries, see
§5/§8), 1,060 Winmate, 370 Getac, 387 CipherLab (replaced entirely 2026-08-25 - see §7's
"Resolved 2026-08-25" note for why the count dropped from the old 1,622).

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

`hubspot_deal_id`, `hubspot_line_item_ids`, and `hubspot_notes` (added 2026-08-25, all
optional/absent until the dormant HubSpot code in §9 is actually wired up and used) — set by
`api_quote_hubspot_push`/`_attach_export`/`_attach_file` in `app.py` once a rep has pushed this
quote's line items to a HubSpot Deal or attached a file to it. `hubspot_notes` is a list, since
a quote can have both the pricing export and the rep's final document attached at different
times; each entry records `note_id`, `file_id`, `filename`, `sent_at`. No read path depends on
these existing today — they're additive, same treatment as `jeeves_part_number` got.

`revisions` (added 2026-08-25, resolves the "quote revision history" limitation that used to
be listed in `CHANGELOG.md`'s Pending/TODO): a list of snapshots, one per real revision this
quote has ever had, built by `revision_snapshot()` in `app.py` and appended to on every save
that actually changes `selections`/`brand`/`platform` (a no-op re-save doesn't add one). Each
entry is `{rev_number, customer, brand, platform, selections, floor_total, msrp_total,
part_number, sales_rep, updated_at}` — deliberately excludes `locked`, since that's a
current-quote-level concept, not something meaningful per historical revision. Backfilled
lazily: a quote saved before this feature existed gets `revisions: [snapshot of its current
state]` seeded the next time it's edited, so history is real and complete from that point
forward — whatever was already overwritten before this landed can't be recovered, and never
will be for quotes that are never touched again. Sales' revision browser (next to Copy to New
Opportunity: two arrow buttons + a "Rev N (i/total)" label, plus Up/Down/Left/Right arrow keys
- Left acts as Down, Right acts as Up, both wrap at either end) fetches this via `GET
/api/quotes/<opportunity_id>/<quote_number>/revisions` and is purely a read-only look back —
browsing never touches `loadedQuote` or the live category dropdowns. It shows a summary panel
for whichever revision the arrows currently point to, **always, including the latest one**
(an earlier same-day version hid it at the latest revision on the assumption the main page
already showed that data — wrong the moment a rep edits something, since the main page then
shows the new unsaved values instead; the user caught this live and it was corrected the same
day, see `CHANGELOG.md`). When Accept Configuration produces a real change from what's saved,
a second block appears directly beneath the first, in the identical format, showing the new
unsaved draft — the two stacked together are the actual before/after comparison a rep needs
before deciding whether to Save. `renderSummaryArea()` in `sales.html` is the single function
behind both blocks; there is deliberately no more than one "read-only config summary"
implementation on this page.

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

### `purchasing_warnings.json` — standing acknowledgeable notices (added 2026-08-18)
List of:
```json
{
  "id": "bf4186af9691f39f",
  "message": "Jeeves Part Number can't be auto-matched from the JLT price book...",
  "created_at": "2026-08-18T23:21:42",
  "acknowledged": false,
  "acknowledged_at": null
}
```
Auto-created on first run (`load_or_create_purchasing_warnings()` in `app.py`, same pattern as
`load_or_create_site_access()`) with one seed warning about the Jeeves USItem#/description
mismatch finding. Shown as an amber banner at the top of Purchasing with an **Acknowledge**
button per warning (`action=acknowledge_warning`) - acknowledging sets `acknowledged: true` +
a timestamp, it's never deleted. Admin shows a live count of unacknowledged ones as its own
stat card. **Tracked in git, not gitignored** - unlike `site_access.json` (a secret) or
`pending_imports/*.json` (ephemeral), this is real durable application state like
`sales_reps.json`.

---

## 7. Multi-brand: what's built and what's real data (all 4 ingested as of 2026-08-16)

`BRANDS = ["JLT", "Winmate", "Getac", "CipherLab"]` (constant in `app.py`) is the fixed
roster shown in every Brand dropdown. All four now have a real parser (`app.py`'s `PARSERS`
dict routes Technical's upload form to the right one per brand) and real ingested data - see
`ingest/` in §4 for what each parser does. Total catalog: 2,536 parts (breakdown in §6).

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

**Resolved 2026-08-25 (per the user - the old source data was "wrong" and replaced entirely,
not merged):** `CipherLab Price Increase effective 4_10_2026 Product List.xlsx` (the flat,
61-family, price-increase-only source described in the three paragraphs above) and every part
row it produced were deleted outright - all 1,622 old CipherLab rows removed from
`parts_vmt_q1_2026.json`, nothing kept. Replaced with a new source workbook, `CipherLab USA
RS38 Price Book 8062025 with formula.xlsx`, structurally nothing like the old one: one sheet per
device platform (RK26, RK95, RS36, RS38) carrying a real per-position option "legend"
(Wireless/RAM+ROM/Barcode Reader/Camera/Battery/Package/GMS/Control Code, plus Keypad on RK95),
each SKU's product code broken into those same codes column-for-column, plus three flat
license/service sheets (904R ReMoCloud, 90W Android-upgrade licenses, 90R OCR) with no Base Unit
rows at all - covers only 4 real device platforms, versus ~61 before, but every platform it does
cover is now completely represented (every dropdown value resolves to a real SKU). New
`ingest/parse_cipherlab.py` (full rewrite, see its own docstring for the row-classification
rules) decodes the legend into `attributes` matching `ATTRIBUTE_CATEGORY_MAP` (`cpu`, `os`/
`os_version`, `ram`, `storage`, `display`, `wireless`, all populated from real per-SKU legend
values, not regex guesses over one flat description) plus three CipherLab-only extras not yet
wired into search (`scanner`, `camera`, `battery`) - harmless if search never uses them, ready if
it does.

**Corrected same day, per the user, after seeing 904R/90W/90R rendered as selectable "systems"
on Sales:** they aren't real systems, they're license/service SKUs. 904R (ReMoCloud) and 90R
(OCR) are device-agnostic - their descriptions never name a specific model - so each of their
rows is now duplicated as an "Add On Options:" record under every real device platform instead
of forming its own platform. 90W is model-specific per row (grouped under section labels like
"RK95 android OS upgrade license"); each row is attached to whichever real platform's name
matches its section label, and rows for a model this workbook has no device sheet for (RK25,
RS35, RS51, Hera51 - an older product no longer part of this configurator, per the user) are
dropped entirely rather than invented as a new platform. Only 4 of 90W's ~24 rows survive this
way (the RK95 and RK95CC ones - RK26/RS36/RS38 have no matching section in this workbook).
Result: 387 CipherLab parts (235 `Base Unit:`, 152 `Add On Options:`) across exactly 4 real
platforms (RK26, RK95, RS36, RS38), catalog total now 2,536 (719 JLT + 1,060 Winmate + 370 Getac
+ 387 CipherLab). Verified live in the browser: the Sales Platform dropdown for CipherLab shows
only the 4 real systems; RK26 and RK95 both show the ReMoCloud/OCR licenses under Add On
Options; RK95 additionally shows its two OS-upgrade licenses. Verified via a real `/api/
search_base_units` POST (Processor Options = "Qualcomm 4490 Octa-Core 2.4GHz" + RAM Memory
Options: = "8GB", brand=CipherLab) returning exactly the 3 real RS38 SKUs with correct prices.
`SEARCH_EXCLUDED_BRANDS` is now an empty set (kept, not deleted, as a reusable mechanism per its
own comment in `app.py`) - CipherLab is no longer greyed out in the search modal's Brand
dropdown. No CipherLab approvals or saved quotes existed to worry about losing (checked before
deleting: 0 of either). `data/parts_vmt_q1_2026.json`'s only pre-existing CipherLab/CipherLab
collision is one vendor-side duplicate row (`BPOWER0000143` on RS38, listed twice in the source
under two section labels with identical price/description) - harmless, not a real data-loss
collision.

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

**"Internal Wireless" is now split into four independent search fields (2026-08-18) - WiFi
radio, WWAN Generation, WWAN Card, and WWAN Carrier - all fully replacing the original flat
field, same pattern as storage/OS/CPU.** JLT/Winmate's real "Internal Wireless" rows jumble WiFi
radio, Bluetooth, GPS, and WWAN cellular into one free-text description (109 distinct real
values as of the original 2026-08-18 audit), e.g. `"Intel Wireless AX210 802.11 ac/a/b/g/n with
WWAN *AT&T*"`. The first version of this split (same day, earlier) kept the raw flat description
list as "Internal Wireless" and only *added* WWAN Generation/Carrier alongside it
(`_KEEP_RAW_ALONGSIDE_FACETS` in `app.py`) - reasoned at the time that dropping the raw field
would lose WiFi-standard/Bluetooth search capability. The user then flagged this live: the
"Internal Wireless" dropdown was still showing the raw WWAN-mixed text, defeating the point of
splitting WWAN out at all. Fixed by replacing the raw field with a real WiFi-only facet instead
of dropping it - `_KEEP_RAW_ALONGSIDE_FACETS` is gone, every real category in `FACET_CATEGORIES`
(including "Internal Wireless" itself now) is fully replaced by its facet(s), no exceptions.

- **Internal Wireless** (`ingest/wifi_facets.py`, `extract_wifi_radio`): WiFi radio only, no
  WWAN/carrier text. JLT names a specific Intel chip (`AX210`/`8265`) so that's returned
  directly; Winmate never names a chip, only an 802.11 standard revision, so the *highest*
  standard mentioned is returned (`802.11ax` > `ac` > `n` > `g` > `b`); `"No Radio"` is
  recognized on either brand. A row with no WiFi component at all (a WWAN-module-only row, or a
  bare "WLAN"/"Wifi" mention with no stated standard) returns `None` rather than a fabricated
  value - the row stays fully selectable directly from the platform's own option list, it's just
  not findable via this search facet. Applied to both JLT and Winmate.
- **WWAN Generation** (`extract_wwan_generation`): plain 3G/4G/5G only (LTE counts as 4G),
  sorted via `wwan_generation_sort_key`.
- **WWAN Card** (`extract_wwan_module`): specific cellular module/card part numbers - Telit
  LN920/FN990, Sierra EM7455/EM7411/EM9291/EM7595/MC7455/MC7411/MC7421, Quectel
  RedCap/RedCap RG255C, MediaTek, HUAWEI. Originally these fed into "WWAN Generation" as extra,
  more-specific values (reasoning: "the cards are tied to 3g 4g 5g more than the carrier") - the
  user revised this the same day once they saw the actual field list: a rep looking for a
  specific card wants its own dropdown, not a search through Generation's 3G/4G/5G entries. Now
  its own category. Deliberately does NOT merge EM7455/MC7455 or EM7411/MC7411 - different
  Sierra Wireless part numbers (M.2 vs mini-PCIe form factor), and nothing in the source text
  confirms they're interchangeable for search the way "Elkhart Lake" confirmed two CPU spellings
  were the same chip. `MC7421` and the specific `Quectel RedCap RG255C` submodel were added to
  the pattern list per the user even though neither appears in the catalog yet, so a future JLT
  spreadsheet update picks them up with no further code change (checked ahead of the generic
  "Quectel RedCap" pattern so a row naming the submodel gets the precise label).
- **WWAN Carrier** (`extract_wwan_carrier`): only the three actual named US carriers
  (AT&T/T-Mobile/Verizon, present on Intel Wireless 8265/AX210 module SKUs). A row with a
  generation/card but no named carrier (the common case) is simply not findable via Carrier,
  same pattern as an untagged storage/OS description.

Getac's own `attributes.wireless` values are untouched by this - already simple/clean (a handful
of values like `"WiFi + BT + 5G Sub-6"`), and this only affects JLT/Winmate's real per-SKU
"Internal Wireless" rows. Verified via the Flask test client against live data: JLT's "Internal
Wireless" is exactly `['802.11ac', 'Intel 8265', 'Intel AX210', 'No Radio']`; Winmate's is
exactly `['802.11ac', '802.11ax', '802.11n']`; JLT's "WWAN Card" is `['Sierra EM7455', 'Sierra
MC7411', 'Telit FN990', 'Telit LN920']`; `WWAN Generation` is back to plain `['4G', '5G']`
(JLT)/`['3G', '4G', '5G']` (Winmate); confirmed `/api/search_base_units` still correctly matches
on the new fields (`Internal Wireless: "Intel AX210"` → 9 JLT matches, `WWAN Card: "Sierra
MC7411"` → 1 match, `WWAN Card: "Sierra EM7455"` → 7 Winmate matches).

**The split above was search-facet-only at first; JLT's real catalog `category` field was
later migrated too (2026-08-18), so Technical (and Sales' main per-platform dropdowns, not
just Search) also show three separate boxes instead of one mixed one - Winmate was NOT
touched, per the user (confirmed JLT-only).** A one-time migration script re-labeled 61 JLT
"Internal Wireless" rows' real `category` field (only that field - code/description/prices
untouched) across all 15 JLT platforms: 5 rows naming a specific cellular module → real
category `"WWAN Card"`; 56 rows naming AT&T/T-Mobile/Verizon, or whose only WWAN signal is a
bare "with External PS_EXT-WWAN/WLAN" antenna-connector mention (no named carrier or module) →
real category `"WWAN Carrier"` (the antenna-only rows get a new 4th carrier value, `"Generic"`
- see `extract_wwan_carrier` in `ingest/wwan_facets.py`, checked after the three named carriers
and only when `extract_wwan_module` found nothing, so a module-named row can't also be tagged
Generic); everything else (pure WiFi, including "No Radio") stays real category `"Internal
Wireless"`. Technical needed **zero template changes** - `technical()`'s existing stable sort
(`plist.sort(key=lambda p: (category_sort_key(p["category"]), p["code"] or ""))`) already
groups options by real category in `CATEGORY_ORDER` position, so the three boxes appear
automatically, correctly ordered, the moment the data itself carries the right category name.

This is why `FACET_CATEGORIES` (above) maps every wireless synthetic category to *all three*
real categories (`_WIRELESS_REAL_CATEGORIES = ["Internal Wireless", "WWAN Card", "WWAN
Carrier"]`) instead of one real category each: which real categories actually hold wireless
data is now brand-dependent (JLT: three real categories; Winmate/Getac/CipherLab: still just
one, "Internal Wireless", untouched) - scanning all three for every synthetic facet means a
JLT row that's now real category "WWAN Card" but also names "AX210" in its own description
text is still findable via the "Internal Wireless" WiFi facet, same as before the split.

**Known, disclosed consequence:** re-labeling changes the `brand+platform+category+code` key
Purchasing's price-upload (`merge_parts`) matches against. A previously-exported Purchasing
pricing sheet covering one of these 61 rows won't match on re-upload after this change - the
row is silently skipped (never wrongly overwritten), and a fresh export reflects the corrected
categories going forward. Checked for saved-quote impact too: quote `selections` are a frozen
snapshot taken at Save time (`build_snapshot()`), not re-resolved against live category names
on every view, so no already-saved quote's stored price/description/total changed. The only
residual risk is cosmetic - re-opening an old saved quote that selected one of these rows for
further editing might not pre-select it correctly in the now-differently-categorized dropdown;
checked live data and found exactly 2 affected saved lines, both under seeded test-customer
quotes (`Acme Manufacturing::2`/`::3`), not real customer data.

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
- **Purchasing has a second, inner PIN gate on top of the Site Access PIN** (added 2026-08-18,
  per the user) — `data/site_access.json`'s `purchasing_pin` key (default `1111`, changeable
  from Admin), checked by a second `before_request` hook (`require_purchasing_pin()`) that
  runs after the site-wide one and covers every `/purchasing*` route. Same "not real security"
  caveat. Session flag is `session["purchasing_authenticated"]`, separate from the site-wide
  `session["authenticated"]` — logging out via the main `/logout` clears the whole session
  (`session.clear()`), so it clears Purchasing access too; there's no separate Purchasing
  logout. Both flags live in the **same** session cookie, so they share one expiry
  (`app.permanent_session_lifetime`, 5 days as of 2026-08-18, refreshed on every request by
  Flask's default behavior - i.e. "5 days after the last visit," not 5 days after login) -
  changing a PIN does **not** retroactively log out a session that already passed the old one;
  it only affects sessions that haven't entered a PIN yet.
- **Sales Reps can be locked (added 2026-08-18, per the user), on top of the existing
  add/remove.** A `locked: true` rep is excluded from the Sales-page rep picker
  (`/api/sales_reps`) and rejected by verify/save/copy (`rep_code_matches()` in `app.py` -
  the one shared check all three call sites use) even with the correct code — but their past
  quotes stay attributed to them (`created_by`/`sales_rep` are frozen strings on the saved
  quote, not a live reference to the rep record, so locking or even removing a rep later never
  changes historical quotes). Admin's **Reset PIN** button generates a new random 4-digit code
  immediately and shows it once in a banner — there's no "admin types the new code" flow, only
  "generate and reveal."
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

**Update, same day:** the code below was first written (`hubspot_client.py`, plus new routes in
`app.py`) deliberately **dormant**, per the user ("do not change where the buttons point
to... effectively not active") — it existed so the integration was ready and reviewable the
moment a real Private App token exists, not so it could be tested that day. There is still no
token (`data/hubspot_config.json`'s `access_token` is `null`), so every function in
`hubspot_client.py` still raises `HubSpotNotConfigured` if called — nothing below changes that.

**Later the same day, the user explicitly asked for the first piece of this to actually be
wired to the UI** (Sales' Opportunity ID row: `Populate` → **Create Quote**, plus a new
**Query Hbst** button, plus `Lookup Saved Quote` → **Find Saved Quote**) — see
`CHANGELOG.md`'s dated entry for the full spec (the exact three button labels, and the three
distinct messages the Opportunity ID hint badge now shows: "HubSpot isn't connected yet" / "No
Request found in Hbst" / "No saved quote found"). Query Hbst is real, tested code that calls
the dormant integration for real over the network — it just can't succeed yet without a token,
which is itself a correctly-surfaced state ("HubSpot isn't connected yet"), not a stub. The
Sales page's "Upload Hspt" button and the rest of the free-typed Opportunity ID flow are
untouched and still point at exactly what they always have (`api_quote_upload()`'s stub) —
only the Opportunity ID row's three buttons changed.

**What's actually unverified in the new code, because there is nothing to test against yet:**
- `hubspot_client.ASSOCIATION_TYPE_LINE_ITEM_TO_DEAL` (`20`) and
  `ASSOCIATION_TYPE_NOTE_TO_DEAL` (`214`) are HubSpot's documented default association type
  IDs for those object pairs, not confirmed against JLT's own portal.
- `push_quote_to_deal()`'s default `amount_field="floor_total"` — whether the Deal's `amount`
  (and each line item's price) should come from the quote's `floor_total` or `msrp_total` is a
  guess, not a decision Jeff has made. Change the keyword argument at the one call site in
  `app.py` (`api_quote_hubspot_push`) once he has.
- The EU API base URL question below is still open.
- Interaction 1 (customer lookup) was implemented against HubSpot's **Company** object, not
  Contact — `customers.json` stores one flat name per customer with no first/last name, which
  maps onto a Company record, and Company is also where the Jeeves linkage fields below live.
  This is a deliberate deviation from a literal "Contact" reading; Contact was never actually
  necessary for what this app tracks as a "customer."

None of the above blocks writing or reviewing the code — only testing it. The single blocking
prerequisite, unchanged, is a HubSpot Super Admin completing the Private App checklist further
down this section.

Nothing is connected to the live UI yet, but as of 2026-08-25 a concrete HubSpot integration
plan exists — worked out interactively with the user and verified against JLT's real, live
HubSpot portal (portal ID `145967326`, `app-eu1.hubspot.com`, owner
`jeff.gilbert@jltmobile.com`), not assumed from docs alone. This section is the durable record
of that plan; a richer visual version (block diagram, a request/response table per
interaction, and a copy-paste Private App setup checklist for a non-technical HubSpot admin)
is published at `https://claude.ai/code/artifact/574c8387-7674-4b36-bbf7-61c91a798e41` — treat
that as a reference rendering of what's written here, not the source of truth, since a future agent
may not have access to open it.

Current placeholders, unchanged until the plan below is built:
- **Opportunity ID**: manually typed (§5/§8).
- **Customer**: local `customers.json` with a `source`/`hubspot_id` field ready for real data
  once a connector exists (§6) — `hubspot_id` is never set by anything today.
- **Upload button** (Sales, per-quote): calls a real endpoint
  (`/api/quotes/.../upload`) that always returns
  `{"status": "not_connected", "message": "HubSpot isn't connected yet..."}`. The button and
  wiring exist; there's nothing on the other end. This is what interaction 5 below replaces.
- **Email button** (Sales): downloads the real Excel export and opens the real printable
  view, but does not send anything — there's no SMTP/Outlook integration in the app itself.
- **Jeeves** (JLT's accounting/inventory system — exact product name still unconfirmed per
  the original brief): Purchasing's manual price-fill workflow is the stand-in. No connector
  research has happened in this codebase at all, beyond the Company-level fields noted below.

**Confirmed live against the real portal, not assumed:**
- The native **Quote** object (HubSpot's own e-sign/payment quote, requires Revenue Hub
  Professional or Enterprise) came back `writeAccess: NOT_AVAILABLE` on this account — either
  the license isn't there or the permission isn't granted. **Decision: don't build against
  it.** Deal, Line Item, Contact, and Company are all standard objects, usable on ordinary
  Sales Hub — read access is already open, write needs the scope grant described below, not a
  license purchase.
- **Deal already has custom fields that look purpose-built for this**: `unit_part_number__c`
  ("Model Part Number") and `unit_quantity__c` ("Unit Quantity"). Before anything writes to
  them, confirm with Jeff whether another process already populates them — don't assume
  they're free just because the configurator doesn't know about them yet.
- **Company already carries a Jeeves ERP linkage**: `jeeves_customer_id__c`,
  `jeeves_customersuid__c` ("Jeeves Customer Number"), `jeeves_internal_company_id__c`. This
  is a *customer*-level mapping, already live, separate from — and does not solve — the
  *part-number*-level Jeeves mismatch already documented in the 2026-08-18 entry below (zero
  overlap between JLT price-book codes and Jeeves `USItem#`).
- The portal's UI runs on `app-eu1.hubspot.com`, suggesting EU data hosting. **Confirm the
  correct API base URL with HubSpot support/docs before writing any client code** — some
  EU-hosted portals need a different base than the standard `api.hubapi.com`; getting this
  wrong fails every call silently in a confusing way.

**Planned architecture (nothing below is built yet):**

Auth is a HubSpot **Private App** access token, not OAuth — a portal-wide credential that
isn't tied to any individual salesperson's HubSpot login or record-visibility settings (this
was raised explicitly as a concern: basing program access on one rep's personal permissions
would be fragile and inefficient). Created once, by a HubSpot **Super Admin** — not a
visibility-restricted seat, since a restricted creator's account could limit what the
resulting token can see — via **Settings → Integrations → Private Apps → Create a private
app**, granting exactly these 11 scopes: `crm.objects.contacts.read/write`,
`crm.objects.companies.read/write`, `crm.objects.deals.read/write`,
`crm.objects.line_items.read/write`, `crm.objects.notes.read/write`, and `files`. The
resulting token (`pat-...`) is stored server-side only — gitignored, same treatment as
`site_access.json` — and never sent to the browser. **This is the single blocking
prerequisite**: no code below can be written or tested without it.

A new `hubspot_client.py` module (doesn't exist yet) is the only code that would ever call
HubSpot directly — token custody and request/response mapping live there, nowhere else.
`app.py` would get new routes calling into it; the Sales screen's existing stubs (the
free-typed Opportunity ID field, the "Upload Hspt" button that currently just reports "not
connected") would be wired to those routes instead of their current no-op behavior.

Five concrete interactions share that plumbing, differing only in payload:
1. **Customer/Company lookup** — `POST /crm/v3/objects/contacts/search`. Replaces
   `customers.json`'s local name search; fills the already-existing `hubspot_id` field.
2. **Deal lookup** — deliberately not a name search (too error-prone). Resolve the customer
   to a Company ID first (step 1), then `GET
   /crm/v4/objects/company/{companyId}/associations/deal` to follow HubSpot's actual
   association graph, batch-read the results (`POST /crm/v3/objects/deals/batch/read`), and
   filter to open `dealstage`s. Replaces the free-typed Opportunity ID field with a real Deal
   ID. Zero associated deals means this customer has no open HubSpot Deal yet — see the open
   decision below.
3. **Push quote → line items + amount** — `POST
   /crm/v3/objects/line_items/batch/create` (associated to the Deal) plus a `PATCH` on the
   Deal's `amount`. Store each returned line-item ID on the local quote record so a later
   revision updates instead of duplicating.
4. **Attach the pricing export** — the real `.xlsx` bytes already produced by the existing
   `/api/quotes/<opportunity_id>/<quote_number>/export.xlsx` route (see §6/app.py), sent via
   `POST /files/v3/files` then `POST /crm/v3/objects/notes` (`hs_attachment_ids`) associated
   to the Deal. `.xlsx` was chosen deliberately over a PDF — see below.
5. **Attach the rep's final customer-facing quote** — same mechanism as #4, for whatever file
   format the rep builds by hand starting from the exported spreadsheet (Word/PDF/polished
   Excel, doesn't matter which). This is what the existing "Upload Hspt" button becomes.

**Explicitly not pursued, and why:**
- The native Quote object — blocked on this account (see above); would only be worth
  revisiting if Jeff confirms Revenue Hub is licensed *and* specifically wants HubSpot's own
  e-sign/payment quote screen instead of this app's export-then-attach flow.
- A server-generated PDF — there is no PDF generation anywhere in this app today. "Print
  (PDF)" is `quote_print.html` (see `app.py`'s `quote_print` route) rendered plain and printed
  via the browser's own Print dialog; it also locks the quote as a side effect if not already
  locked. Building a real PDF generator (e.g. `weasyprint`) was considered and explicitly
  deferred in favor of attaching the `.xlsx` export instead, per the user, since the `.xlsx`
  already exists and a PDF blob was called out as less preferable.

**Open scope decision, not yet made:** whether a rep should be able to create a new Deal from
inside the configurator when Customer Lookup finds no open Deal (interaction 2, zero
results), or whether that stays a manual step in HubSpot — the original project brief assumed
"HubSpot is the front door," i.e. a Deal always originates there first. Needs a decision from
Jeff before interaction 2 is built, not just a technical default.

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
