PULLED by agent observer-1 — stream observer — lease exclusive (acquired 2026-07-20T23:39:10+02:00, expires 2026-07-21T11:39:10+02:00)

WORK PACKAGE sf:program/work/observer-berger-apparatus-160-executable-unary-export  (state: ACTIVE, owner: observer)

## Objective
Repair the certified 160-row replacement-apparatus unary payload by exporting the complete executable q1, pairing and detector matrices required for physical reduction, without changing the already certified action-level pushout.

## Stop condition (what DONE means)
Import BERGER_APPARATUS_COMBINED_Q1_AFTER_REPLACEMENT_112 and BERGER_APPARATUS_PHYSICAL_REDUCTION_NONDEFINITION_AFTER_REPLACEMENT_112 by hash.  Preserve the certified 160-row semantic pushout and derive a canonical row dictionary, coefficient ring, bidegrees, real involution and K_Berger weights.  Emit every sparse q1 entry, the complete odd pairing, embeddings, quotient, detector-smearing matrix and explicit chain groups for each compact-support, time-slice and zero-mode sector used by the receiver.  Recompute hashes from normalized sparse matrices rather than exporting only ranks or verdict booleans.  Verify q1^2=0, cyclicity, real/K commutation, pairing nondegeneracy, embeddings, quotient and detector chain identities directly from the serialized entries.  A method-distinct verifier must reconstruct the pushout from the replacement 112-row and 56-row parent inputs and obtain byte-equivalent normalized matrices.  If any base input lacks coefficients, certify that smallest producer shortfall instead of importing the forbidden old 108-row operator.

## Current gate
content-addressed executable 160-row unary and pairing export

## Forbidden
no old 108-row q1 substituted for changed positive-mixed Phi2 rows; no rank, hash or zero-defect summary used in place of entries; no cohomology guessed from dimensions; no q2, q3, Z2, redshift, recoil or quantum promotion; no same producer routine reused as the independent reconstruction rail

## Activates (downstream this unlocks)
- exact 160-row cohomology, descended pairing and detector-rank recomputation

## Dependencies (verify state before starting)
- sf:program/work/observer-berger-apparatus-combined-q1-after-replacement-112 — DONE (met)

## Additional item fields (schema superset — passed through)
- `allowed_paths`: ["closed_universe_observers/","reports/","residual_atlas/","paper/09-relational-clocks-berger-d-cartan.tex","notes/closed-universe-observer-team-brief.md","planning/forge-requests/"]
- `resource_hint`: "OBSERVER INPUT REPAIR.  This is serialization plus independent reconstruction of an already certified unary pushout, not a new action ansatz."
- `notes`: ["The physical-reduction nondefinition names the exact receiver fields; treat it as the acceptance schema for this export."]
- `input_commit`: "648637ba9"
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
