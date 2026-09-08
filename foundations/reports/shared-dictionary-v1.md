# Shared dictionary pilot — 8 September 2026

The reading-perspective checkbox change was already landed as f4394bc9.
This user-directed website extension centralizes the three existing glossary
entries in editorial/dictionary.json and generates a Dictionary comparison
page. Topic glossaries consume the same source. Each entry has stable ID,
explicit aliases, scope and four audience definitions. The site manifest hashes
the source and assets. Definitions retain their existing source-pinned editorial
context; this migration is not independent expert approval.

Native inline buttons provide dotted underlines and definitions through hover,
focus and tap. Popups use a passage's perspective or the shared selection,
show the scope, and link to all four versions. Escape, close and outside click
dismiss them. Popups remain hoverable and adapt to the viewport. Automatic
annotation also processes dynamically rendered atlas content, covering the
576-coordinate interface without rewriting cell records. Links, code, math,
controls and marked exclusions remain untouched. This is an annotation
mechanism, not complete terminology coverage or an audience rewrite of the atlas.

The initial browser run found a popup obscuring a trigger near the viewport
bottom. Positioning now places it above the trigger when space below is
insufficient; the regression checks desktop behavior and mobile bounds.
An initial editorial-record consistency check also caught the derived glossary
being exported separately from its new canonical dictionary; the generated
record now matches its source again. Final checks are recorded in
../receipts/shared-dictionary-v1.json. Earlier failures are not counted as passes.

Next editorial work: inventory recurring corpus terms, prioritize by frequency
and reader difficulty, identify ambiguous meanings, attach per-entry sources
and review all four definitions. Three entries do not establish glossary
completeness. Structural checks do not establish semantic equivalence.
No scientific result, certificate, dependency tag or lifecycle is promoted.
Tier 3 is unnecessary because no core algebra or scientific claim changed.
