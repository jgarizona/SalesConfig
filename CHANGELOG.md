# Changelog

## Entry attribution

Every repository change must be recorded under the date it was made and identify its author or agent. Changes made by OpenAI Codex begin with `**[Codex]**`. Other contributors and agents use their own clear attribution; existing attribution must not be rewritten.

## Pending / TODO

- **Harden spreadsheet ingestion** — source: 2026-08-15 Codex review of the repository and the JLT, Winmate, Getac, and CipherLab workbooks in Box. Current status: ~~Technical always uses the JLT parser~~ resolved 2026-08-16 (`app.py`'s `PARSERS` dict now routes each brand to its own parser); Getac no longer risks a misleading zero-row success now that it's a real, tested parser. Still open: wrong-vendor uploads can still create unreliable data (no schema/brand validation rejects a mismatched file before parsing it), Purchasing still reads only the active sheet with exact headers, and uploads still have no preflight preview or size limit. Next action: reject unsupported layouts, validate schemas and brands before merging, treat zero parsed rows as an error, preview changes before saving, and enforce an upload-size limit.
- **Normalize and validate spreadsheet prices** — source: 2026-08-15 Codex review. Current status: currency strings containing symbols/special spaces and other unknown text can silently calculate as zero; several existing 1514N wireless prices are affected if those options are approved. Next action: normalize currency cells and explicit included/no-charge values, preserve meaningful statuses such as discontinued, and reject unknown price text instead of silently converting it to zero.
- **Define catalog refresh lifecycle rules** — source: 2026-08-15 Codex review. Current status: exact key changes can create duplicate logical records and rows removed from a workbook remain indefinitely. Next action: detect normalized-key collisions and present renamed, missing, and retired rows for explicit review without silently deleting approved parts.
- **Make JSON catalog writes recoverable and concurrency-safe** — source: 2026-08-15 Codex review. Current status: uploads rewrite the complete catalog JSON directly with no atomic replacement, backup, or write lock. Next action: use atomic writes plus locking/backups now, then migrate to a database when concurrent usage warrants it.
- **Add automated spreadsheet-ingestion tests** — source: 2026-08-15 Codex review and the handoff's known no-tests limitation. Current status: ingestion is verified manually. Next action: add representative JLT, Winmate, Getac, CipherLab, malformed-workbook, pricing-normalization, blank-preservation, and zero-row test fixtures.
- **CipherLab's source file is a price-*increase* list, not a full catalog** — found 2026-08-17 during the search-dropdown audit below. 21 product families (8600, HERA51, and a batch of Wavelink/Ivanti software-license SKUs) have accessories/warranties/licenses in the data but no `Base Unit:` row at all, because their base price didn't change in this particular increase. Per the user, CipherLab is excluded from Search by Requirements entirely until this is fixed at the source (see the second 2026-08-17 entry below) — normal Sales configuration is unaffected, this is search-only. Next action: once a fuller CipherLab catalog is sourced, re-run the ingest and remove `SEARCH_EXCLUDED_BRANDS = {"CipherLab"}` in `app.py` (two usages) and the matching `disabled` branch in `sales.html`'s search-brand-select loop.

- **HubSpot connector** — the plan (defined 2026-08-25, see `HANDOFF.md` §9) is now coded in `hubspot_client.py` + new `app.py` routes (also 2026-08-25), but deliberately **dormant** — no button or template calls any of it yet, per the user. **Blocking next action, unchanged: a HubSpot Super Admin must create the Private App per §9's checklist** — `data/hubspot_config.json`'s `access_token` is still `null`, so every function raises `HubSpotNotConfigured` if called. Once a token exists, still needs real testing before anything is wired up: §9 lists exactly what's unverified (two HubSpot association-type-ID constants, and which quote total becomes the Deal amount). Sales page still uses a manually-typed Opportunity ID and the original stub "Upload Hspt" button in the meantime — confirmed byte-for-byte unchanged.
- ~~**Real HubSpot upload**~~ — folded into the **HubSpot connector** item above on 2026-08-25; the Upload button is exactly interaction 5 in that plan (attach the rep's final quote as a Note on the Deal).
- **Jeeves connector** — cost/inventory reconciliation against JLT's accounting system. Purchasing currently fills in missing Cost/Current Cost by hand. Layout/UX defined 2026-08-18 (see the same-day CHANGELOG entry): "Part # Compare" and "$ Jeeves Compare" buttons exist on Purchasing (top of page) but are stubs — real Jeeves API/database access isn't available yet, so clicking either just shows a "not connected" banner. Blocked on two things before either can do anything real: (1) live Jeeves access, (2) a **Jeeves Part Number mapping for non-JLT parts** — Winmate/Getac/CipherLab parts likely don't have a native Jeeves part number, and per the user (2026-08-18) this is explicitly deferred ("put this in the TODO and we will look at this later"), no field or capture mechanism exists yet. Once both are available: "Part # Compare" checks every catalog part's assigned Jeeves Part Number against Jeeves and lists what's missing/unrecognized; "$ Jeeves Compare" compares local Floor Price/MSRP/Cost/Current Cost against Jeeves' own prices and generates a difference report, exportable and re-importable through the same preview/confirm import flow built the same day for §1's pricing gaps (see `confirm_import`/`cancel_import` in `app.py`). **Update 2026-08-18:** the user provided a real Jeeves export (`Jeeves of Pricelist JLT products v3 - for test.xlsx`, 904 rows, columns `USItem#`/`ItemDecsr`/`seItem#`/`sePrice`) - analysis found **zero automated match** is possible against current data: 0/85 exact overlaps between JLT's option `code` and Jeeves' `USItem#`, only 3/125 exact description matches, and `sePrice` is a uniform `8` on every row (confirmed intentional test data, not real pricing). Jeeves tracks far more granular internal BOM/component part numbers (`CB-00639-50`, `SP-00676-50`, etc.) than JLT's price-book codes. The `jeeves_part_number` field (added same day, see §6 of HANDOFF.md) exists now, but only gets populated via Technical's new "Add a new option" form or manual entry - matching against the real Jeeves file still needs a human-in-the-loop workspace (browse/search Jeeves items, pick the right match per JLT option), not a bulk auto-match. Next action once a real (non-$8) Jeeves export is available: build that matching workspace, likely as what "Part # Compare" becomes.
- ~~**Ingest Winmate, Getac, and CipherLab**~~ — resolved 2026-08-16: dedicated parsers built for all three (`ingest/parse_winmate.py`, `ingest/parse_getac.py`, `ingest/parse_cipherlab.py`), real data ingested (1,060 / 370 / 1,622 parts respectively), catalog now 3,551 parts across all 4 brands.
- **Third-party add-on ingestion path** — not built yet, and deliberately deferred (per the user, 2026-08-16: "addons will come later in this project"). Manufacturer-catalog parts are now auto-approved (`requires_review: false`, see the 2026-08-16 entry below), but a mount vendor's own catalog (RAM Mounts, Gamber-Johnson, etc.) doesn't self-certify fit with a specific host platform the way an OEM's own spec sheet does — that path needs `requires_review: true` and will go through the existing `approvals.json`/Technical-checkbox flow, which still exists specifically for this.
- **Real email sending** — the Email button on the Sales page downloads the Excel file and opens the printable view, but doesn't actually send anything (no SMTP/Outlook integration in the app).
- ~~**Data drift risk**~~ — resolved 2026-08-14: both Technical's and Purchasing's Upload buttons now merge (never blindly overwrite), so a vendor refresh can't erase prices purchasing already filled in.
- ~~**Quote revision history**~~ — resolved 2026-08-25: `app.py`'s `revision_snapshot()` now stores each real revision in a `revisions` list on save, and Sales has a browser for it (see the same-day CHANGELOG entry). A quote saved entirely before this landed only has history starting from the next time it's edited - whatever was already overwritten before this feature existed can't be recovered.
- ~~**Customer/opportunity lookup UI**~~ — resolved 2026-08-15: Customer and saved-quote lookup have real search-as-you-type panels; Manual Customer and Copy no longer use browser prompt() dialogs.
- **Architecture decision (§6 of the project brief)** — single-agent vs multi-agent, agents vs skills, still open.
- **Move off flat JSON files** if data volume/concurrent-editing needs outgrow it — currently `data/*.json`, no database.
- **Remove test data before go-live** — the 5 seeded test customers (Acme Manufacturing, Blue Ridge Industrial, Harborview Freight, Northwind Logistics, Sunrise Distribution) need to be cleared via Admin's "Remove All Test Customers" once the HubSpot connector replaces Customer Lookup. Also sanity-check `data/quotes.json`, `data/customers.json`, and `data/sales_reps.json` for any other leftover test entries (e.g. the "Test" sales rep) before real use.

## 2026-08-25

- **[Claude]** **Redesigned the revision/config summary area into a real comparison view, after
  the previous same-day design turned out to have the wrong root cause.** The user's actual
  report: loading a saved quote at its latest revision showed nothing in the summary area at
  all - `updateRevisionNav()` had a rule hiding the panel specifically when the arrows point at
  the latest revision, on the assumption the main page already showed it. That assumption
  breaks the moment a rep edits something, since the main page then shows the *new* unsaved
  values, not what's actually saved. Removed that rule entirely - the panel now always shows
  whichever revision the arrows point to, including the latest, the instant a quote loads.
  **Consolidated the two separate summary panels from earlier today into one shared area**
  (`renderSummaryArea()`, replacing both `updateRevisionNav()`'s old inline rendering and the
  removed `#accepted-config-summary`/`showAcceptedConfigSummary()`/`hideAcceptedConfigSummary()`):
  it shows the currently-saved/currently-viewed revision as one block, and - only when Accept
  Configuration produces a real difference from what's saved (`acceptConfiguration()` now
  compares the new selections' codes against the latest stored revision's) - a second block
  directly beneath it, separated by a visible dashed divider, showing the new unsaved draft in
  the identical format. Per the user's explicit clarification: "side by side" meant *same
  format, immediately adjacent*, not necessarily a left/right column layout - stacking
  satisfies that. A brand-new quote with nothing saved yet to compare against still shows a
  single block for the accepted draft, preserving the original "always show after Accept" ask
  from earlier today.
  Verified live end-to-end: loading a saved quote (even a single-revision one) shows its
  summary immediately, fixing the reported gap; unlocking, changing an option, and accepting
  produces two distinct stacked blocks with genuinely different part numbers, totals, and rows
  (verified byte-for-byte different, not a duplicate); pressing Save collapses back to a single
  block reflecting the newly-saved state, per the user ("once save is pressed... the oldest
  version is no longer shown").
- **[Claude]** **Reused the revision browser's read-only summary panel for the live,
  not-yet-saved configuration too - shown right after Accept Configuration, per the user
  liking that panel's look and wanting the same treatment there.** Extracted the shared
  rendering (`buildConfigSummaryHtml()` in `sales.html`) so both the historical-revision view
  and this new live-config view come from one function instead of duplicating the markup -
  the historical one (`updateRevisionNav()`) was refactored to use it too, not just the new
  case. New `#accepted-config-summary` panel (separate element from `#revision-viewer`,
  same `.lookup-panel`/`.revision-table` styling) sits directly under the bottom Accept
  Configuration button, populated by reading the live category widgets the same way
  `recalcDisplay()` already does for the on-screen totals/draft part number. Hidden again by
  `onUserChange()` the moment anything changes - a stale "accepted" summary for selections
  that no longer match would be actively misleading, not just outdated - and by
  `showQuote()`/`clearQuote()` when a different quote loads.
  **Formatting, per the user's exact spec:** the draft part number is now its own bold, larger
  line at the top of the summary (previously buried mid-sentence next to Floor/MSRP); the
  Base Unit row gets the same larger/bold treatment (new `.config-summary-baseunit` class,
  15px bold vs. the table's base 12px) since it's the one row that anchors the whole
  configuration; every other row stays at that uniform 12px - already true before, unaffected.
  Verified live: Accept Configuration on a fresh default config shows the panel immediately
  with the correct bold part number and bold Base Unit row; simulating an edit afterward
  hides it again; the historical revision browser (re-tested against a fresh two-revision
  quote after the refactor) still renders correctly with the same new formatting.
- **[Claude]** **Built real quote revision history and a browser for it, resolving a known
  limitation.** The user asked for up/down-arrow revision browsing next to Copy to New
  Opportunity; before building it, checked how Save actually works and found saving a new
  revision overwrote the previous one's data in place (`rev_number` was just a counter) - only
  the latest revision's data existed anywhere, so there was nothing to browse back through.
  Flagged this to the user rather than build a non-functional shell; they chose real storage
  ("customer can have old revisions and if we don't have them stored how can we verify if they
  are real").
  **Backend:** new `revision_snapshot()` in `app.py` captures everything that changes between
  revisions (`selections`, `brand`, `platform`, totals, `part_number`, `sales_rep`,
  `updated_at` - deliberately not `locked`, a current-quote concept). Appended to a new
  `revisions` list on every save that's a real content change (mirroring the existing
  `config_changed` check), on every new quote, and on every Copy to New Opportunity. Backfills
  lazily for a quote saved before this existed - captures its current state the next time it's
  edited, so nothing more gets lost from that point forward, though whatever was already
  overwritten earlier can't be recovered. New `GET
  /api/quotes/<opportunity_id>/<quote_number>/revisions` route serves the list.
  **Frontend:** two small arrow buttons + a "Rev N (i/total)" label next to Copy to New
  Opportunity, plus real keyboard support - Up/Down move through revisions, Left acts as Down
  and Right acts as Up (per the user's exact spec), wrapping at either end (highest + up =
  lowest, lowest + down = highest). Keyboard handling is skipped entirely whenever focus is in
  an input/textarea/select, so it can't hijack normal typing or cursor movement elsewhere on
  the page. Browsing is purely read-only - a detail panel (part number, totals, full selection
  list) shows for whichever revision isn't the current one; it never touches `loadedQuote` or
  the live category dropdowns, and the panel hides automatically when back at the latest
  revision since the main page already shows that one.
  **Verified live end-to-end, not just written:** created a real two-revision test quote via
  direct API calls with a genuinely different Storage Drive Options code between saves,
  confirmed the `/revisions` endpoint returns two distinct stored snapshots (not the same data
  twice), then loaded it in the browser and confirmed: initial load starts at the latest
  revision; clicking down shows the older revision's real (different) part number and totals;
  clicking down again wraps correctly back to latest; the same wrapping works via keyboard
  (`ArrowDown`/`ArrowLeft` then `ArrowRight` exactly matched the expected ping-pong between
  both revisions); and focusing the Opportunity ID field and pressing arrow keys left the
  revision display completely unchanged, confirming normal text-field behavior isn't broken.
- **[Claude]** **Found and fixed the real root cause behind this whole session's "can't tell
  what's clickable" reports: `.qh-buttons .btn` never had a `:disabled` rule at all.** Confirmed
  directly via `getComputedStyle()`, not assumed - a disabled button in this family (Customer
  Lookup, Manual Customer, Clear, Create Quote, Query Hbst, Find Saved Quote) rendered
  pixel-identical to an enabled one (same `#eef1f6` background, same text color), unlike every
  other button family on this page (`.accept-btn`, `.qh-idbar .btn`, `.wselect-trigger`), which
  all correctly grey out. Added `.qh-buttons .btn:disabled` with real muted styling, matching
  the established convention.
  **Also, per the user: removed the Opportunity ID row's inconsistent blinking** (Create Quote
  only flashed on the manual path, Find Saved Quote always flashed, Query Hbst was never
  included in the flash logic at all - three different behaviors for three buttons that are
  conceptually one group) **and replaced it with a permanent, distinct blue color**
  (`.btn-opp-action`, reusing the existing `#4c8dff` from `.qh-idbar .btn` rather than a new
  color) applied to all three unconditionally. Enabled = blue, disabled = the same grey every
  other button now correctly shows. Verified live: fresh load has all three grey/disabled;
  verifying the rep alone leaves Create Quote/Query Hbst grey (Find Saved Quote turns blue,
  since it's never customer-gated); selecting a customer turns all three blue.
- **[Claude]** **Find Saved Quote now checks HubSpot first, then the local cache, and presents
  both to pick from - per the user.** There's no native "saved quote" concept in HubSpot (the
  native Quote object was already ruled out, see `HANDOFF.md` §9), so "check HubSpot" reuses
  the same open-Deal lookup `Query Hbst` already does (`/api/hubspot/deals_for_customer`) -
  a Deal is exactly what a rep would otherwise go find with that separate button anyway. Fires
  both the HubSpot and local (`/api/quotes/all`) requests in parallel for speed; "HubSpot
  first" is honored as **display order** (a "From HubSpot" section renders above "Saved
  locally"), not by making the rep wait through two sequential round trips. Picking a HubSpot
  result fills the Opportunity ID with that Deal's ID (same as Query Hbst); picking a local one
  loads/copies it exactly as before. Added `.lookup-section-heading` CSS to separate the two
  sections inside the existing flex-wrap results panel.
  **A bug surfaced and was fixed during testing:** the "No saved quotes match." fallback was
  wrongly suppressed whenever HubSpot returned its not-configured error (an error note isn't
  real content, but the code treated it like some) - fixed so the local-empty message shows
  regardless of what HubSpot's section did. Verified live via a controlled fetch override
  (real customer data doesn't currently produce a true zero-local-results case, since at least
  one manual-customer orphaned quote always exists in the seed data): both notes now render
  together correctly.
- **[Claude]** **Flash Customer Lookup and Manual Customer once the rep is verified and no
  customer is picked yet, per the user.** Same complaint as the earlier Sales-Rep-gate hint,
  one step later: a rep clears the gate and sees two identically-styled enabled buttons with
  no indication which to use next - the same "where do I click" problem Accept Configuration's
  own flash already solves for its own step. Added `needsCustomer = repOk && !selectedCustomer`
  in `setButtonStates()`, toggling `.flash` on both (same pulsing-ring treatment already used
  everywhere else on this page, `.qh-buttons .btn.flash`). Also fixed `setCustomer()` to call
  the single comprehensive `setButtonStates()` instead of four individual sub-functions -
  `setButtonStates()` already called all four internally, so this was pure duplication, and
  centralizing guarantees the new flash (and everything else) re-evaluates on every customer
  change, including **Clear** - the user specifically flagged Clear as showing "the same
  action" (i.e. no guidance) as the very first screenshot, which this fixes since Clear already
  routes through `setCustomer("")`. Verified live end-to-end: rep verified with no customer ->
  both flash; customer selected -> flash stops; Clear -> flash resumes.
- **[Claude]** **Create Quote and Query Hbst are now always visible on page load, disabled
  rather than hidden until a customer's picked - per the user.** These two were the one
  inconsistent exception on this page: every other progressively-enabled control (Customer
  Lookup, Manual Customer, Save, Lock, etc.) is always visible and only ever gated by
  `.disabled`, but these two used `display:none` until `customerSource` was set, so a rep
  couldn't tell the options existed at all before picking a customer - exactly the earlier
  "options should be identified" complaint. Removed the static `style="display:none"` from
  both buttons' HTML and dropped the display-toggling half of
  `updateOpportunityButtonsVisibility()` entirely; both are now gated purely by `disabled =
  !repVerified || !selectedCustomer`, matching Find Saved Quote's own always-visible treatment.
  **Fixed the underlying ordering bug properly this time, instead of routing around it again:**
  since `disabled` now genuinely needs `selectedCustomer` (unlike the last fix, which removed
  that check specifically because of this same ordering issue), the call to
  `updateOpportunityButtonsVisibility()` was moved to run *inside* `setCustomer()` itself,
  which every call site that changes `selectedCustomer` already calls last - guaranteeing a
  correct read regardless of caller order, rather than relying on each call site getting the
  order right individually. Verified live end-to-end: fresh page load shows all three buttons
  immediately (Create Quote/Query Hbst correctly disabled); rep verified alone still leaves
  them disabled; selecting a customer enables both.
- **[Claude]** **Added a "← Back to Sales Configurator" link on the Purchasing PIN screen,
  per the user getting stuck there with no way out except typing a URL by hand.** Goes
  straight to `/sales`, not back through the site login - reaching `/purchasing/login` at all
  already requires an authenticated site session (`require_purchasing_pin` in `app.py` only
  ever runs after `require_site_pin` has already passed), so re-prompting the site PIN too
  would just be redundant, not a real second gate. Verified live: clicked the link from
  `/purchasing/login` and landed on `/sales` in one step, no PIN re-entry.
- **[Claude]** **Added the version-tag (git commit hash, `app.py`'s `_get_app_version()`) to
  both PIN-gate login screens (`login.html`, `purchasing_login.html`), per the user: any
  screen requiring interaction should show it, not just pages already past a PIN gate.**
  Neither template extends `base.html` (both are fully standalone documents, e.g. for the
  centered-card layout), so neither had it before - added the same markup/style directly to
  both instead, positioned `fixed` bottom-right since there's no nav bar to sit inside of. No
  Python changes needed: `app_version` is already injected into every template's context by
  the existing `@app.context_processor`, not just ones extending `base.html`. Verified live on
  both `/login` and `/purchasing/login`.
  **Related, surfaced while investigating a "something broke" report this same session (see
  the conversation, not reproduced as an actual code bug - the real issue was a
  misinterpreted screen reset after a hard refresh):** the version tag's value lags by one
  commit while a session is actively committing changes, because `_get_app_version()` runs
  `git rev-parse --short HEAD` once at process-restart time, and the dev-server's reloader
  restarts on file *content* changes, not on `git commit` (which doesn't touch file mtimes).
  So it always reflects whichever commit was current *before* the edit that's about to be
  committed, not the one just committed. Confirmed directly: the running server's actual
  served behavior (a brand-new route, a template's newest markup) was fully current while the
  tag still showed an older hash. Not a bug to fix - just a real caveat worth knowing before
  trusting that number mid-session; between sessions (no pending edits) it's accurate.
- **[Claude]** **Create Quote now sets the Opportunity ID hint badge to "Manual quote: not
  tied to Hbst yet", per the user.** Had to set it *after* `clearQuote()` (which runs
  `updateOpportunityHint()` via `setButtonStates()`), not before - `oppInput` now has a value
  at that point, so `needsHint` there is false and `updateOpportunityHint()` would otherwise
  blank the badge right back out immediately if this ran first. Verified live: Create Quote ->
  Opportunity ID fills with the customer name and the badge shows the new text, not the
  generic "Select one →" hint.
- **[Claude]** **Renamed Populate/Lookup Saved Quote and added a third button, "Query Hbst",
  which is the first piece of the dormant HubSpot integration actually wired to the UI - per
  the user's explicit spec.** The Opportunity ID button row is now **Create Quote** (was
  Populate, same unchanged behavior - just fills the field with the customer name, no HubSpot
  connector needed), **Query Hbst** (new), and **Find Saved Quote** (was Lookup Saved Quote,
  same unchanged behavior). Query Hbst calls the dormant HubSpot integration for real: a new
  `hubspot_client.find_open_deals_for_customer_name()` takes just a customer name (the browser
  has never tracked a HubSpot company ID, so this resolves name -> company -> open deals in
  one round trip via a new `/api/hubspot/deals_for_customer` route) rather than requiring the
  frontend to already have a company ID. Shown for both customer paths (Manual and
  Customer-Lookup/simulated-HubSpot), same as Create Quote, and for the same reason recorded
  in the existing 2026-08-17 comment: narrowing either to Manual-only has to wait until Query
  Hbst can actually succeed for the "lookup" path, or it recreates the exact dead end that
  comment already describes fixing once before.
  Per the user's exact spec: the Opportunity ID hint badge (the "Select one →" pill) now also
  carries the *result* of the last lookup attempted, not just the "what to do next" hint -
  **"HubSpot isn't connected yet"** if Query Hbst can't even check (no Private App token -
  this is what it shows today, verified live, and is a distinct, honest state from the next
  one), **"No Request found in Hbst"** if it checked and found nothing, and **"No saved quote
  found"** if Find Saved Quote's initial (unfiltered) load comes back empty - distinct from the
  existing per-keystroke "No saved quotes match." inside that panel, which reacts to the
  filter text instead.
  A real ordering bug surfaced and was fixed during this: `acceptCustomer()` calls the renamed
  `updateOpportunityButtonsVisibility()` (was `updatePopulateVisibility()`, extended to cover
  both buttons) *before* `setCustomer()` updates `selectedCustomer`, so an initial `disabled =
  !repVerified || !selectedCustomer` check on Query Hbst evaluated against the stale (empty)
  value. Fixed by dropping the `selectedCustomer` check entirely, matching Create Quote's own
  existing `disabled` condition (`!repVerified` alone) - the button is only ever visible once
  `customerSource` is "manual"/"lookup", which only happens in lockstep with `selectedCustomer`
  being set, so the extra check was redundant, not extra safety, once traced through.
  Verified live end-to-end, not just written: rep+customer selected -> both new/renamed
  buttons show enabled; clicking Query Hbst with no token configured produces the real 503 from
  `hubspot_client.HubSpotNotConfigured` and shows the honest "not connected" badge text (not
  the empty-result text); clicking Find Saved Quote for a customer with a genuine zero-result
  set (verified via a controlled fetch override, since the seeded seed data always has at
  least one orphaned manual-customer quote that satisfies the existing scoping rule) shows
  "No saved quote found".
- **[Claude]** **Gated Accept Configuration on Customer + Opportunity ID, not just the Sales
  Rep, per the user hitting this live.** The intended flow is Sales Rep -> Customer ->
  Opportunity ID -> Accept Configuration, but `updateConfigAcceptState()` only ever checked
  `repVerified` - the user verified their rep and watched Accept Configuration immediately
  start flashing before picking a customer at all. Added a `flowReady = repVerified &&
  selectedCustomer && oppInput.value.trim()` check; wired `updateConfigAcceptState()` into
  both mutation points that weren't already covered (`setCustomer()`, and typing directly into
  the Opportunity ID field - `oppInput`'s existing `input` listener only called
  `updateOpportunityHint()`). The status text under the button now says "Select a customer and
  enter an Opportunity ID first" instead of always suggesting selections were ready to accept.
  **Search by Requirements deliberately stays gated on `repVerified` alone** - per the user,
  it's a lookup tool usable any time after the rep code, not part of committing a specific
  quote. Verified live end-to-end: rep+code alone leaves Accept Configuration disabled/not
  flashing while Search unlocks; customer picked with no Opportunity ID still leaves it
  disabled; entering the Opportunity ID immediately flips it to enabled+flashing.
- **[Claude]** **Added a hover hint pointing at the Sales Rep gate, per the user hitting this
  live: selecting a rep, then clicking a still-disabled control (Customer Lookup) before
  entering the 4-digit code, got no feedback at all.** Root cause investigated directly in a
  real browser (not assumed): a genuinely `disabled` HTML control fires **zero** mouse events
  on click - not even `mousedown` - confirmed by instrumenting `document` with capturing
  listeners for every mouse event type and clicking a disabled button, which produced no log
  entries whatsoever. `mouseover`/`mouseenter`/`pointerover` **do** still fire on disabled
  elements, and hovering always precedes a click attempt, so that's the mechanism used instead
  of trying to catch the click itself. `sales.html`: one delegated `mouseover` listener
  (guarded by `!repVerified`, which is a complete and safe signal since every control on this
  page is disabled solely for that reason until a rep verifies - see `setButtonStates()`)
  briefly applies a new `.rep-gate-hint` pulsing-ring class (mirrors the existing `.flash`
  ring treatment on Accept/Populate, just amber and finite instead of infinite) to whichever
  of the Sales Rep dropdown or the 4-digit code field is the actual next thing to fill in.
  `static/style.css` adds the class + a `prefers-reduced-motion` fallback. Verified live via
  browser automation, not just by inspection: (1) no rep selected, hover a disabled control →
  dropdown highlights; (2) rep selected, code blank, hover a disabled control → code field
  highlights; (3) rep fully verified, hover a control disabled for an unrelated reason (Lock,
  no saved quote yet) → correctly does **not** fire, confirming no false positives once the
  real blocking reason is something else. No other behavior changed - the rep gate itself
  still works exactly as before, this only adds feedback on top of it.
- **[Claude]** **Built the HubSpot integration code from the plan below — dormant, not wired
  up, per the user's explicit instruction not to change where any button points.** New
  `hubspot_client.py` (the only module allowed to call HubSpot directly, per the plan) plus
  five new `app.py` routes under `/api/hubspot/...` and `/api/quotes/.../hubspot/...`
  implementing the plan's five interactions: `search_customers()` (Company search, not
  Contact — see §9 for why), `get_open_deals_for_company()` (follows the real Associations
  API graph, not a name search), `push_quote_to_deal()` (line items + deal amount),
  `attach_file_to_deal()` (shared by both file-attach interactions). Also extracted
  `build_quote_workbook()` out of the existing `/export.xlsx` route so the new pricing-export
  attach route reuses it instead of duplicating ~50 lines. Token storage mirrors
  `site_access.json`: `data/hubspot_config.json`, auto-created with `access_token: null`, now
  gitignored (added to `.gitignore` alongside `site_access.json`). Added `requests` to
  `requirements.txt` (`flask`/`openpyxl` couldn't make outbound API calls cleanly on their
  own) — confirmed it's already installed in the environment this was built in, and confirmed
  the app still boots and existing routes (login, the old "Upload Hspt" stub) are byte-for-byte
  unchanged by starting the server and curling both the old and new routes side by side, since
  an unconditional `import hubspot_client` at the top of `app.py` would otherwise be able to
  break the entire app on startup if `requests` weren't available. **Every function in
  `hubspot_client.py` currently raises `HubSpotNotConfigured`** — there is no Private App
  token yet, so none of this has been tested against a live HubSpot account. See `HANDOFF.md`
  §9 for exactly what's unverified as a result (two association-type-ID constants, and which
  quote total becomes the Deal amount) — review those specifically once a token exists, before
  wiring any UI to these routes.
