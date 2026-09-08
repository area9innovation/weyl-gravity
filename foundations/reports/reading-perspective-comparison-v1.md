# Compare reading perspectives in place

The Introduction and wave account now use native checkboxes rather than a
single-choice dropdown. Readers can select any nonempty combination of General,
Physics, Mathematics and Specialist. “Compare all four” provides a review
shortcut. This supersedes the one-visible-edition interaction described in the
initial audience-reading-site-v1 report; the scientific prose and shared claim
records are unchanged.

Each selected account has its perspective label, an explicit background note,
and a distinct accent color. Text labels carry the distinction independently
of color. Physics and Mathematics remain different background assumptions,
not a numerical ability ranking. Matching sections display adjacent accounts
in two columns on wide screens and stack them on small screens. Concept
explanations also retain their perspective labels when shown together.

Selections are remembered and propagate in comma-separated audience URLs.
Existing single-perspective links remain valid. Section anchors and the
current reading position are preserved when changing the layout. Unchecking
the last perspective restores it with an accessible explanation. Native
checkboxes support keyboard operation; the selection summary is announced without
moving focus. No JavaScript and unavailable-storage fallbacks are preserved.

The browser regression now covers single and multiple selections, compare-all,
text/background labels, unchanged shared status, selection persistence, keyboard
interaction, the last-selected guard, malformed/duplicate URL values, mobile
layout and legacy atlas links. The independent structural verifier checks all
four checkboxes. Desktop and mobile screenshots were reviewed.

This is an editorial interface change (`LOCAL-ALGEBRAIC` navigation artifact),
not a scientific promotion. The running wt-exposed server serves the rebuilt
files directly. Receipt: `foundations/receipts/reading-perspective-comparison-v1.json`.

CLOSE-OUT: DONE — readers can compare labeled audience editions within each section, with background requirements visible.
EVIDENCE: foundations/site/index.html
