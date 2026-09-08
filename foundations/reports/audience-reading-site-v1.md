# Audience-based reading architecture

The current site now opens with one unified Introduction, rather than the
576-cell matrix. General, Physics, Mathematics and Specialist are four
editions of that account, with different prerequisites and emphasis. The wave
question has been migrated through the same mechanism. This is navigation and
editorial work, tagged `LOCAL-ALGEBRAIC`; it establishes no new physics or
reverse-mathematical theorem.

## Architecture and migration

Primary navigation is Introduction, Questions, Theory journeys, Research atlas
and Papers. The former homepage lives at `atlas.html`. Existing view, cell and
filter hashes on `index.html` redirect with parameters preserved. Existing
technical tools retain their content and are labelled specialist reference
views. Their historical progress claims carry a prominent, readable current
export-rejection notice.

The audience selector preserves topic and section. Explicit audience URLs
win over remembered preferences; storage is optional. Only one edition is
visible, and the general edition is readable without JavaScript. Shared
scientific records supply the same status, boundary and evidence at every
perspective. Precise formulations appear in specialist prose and expandable
evidence sections; the common visible summaries use plain language.

Paper 99 and Paper 98 supplied the introductory material. They remain dated
publications on the Papers page, with an explicit correction to affirmative
full-transfer statements in older accounts. Paper 00 and Paper 21 are also
available locally. The current introduction distinguishes the rejected full
export from the partial repair and the independent wave result.

The wave account separates supplied convergence rates from ordinary Cauchy
promises. The mathematics edition introduces RCA₀ and ACA₀; the specialist
edition states the representation-sensitive equivalence and credits the
standard completeness reversal. Every edition preserves the limits: this is
not a laboratory requirement for stronger axioms and the infinite argument
has not been proof-assistant formalized.

## Authoring and review

`foundations/editorial/reading-content.json` separates audience briefs, stable
topic/section identities, shared claims, concept explanations and pinned
sources. A changed source hash stops generation pending editorial review.
This is a stale-source guard, not a semantic equivalence checker: reviewing
all affected prose remains necessary before repinning. The initial review
was by the AI assistant against repository evidence, not independent human
approval. See `foundations/editorial/README.md` for the authoring workflow.

The page renderer escapes authored prose. The browser switches static editions;
no runtime AI, external model service, account or external script is required.
The topic pages, archive PDFs and evidence can be read from a static host.

## Validation and limits

The independent reading verifier checks pinned sources, audience coverage,
section IDs, shared status instances, local links and current correction
boundaries. Mutation tests reject stale hashes, missing editions and section
drift. Existing atlas tests were updated to inspect its new path and pass.
Real Chromium checks cover all four editions, section preservation, URL and
preference behavior, back navigation, legacy links, mobile overflow,
no-JavaScript reading and unavailable local storage. Desktop and mobile
screenshots were inspected. The older positivity page's navigation regression
is included.

This first migration covers the Introduction and wave question. Other atlas
views remain technical references; the positivity interaction retains its
existing account and is explicitly marked as pending audience migration. No
research grades, operator certificates or historical papers were rewritten.
No hosted deployment was performed. Commands, times and content hashes are in
`foundations/receipts/audience-reading-site-v1.json`.

CLOSE-OUT: DONE — the primary introduction and wave topic use one audience-aware architecture, with shared status and preserved atlas navigation.
EVIDENCE: foundations/site/index.html
