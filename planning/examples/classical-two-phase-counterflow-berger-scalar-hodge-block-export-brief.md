WORK PACKAGE sf:program/work/classical-two-phase-counterflow-berger-scalar-hodge-block-export  (state: ACTIVE, owner: classical-1)

## Objective
Construct the first missing same-background scalar Peter--Weyl carrier for the unrestricted 70-row counterflow Berger parent and export exact harmonic inclusions, projections and physical scalar blocks.

## Stop condition (what DONE means)
Import TWO_PHASE_COUNTERFLOW_UNRESTRICTED_ALL_HODGE_HEALTH_SHORTFALL_V1 and TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V1 by exact hashes. On the biaxial q=9/40 Berger sphere, define normalized scalar Wigner/Peter--Weyl modes with stable (j,m,k), reality, conjugation and exceptional labels. Derive the exact scalar-mode inclusions iota into every scalar-type metric, compensator, relative-phase, diagonal-U1, ghost and antifield row of the 70-component parent and projections pi back to the carrier. Prove pi iota=1, closure under q70, local Diff/Weyl/diagonal-U1 gauge rows and the cyclic real structure. Compute the restricted unary, cocycle/boundary bases, physical quotient, descended pairing Gram/inertia/radical, time characteristic/Jordan data and spatial principal/gradient matrix for generic admissible labels plus every exceptional scalar block. Use exact algebraic arithmetic and give a complete declared label domain or the first exact representation-theoretic obstruction. Supply a method-distinct coordinate/tetrad or direct-integration verifier, normalization/conjugation/gauge mutations, strict schema, tier receipt, report and atlas fragment.

## Current gate
first defined scalar physical block of the counterflow Berger parent

## Forbidden
no round-S3 eigenvalue or degeneracy imported without a Berger crosswalk; no causal Green identity used as a pairing-sign theorem; no sampled low modes called generic; no quotient of charged D or R_rel; no scalar result called all-Hodge health; no observer, Hadamard, particle or unitarity promotion

## Activates (downstream this unlocks)
- sf:program/work/classical-two-phase-counterflow-berger-vector-tensor-hodge-block-export

## Dependencies (verify state before starting)
- sf:program/work/classical-two-phase-counterflow-unrestricted-all-hodge-health#ANY_TERMINAL — DONE (met)

## Additional item fields (schema superset — passed through)
- `allowed_paths`: ["d_quotient_classical/compensator/","d_quotient_classical/atlas/","residual_atlas/","reports/","notes/d-quotient-classical-team-brief.md","planning/forge-requests/"]
- `resource_hint`: "PROOF-FIRST SCALAR SPLIT. Consume the landed exact scalar Wigner kernels where applicable, but the physics row maps and quotient remain action-specific. Conflux may only assist after a typed consumer/importer exists and cannot certify completeness by itself."
- `stream`: "classical"

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

## Orientation
Read tools/science-forge/views/agent_context.md, docs/structure-finding-thesis.md, docs/math-roadmap.md, and lib/math/COMPLETENESS.md before starting.
