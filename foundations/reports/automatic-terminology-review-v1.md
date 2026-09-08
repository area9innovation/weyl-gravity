# Automatic terminology discovery and contextual review

The website now has a terminology review queue linked from the dictionary and
strength-ladder index. It scans the actual matrix producer, selected atlas and
reading prose, dictionary explanations, and source papers. The initial scope
contains 7,699 source units (6,062 distinct texts), including all 576 matrix
cells. The filtered result contains 328 ladder candidates, 2,972 matrix
candidates and 131,584 candidates across all scopes (overlaps mean scope
counts do not sum). PhySH contributes 3,891 concepts and 4,524 labels/aliases;
142 extracted candidates have an external lexical match. A source-scoped browser queue offers search, coverage/type filters,
source highlights, dictionary and external concept links, and downloadable
four-perspective drafting briefs. This is an editorial tool; scientific
certificates, ladder grades and dictionary definitions are unchanged.

The extractor combines spaCy's English parser, KeyphraseVectorizers, nested
noun phrases, content words, abbreviations and hyphenated compounds. Short
claims are retained independently as explanation tasks. The user's initial
ladder block is checked by a separate fixture: it requires nested concepts as
well as whole phrases, including “exact wave-equation residual zero”. The
fixture is not an extraction input. Punctuation-only spans, one-character
fragments and standalone stopwords are filtered after visual review exposed
parser noise among the highest-frequency results.

APS PhySH 2.8.0 supplies a pinned CC0 vocabulary snapshot and reproducible
English labels/aliases. A lexical match identifies a possible concept; it does
not establish contextual sense, mathematical validity, or an adequate
explanation. Every candidate remains UNREVIEWED. Dictionary matches indicate
that four entries exist for the matched concept, with suitability unreviewed.
Other candidates have missing perspective explanations. No new definitions or
automatic annotations are published by this change.

The broad paper extraction deliberately retains overlapping nested phrases
and is noisy. Counts are candidate counts, not distinct scientific concepts,
validated terminology, or measures of reader difficulty. The generic English
model can misparse mathematical prose; PhySH is not a complete mathematics
lexicon. Editorial decisions remain necessary. Downloaded briefs identify the
source scope used for each selection. Browser selections are temporary and do
not create a persistent review ledger or invoke an AI service.

Source occurrences use Unicode code-point offsets. Paper contexts refer to
normalized blocks and retain the original starting line. All relevant source,
producer and model hashes are recorded. The site build checks input freshness
without loading NLP dependencies and refuses stale data, including when
papers are added or removed. Compressed artifacts
and separate source shards keep the default ladder download small; the paper
shard is substantially larger. The browser uses native DecompressionStream.

Initial integration attempts exposed KPV constructor restrictions, its document
prefix/chunk transformations, and an NLTK regex timeout when the library
flattened the entire corpus. The final producer uses the library's tokenizer
and bounded grammar batches with no frequency pruning. A dedicated CPU setup
avoids unused transformer dependencies; an initial missing psutil import was
corrected in the pinned requirements. These failed attempts were not passes.
An intermediate reproduction and scoped run overlapped a subsequent source
correction; only the final unchanged-input checks support this result.

Validation combines independent source-span/alias checks, explicit stale-input
rejection, the user's example coverage fixture, static source/link checks and
browser interaction tests. Re-running NLP is a separate reproduction rail,
not independent semantic verification. Production takes more than a minute;
fast cached checks are separate. Commands, timings, final artifact hashes and
limits are recorded in `../receipts/automatic-terminology-review-v1.json`.
Tier 2 covers the affected site chain. Tier 3 is unnecessary because no shared
mathematical input, theorem or scientific lifecycle changes.
