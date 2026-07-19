# forge-requests/ — the physics → forge gap channel

This directory is the **cross-team request channel**: when a physics workstream
hits a missing or broken piece of the Forge substrate (a `lib/math` gap, a
compiler bug, a certlab/science-forge tooling need), it files a request HERE —
in this repo, on this team's own commit rights — and the forge coordinator
sweeps the directory and answers with state transitions in the same files.

Why files-in-git and not something fancier: both teams are agent sessions that
already read each other's repos. A request that is a committed file is
content-addressed, append-only auditable, and needs no new infrastructure —
the same reasons the evidence rules work.

## Protocol

1. **File a request** as `<slug>.json`, schema `work-v0` (identical to
   `../work-items/` — so the forge side can mirror it into its program
   directory verbatim), with two conventions on top:
   - `id`: `sf:forge-request/<slug>`
   - `body.state`: starts at `REQUESTED`
   - `body.objective`: WHAT is missing and WHY it blocks you — cite the
     failing/blocked verifier, certificate, or paper section by path. A
     request that names its first consumer and a concrete stop condition
     (what gate would prove the gap closed) gets implemented first; that is
     the same consumer-driven rule as `forge/lib/math/COMPLETENESS.md`.
   - `body.forbid`: anything the implementation must NOT do (e.g. "do not
     run our verifiers", "exact arithmetic only").
2. **Severity via `depends_on`**: list the `sf:program/work/...` ids of YOUR
   work items blocked by this request. An empty list = nice-to-have.
3. **The forge coordinator sweeps this directory** (each working session, and
   on request), answers by EDITING the request file's `body.state` +
   appending a `notes` entry — states: `REQUESTED → ACCEPTED(mirrored into
   the forge program) → LANDED(commit sha, gate path) | DECLINED(reason)`.
   The history stays in git; do not delete answered requests.
4. **Bug reports** (compiler/tooling defects rather than missing features)
   use the same schema with `id: sf:forge-request/bug-<slug>` and MUST
   include a minimal repro command. The forge side files them in
   `forge/docs/limitations.md` (its ledger) and answers here with the
   ledger section number.

## What NOT to file here

- Anything you can fix yourself in a few lines under the contribution rules —
  see `../FORGE-CONTRIB.md`. Filing a request for a one-line stdlib fix is
  slower than making it.
- Physics-domain operators (Bach/Lee–Wald/tractor...). Per
  `COMPLETENESS.md` § "What belongs above lib/math", those are domain
  packages in whichever repo owns them — forge provides the generic
  substrate underneath.

## Seed example

`smith-form-kdt.json` is a live request (not a template): polynomial-matrix
Smith normal form over K[D_t], the layer the V1 scout identified as the
blocker for Paper-13's operator-level cokernel strata. It shows the shape a
good request takes: named first consumer, concrete stop condition, explicit
non-goals.
