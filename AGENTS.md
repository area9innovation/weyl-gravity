# AGENTS.md — Pure-Weyl Classical and Quantum Programme

## Scope

These instructions apply to `physics/symplectic-reconstruction/` and all of
its descendants.  The workspace is shared by the classical and quantum
teams.  Both teams work directly on `master`.

## Scientific frame

- Treat the classical BV–BFV complex as the authoritative source for the
  quantum programme.  Import certified classical data; do not reconstruct a
  competing copy in `quantum-weyl/`.
- The certified residual classes `[W_+^2]` and `[W_-^2]` are centered
  deformation/vertex classes.  They are not one-particle graviton states.
- Classify local counterterms and anomalies before computing coefficients.
  Restore the local quantum master equation before transferring a quantum
  correction to the residual complex.
- The two ruled-out Lorentzian architectures are scoped no-go theorems: the
  24-field scalar normally-hyperbolic witness and the fixed-temporal cyclic
  46-parameter first-order strongly-hyperbolic family.  They do not refute
  the classical BRST complex, residual cohomology, or physical spectrum.

## Shared-master discipline

1. Begin every work session with `git status --short --branch`, then
   `git fetch origin master`.  Record pre-existing edits and do not discard,
   reset, overwrite, or silently reformat them.
2. Keep the shared tree current with `origin/master`.  Pull/rebase only when
   it is safe for all visible work.  If unrelated dirty files prevent it,
   preserve them and integrate after a scoped commit instead of stashing or
   resetting somebody else's changes.
3. Stage explicit pathnames.  Never use a broad `git add .` in the shared
   tree.
4. Commit coherent work directly to `master` and push it.  Immediately before
   pushing, fetch again and integrate any new `origin/master` commits without
   rewriting published history.
5. Small, non-substantial overlapping edits from the other team may be
   verified, included in a coherent commit, and pushed on their behalf.
   Coordinate before taking ownership of substantial or scientifically
   consequential overlapping work.
6. Never force-push.  Never use destructive cleanup commands on shared work.

## Quantum claim boundary

Every quantum result must carry at least one of these exact dependency tags:

```text
LOCAL-ALGEBRAIC
EUCLIDEAN-SPECTRAL
REDUCED-MODE
LORENTZIAN-CAUSAL
```

Do not use a `REDUCED-MODE` or `EUCLIDEAN-SPECTRAL` calculation as evidence
for a `LORENTZIAN-CAUSAL` claim.  In particular, none of the following exists
until an explicit certificate says otherwise:

- a complete Lorentzian off-shell BV propagator;
- a BRST-compatible Hadamard state for the full metric BV complex;
- renormalized Lorentzian time-ordered products;
- a causal perturbative AQFT construction;
- a Lorentzian quantum-master-equation theorem.

Use distinct lifecycle states and never promote one implicitly:

```text
CLASSIFIED
COEFFICIENT_COMPUTED
QME_RESTORED
RESIDUAL_TRANSFERRED
LORENTZIAN_CERTIFIED
```

## Classical import gate

- A classical snapshot is fail-closed until it independently passes
  nilpotency, contraction, chain-map, cyclicity, residual-cohomology, and
  pairing checks required by the quantum brief.
- Store the source commit, schema version, content hashes, missing-object
  ledger, assumptions, and exact verification commands.
- Use `pi_cl` for the homological projection.  Reserve `P` or `mathcal_P` for
  kinetic/witness operators.
- No publishable quantum result may claim the classical freeze gate from a
  partial snapshot.

## Exact computation and architecture

- Cohomology certificates use exact rational or algebraic arithmetic.  Do not
  use floating-point arithmetic in canonical forms, ranks, cocycle tests, or
  trivialization certificates.
- Keep `quantum-weyl/local_bv/` independent of `spectral/` and `lorentzian/`.
- Do not hard-code the expected cohomology basis as the computed answer.
  Generate an ansatz, reduce it canonically, and retain cocycle or
  trivialization witnesses.
