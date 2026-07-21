# Science Forge blocked-work triage — 2026-07-21

## Decision

The current `BLOCKED` list is scientifically relevant, but it is not one
operational category.  It currently combines independent research-frontier
questions, ordinary dependency waits, intentionally deferred tool consumers,
and superseded branches.

Use the following lifecycle meanings:

- **BLOCKED** — an unexpected obstruction requiring an accountable action now.
- **WAITING** — a named internal or external prerequisite is not yet terminal.
- **PARKED** — a deliberate long-horizon deferral with a named wake condition
  and optional review date.
- **STALE / REPLAY NEEDED** — the named prerequisite landed; the old disposition
  must be reevaluated, but the item is never silently made READY.
- **RETIRED / SUPERSEDED** — the scientific branch is no longer applicable.
- **PARTIAL / DECOMPOSED** — material work landed, but the remaining stop
  condition has been split into independently pullable children.

`BLOCKED` should therefore remain a small incident queue.  WAITING and PARKED
work remain fully auditable, but do not appear as equally urgent alarms.

## Live thirteen-item classification

### Keep as independent frontier roots

1. `bridge-candidate18-real-radical-orbit-quotient` — PARKED/WAITING_TOOL on
   exact real-primary component and orbit-stratification support.
2. `classical-berger-q26-104-row-free-adjoint-completion` — PARKED/WAITING_TOOL
   on the full sparse chain-complex extension/SDR solver.  The available
   single-free-differential machinery is only a partial prerequisite.
3. `classical-closed-s3-relative-phase-clock-atlas` — WAITING_TOOL on the
   certified Conflux consumer/importer.
4. `observer-temporal-curl-second-jet-or-all-jet-disposition` — WAITING_TOOL on
   differential PBW-module membership.
5. `quantum-tau-adic-full-bv-hadamard-feynman-kernel` — PARKED pending a
   deliberately selected same-background tau-adic classical BV analytic
   producer.  No matching structural producer is presently declared.

These are relevant research frontiers.  They should remain in the programme,
but should not be reported as five immediate incidents.

### Convert the C26 group into one structured dependency chain

The producer
`quantum-c26-bikernel-support-profile-export` is terminally OBSTRUCTED and its
obstruction is a valid input to the next theorem.  The intended chain is:

1. `quantum-c26-bikernel-support-profile-export` (terminal disposition), then
2. `classical-c26-support-domain-completion`, then
3. `classical-bikernel-homotopy-extension-for-q26`, then
4. `quantum-berger-retained-bv-hadamard-restriction`, then
5. `quantum-berger-physical-cohomology-positivity`.

The last four entries are not independent blockers.  They are WAITING
descendants.  Their current free-text missing-dependency events are not enough
for deterministic folding; append-only typed `blocked_on` or dependency-edge
events are required.  The accepted blocker-frontier request correctly refuses
to infer these links by fuzzy prose matching.

### Retire the superseded Observer branch

The certified 132-defect minimal-repair no-go reports that the fixed-background
single-action replacement-112 family cannot define the old 160-row pushout.
The repair is now terminally obstructed, so the following legacy items were
retired as superseded:

1. `observer-berger-apparatus-160-executable-unary-export`;
2. `observer-berger-apparatus-base-unary-executable-producers`;
3. `observer-berger-apparatus-reduced-cohomology-pairing`;
4. `observer-berger-apparatus-z2-memory-response`.

The three descendants that would otherwise have become spuriously pullable
when a retired dependency counted as terminal were retired at the same time:

1. `observer-berger-apparatus-physical-reduction-after-160-export`;
2. `observer-berger-apparatus-z2-after-160-reduction`;
3. `observer-berger-relational-redshift-after-160-z2`.

The authoritative successor is
`observer-repaired112-apparatus-pushout-after-132-defect-disposition`, whose
negative branch records nonactivation and whose positive branch would rebuild
from an actually repaired unary.  Do not reopen the four legacy branches.

## Oversized-work and shortfall rule

A SHORTFALL is evidence, not a reason to offer the unchanged oversized task
again indefinitely.

When a package has several independent remaining proof obligations:

1. Record which stable stop-condition clauses are already satisfied and their
   receipts.
2. Move the parent to non-pullable `PARTIAL / DECOMPOSED`.
3. Create one bounded child per coherent residual obligation, with explicit
   `SPLIT_FROM` and `IMPLEMENTS_CLAUSE` relations.
4. Give each child its own owner, allowed paths, resource budget, falsifier and
   stop condition.
5. Add a join item only when integration is itself nontrivial.
6. Fold the parent to DONE only when every mandatory clause is terminally
   satisfied; preserve any obstruction in the aggregate verdict.

Missing external input remains WAITING/BLOCKED, not DECOMPOSED.  A split is a
scientific declaration of independent residual obligations, never an automatic
text partition.

The implementation request is
`sf:forge-request/science-forge-shortfall-work-splitting-and-join`.

## Dashboard consequence

The default coordinator view should show:

- actionable blocker roots;
- WAITING and PARKED counts;
- stale items requiring replay;
- one compact line per decomposed parent, including child counts;
- one-command exact drill-down for every hidden item and dependency path.

This retains fail-closed completeness while making the dashboard describe what
someone can actually do next.
