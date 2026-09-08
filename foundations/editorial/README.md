# One reading system, several assumed backgrounds

The website is the current explanatory account. Dated papers remain
publications, not competing current entrances. This first migration replaces
the matrix homepage with one introduction and ports the wave topic into the
same four-perspective structure. Questions and Papers organize the reading
route; Theory journeys and Research atlas retain existing technical tools.
The positivity demonstration retains its existing interactive account and is
explicitly marked as awaiting audience migration. The atlas itself remains a
specialist reference, not an automatically simplified audience edition.

## Content contract

`reading-content.json` is the editable source. It separates:

- sources: repository paths and hashes reviewed for this edition;
- claims: one current status, statement, boundary and evidence list per result;
- audiences: assumed knowledge and editorial purpose;
- topics: a common title and stable section IDs with four different accounts;
- dictionary.json: shared definitions appropriate to each background.

The four perspectives are General, Physics, Mathematics and Specialist.
They are not a single ability ranking. Mathematics does not assume field
theory or reverse mathematics; Physics does not assume mathematical logic.
Specialist sections explicitly identify the prerequisites of the result.
Audience selection changes the argument and emphasis, not its scientific
strength. Checkboxes select one or more editions for review. Each section
shows the selected accounts together, in two columns on wide screens and a
single stack on mobile. Labels, accent colors and explicit background notes
identify each perspective; color is never the only indication. The selection
preserves the topic, section anchor and common status record.

The site contains fixed, reviewed editions. There is no runtime AI rewriting.
The initial editorial review was performed by the AI assistant against pinned
repository sources; it is not independent human approval or peer review.

## Revising an account

1. Read the current evidence, including corrections to older papers.
2. Update the shared claim and its boundary before revising prose. Record
   which source changed and why the new status follows.
3. Review every audience edition that uses that claim. Explain essential
   concepts in the body; use optional definitions for reminders. A specialist
   account should lead with the actual contribution and credit standard results.
4. Keep section identities aligned. Do not copy introductory explanations into
   a new standalone entrance; update the existing topic.
5. Refresh the reviewed source hashes only after this review. A hash change
   blocks generation; it does not authorize automatic acceptance of new claims.
6. Build, verify local evidence links, exercise audience switching and old
   permalinks, and inspect the desktop and mobile reading experience.

Shared records mechanically prevent different displayed statuses. The build
cannot prove that prose preserves meaning: editorial review remains necessary.
The structure/provenance verifier is explicitly not a semantic proof checker.

## Build and checks

```
python3 foundations/build_matrix_site_v2.py
python3 foundations/verify_reading_site.py
python3 -m unittest foundations.tests.test_reading_site foundations.tests.test_matrix_site
PYTHONPATH=/tmp/tt-browser-deps python3 foundations/tests/browser_reading_site.py
```

`reading_site.py` renders static HTML with the general edition visible without
JavaScript. `reading.js` shows the selected, already-rendered editions. An
explicit `?audience=general,mathematics` link takes precedence over stored
preference; older single-perspective links still work. At least one edition
stays selected, and “Compare all four” is a shortcut. A section anchor such as
`#inputs` survives switching. Local storage is optional.

The old `index.html#view=...`, cell and filter links redirect to `atlas.html`
with their query and hash preserved. Research data, matrix grades and
historical certificates are unchanged. The local PDFs are downloadable;
affirmative full-transfer statements in earlier introductions carry a visible
correction on the Papers page. No hosted deployment is implied by building.

## Shared dictionary

`dictionary.json` (schema version 2) owns both short definitions and expanded
explanations. The seven current entries include separate RCA₀ and ACA₀ entries;
`#rca` remains a valid link. Entries are sorted alphabetically, with a word list
that also exposes useful alternative names such as Modulus. General remains
readable without JavaScript.

Each stable ID has explicit aliases, scope, four short definitions, four sets
of explanatory blocks, related terms, and content-hashed source records.
External reference links supplement the pinned project sources. The builder
fails on stale source hashes, missing perspectives, duplicate IDs or aliases,
and unknown related terms. Topic glossaries use the same short definitions
and link to the fuller account. Popups offer expandable detail for each active
perspective; the dictionary page displays that detail directly.

Write for the reader's next question:

- General: explain the idea without relying on the term being defined; use a
  concrete example and say why the distinction matters.
