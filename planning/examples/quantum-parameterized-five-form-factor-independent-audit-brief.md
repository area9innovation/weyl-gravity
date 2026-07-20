PULLED by agent quantum-qme-1 — stream quantum-qme — lease exclusive (acquired 2026-07-20T19:29:15Z, expires 2026-07-20T23:29:15Z)

WORK PACKAGE sf:program/work/quantum-parameterized-five-form-factor-independent-audit  (state: ACTIVE, owner: quantum-qme)

## Objective
Independently audit the theorem that the generic parity-even third-curvature form factors form an affine family over global primed spectral data and contain no nonzero universal Schur-sensitive finite combination.

## Stop condition (what DONE means)
Import the terminal parameterized five-form-factor result and every physical, ghost, contact, zero-mode and Schur input by hash without running its producer.  Reconstruct the labelled carrier quotient and finite determinant dependence by a method-distinct resolvent, finite-matrix or covariant-perturbation route.  Build at least two admissible global primed completions with identical complete local symbol, residues, scale response, zero-mode projector and subtraction but distinct finite third variations.  Prove the dimension and kernel of the universal combinations, replay all labelled-box symmetries and contact endpoints, and verify that the round-S4 and S2xS2 holdouts do not interpolate the generic datum.  Export either an exact freeze audit of the affine-family theorem or the smallest coefficient-level contradiction.

## Current gate
method-distinct freeze audit of global-spectral nonuniqueness and the universal-combination kernel

## Forbidden
no producer serialization called verification; no special-background agreement called generic determination; no local symbol or Wodzicki residue used to fix a smoothing-sensitive finite trace; no parity-odd, QME, Lorentzian, state, particle or unitarity promotion

## Activates (downstream this unlocks)
- quantum-background-specific-five-form-factor-spectral-realization
- or a repaired parameterized form-factor theorem

## Dependencies (verify state before starting)
- sf:program/work/quantum-complete-five-form-factor-assembly-after-schur-kernel — DONE (met)

## Additional item fields (schema superset — passed through)
- `allowed_paths`: ["quantum-weyl/","reports/","paper/12-pure-weyl-one-loop-bv-anomaly.tex","paper/12-pure-weyl-one-loop-bv-anomaly-claim-map.json","notes/d-quotient-quantum-team-brief.md","notes/universe-building-roadmap.md","planning/forge-requests/"]
- `resource_hint`: "QUANTUM INDEPENDENT RAIL.  The theorem is nonuniqueness of a finite global datum, not failure to calculate a locally determined number."
- `notes`: ["The audit must make the space of admissible global completions and its action on the five functions explicit."]
- `input_commit`: "ed265d70c"
- `stream`: "quantum-qme"

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
