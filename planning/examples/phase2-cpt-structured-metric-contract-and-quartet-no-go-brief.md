WORK PACKAGE sf:program/work/phase2-cpt-structured-metric-contract-and-quartet-no-go  (state: PROPOSED, owner: phase2-cpt-1)

## Objective
Define the nontrivial structured pseudo-Hermitian/CPT feasibility contract and certify the counterflow Hamiltonian-Hopf quartet as an exact negative control.

## Stop condition (what DONE means)
Import the frozen counterflow j=1/2 reduced generator and characteristic polynomial by exact hashes. Define the accepted eta/C data: invariant-commutant membership, Hermiticity and strict positivity, real-structure and momentum/frequency compatibility, nonsingular parameter dependence, C^2=1 and [C,H]=0 where a C operator is claimed, and chain-map/cohomology descent for BRST. Prove that Q^dagger eta=eta Q with eta>0 is impossible for nonzero nilpotent Q and is therefore not the BRST gate. Give an exact infeasibility certificate for eta>0 and H^dagger eta=eta H on the complex quartet, with a verifier rejecting a real-spectrum or norm-only mutation. Export schema, certificate, independent verifier, tests, report and receipt.

## Current gate
Exact structured-CPT contract plus broken-PT spectral no-go

## Forbidden
no arbitrary eigenbasis metric accepted; no positive eta called a C operator without the involution; no BRST Q required to be positive-metric self-adjoint; no finite-block statement called a field-theoretic unitarity theorem; no anomaly claim

## Activates (downstream this unlocks)
- sf:program/work/phase2-cpt-compact-block-feasibility
- sf:program/work/phase2-cpt-cylinder-brst-feasibility

## Dependencies (verify state before starting)
- sf:program/work/programme-phase1-viability-classification-freeze-v5 — DONE (met)

## Additional item fields (schema superset — passed through)
- `stream`: "quantum-qme"
- `priority`: 0
- `allowed_paths`: ["quantum-weyl/pt_cpt/negative_control/","reports/phase2-cpt-quartet-negative-control-2026-07-22.md","planning/forge-requests/phase2-cpt-structured-exact-solver.json"]
- `resource_hint`: "Small exact linear-algebra theorem and schema. Prefer forge/lib/math exact Hermitian, commutant and positivity machinery; request missing exact support rather than diagonalizing numerically."
- `input_commit`: "4a212883aefa5525cc847d0c12763c74c1c3411a"

## Standing constraints
# Standing constraints for programme agents (included in every work package)

- This tree is the READ-authority. Follow the repo AGENTS.md exactly:
  shared-master discipline (explicit pathspec, never `git add .`, never
  force-push, preserve other teams' dirty files), the quantum claim boundary
  (LOCAL-ALGEBRAIC / EUCLIDEAN-SPECTRAL / REDUCED-MODE / LORENTZIAN-CAUSAL tags;
  never promote one implicitly), exact rational/algebraic arithmetic in every
  canonical form/rank/cocycle test, and the receipts requirement.
- Follow this repository's shared-master Git discipline. At the next coherent
  checkpoint whose changed paths already exist in the declared current commit,
  run `s-f work check --item <id> --agent <you>` and confirm that only
  report∩allowed paths would stage and every unrelated dirty path is left
  alone. Until
  `sf:forge-request/bug-science-forge-precommit-report-new-files` lands and its
  new-file pilot passes, packages that create new files use the manual
  explicit-path audit/commit/push fallback and then report the resulting commit
  through `s-f`; never bypass containment with a fake SHA. After that gate, prefer
  `s-f work commit --item <id> --agent <you> --push --now <ISO>`, whose isolated
  index and prospective-tree verifier mechanize the same discipline. Do NOT
  edit generated views, IR graphs, gate/receipt files, or another team's
  certificates, snapshots, or history.
- Research leases do not edit `notes/universe-building-roadmap.md` or maintain
  lifecycle prose in a shared planning document.  The certificate, report,
  atlas fragment, `s-f work report`, and append-only close-out event are the
  complete team handoff; the coordinator integrates those committed handoffs
  into the roadmap in a separate scoped pass.  A legacy `allowed_paths` entry
  for the roadmap is not authorization to touch it unless the work item's
  objective explicitly is roadmap integration.
- Honor the work item's `stop_condition`, `current_gate`, and `forbid`
  LITERALLY. If the main construction fails, the exact first obstruction is the
  deliverable — do not spend the run polishing prose around an unclosed gate.
- The five Science Forge laws are MANDATORY: fail closed (a skip/timeout is
  never a pass); append-only history (repairs and transitions are new events,
  never edits); independent rails (re-running a producer is reproduction, not
  verification — agreement across independent implementations is the evidence);
  honest boundaries (does_not_establish is not a claim; never promote past the
  evidence); exact and numeric are distinct types with distinct lifecycle labels.
- Test tiers per AGENTS.md: run the smallest deterministic suite that can
  falsify the changed claim (Tier 0/1 always; Tier 2 on shared-input change;
  Tier 3 only for a freeze/tag/release). Record exact commands, elapsed time,
  pass/fail, and which higher tiers were skipped with the criterion.
- The Science Forge substrate (certlab audits, three-rail recomputation, the
  evidence-graph impact queries) lives in the `tango/forge` repo under
  `forge/tools/{science-forge,certlab,claimlang,physics-*}`. It runs READ-ONLY
  over this tree; the advisory CI rail is `ci/science-forge-shadow.sh`.
- Conflux is OPT-IN, not implied by Science Forge adoption. Use it only when the
  work item explicitly enables a consumer-specific Conflux gate. Read
  `planning/SCIENCE-FORGE-ADOPTION.md` and the Conflux README, discovery-sweep,
  provenance, and structure-finding-thesis documents named there. If an
  importer, rule kind, independent replay, resource control, or CLI seam is
  missing, file a committed `work-v0` request under `planning/forge-requests/`
  following its README; do not patch Tango from a physics ticket or negotiate
  an unrecorded workaround. Conflux candidates never promote physics claims.
- Report at the end: deliverables, gate results, deviations from the work item,
  and anything `stop_condition` required that you could not meet (honest
  shortfall, never silent narrowing).

## Close-out footer — COPY VERBATIM at the END of your report
The transition is chosen MECHANICALLY from these two literal lines; a missing
`CLOSE-OUT:` or (for a DONE) `EVIDENCE:` line makes `s-f work close` REFUSE. Paste and fill:

```
CLOSE-OUT: DONE — <one-line rationale>
EVIDENCE: <path to a receipt / certificate / gate that backs it>
```

Markers: `DONE` (objective met) | `OBSTRUCTED` (blocked, cannot proceed) | `SHORTFALL`
(substantive work landed, stop-condition not fully met — keeps the item ACTIVE; add a
`MISSING-DEP: <typed need>` line to fold to BLOCKED). A `DONE` close REQUIRES an `EVIDENCE:` line.
Deliver with `s-f work close --item <id> --agent <you> --report <file> --now <T>` (report+close in
one) — NOT report-then-`yield`, which releases the lease and folds the item back to READY without a
terminal transition (the coordinator overview then flags it as a lagging terminal disposition).

## Orientation
Read tools/science-forge/views/agent_context.md, docs/structure-finding-thesis.md, docs/math-roadmap.md, and lib/math/COMPLETENESS.md before starting.
