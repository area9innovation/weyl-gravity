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
explanations. The 67 current entries include separate RCA₀ and ACA₀ entries;
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

## Strength-ladder index

The ladder has a dedicated alphabetical “Terms on this page” index.
`ladder-terms.json` is its curated vocabulary registry; `ladder_terms.py`
indexes the actual displayed fields, including stage identifiers, conditional
results, open/excluded statements and separation notes. `site/ladder-terms.json`
retains exact strings and character offsets for every match. The broad corpus
inventory embeds this focused index and now also reads the formerly omitted
conditional/open/separation fields.

The initial index has 52 concepts and four status labels. Five links point to
related dictionary entries; other entries explicitly say Definition pending.
A related entry is not a claim that the entire phrase is explained. No new
four-perspective definitions are invented by indexing. Stages and historical
scientific grades remain unchanged. Visible underscore-separated stage names
are indexed as displayed labels, unlike hidden machine identifiers.

Stage links preserve `view=ladder`, `termStage` and the audience query; the
selected stage is focused on navigation and reload. Add reviewed vocabulary
to the registry, then rebuild the site and inventory. The browser check
compares every recorded source string with the rendered ladder so missing
rendered-field coverage is exposed separately from extraction reproduction.

## Automatic terminology discovery and review

Start at `dictionary.html` through the global Dictionary navigation; the
ladder links to the same index with a source filter. Enable Show editing tools
for drafting controls. Old `term-review.html` links redirect here.
The queue covers the 576 matrix cells, ladder, other selected atlas prose,
reading accounts, dictionary explanations and source papers. Search and filter
by source, explanation status or candidate type. Select candidates and download
a JSON drafting brief with source contexts and requirements for all four
perspectives. Selections last only for the current page session; each selection
retains occurrences from the source scope where it was made.

`extract_editorial_terms.py` combines spaCy English tagging and noun chunks,
KeyphraseVectorizers grammar candidates, nested phrases, abbreviations,
hyphenated compounds, known dictionary aliases and APS PhySH labels. Complete
short text units are retained as explanation tasks, so a claim such as “exact
wave-equation residual zero” is not lost when a parser splits its terminology.
Single content words are deliberately retained too: this favors discovery
coverage at the cost of noise. Frequency is not a difficulty score. The existing
curated alphabetical ladder registry remains the reader-facing index; the
automatic review queue supplies candidates for improving it and the dictionary.

No generated candidate is approved or published as a definition. Even an exact
dictionary match requires checking the sense in its passage. An external
vocabulary match supplies an identifier and aliases, not audience explanations.
PhySH covers physics topics; it is not a complete reverse-mathematics lexicon.
There is no global recall guarantee. The user's initial ladder block is an
independent coverage fixture, never an extraction input.

Rebuild with Python 3.12 and a separate CPU grammar environment:

```sh
bash foundations/setup_editorial_nlp.sh /tmp/editorial-nlp-cpu
python3 foundations/import_editorial_vocabulary.py --check
/tmp/editorial-nlp-cpu/bin/python foundations/extract_editorial_terms.py
python3 foundations/build_matrix_site_v2.py
python3 foundations/build_term_inventory.py
python3 -m unittest foundations.tests.test_editorial_extraction
python3 foundations/verify_reading_site.py
PYTHONPATH=/tmp/tt-browser-deps python3 foundations/tests/browser_term_review.py
```

The setup intentionally omits the vectorizer's unused transformer extras;
this pipeline uses neither embeddings nor GPU packages. `--reproduce` reruns
NLP and byte-compares the result. Routine site builds require no NLP installation:
they validate the cached extraction's input hashes and fail closed if stale.
The expensive production/reproduction rail is separate from fast cached span,
source freshness and example coverage checks. KPV grammar fits use bounded
batches without frequency pruning to avoid its flattened-document regex limit.

`results/TERM_EXTRACTION_V1.json.gz` records exact source occurrences, discovery
methods, unreviewed status, per-perspective availability, source/model hashes
and package versions. Website JSON is compressed and split by source scope so opening the
ladder does not download the paper corpus. Browsing uses the browser’s native
`DecompressionStream`; compressed downloads remain available without JavaScript. Offsets count Unicode code points;
paper text is normalized and carries its original block starting line. The
virtual matrix input is hashed from the actual matrix producer, avoiding a
stale-site circular dependency.

