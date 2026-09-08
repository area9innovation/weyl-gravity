# Standalone dictionary pages and removal of appended lists

Each of the 143 explained concepts now has a static `term-<id>.html` page,
with its own title, four perspective accounts, related links and source references.
The global dictionary contains the searchable alphabetical index and optional
editorial inventory, with no full term accounts embedded beneath them. Hover,
focus and tap still provide previews; the comparison link opens the term's page.
Native index links support opening a new tab and work without JavaScript.

The introduction and wave pages no longer append the separate 143-term
“Terms used in this account” list. That duplicate list was missed in the previous
compact-dictionary change and explains the reported “Causality and causal support”
item. Inline annotations and a short link to the global dictionary replace it.

Authored crosslinks and editorial inventory links point directly to term pages.
Old `dictionary.html#<id>` links redirect to the corresponding page, preserving
the audience query, when JavaScript and dictionary data are available. Without
JavaScript the index remains usable, but old fragments do not auto-redirect.
No definitions or mathematical claims changed.

Validation: 10 scoped unit tests, three Chromium suites, the independent reading
verifier and full generated-site verifier pass. Checks cover removal of appended
lists on both reading pages, inline previews, single-term pages, four-perspective
comparison, legacy bookmarks, no-JavaScript entry reading, alphabetical column
flow and mobile bounds. Desktop term-page rendering was visually inspected.
The initial reading-browser assertion failed because the audience mechanism adds
a query to dictionary links; the corrected test checks the destination path.
Exact commands, timings and hashes are in the companion receipt.

Tier 0: syntax, structured data, source hashes and scoped diff checks. Tier 1:
changed editorial package and browser consumers. Tier 2: deterministic generated
site and independent link/provenance audit. Tier 3 not run: no mathematical input,
shared algebra, lifecycle promotion or release changed. Scientific dependency
tags are empty; no scientific result or independent semantic review is claimed.
