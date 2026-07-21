PULLED by agent quantum-qme-1 — stream quantum-qme — lease exclusive (acquired 2026-07-20T16:22:31Z, expires 2026-07-20T20:22:31Z)

WORK PACKAGE sf:program/work/quantum-dressed-evanescent-geometric-bv-module-preflight  (state: ACTIVE, owner: quantum)

## Objective
Construct or exactly obstruct the action-independent d-dimensional evanescent geometric BV module required by the certified DR/MS QAP obstruction, leaving explicit extension slots for the later selected Candidate A scalar or Candidate B three-form sector.

## Stop condition (what DONE means)
Import TAU_ADIC_DR_MS_QAP_EVANESCENT_CLOSURE_OBSTRUCTION and the four-dimensional H04/H14 quotient by exact hashes. In dressed metric plus algebraic Weyl-quartet variables, enumerate the complete parity-even and parity-odd local curvature/ghost/antifield densities through canonical dimension four in d=4-epsilon, including d-dimensional Weyl-squared, Euler continuations, R^2, total derivatives and every evanescent difference that can mix through poles and subdivergences. Derive exact projection, finite-renormalization and one-loop mixing maps to the certified four-dimensional module; prove closure under Diff BRST and the canonical quartet or exhibit the first missing evanescent antifield completion. Distinguish basis changes from physically different subtraction prescriptions and reject a mutation that silently identifies E_d with E_4 before pole subtraction. Export a strict schema with separate unfilled Candidate A scalar and Candidate B reducible-three-form extension slots. Stop before choosing either action, computing its Hessian/determinant, asserting a regulator/QAP theorem or performing higher-loop coefficient calculations.

## Current gate
common d-dimensional evanescent geometry needed by any selected-action DR/MS completion

## Forbidden
no four-dimensional identity imposed inside d-dimensional pole algebra; no scalaron or three-form rows guessed before action selection; no basis enumeration called renormalization closure without BRST/mixing maps; no one-loop obstruction promoted to all regulators; no QAP, all-loop QME, global anomaly, Lorentzian, state, particle, scattering or unitarity claim

## Activates (downstream this unlocks)
- a common geometric input to quantum-selected-compensator-repair-dressed-regulator
- a typed Candidate A/B evanescent extension contract
- or a precise obstruction to ordinary DR/MS even before matter-sector completion

## Additional item fields (schema superset — passed through)
- `allowed_paths`: ["quantum-weyl/local_bv/","quantum-weyl/anomalies/","quantum-weyl/spectral/","quantum-weyl/reports/","quantum-weyl/atlas/","reports/","residual_atlas/","paper/12-pure-weyl-one-loop-bv-anomaly.tex","notes/d-quotient-quantum-team-brief.md","notes/universe-building-roadmap.md","planning/forge-requests/"]
- `resource_hint`: "SECOND READY QUANTUM RESERVE. It is common geometric preparation only; the final evanescent module and regulator remain selected-action work."
- `notes`: ["The existing exact obstruction is the noncommutativity of minimal subtraction and four-dimensional projection when the Euler residue is nonzero.","Keep evanescent basis dependence, finite scheme dependence and cohomological triviality as separate fields."]
- `input_commit`: "e2c48b7a2"
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
