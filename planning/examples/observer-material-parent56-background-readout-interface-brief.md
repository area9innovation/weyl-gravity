PULLED by agent observer-1 — stream observer — lease exclusive (acquired 2026-07-21T01:14:05+02:00, expires 2026-07-21T13:14:05+02:00)

WORK PACKAGE sf:program/work/observer-material-parent56-background-readout-interface  (state: ACTIVE, owner: observer)

## Objective
Construct the missing row-indexed background-readout interface for each detector profile F_a so the four nonzero mixed lambda-F Hessian entries in the material-parent-56 action become executable rather than symbolic placeholders.

## Stop condition (what DONE means)
Import BERGER_DYNAMICAL_APPARATUS_PARENT and BERGER_MATERIAL_PARENT56_EXECUTABLE_UNARY_EXPORT_SHORTFALL by content hash.  Define F_a as an explicit linear functional or field/profile map on the certified Berger base carrier, with canonical source and target rows, degrees, real/K weights, detector localization, support category and zero-mode restriction.  Serialize the profile coefficients and its adjoint with respect to the declared odd/current pairing.  Differentiate -lambda_a bar(P)_a dot F_a to obtain the four ordered mixed unary entries of coefficient -1 with complete row labels and signs; prove the map is a chain map on every declared support/zero-mode sector.  Reproduce the existing coarea detector-density control and reject profile, sign, support and zero-mode mutations.  A method-distinct verifier must derive the same mixed block directly from the local action and detector profile rather than reading the producer matrix.  If F_a depends on an unexported base field or smearing distribution, emit that smallest typed dependency instead of inventing a row.

## Current gate
executable detector background-readout profile and mixed Hessian interface

## Forbidden
no abstract symbol F_a used as a matrix entry; no detector coordinate named without a base-row embedding; no delta support multiplied without a declared distribution domain; no rank-four assertion substituted for entries; no physical reduction, q2, memory, redshift or recoil promotion

## Activates (downstream this unlocks)
- complete executable material-parent-56 q1 and detector chain map

## Dependencies (verify state before starting)
- sf:program/work/observer-material-parent56-executable-unary-export#ANY_TERMINAL — OBSTRUCTED (met)

## Additional item fields (schema superset — passed through)
- `allowed_paths`: ["closed_universe_observers/","reports/","residual_atlas/","paper/09-relational-clocks-berger-d-cartan.tex","notes/closed-universe-observer-team-brief.md","planning/forge-requests/"]
- `resource_hint`: "OBSERVER INTERFACE PRODUCER.  Keep local distribution/support claims typed and fail closed; use the certified coarea fixture as an independent scalar control only."
- `notes`: ["This task supplies four missing mixed entries; it does not recompute the already certified 52 internal entries or pairing."]
- `input_commit`: "5357d0644"
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
