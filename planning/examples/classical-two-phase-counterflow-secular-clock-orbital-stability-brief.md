PULLED by agent classical-1 — stream classical — lease exclusive (acquired 2026-07-21T04:59:29Z, expires 2026-07-21T12:59:29Z)

WORK PACKAGE sf:program/work/classical-two-phase-counterflow-secular-clock-orbital-stability  (state: ACTIVE, owner: classical-1)

## Objective
Decide whether the exact size-two zero Jordan block of the unrestricted counterflow clock is a genuine physical instability or the linear tangent to an exact stable action-angle family with shifted relative charge and clock rate.

## Stop condition (what DONE means)
Import TWO_PHASE_COUNTERFLOW_CHARGE_CLOCK_COMPLEMENTARITY_V1 and its causal-parent/background dependencies by exact hashes. Derive the exact reduced homogeneous Hamiltonian and symplectic flow in the relative phase/charge sector, including the nearby family of stationary or helical counterflow solutions and the charge dependence of the clock rate. Prove or disprove that delta psi(t)=psi_1+t q_1/I is precisely the parameter derivative of that exact family. State and separately decide bounded linear stability in a lifted phase coordinate, stability of the compact S1-valued clock, fixed-charge orbital stability, and modulated stability under a shifted frequency; do not quotient the charged R_rel or D actions as gauge. Compute the constrained energy Hessian and any canonical normal form needed to distinguish a healthy integrable clock from a negative-energy, exponentially growing or genuinely secular physical instability. Export the exact first verdict, independent symbolic verifier, charge/frequency and sign mutations, schema, receipt, report and atlas fragment. If the Jordan direction is an integrable family tangent, identify the precise all-Hodge health gate that remains; if it is a genuine instability, give the invariant separator and stop without extending the action family.

## Current gate
physical meaning of the charged clock's zero-frequency Jordan partner

## Forbidden
no zero Jordan block called a ghost or fatal instability without an invariant stability definition; no compact phase treated as an unbounded real observable without declaring the lift; no frequency/charge modulation silently quotiented as gauge; no fixed-Q_rel clock resurrected; no all-Hodge, observer, particle or unitarity promotion from a homogeneous normal form

## Activates (downstream this unlocks)
- the unrestricted all-Hodge physical health audit
- a defensible charged-time observer interpretation
- the final classical disposition of the two-phase counterflow successor

## Dependencies (verify state before starting)
- sf:program/work/classical-two-phase-counterflow-charge-clock-complementarity-and-unrestricted-health#ANY_TERMINAL — DONE (met)

## Additional item fields (schema superset — passed through)
- `allowed_paths`: ["d_quotient_classical/compensator/","d_quotient_classical/atlas/","residual_atlas/","reports/","notes/d-quotient-classical-team-brief.md","notes/universe-building-roadmap.md","paper/"]
- `resource_hint`: "PROOF-FIRST FINITE-DIMENSIONAL NORMAL FORM. Resolve the action-angle versus instability ambiguity exactly before spending resources on the all-Hodge carrier or another action family."
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