- Keep local BRST cohomology, integrated functionals modulo boundary terms,
  and residual state cohomology as separate result kinds.
- Determinants, literature coefficients, beta functions, background trace
  anomalies, and BV master-equation breakings are distinct objects.

## Receipts and documentation

Every material change must leave receipts:

- a deterministic test or verifier command;
- a machine-readable result or certificate with dependency tags;
- content hashes and provenance for imported/generated inputs;
- explicit assumptions, unresolved fields, and fail-closed claim flags;
- a human-readable report entry explaining what was established and what was
  not.

Update the related note or paper as progress is made, in the same coherent
commit when practical.  Paper text must cite the relevant certificate and
preserve its dependency boundary.  Scaffolding and negative results belong
in reports even when they do not yet justify a paper theorem.

## Test tiers

The complete classical verification pipeline is intentionally **not** a
per-commit requirement.  Run the smallest deterministic suite capable of
falsifying the changed claim.

### Tier 0 — edit checks (always)

- parse/compile changed source and structured-data files;
- run `git diff --check` on the scoped paths;
- inspect the exact staged diff and imported content hashes.

### Tier 1 — scoped tests (always for code or certificates)

- run the unit tests and verifier for the changed package or certificate;
- include direct consumers when an interface or schema changes;
- target a fast feedback loop.  If the scoped suite routinely exceeds about
  60 seconds, profile it and split a fast invariant/smoke rail from the
  expensive exhaustive certificate instead of normalizing a slow commit
  loop.

### Tier 2 — affected certificate chain

Run the transitive certificate chain only when a mathematical input, shared
operator, schema, generated artifact, or claim used by that chain changes.
An unchanged, content-addressed classical input may be checked by its hash;
quantum documentation or isolated schema work does not require rebuilding
the entire classical chain.

### Tier 3 — full suite

Run the full repository verification only for:

- a classical or quantum freeze/tag;
- promotion of a paper theorem or lifecycle state;
- changes to shared core algebra used across many certificate chains;
- release preparation, scheduled CI/nightly runs, or an explicit request.

Every receipt records the exact commands, elapsed time, pass/fail status, and
which higher tiers were not run with the criterion that made them
unnecessary.  A timeout or skipped exhaustive run is not a pass and must not
promote a claim.

Before committing, complete the applicable tiers and inspect the exact
staged diff.  Report unrelated working-tree changes without including them.

<!-- science-forge:begin 14e2f2b8b60280ad -->
This programme has adopted Science Forge — auditable, falsifiable computer-assisted research coordination.
The substrate (exact kernels, certificate audits, the evidence graph, the `sfc` coordinator) lives in the
tango/forge repo under `forge/tools/{science-forge,certlab,claimlang,physics-*}` + `forge/lib/math`; read
`forge/tools/science-forge/GUIDE.md` THERE first. In THIS repo:
- `planning/` is the work-item coordination model (one file per stream, append-only events, generated
  briefs) — see `planning/README.md`; it is the operational face of `notes/universe-building-roadmap.md`.
- `reports/science-forge-handoff-2026-07-19.md` is the substrate handoff (a new result, corpus drift
  findings, and what is usable today, all read-only over this tree).
- `ci/science-forge-shadow.sh` is the advisory certlab audit rail — read-only, reports drift WITHOUT
  failing the build (`--strict` to fail closed).
The five Science Forge laws are MANDATORY and match this repo's own discipline: fail closed (a skip or
timeout is never a pass), append-only history (transitions and repairs are new events, never edits),
independent rails (re-running a producer is reproduction, not verification), honest boundaries
(does_not_establish is not a claim), and exact vs numeric are distinct types. This block is ADDITIVE and
managed by hash markers; change the sources (`planning/`, the roadmap), never these bytes by hand.

<!-- science-forge:end -->
