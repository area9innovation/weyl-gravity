# Readable term occurrences and case presentation

All 143 standalone term pages now load a term-specific occurrence file and show
at most eight indexed passages per page, with Previous/Next controls. Matches
are highlighted in rendered prose. Source links open readable indexed-prose views;
papers additionally link to their typeset PDF where one exists. Original source
files and machine-readable spans/hashes remain secondary provenance downloads.

The occurrence producer reuses dictionary associations from the extraction cache,
deduplicates identical unit/start/end spans, and excludes the term's own dictionary
entry. These are lexical matches, not certified semantic uses. Counts may include
repeated representations of a passage. Normalized paper prose omits mathematical
displays and other regions excluded during extraction; it is explicitly not a
replacement for the original paper. No formulas are reconstructed from missing data.

Markdown formatting is rendered through the pinned Markdown 3.5.2 dependency,
then reduced to passive prose tags with no attributes or active links. Input HTML
is escaped. The indexed spans remain in Unicode code-point coordinates over the
unchanged extracted text. The UI displays formatting rather than source code.

Matching already ignored case. The four dependency-tag labels now use sentence
case in the index, tooltips and page headings. Canonical uppercase tag strings
remain unchanged in definitions and aliases. Acronyms retain their conventional
capitalization. No dictionary prose, extraction input or scientific claim changed.

Validation: 13 unit tests, two Chromium suites, the independent reading verifier
and deterministic site verifier pass. Checks cover mixed-case annotation, acronym
preservation, Markdown emphasis and highlight rendering, active-markup exclusion,
pagination, readable source navigation and unchanged source-span identity/completeness.
The occurrence section was visually inspected in Chromium. The companion receipt
records exact commands, elapsed times and source/output hashes.

Tier 0 covers syntax, structured data, hashes and whitespace. Tier 1 covers the
changed editorial package and browser behavior. Tier 2 covers generated consumers
and independent occurrence/source checks. Tier 3 is not needed: no mathematical
input, shared algebra, scientific lifecycle promotion or release changed. Empty
dependency tags and scientific_claims_promoted=false identify this as editorial UI
work, not a new scientific certificate or independent semantic review.

The staged whitespace check flags pre-existing trailing spaces in two exact source
copies (including Markdown hard breaks). Copies are byte-identical to repository
originals and intentionally preserved; the scoped check passes on authored and
other generated files. This exception does not alter imported evidence.