- **[Claude]** **Defined a full HubSpot integration plan — planning only, no code changed.**
  The user asked for a review of HubSpot's Quotes/CRM/Files/Webhooks API docs and a
  recommendation for connecting this configurator to HubSpot. Recorded durably in
  `HANDOFF.md` §9 (rewritten) rather than left only in the interactive session, since a future
  Codex session can't open that conversation; a richer visual version (block diagram, a
  request/response table per interaction, and a copy-paste Private App setup checklist for a
  non-technical HubSpot admin) is published as a Claude Artifact at
  `https://claude.ai/code/artifact/574c8387-7674-4b36-bbf7-61c91a798e41`. Key findings were
  verified live against JLT's real HubSpot portal (portal `145967326`,
  `jeff.gilbert@jltmobile.com`, `app-eu1.hubspot.com`) rather than assumed from docs: the
  native Quote object is blocked on this account (no Revenue Hub license, or permission not
  granted), so the plan targets Deal + Line Item + Notes + Files instead; Deal already has
  `unit_part_number__c`/`unit_quantity__c` custom fields that look purpose-built for this
  (needs confirming with Jeff that nothing else already uses them before writing to them);
  Company already carries Jeeves customer-ID fields (`jeeves_customer_id__c` and others) —
  separate from, and not a fix for, the part-number-level Jeeves mismatch already logged in
  the 2026-08-18 entry below. Auth design deliberately avoids tying program access to any one
  salesperson's HubSpot login (raised as an inefficiency concern) — a Private App token,
  created by a Super Admin, is portal-wide and independent of individual seat visibility.
  **Blocking next action before any code can be written:** a HubSpot Super Admin needs to
  create the Private App per the checklist in `HANDOFF.md` §9.

