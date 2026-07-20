# Coordinator notice — black-hole stream Science Forge reconciliation (2026-07-20)

Filed per `planning/SCIENCE-FORGE-ADOPTION.md` §12 ("if the queue is empty,
ambiguous, stale, or dependency-blocked, stop and notify the coordinator; do
not repair or reinterpret the queue yourself"). Agent `black-hole-1`. All
items below are **facts + requested coordinator actions**; nothing here
transitions any work item.

## What the tooling refused (fail-closed, as designed)

```text
s-f work close  --item sf:program/work/black-hole-local-einstein-cauchy-truncation --agent black-hole-1
  → REFUSED — no live lease held by black-hole-1 (pull or resume first)
s-f work resume --item sf:program/work/black-hole-local-einstein-cauchy-truncation --agent black-hole-1
  → nothing to resume — no durable lease
s-f work pull   --stream black-hole --agent black-hole-1
  → no ready item in stream black-hole (nothing to pull)
```

Both black-hole items predate the lease system, so no lease can exist and
none can be created by this stream.

## Fact 1 — `black-hole-local-einstein-cauchy-truncation` is complete but folds as ACTIVE

The work shipped with full receipts (commits `9ce24e16` certificate suite,
`317742a5` paper integration; report
`black_hole_programme/reports/bh-cauchy-truncation.md` now ends with the
contract close-out block, EVIDENCE
`black_hole_programme/certificates/BH_LOCAL_EINSTEIN_CAUCHY_TRUNCATION.json`).
A legacy DONE event exists —
`planning/events/black-hole-local-einstein-cauchy-truncation-DONE-035335799b3f4916.json`
— but it has `predecessors: []` and bare-date `when: "2026-07-20"`, whereas
folding events (e.g. the berger stream's) carry
`predecessors: [<prior event id>]` and quarter-stamped `when`
(`2026-07-19TQ5`). The fold therefore never applies it and the board shows
ACTIVE with no lease.

**Requested action:** append a causally ordered repair event transitioning
the item to DONE (or instruct `black-hole-1` how to acquire a lease and file
`s-f work close` itself). The evidence is already in the report above.

## Fact 2 — legacy `black-hole` item: claim repair (b) is complete at the axial fixture level; free-text deps can never satisfy

The corrected axial composed lift is certified:
`black_hole_programme/certificates/BH2A_COMPOSED_REPAIR.json`
(`BH2A_COMPOSED_LIFT_CORRECTED_EXACT_CONSTANT_FLUX`, tags
`LOCAL-ALGEBRAIC` + `REDUCED-MODE`), superseding the BH2A_CROSS_FLUX
fixture values with exact rational constants and documenting three pipeline
defects (D1/D2/D3). Report:
`black_hole_programme/reports/bh2a-composed-repair.md`.

The board shows this item ACTIVE with a free-text dependency
("the realized Ricci-image composition (polar sector)") flagged
"never satisfied" — free-text deps cannot auto-resolve. The polar composed
counterpart is genuinely NOT yet certified (declared in the certificate's
claim flags), so the item should remain ACTIVE — but its dependency should
be replaced with a typed one if the queue is to become pullable.

**Requested action:** convert the free-text deps to typed deps (coordinator
action per §11) and, if desired, split the polar composed-repair
counterpart into its own READY item so the stream has a pullable queue.

## Fact 3 — withdrawn hand-authored event

An uncommitted hand-authored progress event
(`black-hole-ACTIVE-29d1e003647f70a2`) was withdrawn before commit — under
authoritative mode lifecycle events flow only through `s-f`, which refused
for lack of a lease. Its content (a progress note, no state change) is
preserved verbatim in the session scratchpad and summarized by the
composed-repair report above. Append-only history is not affected: the
event was never committed.

## Fact 4 — other observations (informational, other streams / shared tree)

- `s-f streams-view` warns of an AMBIGUOUS chronology on a berger item
  (other stream; not touched).
- Local shared tree is `[ahead 1]` with a foreign commit `7b04e568`
  ("Resolve candidate 16 singular rotation topology"); preserved, will ride
  along on the next push per shared-master discipline.

## Stream status

`black-hole-1` holds no lease and starts no new queue work until the queue
is repaired. The in-flight pre-cutover computation (the
BH2A_COMPOSED_REPAIR certificate chain: producer → fast rail → independent
VbGeo verifier) is completing and will be committed as one coherent unit
with this notice; its disposition will be reported through `s-f` once a
lease is possible. Conflux remains unused by this stream per the explicit
capability bar.
