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
- concepts: optional definitions appropriate to the selected background.

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