## 2026-08-19

- **[Claude]** **"Add a new option"'s Category dropdown vs. Search by Requirements' category
  list mismatch - corrected after getting the fix backwards the first time.** The user pointed
  out the two didn't match (comparing them directly). First attempt (same day, since reverted
  below): assumed `CATEGORY_ORDER` was *missing* 7 real category names (Winmate's `CANBUS`/
  `DIDO`/`LAN`/`Camera`/`Data Collection:`/`Data Collection: (2)`, JLT's `Dock`) and added them
  to it - but `CATEGORY_ORDER` is also what Search by Requirements uses to decide which fields
  to offer, so this **wrongly changed Search too**, which the user explicitly did not want
  touched. Corrected: **reverted `CATEGORY_ORDER` back to its original contents**, and instead
  scoped "Add a new option"'s Category dropdown down to that same original curated list (minus
  its search-only pseudo-categories - Storage Capacity/Storage Technology/WWAN Generation/OS
  Version/OS Edition, which no real part can ever have as its actual category). The dropdown
  now reflects exactly what the user marked up as correct: `Base Unit:` through `Operating
  System:`, with none of the narrow vendor pass-through categories that `ingest/
  category_map.py` deliberately keeps separate from the canonical vocabulary (see that file's
  docstring - those categories reuse tiny codes like `X`/`A`/`1`/`2` that collided when
  folded into a shared bucket before, confirmed 2026-08-15). Verified via the Flask test
  client: `CATEGORY_ORDER` back to its pre-2026-08-19 contents exactly (diffed against the
  commit before this change); Add Option's Category dropdown now lists exactly the 13 curated
  categories; confirmed live in the browser on Winmate (which has all 7 of the excluded raw
  categories in its real data) that none of them appear in the dropdown.

