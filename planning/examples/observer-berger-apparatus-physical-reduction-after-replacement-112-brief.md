PULLED by agent observer-1 — stream observer — lease exclusive (acquired 2026-07-20T23:05:17+02:00, expires 2026-07-21T11:05:17+02:00)

WORK PACKAGE sf:program/work/observer-berger-apparatus-physical-reduction-after-replacement-112  (state: ACTIVE, owner: observer)

## Objective
Compute physical apparatus cohomology, pairing and detector rank on the replacement-theory combined unary carrier.

## Stop condition (what DONE means)
Import the terminal replacement-theory apparatus crosswalk.  If no valid combined complex is exported, independently replay the obstruction and preserve physical reduction as undefined.  Otherwise compute exact graded q1 cohomology; descend the odd pairing, real structure and K_Berger action; classify radicals, signatures and zero modes; and identify canonical reduced rods, polarization, emitter, detector-record and persistent-memory classes.  Prove whether the leading two-record detector map descends and report its exact rank and kernel.  Export projection, inclusion and contraction data with method-distinct verification.

## Current gate
physical reduction of the replacement-theory combined apparatus complex

## Forbidden
no old 108-row cohomology imported as replacement cohomology; no raw row called an observable; no obstructed dependency treated as success; no Z2, redshift, positivity or quantum promotion before reduction

## Activates (downstream this unlocks)
- observer-berger-apparatus-z2-after-repaired-reduction
- or a theorem-frozen physical-reduction nondefinition

## Dependencies (verify state before starting)
- sf:program/work/observer-berger-apparatus-combined-q1-after-replacement-112#ANY_TERMINAL — not in program (UNRESOLVED)

## Additional item fields (schema superset — passed through)
- `allowed_paths`: ["closed_universe_observers/","reports/","residual_atlas/","paper/09-relational-clocks-berger-d-cartan.tex","notes/closed-universe-observer-team-brief.md","notes/universe-building-roadmap.md","planning/forge-requests/"]
- `resource_hint`: "OBSERVER REPLACEMENT PHYSICAL REDUCTION.  Begin only from a valid action-derived replacement unary union."
- `notes`: ["This is the replacement-theory successor to the now-stranded old 160-row reduction lane."]
- `input_commit`: "135b6d660"
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
