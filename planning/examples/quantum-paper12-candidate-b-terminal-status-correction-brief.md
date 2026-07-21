PULLED by agent quantum-qme-1 — stream quantum-qme — lease exclusive (acquired 2026-07-20T17:24:13Z, expires 2026-07-20T21:24:13Z)

WORK PACKAGE sf:program/work/quantum-paper12-candidate-b-terminal-status-correction  (state: ACTIVE, owner: quantum)

## Objective
Remove the stale Candidate-B-under-test statement that raced the Paper 12 regulator refresh and replace it with the exact two-candidate terminal status.

## Stop condition (what DONE means)
Import COMPENSATOR_CANDIDATE_A_R2_AUXILIARY_SCALAR_OBSTRUCTION_V1 from result commit 5c642e2ad14d45f6074b1327c69707b7b9b08f5d and close 218cd5ad9, and COMPENSATOR_CANDIDATE_B_UNIMODULAR_THREEFORM_OBSTRUCTION_V1 from result commit cc0e0036c6acce2bc3d8ba81057031d90a71333a and close c7af7b707831a848e3e110f45bb746478473dbc6. Replace every Paper 12 or referee-response statement that Candidate B is under test with: both declared minimal classical repairs are scoped obstructions, no action is selected, and neither Hessian is imported into the conditional quantum theorem. State immediately that this does not prove a universal compensator no-go. Update the generated claim map only if it carries the stale lifecycle, regenerate the PDF and publication hashes, run the existing independent claim-map verification and two warning-free TeX passes, and answer request classical-compensator-candidate-ab-neither-comparison-to-quantum-qme-b6ba3205f57b7991 with the corrected artifact IDs. Search the complete Paper 12 publication bundle for stale Candidate-B-under-test wording before closing.

## Current gate
factual lifecycle correction after Candidate B closed before the Paper 12 refresh

## Forbidden
no change to the regulator theorem beyond the raced lifecycle correction; no universal compensator no-go; no selected action; no Candidate A/B Hessian imported into the quantum claim; no QAP, Lorentzian, Hadamard, particle, scattering or unitarity promotion

## Activates (downstream this unlocks)
- a publication-current Paper 12
- verified delivery of the Candidate A/B terminal-status request

## Additional item fields (schema superset — passed through)
- `allowed_paths`: ["paper/12-pure-weyl-one-loop-bv-anomaly.tex","paper/12-pure-weyl-one-loop-bv-anomaly.pdf","paper/12-pure-weyl-one-loop-bv-anomaly-claim-map.json","paper/12-pure-weyl-one-loop-bv-anomaly-referee-response.md","paper/12-pure-weyl-one-loop-bv-anomaly-science-forge-paper-coverage.json","paper/12-pure-weyl-one-loop-bv-anomaly-paper-coverage-report.json","paper/generate_12_pure_weyl_one_loop_bv_anomaly_claim_map.py","paper/verify_12_pure_weyl_one_loop_bv_anomaly_claim_map.py","reports/","planning/forge-requests/"]
- `resource_hint`: "IMMEDIATE QUANTUM PUBLICATION CORRECTION. This is intentionally small but fail-closed because the completed manuscript presently contradicts a terminal classical result."
- `notes`: ["The stale wording is currently present in the main TeX and referee response.","The conditional all-loop cohomology theorem remains unchanged.","The two classical failures motivate the general action classification; they do not select a quantum receiver."]
- `input_commit`: "bb2c1011f"
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