- **[Claude]** **Reworked Technical's "Add a new option" form after live feedback from the
  user testing it.** Several real problems with the first version:
  - The Platform field was free text with an HTML `<datalist>` popup, which rendered off the
    left edge of the page for the user during testing - a real browser positioning bug, not
    just a style nitpick. Replaced entirely with a **Platform checkbox list** scoped to
    whichever **Vendor** is selected (Vendor is now its own real `<select>`, not a hidden field
    tied to whichever brand happened to be showing on the page) - a technician can now add the
    same option to several platforms at once in one submission, and there's no popup to
    mis-position. Vendor changes swap which platform-group is visible via a small JS toggle
    (`onAddVendorChange()`) - one checkbox group per brand is always rendered, only the
    matching one is shown.
  - **Category is now a dropdown** instead of free text a technician had to spell/capitalize
    correctly - originally sourced from every real category name used anywhere in the catalog,
    corrected the same day (see the entry above) to the curated `CATEGORY_ORDER` vocabulary
    instead, once that turned out to include vendor-internal categories that shouldn't be
    offered for a *new* option.
  - **Removed all four price fields (Floor Price/MSRP/Cost/Current Cost) from the form
    entirely** - per the user, Technical should never touch pricing, that's Purchasing's job.
    `add_option`'s backend no longer reads them from the request at all; every new option is
    always created with all four blank, unconditionally.
  - **Relabeled "Code" with an inline tooltip** clarifying it's the short internal catalog
    identifier used to select the option (e.g. `"H"`, `"KA"`, `"TP"`) - not the same thing as
    the Jeeves Part Number field next to it, after the user asked "what is code, do you mean
    part number?". Both fields still exist; they mean different things and both stay.
  - Backend (`technical()` in `app.py`) now takes `add_platforms` (a list via
    `request.form.getlist`) instead of a single `add_platform`, and creates one new part row
    per selected platform in one request - partial success is supported (a platform that
    already has that exact `(brand, platform, category, code)` is skipped and reported
    separately, the rest still get created), not all-or-nothing.
  - **Caught and fixed a real CSS bug of my own while verifying this live**: the
    per-vendor platform-group `<div>` had both `display:none` (conditional) and `display:flex`
    (unconditional) in the same inline `style` attribute - the later declaration always wins
    for the same CSS property, so every vendor's platforms showed at once regardless of which
    Vendor was selected. Fixed by making the whole `display` value conditional
    (`display:{% if ... %}flex{% else %}none{% endif %}`) instead of stacking two separate
    declarations for the same property.
  - Verified via the Flask test client: a two-platform submission created exactly 2 rows
    (both unapproved); resubmitting including one already-added platform correctly skipped
    just that one and added the new third platform, with both outcomes reported separately.
    Verified live in the browser: Category dropdown lists real categories (including ones from
    Getac/CipherLab's own vocabulary); switching Vendor from JLT to Winmate correctly swapped
    the visible platform checkboxes with no other vendor's platforms showing.

## 2026-08-18

- **[Claude]** **New "Purchasing warnings" mechanism: standing, acknowledgeable notices on
  Purchasing, with an Admin counter for what's still unacknowledged.** Per the user - the
  Jeeves part-number mismatch finding (see the Jeeves TODO update above) is exactly the kind
  of "purchasing needs to know this" note that doesn't fit the existing per-part/per-quote
  Dashboard counts, and needs a way for purchasing to actually see and dismiss it rather than
  it just sitting in a CHANGELOG entry nobody in Purchasing reads.
  - New `data/purchasing_warnings.json` (tracked, not gitignored - real application state like
    `sales_reps.json`/`customers.json`, not a secret or ephemeral file): a list of
    `{id, message, created_at, acknowledged, acknowledged_at}`. Auto-created on first run via
    `load_or_create_purchasing_warnings()` (same pattern as `load_or_create_site_access()`),
    seeded with one warning: the Jeeves USItem#/description mismatch finding, written out in
    full so Purchasing doesn't have to go dig through CHANGELOG.md to understand it.
  - **Purchasing** shows every unacknowledged warning as an amber banner at the very top of
    the page (above the Dashboard stat cards), each with its own **Acknowledge** button
    (`action=acknowledge_warning`, `app.py`) - clicking it marks that one warning acknowledged
    and it stops showing, but stays in the file (not deleted) with a timestamp.
  - **Admin** gets a new 6th stat card, "Purchasing warnings not acknowledged" - amber-styled
    like the other pending-work cards when the count is above zero, same pattern as
    "Purchasing action items pending."
  - New `.banner.warn` CSS class (amber, `static/style.css`) - the existing `.banner`/
    `.banner.error` only covered success/error, nothing for "important but not wrong."
  - Verified via the Flask test client and live in the browser: warning renders on Purchasing
    with a working Acknowledge button; Admin's counter shows 1 before acknowledging, 0 after;
    acknowledging is idempotent-safe (stores `acknowledged: true` + timestamp, doesn't delete
    the record). **Reset the seed warning back to unacknowledged before committing** - it was
    acknowledged once during testing, but the point is for Purchasing to actually see and
    dismiss it themselves, not have it pre-dismissed by test automation.

- **[Claude]** **Appended each WWAN Card's generation to its name** (e.g. "Sierra EM7411" ->
  "Sierra EM7411 4G"), per the user. Generations were grounded in the actual source text where
  possible - checked every real row mentioning each card name for a 3G/4G/5G mention elsewhere
  in the same description (`extract_wwan_generation` cross-referenced against
  `extract_wwan_module` across every Internal Wireless/WWAN Card/WWAN Carrier row): 5G -
  Quectel RedCap RG255C, Sierra EM9291, Telit FN990; 4G - Sierra EM7411/EM7455/EM7595/MC7455,
  Telit LN920, MediaTek; 3G - HUAWEI (Winmate's raw text literally says "3G-Module (HUAWEI)").
  **Sierra MC7411/MC7421 are the one exception** - no source text states their generation
  anywhere; labeled 4G by inference only (same LTE Cat 6 module family as EM7411/EM7455, per
  general knowledge of the real Sierra Wireless AirPrime MC74xx line), flagged in
  `ingest/wwan_facets.py`'s comment as worth confirming with whoever specs these if it needs
  to be authoritative. `_MODULE_PATTERNS` labels updated in place (regex matching logic
  unchanged - only the returned label string changed, so Winmate's real rows needed no data
  edit, same as the earlier RG255C fix). Updated the 165 real JLT "WWAN Card" rows' description
  text to match (160 seeded + the 5 pre-existing real vendor rows) via
  `extract_wwan_module(current_description)` - safe because the regex patterns match on the
  base part number substring regardless of whether the current description is the old clean
  label or the original full vendor sentence. Verified idempotent this time (learned from the
  "Generic" regression a few entries up) - re-ran the facet computation after the change and
  confirmed no value dropped out. Verified live in the browser: 1014P's WWAN Card list now
  reads "Sierra EM7411 4G", "Sierra EM9291 5G", "Quectel RedCap RG255C 5G", "HUAWEI 3G", etc.,
  and existing Technical approvals (9 of the 11 cards + all 4 Add On Options, checked live by
  the user while testing this feature) were unaffected by the rename.

- **[Claude]** **Corrected "Quectel RedCap" to "Quectel RedCap RG255C" everywhere** - per the
  user, there's no separate bare "Quectel RedCap" product, the two labels from the earlier
  same-day WWAN Card work were redundant. Merged `ingest/wwan_facets.py`'s two Quectel
  patterns into one (`Quectel\s*RedCap(\s*RG255C)?`, always labeled "Quectel RedCap RG255C"),
  and fixed the 15 seeded JLT WWAN Card rows' `description` (one per platform, code
  `REDCAP`) to match. Winmate's real "Quectel RedCap" rows needed no data edit - only the
  extractor's label changed, and their live-derived Search facet value picked up the rename
  automatically (verified: `['HUAWEI', 'MediaTek', 'Quectel RedCap RG255C', ...]`). Confirmed
  the seeded JLT rows are still correctly excluded from Search (unapproved,
  `is_selectable() == False`) - that's the intended pending-review state, not a bug. Confirmed
  live in the browser: 1014P's WWAN Card list now reads "Quectel RedCap RG255C".

