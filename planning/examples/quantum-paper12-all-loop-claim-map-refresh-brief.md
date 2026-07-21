PULLED by agent quantum-qme-1 — stream quantum-qme — lease exclusive (acquired 2026-07-20T15:48:19Z, expires 2026-07-20T19:48:19Z)

WORK PACKAGE sf:program/work/quantum-paper12-all-loop-claim-map-refresh  (state: ACTIVE, owner: quantum)

## Objective
Refresh Paper 12's generated claim map and publication artifacts so the landed conditional all-loop QME theorem is covered bidirectionally by current evidence without broadening its lifecycle.

## Stop condition (what DONE means)
Import TAU_ADIC_ALL_LOOP_LOCAL_QME_STABILITY from commit 7fabe9878 and the exact TeX hash recorded in planning/forge-requests/paper12-tau-adic-all-loop-claim-map-refresh.json. Update the Paper 12 claim-map generator, not only its output hash, to record the conditional-QAP theorem, the strict-theory one-loop obstruction, the compensator theory change, and every open regulator/global/Lorentzian/state boundary. Regenerate the claim map, PDF and publication hashes from clean sources; run two warning-free TeX passes and the independent claim-map verifier. Add HUMAN-authored materiality and typed result-to-paper edges for this result under the newly landed Science Forge paper-coverage schema, run the advisory bidirectional coverage audit, and resolve every flag concerning this theorem or record an explicit review item for unrelated unclassified results.

## Current gate
Paper 12 claim-map and bidirectional evidence coverage for the conditional all-loop theorem

## Forbidden
no manual hash-only repair; no unconditional all-loop QME wording; no constructed-regulator, convergence, strict-theory anomaly-freedom, global-anomaly, Lorentzian-product, Hadamard, residual-transfer, particle or unitarity claim; no machine-inferred materiality or result-to-paper edge; no unrelated paper rewrite

## Activates (downstream this unlocks)
- current Paper 12 publication artifacts
- the first live physics use of the bidirectional paper-result coverage gate

## Additional item fields (schema superset — passed through)
- `allowed_paths`: ["paper/12-pure-weyl-one-loop-bv-anomaly.tex","paper/12-pure-weyl-one-loop-bv-anomaly.pdf","paper/12-pure-weyl-one-loop-bv-anomaly-claim-map.json","paper/generate_12_pure_weyl_one_loop_bv_anomaly_claim_map.py","paper/verify_12_pure_weyl_one_loop_bv_anomaly_claim_map.py","paper/","quantum-weyl/anomalies/","quantum-weyl/reports/","reports/","notes/d-quotient-quantum-team-brief.md","planning/forge-requests/"]
- `resource_hint`: "PUBLICATION-INTEGRATION RESERVE. The scientific theorem is already committed; this item owns only generated claim-map/PDF/evidence-coverage closure. Pull after higher-priority scientific reserves unless the coverage gate blocks a release."
- `notes`: ["The newly landed paper-coverage substrate does not infer materiality or edges; this item must author them explicitly.","An empty live coverage graph is not a pass.","Keep the public claim wording subordinate to the certificate's LOCAL-ALGEBRAIC boundary."]
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
