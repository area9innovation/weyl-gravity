PULLED by agent quantum-qme-1 — stream quantum-qme — lease exclusive (acquired 2026-07-20T15:25:26Z, expires 2026-07-21T03:25:26Z)

WORK PACKAGE sf:program/work/quantum-all-loop-qap-regulator-construction  (state: ACTIVE, owner: quantum)

## Objective
Construct or exactly obstruct the regulator and subtraction scheme required to turn the conditional tau-adic all-loop local QME induction into an unconditional theorem on its declared formal local algebra.

## Stop condition (what DONE means)
Import TAU_ADIC_ALL_LOOP_LOCAL_QME_STABILITY from commit 7fabe9878 by exact certificate and manuscript hashes. Declare one all-order regularization/subtraction architecture for the fourth-order compensator BV complex, including the minimal and nonminimal measure, antifield insertions, formal tau-adic topology, power-counting domain, coupling chart and treatment of zero modes. Prove the quantum action principle hypotheses used by the certificate: every first Slavnov/QME breaking is local, ghost number one and homogeneous dimension four in the completed algebra; it obeys Wess-Zumino consistency; subtraction and canonical transformations are continuous in the filtration; and the regular Koszul-Tate chart remains nonsingular. Prove closure under the complete H^{0,4} module including R(g_hat)^2 and parity-odd/topological directions. Supply a second independent regulator/QAP rail rather than replaying the cohomology induction. If no declared architecture satisfies all hypotheses, certify the first incompatibility and its precise scope. Emit a strict receiver payload that changes the all-loop lifecycle from conditional only if every hypothesis passes.

## Current gate
analytic quantum-action-principle and regulator realization for the formal tau-adic all-loop theorem

## Forbidden
no H^{1,4}=0 or one-loop determinant restated as a regulator theorem; no dimensional-regularization slogan without measure, domain and subtraction maps; no finite tau truncation; no omission of nonminimal or positive-antifield insertions; no omission of R(g_hat)^2; no strict pure-Weyl anomaly repair; no local Euclidean theorem promoted to convergence, global anomaly freedom, Lorentzian QME, states, particles, scattering or unitarity

## Activates (downstream this unlocks)
- an unconditional formal local all-loop QME theorem on the declared regular chart
- or an exact analytic obstruction to the compensator extension
- a sharper input to the final compensator quantum synthesis

## Additional item fields (schema superset — passed through)
- `allowed_paths`: ["quantum-weyl/local_bv/","quantum-weyl/anomalies/","quantum-weyl/spectral/","quantum-weyl/reports/","quantum-weyl/atlas/","reports/","residual_atlas/","paper/12-pure-weyl-one-loop-bv-anomaly.tex","notes/d-quotient-quantum-team-brief.md","notes/universe-building-roadmap.md","planning/forge-requests/"]
- `resource_hint`: "PRIMARY QUANTUM SUCCESSOR after the conditional all-loop theorem. It is input-pinned because the scientific certificate is committed even if publication integration closes separately. A precise first regulator/QAP incompatibility is a successful terminal result."
- `notes`: ["The source request is planning/forge-requests/tau-adic-all-loop-qap-regulator.json.","A literature theorem may be imported only through a complete hypothesis map to this exact BV complex and completed algebra.","The classical dressed-trace causal obstruction is a separate Lorentzian issue and must not be hidden by a local Euclidean regulator."]
- `input_commit`: "7fabe9878"
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