- **[Claude]** **Cleaned up the real WWAN Carrier rows' description text to just the carrier
  name** - the user caught that recategorizing these rows (see the earlier same-day entry)
  only changed their `category` field; Technical still showed the full original sentence
  ("Intel Wireless AX210 ac/a/b/g/n with WWAN *AT&T*") instead of a clean "AT&T", inconsistent
  with the newly-added WWAN Card rows which show clean names. Ran a one-time script setting
  `description = extract_wwan_carrier(description)` for all 56 real JLT "WWAN Carrier" rows
  across all 15 platforms - `AT&T`/`T-Mobile`/`Verizon`/`Generic` replacing the original
  sentence; nothing else (code, price, category) touched. **Caught and fixed a real regression
  from this**: `extract_wwan_carrier`'s "Generic" detection required the literal substring
  "WWAN" in the text, which no longer exists once the description *is* "Generic" - the very
  next Search facet computation lost "Generic" entirely (0 matches instead of 12). Fixed by
  making `extract_wwan_carrier` idempotent on its own output (`ingest/wwan_facets.py` -
  `_GENERIC_WWAN_RE` now also matches a description that's exactly "Generic"). Verified via
  the Flask test client after the fix: `WWAN Carrier` facet back to `['AT&T', 'Generic',
  'T-Mobile', 'Verizon']`, `Generic` search back to 12 matches, `WWAN Card`/`Internal Wireless`
  facets unaffected; confirmed live in the browser that 1014P's WWAN Carrier box now reads
  cleanly (AT&T / T-Mobile / Verizon / Generic).

- **[Claude]** **Seeded the full WWAN Card list (11 cards) across all 15 JLT platforms** -
  closes the loop on the 1014P WWAN Card gap first flagged a few entries below: building the
  "Add a new option" form and the accessory add-ons wasn't the same as actually adding the
  missing WWAN Card options themselves, which the user caught. Per the user, the complete set
  shown in Search's "WWAN Card" dropdown (HUAWEI, MediaTek, Quectel RedCap, Sierra
  EM7411/EM7455/EM7595/EM9291/MC7411/MC7455, Telit FN990/LN920) is valid on every JLT model.
  One-time seed script, same shape as `add_option` would produce (`requires_review: true`,
  blank pricing/Jeeves Part #, consistent code per card e.g. `EM7411`/`REDCAP`/`MTK`):
  - **Skipped 5 (platform, card) combinations that already had a real vendor row** so as not
    to create a redundant duplicate next to an already-priced SKU - matched by running the
    existing `extract_wwan_module()` against each platform's real "WWAN Card" descriptions
    (1214P already has MC7411 as code `MC`; 6012 has Telit LN920 as `DB`; 6012A has Sierra
    EM7455 as `SW`; 6015 has both Telit FN990 `WL` and Telit LN920 `WU`).
  - **Added 160 rows** (15 platforms × 11 cards, minus those 5 already-real ones) - purely
    additive, only new rows, nothing existing touched.
  - Verified via the Flask test client and live in the browser: 1014P (which had zero WWAN
    Card rows before this) now shows all 11, unapproved; 1214P shows its 1 pre-existing
    auto-approved MC7411 row alongside the 10 new unapproved ones, with no duplicate MC7411.

- **[Claude]** **Technical can now add a brand-new option by hand (not just approve/upload),
  and Purchasing gets a real Dashboard of what that surfaces once quoted.** Follows from the
  1014P WWAN Card discussion: the standard 1014P genuinely doesn't have a WWAN Card option in
  JLT's price book, and per the user, that's exactly what Technical is for - a technician
  adding a valid option JLT engineering has qualified but that isn't in the current vendor
  spreadsheet snapshot yet.
  - **New "Add a new option" form on Technical** (`app.py`'s `technical()`, `action=add_option`):
    Platform/Category/Code/Description required, all 4 price fields and a new **Jeeves Part
    Number** field optional. Always saved with `requires_review: true` (same flag third-party
    add-ons will use) - it needs a checkbox approval before it's selectable on Sales, same as
    anything not from the official catalog. Create-only: adding a `(brand, platform, category,
    code)` that already exists is a rejected error, not a silent overwrite (unlike the bulk
    vendor-spreadsheet upload path, which intentionally does overwrite/merge).
  - **New `jeeves_part_number` field** on the part schema (optional, `None` by default) -
    groundwork for the deferred Jeeves integration, and now also what "Add a new option"
    captures directly.
  - **Seeded 4 real add-on options across all 15 JLT platforms** under "Add On Options:", per
    the user: Tamper Plate, Roxtec, Dome w/SMA, external SMA x3 (60 new rows total: 4 × 15,
    codes `TP`/`RX`/`DS`/`SX3`). All unapproved, no pricing yet - exactly the scenario this
    whole feature exists to support.
  - **`compute_quote_action_items()` (shared by Purchasing's §2 report and the new dashboard)
    extended from checking just Cost/Current Cost to also checking Jeeves Part Number, Floor
    Price, and MSRP** - so a technician-added option that gets quoted before Purchasing has
    priced it or assigned it a Jeeves Part Number shows up immediately, not just once Cost is
    missing. New `compute_quote_action_item_counts()` gives the per-field breakdown.
  - **New Dashboard at the top of Purchasing**: 5 stat cards (Missing Jeeves Part #/Floor
    Price/MSRP/Cost/Current Cost), scoped to **quoted line items only** (not the whole
    3,551+-part catalog - that's what §1's existing "Catalog pricing gaps" already covers),
    per the user's explicit scope confirmation. §2's description text and CSV export
    (`purchasing_quotes_report_*.csv`) updated to reflect the fuller "Missing" reasons.
  - Verified via the Flask test client: `add_option` correctly created a real row, rejected a
    duplicate `(brand, platform, category, code)`, and the new row was correctly excluded from
    `is_selectable()` (unapproved); the seed script added exactly 60 rows (spot-checked no
    collisions with the existing "No Add Ons" `X` code); the CSV export's `DictWriter` needed a
    fix (`writerow({k: item[k] for k in fieldnames})` instead of `writerow(item)`) since
    `action_items` now carries an extra `missing_fields` list key the CSV doesn't include - a
    real bug caught by testing the export, not by inspection. Dashboard counts verified against
    live quote data: 84 missing Jeeves Part # (expected - no part has one yet), 27 missing
    Current Cost (matches §2's pre-existing count), 4/3/5 missing Floor/MSRP/Cost respectively.
    Confirmed live in the browser: the 4 new add-ons render under 1014P's "Add On Options:"
    section with unchecked checkboxes, alongside the existing auto-approved "No Add Ons".

- **[Claude]** Reduced the session lifetime (`app.permanent_session_lifetime`) from 7 to 5
  days, per the user, after they asked why reloading Purchasing didn't re-prompt for the PIN
  post-change - confirmed that was expected (a session that already passed a PIN stays valid
  until the session itself expires; changing the PIN only affects sessions that haven't
  entered one yet) and this was the follow-up they wanted rather than a bigger behavior change
  (forced re-challenge on every visit, or invalidating existing sessions on PIN change).
- **[Claude]** **Added a second, inner "Purchasing PIN" gate scoped to just the Purchasing
  section, and extended Admin's Sales Rep management with Lock/Unlock and Reset PIN.** Per the
  user: even someone who already has the site-wide PIN shouldn't see Purchasing (cost data,
  purchasing-internal pricing) without a second code. Defaults to `1111` (fixed, not random
  like the site PIN), changeable from Admin under a new "The Purchasing PIN" section - same
  UI pattern as the existing Site Access PIN section. Implementation:
  - `data/site_access.json` gained a `purchasing_pin` key (backfilled automatically for an
    existing install's file, not just fresh ones).
  - New `require_purchasing_pin()` `before_request` hook runs *after* the existing site-wide
    `require_site_pin()` (Flask runs before_request handlers in registration order and stops
    at the first redirect) - so the site PIN is always required first, and the Purchasing PIN
    is a strictly additional layer on top, covering all of `/purchasing`, `/purchasing/
    pricing_gaps`, and `/purchasing/download/<file>`. New `/purchasing/login` route +
    `templates/purchasing_login.html` (mirrors the existing standalone `login.html`).
  - **Sales Rep management** (Admin, previously add/remove only) gained **Lock/Unlock** and
    **Reset PIN** per rep. A locked rep is excluded from the Sales-page rep picker
    (`/api/sales_reps`) and can't verify/save/copy a quote even with the correct code
    (`rep_code_matches()` in `app.py`, now the single shared check used by all three call
    sites) - but their past quotes stay attributed to them unchanged, since `created_by`/
    `sales_rep` are frozen strings on the quote, not a live reference to the rep record.
    Reset PIN generates a new random 4-digit code immediately (no re-typing/confirming a new
    one) and shows it once in a banner for the admin to relay to the rep - the old code stops
    working the instant it's reset.
  - Verified via the Flask test client: unauthenticated request to `/purchasing/login` still
    redirects to the site login first; site-authenticated-only session redirects `/purchasing`
    and `/purchasing/pricing_gaps` to `/purchasing/login` while `/technical` stays unaffected;
    wrong PIN rejected, correct PIN (`1111`) grants access; locking a rep removed them from
    `/api/sales_reps` and made `/api/sales_reps/verify` return 403 even with their correct
    code; unlocking restored both; Reset PIN changed the stored code and the old code
    immediately stopped verifying while the new one worked. Also confirmed live in the
    browser: Lock/Unlock toggle updates the Status column and button label correctly.

- **[Claude]** **Split "Internal Wireless" into a clean WiFi-only search field, plus a new
  standalone "WWAN Card" field.** Reported by the user from a Search by Requirements
  screenshot: JLT's "Internal Wireless" dropdown mixed WiFi radio, WWAN generation, and
  carrier together (e.g. "Intel Wireless AX210 802.11 ac/a/b/g/n with WWAN *AT&T*" as one
  option), when the field should be WiFi-only. Root cause: the same-day WWAN Generation/
  Carrier split (see below) had *added* those two facets alongside the original raw flat
  "Internal Wireless" description list rather than replacing it, so the raw WWAN-laden text
  was still what populated the "Internal Wireless" dropdown itself.
  - New `ingest/wifi_facets.py` (`extract_wifi_radio`) derives a clean WiFi-only value per
    row: JLT names a specific Intel chip (AX210/8265) so that's returned directly; Winmate
    never names a chip, only an 802.11 standard revision (ac/ax/n), so the highest one
    mentioned is returned instead; "No Radio" is recognized on either brand; a row with no
    WiFi component at all (a WWAN-module-only row, or a bare "WLAN"/"Wifi" mention with no
    stated standard) correctly returns nothing rather than a fabricated value — still fully
    selectable directly from the platform's own option list, just not via this search facet.
    Applied to **both JLT and Winmate** (per the user - Winmate's raw text has the identical
    mixing problem, just messier: ~71 distinct variants vs JLT's 35).
  - `app.py`'s `FACET_CATEGORIES` now maps "Internal Wireless" to itself via this new
    extractor (previously only Storage/OS/Processor did a real-category-to-itself or
    -to-two-synthetics mapping; "Internal Wireless" used to be the one exception that kept
    its raw text). The old `_KEEP_RAW_ALONGSIDE_FACETS` mechanism that caused this is
    removed entirely — every real category in `FACET_CATEGORIES` is now fully replaced by
    its facet(s), no exceptions.
  - **New "WWAN Card" search field**, separate from "WWAN Generation" — per the user
    (revising the same-day decision below), a rep looking for a specific card (Sierra
    Wireless MC7411, Quectel RedCap, etc.) wants its own dropdown rather than hunting
    through the 3G/4G/5G list. `extract_wwan_module` (`ingest/wwan_facets.py`) now feeds
    "WWAN Card" instead of "WWAN Generation"; Generation is back to a plain 3G/4G/5G list.
    Also added `MC7421` and a specific `Quectel RedCap RG255C` pattern (checked before the
    generic "Quectel RedCap" one) per the user's named examples — neither appears in the
    catalog yet, added ahead of time so a future JLT spreadsheet update picks them up
    without another code change.
  - Verified via the Flask test client against live data: JLT's "Internal Wireless" is now
    exactly `['802.11ac', 'Intel 8265', 'Intel AX210', 'No Radio']`; Winmate's is exactly
    `['802.11ac', '802.11ax', '802.11n']`; JLT's "WWAN Card" is
    `['Sierra EM7455', 'Sierra MC7411', 'Telit FN990', 'Telit LN920']`; confirmed
    `/api/search_base_units` still correctly matches base units on the new "Internal
    Wireless" and "WWAN Card" values (e.g. `Internal Wireless: "Intel AX210"` → 9 JLT
    matches, `WWAN Card: "Sierra MC7411"` → 1 match).

- **[Claude]** **Applied the WiFi/WWAN split above to JLT's real catalog data, not just the
  search facet - Technical (and every other screen) now shows three separate boxes instead of
  one mixed "Internal Wireless" box, and added a 4th carrier value.** The previous entry only
  changed how the *Search by Requirements* dropdown derives its values from JLT's raw
  "Internal Wireless" rows; Technical (and Sales' main per-platform dropdowns) still grouped
  every option by its real `category` field, which was still the one mixed "Internal Wireless"
  bucket for every screen except Search. Per the user - confirmed JLT-only, not Winmate - this
  needed to actually be a real data change: a one-time migration re-labeled each JLT
  "Internal Wireless" row's real `category` (61 rows across all 15 platforms, only the
  `category` field touched - code/description/prices untouched) into whichever of three real
  categories its description actually describes: **"Internal Wireless"** (pure WiFi, no WWAN
  component - 5 rows now real category "WWAN Card": a row naming a specific cellular module;
  56 rows now real category "WWAN Carrier": AT&T/T-Mobile/Verizon, or the row's only WWAN
  signal is a bare "with External PS_EXT-WWAN/WLAN" antenna connector mention with no named
  carrier or module, which now gets a 4th carrier value, **"Generic"**
  (`extract_wwan_carrier` in `ingest/wwan_facets.py`, checked after AT&T/T-Mobile/Verizon and
  only when no module also matched, so a module-named row isn't wrongly tagged Generic too).
  Technical needed no template changes - it already groups options by real category via a
  stable sort keyed on `CATEGORY_ORDER` (`app.py`'s `technical()` view), so the three boxes
  render in the right position and order automatically once the data itself carries the right
  category. `app.py`'s `FACET_CATEGORIES` was generalized so each synthetic wireless field
  (Internal Wireless/WWAN Generation/WWAN Card/WWAN Carrier) scans *all three* real wireless
  categories, not just one - since which real categories actually hold wireless data is now
  brand-dependent (JLT: three; Winmate/Getac/CipherLab: still just "Internal Wireless") - so a
  JLT row that's now real category "WWAN Card" but also names "AX210" in its description is
  still findable via the "Internal Wireless" WiFi facet too, nothing lost by the re-label.
  - **Known consequence, disclosed rather than silently absorbed:** re-labeling changes the
    `brand+platform+category+code` key Purchasing's price-upload matches against. Any
    previously-exported Purchasing pricing sheet covering one of these 61 JLT rows would no
    longer match if re-uploaded - the row would just be silently skipped (not wrongly
    overwritten), and any *new* export going forward reflects the corrected categories.
  - Checked for compatibility impact on already-saved quotes: quote `selections` are frozen
    snapshots taken at Save time (`build_snapshot()`), not re-resolved against live category
    names later, so no already-saved quote's stored price/description/total is affected. Only
    cosmetic risk: re-opening a saved quote that selected one of the recategorized rows for
    further editing might not correctly pre-select it in the (now differently-categorized)
    dropdown. Checked live data: exactly 2 saved quotes (`Acme Manufacturing::2/3`, both seeded
    test data) selected an affected row (`KA`, now "WWAN Carrier") - real quote data unaffected.
  - Verified via the Flask test client: JLT's `WWAN Carrier` facet is now
    `['AT&T', 'Generic', 'T-Mobile', 'Verizon']`; `Internal Wireless`/`WWAN Card` facet values
    unchanged from the previous entry (cross-category scanning confirmed working); live
    Technical render of JLT 1214P shows, in order, "Internal Wireless" (AX210/No Radio rows
    only) → "WWAN Card" (the MC7411 row) → "WWAN Carrier" (AT&T/T-Mobile/Verizon/Generic rows)
    as three separate boxes, each option keeping its own checkbox/code/price.

- **[Claude]** **Fixed a real dead end the user hit live: the "existing quotes" panel under
  Opportunity ID was an interactive "select one to load" dropdown, and picking the wrong thing
  out of it silently blocked Save with no clear explanation.** Reported sequence: rep populates
  an Opportunity ID that already has quotes, sees "N existing quotes for this Opportunity -
  select one to load," picks the existing one (a reasonable guess for what to do with new UI
  appearing on screen) - which loads that quote instead of starting a new one, and since it was
  locked, Save silently disabled with no visible reason why. Root cause wasn't the quote-
  numbering logic (verified correct: `next_quote_number()` in `app.py` already computes
  max-existing+1 correctly - confirmed live, Quote #2 Rev 0 was assigned correctly when the
  panel was left alone) - it was that this panel duplicated Lookup Saved Quote's job while also
  being the thing sitting directly under Populate, where a rep would naturally look for "the
  quote number." Per the user, loading an existing quote to revise it should only be reachable
  through Lookup Saved Quote - this panel now shows read-only text instead of a clickable
  `<select>`: "N existing quotes for this Opportunity. Saving now will create Quote #X, Rev 0.
  To view or revise an existing one instead, use 'Lookup Saved Quote' above." If a quote for
  this same Opportunity ID is already loaded (via Lookup Saved Quote), the message correctly
  switches to "Editing <display_id>... Saving now will revise this quote" instead, so it never
  says something false. Removed the now-unused `.existing-quotes-select` CSS rule. Verified
  live both branches: populating a fresh Opportunity ID with 2 existing quotes showed "Saving
  now will create Quote #3, Rev 0" and Save produced exactly that; loading an existing quote
  first and re-checking showed the correct "Editing ... will revise this quote" message.
- **[Claude]** **Deduped "Processor Options" search - per the user, who spotted 4-5
  near-identical "Intel 6413E" entries stacked at the top of the dropdown and asked "you see
  the issue."** Pulled the full list: 55 distinct real values, at least 8 groups of which are
  the same real chip spelled differently (whitespace, capitalization, ®/™ symbols, or a
  codename like "Elkhart Lake" present in one variant and not another). Unlike storage/OS, a
  CPU model name has no predictable pattern to regex-extract a clean facet from, so this
  couldn't be a blind fuzzy-match - a real near-miss found during review: "Qualcomm 660" is a
  *different, older* SoC than "Qualcomm QCS6490," despite both being "Qualcomm." New
  `ingest/cpu_facets.py` does the cleanup in two tiers: a mechanical pass that's always safe
  (strip ®/™, collapse whitespace including an invisible soft-hyphen character found in one real
  description, drop a trailing "(Optional)"/"No Longer available" annotation) merges purely
  cosmetic duplicates on its own (e.g. `"i7-7600U"` + `"i7-7600U No Longer available"`); a small
  hand-curated alias table (8 groups) handles the rest, built by manually reviewing all 55
  values and presented to the user for confirmation before merging anything - e.g. "Intel 6413E"
  and "Intel 6413E Elkhart Lake" both refer to the Atom x6413E (Elkhart Lake is Intel's codename
  for it), but nothing about the text alone proves that. One pair deliberately left unmerged:
  "ARM 2 x A78 2.0GHz + 4 x A55 2.0GHz" and "ARM Genio 510 2 x A78 2.0GHz + 4 x A55 2.0GH" have
  identical core configs and look like the same chip (MediaTek Genio 510), but that core layout
  isn't unique to one SoC, so it wasn't safe to assume - flagged to the user rather than guessed.
  Per the user, the dropdown now sorts the 8 curated/deduped labels first, everything else
  alphabetically after (`cpu_sort_key`). Wired via the same `FACET_CATEGORIES` mechanism as
  storage/OS, but mapped to itself (`"Processor Options": ("Processor Options",
  normalize_cpu_label)`) since this is a dedup, not a two-category split. Getac's own
  `attributes.cpu` values are untouched (already clean, verified earlier) - this only affects
  JLT/Winmate's real per-SKU rows. 55 raw values collapsed to 40 distinct search values; full
  audit re-run: 0 issues across 607 brand-scoped values. Verified live: dropdown shows the 8
  canonical labels first, and searching "Intel Atom x6413E (Elkhart Lake)" returns 7 real
  matches spanning 1014P/1214N/1214P/1514N/6012/6015/VM1007E FM07E - platforms that used to be
  split across up to 5 separate, un-mergeable search terms.
- **[Claude]** **Split WWAN Generation and WWAN Carrier out of "Internal Wireless," per the
  user** ("wwan is mixed up with wifi... the carrier should be separated from wwan, similar to
  what you did with storage capacity and storage technology"). 109 distinct real values, jumbling
  WiFi standard, Bluetooth version, GPS, and cellular generation/carrier all into one free-text
  string (e.g. `"WLAN (802.11 a/b/g/n/ac) + BT 5.0 + GPS 4G Sierra EM7455"`). Unlike storage/OS/
  CPU, this did NOT fully replace the real category - a single description here can encode WiFi
  standard AND Bluetooth version AND GPS AND cellular simultaneously, so removing the flat
  "Internal Wireless" list the way storage/OS's raw categories were removed would have lost real
  search capability (e.g. searching by WiFi standard alone). New `ingest/wwan_facets.py` extracts
  two facets that are *added* alongside the still-intact original list: **WWAN Generation**
  (3G/4G/5G, LTE counts as 4G) and **WWAN Carrier** (named US carriers AT&T/T-Mobile/Verizon, or
  a specific cellular module - Telit LN920/FN990, Sierra EM7455/EM7411/EM9291/EM7595/MC7455/
  MC7411, Quectel RedCap, MediaTek, HUAWEI). Deliberately did NOT merge EM7455/MC7455 or
  EM7411/MC7411 - different Sierra Wireless part numbers (M.2 vs mini-PCIe), and nothing in the
  source text confirms they're interchangeable for search, unlike the CPU codename pairs that
  were confirmed same-chip. New `_KEEP_RAW_ALONGSIDE_FACETS` set in `app.py` (`{"Internal
  Wireless"}`) marks this category as "facets plus the original," a new mode alongside
  `FACET_CATEGORIES`'s existing full-replacement mode. Getac's own `attributes.wireless` is
  untouched (already simple/clean) - this only affects JLT/Winmate's real per-SKU rows. Full
  audit re-run: 0 issues across 628 brand-scoped values, and "Internal Wireless" itself still has
  all 109 original values (confirmed nothing was lost). Verified live and via direct API calls:
  `WWAN Generation` dropdown shows `3G, 4G, 5G`; searching Generation="5G" alone returns 6 real
  matches across differently-worded platforms; searching Carrier="AT&T" returns 12 matches; the
  original exact-match "Internal Wireless" search still works unchanged.
- **[Claude]** **Re-partitioned the WWAN split from the entry above, per the user:** cellular
  module part numbers (Telit LN920, Sierra EM7455/EM7411/EM9291/EM7595/MC7455/MC7411, Quectel
  RedCap, MediaTek, HUAWEI) moved out of "WWAN Carrier" into "WWAN Generation" instead, sorted
  after the plain 3G/4G/5G entries. Rationale, from the user: "the cards are tied to 3g 4g 5g
  more than the carrier" - a specific module identifies which generation a unit supports more
  directly than it identifies a telecom carrier, so it belongs alongside Generation, not lumped
  in with the three actual named carriers (AT&T/T-Mobile/Verizon) that remain in "WWAN Carrier."
  Required generalizing `FACET_CATEGORIES` in `app.py`: each synthetic category now maps to a
  *list* of extractor functions instead of one, so a single row can contribute both a generic
  value (e.g. "4G") and a more specific one (e.g. "Sierra EM7455") to the same "WWAN Generation"
  dropdown - `ingest/wwan_facets.py` gained `extract_wwan_module` (the part-number patterns,
  split out of what was `extract_wwan_carrier`) and `wwan_generation_sort_key` (plain generations
  first in 3G/4G/5G order, module names alphabetically after). Every existing single-extractor
  `FACET_CATEGORIES` entry (storage, OS, CPU) was updated to wrap its extractor in a one-item
  list for consistency - no behavior change for those. Full audit re-run: still 0 issues across
  628 brand-scoped values (same total, just repartitioned - nothing added or removed). Verified
  live: `WWAN Generation` dropdown now shows `3G, 4G, 5G` followed by the module names
  (`HUAWEI, MediaTek, Quectel RedCap, Sierra EM7411, ...`); `WWAN Carrier` shows only
  `AT&T, T-Mobile, Verizon`; searching a module name from the Generation field still returns the
  same real matches as before (8 for "Sierra EM7455").
- **[Claude]** Moved Purchasing's "Generate Report" button (§2, "What's been quoted to Sales —
  action items") from below the action-items table to right above it, per the user - previously
  a rep had to scroll past every flagged line item to find it. `templates/purchasing.html`
  only; the "Generate Catalog Report" button in §1 is unaffected. Verified via the rendered
  HTML: the button now appears immediately after the section heading/description, before
  `<table>`.
- **[Claude]** **Purchasing navigation overhaul, per the user ("this page is difficult to
  navigate"), which surfaced a real, serious pre-existing bug along the way: Save Prices was
  completely broken for the full pricing-gaps table.** Three requested changes:
  1. **"Export Pricing Sheet" button + "Jump to §2" link at the very top of the page** (before
     the Upload box), so the export → edit → re-upload round trip and the quote-action-items
     section are both reachable with zero scrolling. Triggers the same `generate_catalog_report`
     action as §1's button, in its own minimal form.
  2. **"Generate Catalog Report" duplicated at the top of §1** in addition to staying at the
     bottom, per the user ("should also be at the top").
  3. **Generated reports are now real browser downloads**, not just a filename shown as text.
     New `/purchasing/download/<filename>` route serves files from `data/reports/` (path
     validated against the reports directory to block `../` traversal). Applies to both
     `report_generated` and `quotes_report_generated` banners.

  **The bug found while testing #2 live:** clicking "Generate Catalog Report" produced a live
  413 "Request Entity Too Large." Root cause had two layers. First, a real bug in the existing
  HTML: the pricing-gaps form had a hidden `<input name="action" value="save_prices">` *and* a
  `<button name="action" value="generate_catalog_report">` sharing the same field name - browsers
  submit both, and Flask's `request.form.get("action")` returns whichever comes first in
  document order (the hidden input), so clicking "Generate Catalog Report" silently ran
  `save_prices` instead and never actually generated a report. Fixed by giving every button in
  that form (`Save Prices`, `Generate Catalog Report` x2) its own explicit `name="action"
  value="..."` and removing the hidden default entirely. Second, and more serious: the pricing
  table has one row per flagged part (3,421 today) x 5 fields each (`row_key` + 4 price fields)
  = ~17,100 form fields - Werkzeug 3.x's default `max_form_parts=1000` safety limit rejects the
  request before `app.py` ever runs. **This meant Save Prices itself - the core Purchasing
  editing workflow - was already completely broken for the full table**, not just the report
  button; confirmed via the Flask test client (`Save Prices` on all 3,421 rows: `413`, both
  before and independent of the button-collision fix). Fixed by raising
  `app.config["MAX_FORM_PARTS"]` to 50,000 and `MAX_FORM_MEMORY_SIZE"]` to 5,000,000 (well above
  today's ~17K fields / ~900KB, with headroom for catalog growth). Also decoupled "Generate
  Catalog Report" (all three copies) from the giant Save-Prices form entirely - it doesn't need
  any of that row data, so there's no reason for it to submit 17K fields at all going forward.

  **A mistake made while testing this, caught and fixed the same turn:** an early verification
  pass submitted a full-size test payload with every price field blank, which - because it used
  the real `/purchasing` route rather than a dry run - actually saved `null` over 3,421 rows'
  real Floor Price/MSRP/Cost values in `data/parts_vmt_q1_2026.json` (confirmed via `git diff`:
  5,984 changed lines, all real values replaced with `null`). Caught immediately via `git diff`
  before this was committed anywhere; reverted with `git checkout -- data/parts_vmt_q1_2026.json`
  and confirmed restored (spot-checked known values, e.g. 1014P/H back to Floor 50/MSRP 100/
  Cost 30) - nothing was pushed or committed in the corrupted state.

  Verified after all fixes: Save Prices on the real, full 3,421-row/17,106-field form now
  returns `200` (was `413`); Generate Catalog Report (top of page, top of §1, bottom of §1) all
  correctly generate a report without touching Save Prices; the download link works end-to-end
  live (clicked "Export Pricing Sheet," got a real `<a href="/purchasing/download/...">` link,
  confirmed via `read_page`); "Jump to §2" scrolls straight past the 3,421-row table.
- **[Claude]** Two follow-up fixes to the above, per the user: **"Save Prices" now also appears
  at the top of §1**, next to "Generate Catalog Report" (the user noticed only one of the pair
  was duplicated up top). Uses the HTML5 `form="pricing-form"` attribute on a button physically
  outside the giant form - clicking it still submits the full table's real field data (the id'd
  form, not an empty duplicate), so it stays a genuine save, not a no-op. Also added a
  **"Back to top" link at §2**, mirroring the "Jump to §2" link already at the top, since the
  page only had one-way navigation before. Verified live: clicked the new top Save Prices button
  against the real full-size form (200, not 413, confirmed via `git diff` then reverted since it
  was a test); clicked "Jump to §2" then "Back to top" and landed correctly both times.

  **Incidental finding while testing, not a bug to fix:** re-saving via either Save Prices
  button converts touched fields from JSON numbers to numeric strings (`50` -> `"50"`) - HTML
  forms only ever submit text, and `save_prices` doesn't cast it back. Confirmed harmless:
  `money_value()` (`app.py`) already handles both types identically for every downstream total.
  Reverted the test save's byte diff via `git checkout --` regardless, to keep the file's
  existing formatting/types undisturbed by testing.
- **[Claude]** **Replaced §1's inline price-editing table with export/view + a two-step
  preview-then-confirm import, and added two Jeeves stub buttons - a bigger redesign than the
  form-limit fix earlier today, per the user.** Rather than keep raising Werkzeug's form
  limits as the catalog grows, §1's ~17,000-field editable table and both "Save Prices"
  buttons are gone entirely. In their place:
  - **View Report** (new, top of page and top of §1) - new `GET /purchasing/pricing_gaps`
    route + `templates/purchasing_pricing_gaps.html`, a read-only table of the same flagged
    parts, no form, no inputs. The only way to change a price now is Export -> edit offline
    -> Upload.
  - **Upload now previews before applying.** `merge_parts()` already returned
    `(added, updated, skipped)` without saving anything itself - the caller always called
    `save_parts()` separately - so a true dry run just meant calling it against
    `copy.deepcopy(parts)` first. Uploading now parses the file, dry-runs the merge for
    real counts, and stashes the already-parsed rows as JSON in new `PENDING_IMPORTS_DIR`
    (`data/pending_imports/<token>.json`, gitignored like `data/reports/`) instead of saving
    immediately. Shows "This will update N row(s) and skip M" with **Continue**
    (`action=confirm_import`) and **Cancel** (`action=cancel_import`) buttons, each posting
    just the token. Continue re-loads the JSON (no re-parsing the original CSV/XLSX needed),
    runs the real merge against the live `parts` list, saves, and deletes the temp file.
    Cancel just deletes it - nothing applied. Confirming an expired/already-used token shows
    an error instead of silently no-op'ing.
  - **Part # Compare** and **$ Jeeves Compare** (new, top of page) - stubs, matching the
    existing "Upload Hspt" pattern (`api_quote_upload()`) since there's no live Jeeves
    access yet (confirmed with the user). Each posts a dedicated action
    (`jeeves_part_compare`/`jeeves_price_compare`) that renders a "Jeeves isn't connected
    yet..." banner describing what it'll do once connected - checking Jeeves Part Number
    mappings and comparing local vs. Jeeves prices respectively (see the updated Jeeves
    connector TODO entry above for the deferred Jeeves Part Number mapping problem this is
    blocked on). Every top-row button (`Export Pricing Sheet`, `View Report`,
    `Part # Compare`, `$ Jeeves Compare`) now has a `title` hover tooltip explaining its
    use, per the user - matches this codebase's existing tooltip convention (`title=` is
    already used on Sales' HubSpot badge and the disabled-brand search option, not a new
    pattern).

  Verified: `GET /purchasing` no longer has a `<table>` in §1's HTML; `GET
  /purchasing/pricing_gaps` returns a real 3,422-row (3,421 + header) read-only table with
  zero `<input>` elements; both Jeeves buttons render their correct stub message. Full
  import round trip scripted via the Flask test client: uploading the real 3,421-row export
  unchanged showed a preview of "2,970 updated, 0 skipped" with **zero** change to
  `data/parts_vmt_q1_2026.json` (`git diff` empty) until Confirm was actually clicked, at
  which point the diff appeared and matched the preview exactly; separately, Upload -> Cancel
  left zero diff and deleted the pending JSON; confirming an already-cancelled token
  correctly showed the expired-token error instead of applying anything. All test diffs
  reverted via `git checkout --` before committing.

## 2026-08-17

- **[Claude]** **Fixed: the quote status banner's "(LOCKED)" state was unreadable** — dark
  near-black text (inherited from `body`'s default `color: #1b1f27`) on a dark brown
  background (`#7a3b12`). Same root pattern as the earlier `.wselect-trigger` white-on-white
  bug: `.quote-status` set a dark `background` for all three states (default navy, saved
  green, locked brown) but never its own `color`, so it fell through to the page default
  instead of the white every other dark-background element in this app uses. Fixed by
  setting `color: white` on the base `.quote-status` rule (covers all three states via
  inheritance, not just `.locked`). Proactively scanned the rest of `static/css` for the
  same pattern (dark background, no explicit color) - the two other hits (`.part-number`,
  `button:hover`) both turned out to be false positives once checked against their actual
  parent/base rule, which already supplies `color: white` via inheritance - no other real
  instances found.
- **[Claude]** **Every Save now locks the quote, and Rev now bumps on any real content
  change regardless of lock state** — two related changes to quote lifecycle rules, per the
  user, reported live: loaded an existing quote, changed an option, Accept, Save — Rev
  didn't move. Root cause: the original rule only bumped Rev if the quote had *ever* been
  locked, which this quote hadn't. Rather than just fix that check, the user confirmed (via
  a direct tradeoff question) they want Save to auto-lock every time, which makes the old
  check meaningless on its own — replaced it with a real diff against what's stored
  (`selections`/`brand`/`platform`), so a no-op re-save (Accept+Save clicked twice with
  nothing actually different) doesn't spuriously bump Rev. Applies to the very first save
  too, not just revisions. To make another change after a save: Unlock (immediately
  clickable — `dirty` is false right after a fresh save) → edit → Accept → Save, which locks
  it again. Verified live end-to-end: load → `locked:false` → change → Accept → Save →
  `locked:true` + Rev bumped + Unlock clickable → Unlock → dropdowns re-enabled → change
  again → Accept → Save → locked again + Rev bumped again; also confirmed a genuine no-op
  re-save leaves Rev untouched.
- **[Claude]** **Fixed: Opportunity ID survived Clear, and survived switching to a different
  customer entirely**, leaving a real, confusing mismatch (Customer: Blue Ridge Industrial,
  Opportunity ID still "Acme Manufacturing" from before) - reported live by the user after
  clicking Clear then picking a new customer. Neither the Clear button nor any of the
  "confirm a customer" entry points (Customer Lookup pick, Manual Customer Accept) ever
  touched Opportunity ID before. Added `resetOpportunityIfCustomerChanging()`, called at
  each of those three entry points before the customer actually changes: if there's a
  non-blank Opportunity ID and the customer is genuinely changing, it's cleared along with
  any loaded-quote state. Deliberately NOT called from `loadQuote()`/
  `copyQuoteConfigToCurrentCustomer()`, which set their own correct Opportunity ID on
  purpose and would have had it wiped right back out by this. Verified via direct function
  calls reproducing the exact reported sequence (pick Acme → Populate → Clear → pick Blue
  Ridge): Opportunity ID went `"Acme Manufacturing"` → `""` → stayed `""` for Blue Ridge,
  never carrying the old value forward.
- **[Claude]** **Fixed a real dead end: Populate was hidden for the Customer-Lookup
  (simulated HubSpot) path, leaving no way to get an Opportunity ID at all for that path.**
  The user hit this directly: selected a customer via Customer Lookup, accepted a
  configuration, and Save was blocked on a required Opportunity ID with no visible way to
  supply one (Populate only showed for Manual customers; typing directly into the field
  still worked but nothing in the UI said so). Root cause was my own earlier reasoning that a
  real HubSpot connector would supply a real deal ID for "lookup" customers - true once that
  connector exists, not true today. Populate now shows for both customer paths until a real
  connector actually can supply one. Verified live: Customer Lookup → Acme Manufacturing →
  Populate → Opportunity ID fills with "Acme Manufacturing" → Save unblocked.
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
- **[Claude]** **Expanded Getac's free-text attribute extraction from 2 fields (cpu, os) to
  6** (cpu, os, ram, storage, display, wireless), per the user's original ask to catalog specs
  beyond just CPU. Added `extract_ram`, `extract_storage`, `extract_display`, and
  `extract_wireless` to `ingest/parse_getac.py`, each pulling its value out of the same
  Description free text `extract_cpu`/`extract_os` already used. `extract_display` needed a
  workaround: source rows consistently pair display size with the nearby "webcam" mention in
  a comma-separated clause, but the literal `"` character after the size number is corrupted
  (mojibake) on several rows (e.g. S510AD) — so it matches the leading number in that clause
  instead of requiring the quote mark. Re-ingested the real 370-row Getac catalog and verified
  all six attributes hit 100% (370/370). Wired all six into `app.py`'s
  `ATTRIBUTE_CATEGORY_MAP` (was cpu/os/ram only) so Search by Requirements can filter Getac
  units by storage, display, and wireless too, not just cpu/os/ram.
- **[Claude]** **Fixed a real bug the user caught by hand: Sales Search by Requirements
  returned zero results for most Getac processor values**, even though the value came straight
  from the search dropdown itself. Root cause in `api_search_base_units` (`app.py`): a Getac
  platform (e.g. B360G3) can have several "Base Unit:" rows - one per sellable SKU, each with
  its own cpu/ram/storage/etc in `attributes` - but the search grouped all of a platform's rows
  together and checked the attribute criteria against only the *first* one found, silently
  ignoring every other SKU's attributes. 14 of the 22 distinct Getac CPU values (confirmed by
  reproducing the exact matching logic against the real 370-row catalog) returned zero matches
  as a result, purely because whatever SKU happened to be first in file order for a platform
  determined the only CPU that platform could ever match on. Rewrote the matching so, for
  brands with more than one Base Unit row per platform, every attribute criterion is checked
  against each row individually (and all criteria must be satisfied by the *same* row - checking
  each criterion independently against different rows would wrongly match cpu+ram/storage/etc
  combinations no real SKU actually offers). JLT/Winmate's real per-category matching (a single
  Base Unit per platform, options mixed freely) is untouched. Also fixed a related gap this
  surfaced: `search-overlay`'s "Select" button only ever set brand+platform, so even a correct
  search result would load the platform's default Base Unit rather than the specific SKU that
  matched - now the backend returns the matched SKU's `code` and the frontend passes it as
  `presetSelections` so Select loads the exact unit found. Verified: reproduced the matching
  logic standalone (0 of 22 Getac CPU values now return zero matches, was 14/22) and live in
  the browser (searched a previously-broken CPU, got real F120/UX10G5 matches, Select loaded
  the exact matching SKU - F120's FW8739DA4IA, not a default).
- **[Claude]** **Also found and fixed a related data-quality bug while investigating the above**
  (same root cause category - "the search should reflect the actual inventory," per the user):
  one real CPU (Intel Core i5-1335U) was silently split into two separate dropdown entries
  because the F110G7 rows' source description used a non-breaking space (U+00A0) between "Core"
  and "i5-1335U" where every other row uses a regular space - textually different strings for
  the same real spec, so searching the regular-space form missed all 30 F110G7 SKUs using the
  nbsp form. Fixed by normalizing all whitespace runs (including nbsp) to a single regular
  space on the Description text before any attribute extraction runs, in `ingest/parse_getac.py`
  - applies to all six extracted fields, not just cpu, so the same class of bug can't recur in
  ram/storage/display/wireless/os either. Re-ingested; Getac's distinct CPU count went from 22
  to 21 (the duplicate merged away), total row count unchanged at 370.
- **[Claude]** **Audited every Search by Requirements dropdown value across all 4 brands, per
  the user's follow-up ask** ("make sure that if you search on an option it will result in one
  or more systems"), after the Getac bug above. Scripted every value from `/api/search_options`
  through `/api/search_base_units` (the exact same data path a rep uses) and checked each
  returns >=1 match with a real part `code`. JLT, Winmate, and Getac: 0 issues across 660
  brand-scoped values. **CipherLab: 160 dead-end values** (51 "Add On Options:", 109 "Operating
  System:") that could never return a match, for a different reason than the Getac bug - not a
  matching-logic bug, a genuine data gap. `CipherLab Price Increase effective 4_10_2026 Product
  List.xlsx` is a price *increase* list, not a full catalog: a product family whose base-unit
  price didn't change in this increase (8600, HERA51, and a batch of Wavelink/Ivanti
  software-license SKUs numbered 901/903/904/etc.) shows up with only its accessories,
  warranties, or licenses and **no `Base Unit:` row anywhere in the file** - there's no system
  in this data for those options to ever attach to, so offering them as a search requirement was
  always a dead end regardless of matching logic. Fixed in `api_search_options` (`app.py`): the
  dropdown now only pools values from a (brand, platform) that has at least one `Base Unit:` row
  among approved parts. CipherLab's dropdown count dropped from 702 to 542 (exactly the 160
  dead-end values). Re-ran the full audit after the fix: 0 issues across 1,202 brand-scoped
  values and 1,190 unscoped ("Any brand") values. Verified live: CipherLab's "Add On Options:"
  dropdown no longer offers 8600/HERA51 accessories, only options tied to real in-file systems
  (e.g. RS38 cradles); searching one returns real CipherLab RS38 matches with prices.
- **[Claude]** **Excluded CipherLab from Search by Requirements entirely, per the user** - until
  the price-increase-only source file above is replaced with a fuller catalog, CipherLab's
  option is now greyed out and disabled in the search modal's Brand dropdown (labeled "CipherLab
  (search unavailable)", with a title tooltip pointing at this entry), and the backend excludes
  CipherLab parts from both `/api/search_options` and `/api/search_base_units` regardless of
  which brand is requested - so even a direct API call with `brand=CipherLab`, or the unscoped
  "Any brand" pool, can't surface a CipherLab result. New `SEARCH_EXCLUDED_BRANDS` set in
  `app.py`, checked in both endpoints; the disabled option is rendered from the same set (passed
  to the template as `search_excluded_brands`) so the UI can't drift out of sync with the
  backend. Normal Sales configuration (Brand/Platform/Base Unit dropdowns) is untouched - this
  is search-only, since that's what's actually broken. Meant to be temporary: see the Pending/TODO
  entry above for what to remove once a fuller CipherLab catalog is sourced. Verified: the
  Brand dropdown shows CipherLab greyed out and unselectable; `/api/search_options?brand=
  CipherLab` returns `{}`; an unscoped no-criteria search returns 425 matches across
  JLT/Winmate/Getac only, zero CipherLab.
- **[Claude]** **Split "Storage Drive Options:" search into "Storage Capacity" and "Storage
  Technology", per the user.** Screenshot-driven feedback: searching a specific capacity (e.g.
  60GB) shouldn't require caring whether it's SSD/CFAST/eMMC/etc, and searching a technology
  (e.g. "M.2") should return every drive of that type at every capacity - the old single dropdown
  of 48 distinct full descriptions (JLT+Winmate combined, e.g. "64GB eMMC" vs "64GB M.2 SSD" vs
  "60 GB CFAST" as three unrelated exact-match strings) could do neither. New shared
  `ingest/storage_facets.py` module extracts both facets from free text: capacity normalizes
  industry rounding-convention pairs into one canonical tier (60GB/64GB, 120GB/128GB,
  240GB/256GB, 480GB/512GB, 960GB/1TB all collapse together - different vendors' marketing
  numbers for the same real capacity class), technology checks for M.2/mSATA/CFAST/eMMC/Micro
  SD/NVMe/SSD in that priority order (M.2 wins even when the text also says SSD/NVMe/SATA).
  Getac precomputes both at ingest time (`attributes.storage`/`attributes.storage_tech`, same
  pattern as its other five attributes) via a new `_storage_clause()` helper in
  `ingest/parse_getac.py` that isolates the storage-specific snippet first (the full description
  also states RAM as a GB quantity earlier in the same string, so classifying the whole thing
  risked grabbing the wrong number). JLT/Winmate have no precomputed attributes on their real
  per-SKU option rows, so `app.py` derives both facets on the fly at dropdown-build time
  (`api_search_options`) and match time (`api_search_base_units`, via a new
  `STORAGE_FACET_CATEGORIES` map) using the identical extractor functions, so the two can't drift
  out of sync. Re-ingested Getac (336/370 rows gained `storage_tech`; the other 34 - all
  ZX10G2/ZX80 Android tablets - only say generic "Storage" in their source text, no technology
  stated, same as JLT/Winmate rows with no technology keyword). Full audit re-run after the
  change: 0 issues across 633 brand-scoped values (down from 660 pre-split, since collapsing 48
  raw storage descriptions into 8 capacity + 7 technology values is the whole point). Verified
  live and via direct API calls: Storage Technology = "M.2" returns 14 matches spanning both
  JLT and Winmate across every capacity from 64GB to 512GB; Storage Capacity = "64GB" returns 27
  matches spanning SSD/eMMC/CFAST/M.2/unspecified technology.
- **[Claude]** **Split "Operating System:" search into "OS Version" and "OS Edition", per the
  user** ("when someone's looking at Windows or Android they don't care about GAC or LTSC").
  The real data was messier than storage's: 31 distinct "Any brand" OS descriptions mixed
  version, licensing/servicing channel (Pro/IoT Enterprise/LTSC/LTSB/GAC/SAC), bit-width, and
  even a leftover CPU model in a few rows (`"Windows 11 IoT Enterprise LTSC  i7-1185GRE"`,
  `"...(Intel Quad-Core E3845 Processor)"`) into one exact-match string. New
  `ingest/os_facets.py` (mirrors `storage_facets.py`) extracts OS Version
  (`Android 9/11/12/13/15`, `Windows 7/10/11`, `Linux Ubuntu 20.04` - dedupes `Android 11.0` into
  `Android 11`) and OS Edition (`GAC`/`SAC`/`LTSC`/`LTSB`/`IoT Enterprise`/`Pro`, checked in that
  priority order). CPU mentions inside OS descriptions are simply never matched by these
  patterns, so they're ignored rather than corrupting the version - that's Processor Options'
  job. Order matters for one real row: `"Windows 11 IoT Enterprise GAC (64-bit) - Microsoft has
  not released Win 11 IoT Enterprise LTSC yet"` mentions LTSC only to say it's *not* what this
  SKU is - checking GAC/SAC before LTSC/LTSB avoids misclassifying it (verified: that row's
  platform correctly shows under OS Edition = GAC, and does *not* also show under LTSC unless a
  separate real LTSC option genuinely exists on the same platform, which one of its neighbors
  does).

  Generalized `STORAGE_FACET_CATEGORIES` into `FACET_CATEGORIES`, now mapping each synthetic
  search category to `(real_category, extractor)` instead of just an extractor, since storage
  and OS pull from two different real categories ("Storage Drive Options:" vs "Operating
  System:"). Getac precomputes both new attributes at ingest time
  (`attributes.os_version`/`os_edition`, fed its already-isolated `os` attribute) the same
  pattern as its other five. Added `_os_version_sort_key` (groups by family, then sorts
  numerically within it) since plain string sort would put "Windows 7" after "Windows 10"/"11"
  and "Android 11" before "Android 9". Re-ingested Getac (370/370 rows gained `os_version`,
  336/370 gained `os_edition` - the other 34 are the same ZX10G2/ZX80 Android tablets with no
  edition concept). Full audit re-run: 0 issues across 618 brand-scoped values. Verified live
  and via direct API calls: `OS Version` dropdown shows `Android 9, 11, 12, 13, 15, Linux
  Ubuntu 20.04, Windows 7, 10, 11` in that exact grouped/ascending order; searching OS
  Version = "Windows 11" returns 356 real matches across all three non-excluded brands.

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
