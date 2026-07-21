PULLED by agent quantum-qme-1 — stream quantum-qme — lease exclusive (acquired 2026-07-20T18:59:39Z, expires 2026-07-20T22:59:39Z)

WORK PACKAGE sf:program/work/quantum-generic-primed-schur-finite-relative-trace-kernel  (state: ACTIVE, owner: quantum-qme)

## Objective
Construct the generic primed Schur finite relative-trace kernel required to complete the parity-even one-loop five-form-factor functions, or prove the first exact analytic obstruction in a complete declared kernel class.

## Stop condition (what DONE means)
Import PARITY_EVEN_THIRD_CURVATURE_FIVE_FORM_FACTOR_ASSEMBLY and its receiver contract by exact hash.  On the same compact scalar-flat Euclidean carrier, fix the full longitudinal Schur operator S_L(W)=2/3 I+1/3 delta(F+W)^{-1}d, its domain, primed zero-mode projector and common Mellin/proper-time subtraction.  Construct a content-addressed primed Green/resolvent kernel or an equivalent complete spectral measure sufficient to determine R_mu0(K), FP R_mu0(K^2) and the generic det_3(I+K) tail through third curvature order.  Derive their five-carrier variations with labelled-box dependence and prove compatibility with the known Wodzicki scale derivative.  Recover round-S4 and S2xS2 only as holdouts.  If no background-universal finite kernel is determined by the declared local operator data, prove nonuniqueness with two admissible kernels sharing symbol, residues, zero modes and subtraction but giving different finite rows, and state the additional global geometric datum needed to specialize the receiver.  Export exact or rigorously enclosed witnesses and a method-distinct verifier.

## Current gate
generic primed Schur finite kernel, or exact nonuniqueness and its minimal global input

## Forbidden
no special-background interpolation; no Wodzicki residue called a finite determinant; no unprimed zero-mode treatment; no arbitrary smoothing choice hidden in a normalization; no full-BV five-function promotion before all five variations are supplied; no QME, Lorentzian, particle or unitarity claim

## Activates (downstream this unlocks)
- a renewed complete five-form-factor assembly
- or a theorem that the generic finite functions require explicitly parameterized global spectral data

## Additional item fields (schema superset — passed through)
- `allowed_paths`: ["quantum-weyl/","reports/","paper/12-pure-weyl-one-loop-bv-anomaly.tex","paper/12-pure-weyl-one-loop-bv-anomaly-claim-map.json","notes/d-quotient-quantum-team-brief.md","notes/universe-building-roadmap.md","planning/forge-requests/"]
- `resource_hint`: "QUANTUM ANALYTIC PRODUCER.  Resolve the exact smoothing ambiguity rather than fitting the two certified special backgrounds."
- `notes`: ["This task imports an OBSTRUCTED predecessor by certificate hash rather than treating its terminal state as a successful dependency.","An exact nonuniqueness theorem with the minimal missing global datum is a complete result."]
- `input_commit`: "61988be7d"
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