The PhySH 2.8.0 JSON-LD snapshot and CC0 license are stored in `vocabularies/`;
`import_editorial_vocabulary.py` verifies its pinned hash and reproduces the
English label/alias file. Source: <https://physh.org/releases>. NLP tools:
<https://spacy.io/> and <https://github.com/TimSchopf/KeyphraseVectorizers>.

## One global terminology destination

`dictionary.html` is now the reader-facing index for the entire project. The
existing global Dictionary navigation opens it. Explained terms retain their
four-perspective entries and anchors;
the integrated searchable word list defaults to the whole corpus, in
alphabetical order. Source filters narrow this same index to the ladder,
matrix, atlas, reading accounts, dictionary explanations or papers. Unknown
phrases say Definition pending; a lexical match links to a related entry
without claiming the senses agree.

Symbolic/parser fragments are hidden from the reader list unless they match
an existing dictionary entry; editing tools expose the unfiltered candidates.
Draft selection, extraction methods and short-claim tasks are optional editing
tools on this page, hidden by default. `term-review.html` redirects here and
preserves audience and source filters; it no longer hosts a competing interface.
The ladder links directly to the same dictionary with its source filter set.
The global corpus shard is larger than a page-specific shard; full definitions
remain available without JavaScript while the index loads.

## Excluding equations and references at the source

`term_source_filter.py` identifies source spans before prose normalization and
NLP. It excludes marked inline/display math, standard math environments,
bibliography blocks and known citation records copied into the atlas appendix,
citation/reference arguments, author metadata and explicit
initials/“et al.” attributions, code blocks and structural markup. Prose before
and after an excluded span is processed separately: removing an equation cannot
join its two neighboring phrases into an invented term. Source units retain raw
start/end offsets and original line locations, in addition to normalized-text
occurrence offsets.

An exact registered dictionary alias inside inline math is retained (for
example ACA₀). Names are not globally blacklisted: Weyl curvature and Cauchy
sequence remain eligible concepts. Unmarked residual notation is rejected at
the candidate boundary unless it is a registered alias. Unknown custom TeX
macros are not expanded; this is a source filter, not a general TeX engine or a
semantic classifier of every name. Unclosed recognized math/code environments
are excluded through end of file and reported in the exclusion ledger.

The compressed extraction artifact records every excluded span and its reason,
plus retained symbolic aliases. The website summary exposes the counts; the
complete ledger remains in the extraction artifact. No dictionary definitions
or scientific claims are changed by filtering. Independent checks:

```sh
python3 -m unittest foundations.tests.test_term_source_filter foundations.tests.test_editorial_extraction
```

## Proposed core dictionary

The [150-concept proposal](../reports/core-terminology-proposal-v1.md) is the
next editorial selection exercise, not an automatic publication list. It proposes
67 introduction essentials (including seven existing entries), 76 atlas bridges
and seven specialist topics. The editable selection is
`core-terminology-proposal.json`; each row has a reason, priority and source-search
phrases. Those phrases locate evidence and must not become annotation aliases
without separate semantic review.

Generate its source inventory with
`python3 foundations/build_core_terminology_proposal.py`; reproduce with `--check`
and independently check structure and source spans with
`python3 foundations/verify_core_terminology_proposal.py`. Approve, consolidate,
defer or remove proposed concepts before writing their four perspectives. The
public dictionary and existing extraction publication policy are unchanged by
this proposal.

## Core dictionary, first batch implemented

The user approved implementation of the proposal’s first batch: all 67 concepts
now have four authored accounts, including 60 new entries and expanded explanations
for the seven original entries. The remaining 83 proposals are a writing backlog,
not empty public dictionary entries. See [the implementation report](../reports/core-dictionary-v1.md).

The default dictionary is a searchable static A–Z list of explained concepts.
The extraction queue is behind a closed Editorial inventory disclosure and loads
only when requested. Public lookup works through canonical labels, explicit aliases
and acronym expansions; no extracted phrase automatically becomes a definition.
Bare ACA/RCA are no longer aliases of ACA₀/RCA₀. Ambiguous vocabulary such as field
and support is searchable but does not automatically annotate surrounding prose.

Run `python3 -m unittest foundations.tests.test_core_dictionary foundations.tests.test_reading_site`
after rebuilding the site, plus the dictionary and term-review browser tests.
Structural and source checks do not certify the semantics of these AI-authored
explanations or replace independent scientific review.
