# Programme-wide paper-coverage baseline preflight

## Disposition

`BLOCKED_ON_TYPED_DISCOVERY_ADAPTER`, with a nonempty full-corpus census.

This preflight ran the first full-repository Science Forge discovery pass for
the Phase 1 reverse result-to-paper audit.  It did **not** accept the subsequent
empty paper-coverage output as a publication verdict.

## Corpus census

The deterministic shadow import reported:

- 24 certificate families;
- 1,359 certificate nodes;
- 1,022 claim nodes;
- 2,310 `DEPENDS_ON` edges;
- 2,436 references, of which 1,864 resolved within a family and 451 resolved
  across families;
- 121 unresolved references after global resolution.

The source inventory separately found 26 primary manuscript, supplement,
bridge, executive-summary, and public-introduction source files under
`paper/`.  This is a file census only; it is not a human materiality judgment.

## Fail-closed finding

The shadow graph contained only the node kinds `certificate` and `claim`.
It contained no typed `result`, `paper`, or `paper-claim` nodes.  Passing that
nonempty graph directly to `s-f paper-coverage --mode advisory` returned:

```text
results=0 classified=0 unclassified=0 papers=0 paper_claims=0
review_queue=0 flags=0
```

That output is vacuous.  It does not mean that the programme has no uncovered
results or unsupported paper claims.  The discovery vocabulary and the
paper-coverage vocabulary have not yet been connected on the adoption corpus.

The exact adoption defect is recorded in
`sf:forge-request/bug-paper-coverage-shadow-import-vacuous-pass`.  The request
requires both a typed discovery/adapter path and a non-vacuity guard so that a
large incompatible graph cannot silently look like an empty successful audit.

## Reproduction

```text
s-f shadow-import-all <physics-root> <forge-root> \
  /tmp/sf-paper-coverage-phase1/evidence.json \
  /tmp/sf-paper-coverage-phase1/import-ledger.json

s-f paper-coverage \
  /tmp/sf-paper-coverage-phase1/evidence.json \
  --mode advisory --stamp 2026-07-21T08:42:00Z \
  -o /tmp/sf-paper-coverage-phase1/report.json
```

Content hashes and the complete manuscript-source inventory are recorded in
`planning/paper-coverage/phase1-baseline-census-2026-07-21.json`.

## Human-review boundary

No materiality annotation has been labeled human-authored by this preflight.
All 1,359 imported certificate candidates remain unclassified pending a typed
review queue.  Once the adapter lands, the human coordinator must review at
least the recent results and every headline currently used in Papers 00,
09--14, 90--92, 98, and 99.  Machine-generated similarity, filenames, or
citation counts must not substitute for that review.

## Does not establish

This preflight does not establish paper completeness, publication debt,
release readiness, or Phase 1 closure.  It establishes the corpus scale and
the first exact obstruction to running the intended bidirectional audit.

CLOSE-OUT: BLOCKED_ON_TYPED_DISCOVERY_ADAPTER

EVIDENCE: `planning/paper-coverage/phase1-baseline-census-2026-07-21.json` and
`planning/forge-requests/bug-paper-coverage-shadow-import-vacuous-pass.json`
