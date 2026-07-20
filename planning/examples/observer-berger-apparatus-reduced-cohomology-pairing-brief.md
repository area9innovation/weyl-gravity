PULLED by agent observer-1 — stream observer — lease exclusive (acquired 2026-07-20T20:13:54+02:00, expires 2026-07-21T08:13:54+02:00)

WORK PACKAGE sf:program/work/observer-berger-apparatus-reduced-cohomology-pairing  (state: ACTIVE, owner: observer)

## Objective
Determine which of the new dynamical rod, polarization, memory and emitter directions are physical after the complete linear gauge and constraint reduction.

## Stop condition (what DONE means)
Import BERGER_DYNAMICAL_APPARATUS_PARENT by exact hash.  Compute the exact q1 cohomology of the full 56-row odd-cotangent apparatus extension together with the imported Berger gravity-clock-Maxwell rows, using a declared grading and basis.  Descend the cyclic pairing, real structure and K_Berger action to cohomology; classify radicals, signs, zero modes and rigid-family directions; and identify the precise reduced classes that support the two detector records and persistent memory pairs.  Verify that the rank-two probe response descends to nonzero reduced classes rather than coordinate or auxiliary representatives.  Export canonical representatives, projection/inclusion/contraction data where defined, exact rank witnesses and a method-distinct verifier.  If a complete combined q1 import is missing, export its exact crosswalk contract rather than silently reducing the 56 rows in isolation.

## Current gate
physical reduction and pairing health of the action-derived measuring apparatus

## Forbidden
no raw apparatus coordinate called an observable; no rigid Berger U(1) family covariance promoted to a gauge ghost; no probe-level rank called nonlinear memory; no positivity theorem before radical and real-structure descent; no q2/q3, redshift, particle or quantum promotion

## Activates (downstream this unlocks)
- reduced apparatus representatives for the Berger Z2 and redshift lanes
- or an exact physical-reduction obstruction identifying the missing gauge/constraint row

## Dependencies (verify state before starting)
- sf:program/work/observer-dynamical-apparatus-parent-after-pbw-shortfall — DONE (met)

## Additional item fields (schema superset — passed through)
- `allowed_paths`: ["closed_universe_observers/","reports/","residual_atlas/","paper/09-relational-clocks-berger-d-cartan.tex","notes/closed-universe-observer-team-brief.md","notes/universe-building-roadmap.md","planning/forge-requests/"]
- `resource_hint`: "OBSERVER INDEPENDENT PHYSICAL-STATE LANE.  Audit what survives q1 before interpreting the apparatus records."
- `notes`: ["This lane can run independently of the same-background second-order tangent-cone calculation.","The parent currently proves action derivation and arity-two cyclicity, not that every apparatus coordinate is a physical record."]
- `input_commit`: "87ddc2626d500343fe92914de561f6ccc942c355"
- `stream`: "observer"

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
