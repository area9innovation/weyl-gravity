PULLED by agent quantum-qme-1 — stream quantum-qme — lease exclusive (acquired 2026-07-20T16:56:29Z, expires 2026-07-20T20:56:29Z)

WORK PACKAGE sf:program/work/quantum-paper12-regulator-measure-obstruction-refresh  (state: ACTIVE, owner: quantum)

## Objective
Integrate the complete post-QAP regulator and measure preflight sequence into Paper 12 so its conditional all-loop theorem is accompanied by the exact reasons no implementing action-independent regulator has yet been constructed.

## Stop condition (what DONE means)
Import by exact hashes TAU_ADIC_DR_MS_QAP_EVANESCENT_CLOSURE_OBSTRUCTION, DRESSED_CANONICAL_BEREZINIAN_LOCALITY_PREFLIGHT, DRESSED_EVANESCENT_GEOMETRIC_BV_MODULE_PREFLIGHT and DRESSED_FOUR_DIMENSIONAL_COVARIANT_REGULATOR_PREFLIGHT. Add one coherent regulator-status section to Paper 12: (1) ordinary DR/MS on the strict four-dimensional stable module is obstructed by Euler evanescence; (2) the dressed canonical BV transformation has exact nonunit finite-carrier Berezinian and no action-independent continuum counterterm; (3) the common d-dimensional even AFN0 premodule is exact but full BV closure requires selected-action Koszul-Tate rows and a parity-odd scheme; and (4) a bounded strictly four-dimensional covariant receiver theorem exists under explicit selected-Hessian symbol/domain hypotheses but is not instantiated. Preserve the conditional all-loop cohomological induction and state that Candidate A has now failed classically while Candidate B is under test, without importing an unselected action into the quantum theorem. Update the TeX, generated claim map, referee response, PDF and publication hashes; run two warning-free TeX passes and independent claim-map/table verification. Add human materiality plus typed result-to-paper edges for all four results and rerun the full-corpus advisory coverage audit, explicitly recording its current annotation scope. Reject mutations that call the finite Berezinian one, identify DR/MS with the four-dimensional route, omit the action-specific Koszul-Tate requirement, or promote the conditional receiver to QAP. Leave selected-action determinant, mixing, global, Lorentzian and state gates open.

## Current gate
Paper 12 regulator/QAP status after the complete common action-independent preflight sequence

## Forbidden
no unconditional all-loop QME; no strict/compensator equivalence; no action-independent continuum Jacobian; no unselected Candidate B Hessian; no DR/MS and four-dimensional scheme equivalence; no determinant, anomaly-coefficient, global-anomaly, Hadamard, positivity, particle, scattering or unitarity promotion

## Activates (downstream this unlocks)
- publication-current Paper 12
- selected-action regulator instantiation after the A/B gate
- full-project bidirectional coverage baseline

## Additional item fields (schema superset — passed through)
- `allowed_paths`: ["paper/12-pure-weyl-one-loop-bv-anomaly.tex","paper/12-pure-weyl-one-loop-bv-anomaly.pdf","paper/12-pure-weyl-one-loop-bv-anomaly-claim-map.json","paper/12-pure-weyl-one-loop-bv-anomaly-referee-response.md","paper/12-pure-weyl-one-loop-bv-anomaly-science-forge-paper-coverage.json","paper/12-pure-weyl-one-loop-bv-anomaly-paper-coverage-report.json","paper/generate_12_pure_weyl_one_loop_bv_anomaly_claim_map.py","paper/verify_12_pure_weyl_one_loop_bv_anomaly_claim_map.py","paper/generate_12_quantum_anomaly_tables.py","paper/verify_12_quantum_anomaly_tables.py","quantum-weyl/reports/","reports/","notes/d-quotient-quantum-team-brief.md","notes/universe-building-roadmap.md","planning/forge-requests/"]
- `resource_hint`: "IMMEDIATE QUANTUM PUBLICATION RESERVE. The common action-independent science is terminal and the selected-action quantum work is gated on Candidate B, so this is the correct current pull."
- `input_commit`: "5bf7a254183e407d439ea85ed99a979ed61917b4"
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
