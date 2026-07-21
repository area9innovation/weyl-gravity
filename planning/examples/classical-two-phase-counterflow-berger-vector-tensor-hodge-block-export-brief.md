PULLED by agent classical-1 — stream classical — lease exclusive (acquired 2026-07-21T06:04:26Z, expires 2026-07-21T10:04:26Z)

WORK PACKAGE sf:program/work/classical-two-phase-counterflow-berger-vector-tensor-hodge-block-export  (state: ACTIVE, owner: classical-1)

## Objective
Extend the exact counterflow Berger harmonic carrier from scalar rows to the complete vector and tensor physical blocks, with longitudinal/coexact and anisotropic representation mixing explicit.

## Stop condition (what DONE means)
Import the terminal scalar-block export and the same frozen 70-row parent. Construct convention-explicit vector and symmetric-tensor Peter--Weyl bases on the biaxial Berger sphere, including longitudinal/coexact decomposition, trace/traceless splitting, parity/reality, anisotropic k-mixing and all low-representation exceptions. Export exact iota/pi maps into the 70 rows and prove pi iota=1, q70 closure, local gauge compatibility, cyclicity and conjugation. For every generic vector/tensor label family and exceptional block compute the physical cohomology quotient, descended Gram/inertia/radical, time characteristics and Jordan chains, spatial principal/gradient matrices and causal cones. Verify independently through exact differential-harmonic identities and direct row substitution; mutations must reject round-sphere degeneracies, omitted anisotropic mixing and wrong longitudinal projectors. If the generic vector/tensor harmonic calculus is unavailable, land the smallest exact missing operator/table request and a finite-band nonpromotion witness rather than guessing it. Supply schema, receipt, report and atlas fragment.

## Current gate
complete non-scalar physical carrier on the selected Berger background

## Forbidden
no scalar-only result called complete; no round-space transverse harmonics transplanted to Berger; no numerical eigensystem without exact or certified-algebraic typing; no finite band called generic; no charged global symmetry deleted as local gauge; no positivity or stability claim before exceptional/global assembly

## Activates (downstream this unlocks)
- sf:program/work/classical-two-phase-counterflow-berger-exceptional-stabilizer-block-export

## Dependencies (verify state before starting)
- sf:program/work/classical-two-phase-counterflow-berger-scalar-hodge-block-export#ANY_TERMINAL — DONE (met)

## Additional item fields (schema superset — passed through)
- `allowed_paths`: ["d_quotient_classical/compensator/","d_quotient_classical/atlas/","residual_atlas/","reports/","notes/d-quotient-classical-team-brief.md","planning/forge-requests/"]
- `resource_hint`: "SECOND HODGE SPLIT. Use or request the homogeneous-space vector/tensor Hodge layer, but keep the action-specific 70-row maps and exact physical quotient in this repository. Split vector and tensor again if the declared exact carrier cannot close in one lease."
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
