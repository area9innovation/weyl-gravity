# Terminology publication frequency filter

The global dictionary now publishes extracted candidates only after five corpus
occurrences, with an exception for matches to existing dictionary entries.
The threshold is applied before source filtering: a term can legitimately have
one occurrence in the ladder while qualifying through its use elsewhere.
The alphabetical list and all seven downloadable scope shards use this policy.
Unused source contexts are omitted from the shards.

This reduces 110,990 raw candidates to 6,205 published candidates (104,785
excluded). Three dictionary matches are retained below the threshold. The full,
content-addressed extraction is unchanged and remains available for editorial
review. Published metadata records both counts and the counting policy; each
candidate records its global occurrence count.

Counts include repeated representations of material, such as prose reproduced
in a paper. They are not counts of independent sources. Frequency does not
establish that a phrase is a useful technical term, correctly explained, or
scientifically important. No scientific claim or lifecycle state changes.

Validation: 19 scoped tests, both dictionary/browser suites, the deterministic
site verifier and reading-site verifier pass. The initial new test incorrectly
used an integer to look up a JSON object key; corrected to its string form and
the complete scoped suite rerun successfully. Tier 3 is unnecessary because no
scientific inputs, core algebra or theorem claims changed. Exact commands,
timings and content hashes are in
[the receipt](../receipts/terminology-frequency-filter-v1.json).
