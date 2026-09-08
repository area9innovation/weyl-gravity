# Exclude mathematical notation and references before terminology extraction

The previous normalizer removed TeX command names before determining whether
text belonged to an equation or bibliography. This exposed coefficient strings,
environment names, citation keys and author names as apparent noun phrases.
The extraction now locates and excludes those source regions before invoking
spaCy/KeyphraseVectorizers. Adjacent prose is processed as separate fragments;
no phrase can bridge an excluded equation or reference.

Recognized regions include inline/display math delimiters and standard math
environments, bibliography blocks, citation records identified from the structured atlas
metadata (using the appendix generator’s escaping), citation/reference arguments, author
metadata and initials/“et al.” attributions, code, comments and structural
markup. Exact registered dictionary aliases in inline math survive. A surname
alone is not a global exclusion rule: Weyl curvature, Cauchy sequence and
Noether theorem remain eligible. Residual explicit notation is also rejected
at candidate insertion unless registered in the dictionary.

The reported coefficient block in Paper 12 is omitted while its following
“pointwise polynomial identity” remains discoverable. Abbott author/citation
occurrences are removed from the corpus. Every excluded span has raw source
offsets and a reason; retained paper units have raw offsets and original line
locations. Counts and retained symbolic-name records are included in the
machine-readable artifact. Browser drafting briefs retain paper raw offsets.

This is a bounded source lexer, not a TeX expansion engine or a universal
person-name classifier. It cannot promise zero noisy terms or complete recall.
Unknown custom macros are not expanded. Unclosed recognized math/code regions
are excluded to EOF and reported; they are not silently accepted as prose.
Generic English parsing and contextual sense review remain separate limits.
The final scan records 15,962 excluded math regions, 426 citation commands,
24 bibliography blocks and 51 copied bibliographic records. No recognized
regions were left unclosed in this corpus. No definitions or scientific
statuses are promoted.

Tests independently exercise math delimiters, nested environments, citations
with optional arguments, bibliography/code boundaries, retained prose, named
concepts, registered symbolic aliases and fail-closed unclosed math. Artifact
checks ensure no paper unit overlaps an excluded source span and check the
reported examples. Browser checks cover the absence of Abbott and the survival
of the polynomial-identity concept, as well as existing dictionary behavior.
The first full run exposed KeyphraseVectorizers shrinking the shared spaCy
length limit; restoring its original value before phrase matching fixed that
integration error. It was not counted as a pass.

Commands, timings, counts, hashes and boundaries are recorded in
`../receipts/terminology-source-filter-v1.json`. Tier 2 covers the affected site
chain. Tier 3 is not required because no mathematical input, theorem or
scientific lifecycle changes. NLP reproduction is not independent semantic
verification; the source-span and example checks are separate rails.