- Physics: connect to modeling, measurement or approximation, while explaining
  unfamiliar logic and representation assumptions.
- Mathematics: give the defining structure and conditions; explain unfamiliar
  physical interpretation and the coding used by the result.
- Specialist: state the exact role, hypotheses, contribution and claim boundary.
  More detail need not mean more elementary background.

Every entry should explain its use and a likely misunderstanding, not merely
replace one unfamiliar phrase with another. Sources and an AI editorial review
statement remain visible. These are not independently approved definitions or
new scientific certificates. Structural checks cannot certify semantic accuracy.

Annotation matches explicit aliases, longest first, with Unicode boundaries,
and processes dynamically rendered atlas prose. Links, controls, code, formulas,
navigation, glossary blocks and dictionary entries are excluded. Use
`data-no-dictionary` for a passage or `auto_annotate: false` for an entire entry.
State is currently dictionary-only because its meanings need contextual
selection. No runtime AI generates text. Missing dictionary requests preserve
ordinary reading. Hover, focus and tap open definitions; Escape dismisses them.

## Repeatable terminology inventory

`python3 foundations/build_term_inventory.py` writes
`results/TERM_INVENTORY_V1.json` and `reports/term-inventory-v1.md`.
Use `--check` to detect drift. Rebuild the site first if matrix data changed.
The inventory reads all 576 cell prose records, six atlas prose collections,
38 current paper/source documents and the reading account. It excludes duplicate
same-stem Markdown when TeX exists, PDFs, site copies and machine identifiers.
The exact corpus is content-hashed; its size may change on future runs.

The inventory contains 75 manually selected alias families plus 200 automatically
extracted word/phrase candidates. It records cell and paper reach, raw frequency,
distinct whole-document text counts, source locations and sample contexts.
Repeated templates still affect rankings; frequency is not reader difficulty.
TeX normalization is heuristic. Inventory hits do not validate historical claims.

Use the proposed prerequisite → bridge → specialist sequence in the report to
plan future definitions. Resolve overloaded senses before enabling annotation.
The automatic discovery list is an editorial queue, never an automatic publish
list. A dictionary match does not mean all uses of that term are explained.

Checks:

```
python3 foundations/build_term_inventory.py --check
python3 -m unittest foundations.tests.test_term_inventory foundations.tests.test_reading_site
PYTHONPATH=/tmp/tt-browser-deps python3 foundations/tests/browser_dictionary.py
```

## Shared layout and the living introduction

The current technology remains Python-generated static HTML, plain CSS and
small JavaScript modules. This fits a source-pinned publication with a rich
client-side atlas. A framework migration would not itself fix inconsistent
content or page components. Reconsider a backend if editorial accounts,
concurrent browser editing or permissions become requirements; reconsider a
larger client framework if shared application state becomes substantially
more complex than the current menus and atlas.

`reading_site.site_header()` is the single source for main navigation and the
perspective menu on all seven main routes. `site-shell.css` scopes the shared
header and menu styles, including legacy atlas/case pages. `reading.js` owns
selection, persistence, link propagation and menu dismissal. Native details,
summary and checkboxes provide the keyboard interaction; this is a form
popover, not an ARIA application menu. Shared pages explicitly say that only
their term definitions change; the atlas is not presented as four rewritten
research editions. Specialized atlas controls keep their own layout.

The introduction is the living adaptation of Papers 99 and 98, with eight
aligned sections: programme, assumptions, map, examples, results, limits,
evidence and exploration. Each section has the same identity across all four
perspectives. `section_sources` records the source-paper or correction links
reviewed for each part. The title and visible source links make the papers'
role explicit; current export corrections override their dated affirmative
full-transfer language. The papers themselves remain unchanged.

Dictionary abbreviation entries declare `abbreviation` and `expansion`.
The expansion must occur in the general definition; the build rejects its
absence. The full entry also displays “Stands for”. Explain new abbreviations
at first use in general prose—do not assume an acronym is helpful simply
because it has a dictionary entry.

`linked_text()` adds static crosslinks to unambiguous dictionary terms inside
other entries. It escapes authored text, excludes self-links, links each target
once per paragraph, and respects `auto_annotate: false`. Existing related-term
links handle deliberate connections, including ambiguous terms. Links work
without JavaScript and preserve selected perspectives when JavaScript is
available. Crosslinking is not a substitute for a self-contained explanation.
