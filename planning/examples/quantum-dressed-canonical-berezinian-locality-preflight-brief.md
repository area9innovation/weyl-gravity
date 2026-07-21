PULLED by agent quantum-qme-1 — stream quantum-qme — lease exclusive (acquired 2026-07-20T16:04:00Z, expires 2026-07-20T20:04:00Z)

WORK PACKAGE sf:program/work/quantum-dressed-canonical-berezinian-locality-preflight  (state: ACTIVE, owner: quantum)

## Objective
Determine, before choosing Candidate A or B, whether the common dressed canonical transformation and Weyl-quartet reduction have a local and action-independent Berezinian/Jacobian disposition suitable for a later selected-action regulator.

## Stop condition (what DONE means)
Import COMPLEX_COMPENSATOR_ACTION_QUARTET_PREFLIGHT_V1 and the complete tau-adic local BV atom/pairing ledger by exact hashes. On the formal rho!=0 chart, derive the regulated super-Jacobian of the canonical change (g,tau,ghosts,antifields) to (g_hat,Diff fields) direct-sum (tau,omega,omega_star,tau_hat_star), including minimal and nonminimal sectors, the cotangent lift, real contour and every zero-mode convention that is definable without selecting Candidate A or B. Prove one of: the finite-dimensional/cutoff Berezinian is exactly one and the continuum defect is a local functional in a declared regulator class; a unique local counterterm module absorbs it; or a precise measure/regularization obstruction prevents action-independent locality. Check composition, inverse and canonical-one-form identities and reject a missing-antifield or sign mutation. Export a strict receiver stating which parts are genuinely action-independent and which must be recomputed from the selected Hessian. Stop before determinants, QAP, anomaly coefficients or all-loop promotion.

## Current gate
action-independent locality of the dressed canonical BV measure transformation

## Forbidden
no formal canonical transformation assumed measure preserving without a regulated Berezinian; no finite-dimensional determinant called a continuum theorem; no scalaron or three-form determinant computed before action selection; no regulator/QAP or H14 theorem inferred from locality of the change of variables; no global-anomaly, Lorentzian-QME, state, particle, scattering or unitarity claim

## Activates (downstream this unlocks)
- quantum-selected-compensator-repair-dressed-regulator
- a pinned Jacobian/local-counterterm input common to Candidates A and B
- or an exact obstruction to the proposed dressed-variable regulator architecture

## Additional item fields (schema superset — passed through)
- `allowed_paths`: ["quantum-weyl/local_bv/","quantum-weyl/anomalies/","quantum-weyl/spectral/","quantum-weyl/reports/","quantum-weyl/atlas/","reports/","residual_atlas/","paper/12-pure-weyl-one-loop-bv-anomaly.tex","notes/d-quotient-quantum-team-brief.md","notes/universe-building-roadmap.md","planning/forge-requests/"]
- `resource_hint`: "READY QUANTUM RESERVE after the Paper 12 coverage refresh. This is the largest rigorous quantum calculation that is common to both A and B and therefore does not prejudge the classical selector."
- `notes`: ["The rho!=0 domain and possible winding between polar charts must be explicit.","Any continuum-locality statement must name its regularization assumptions.","A result here narrows but does not replace the selected-action regulator/QAP gate."]
- `input_commit`: "306ff78a2"
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
