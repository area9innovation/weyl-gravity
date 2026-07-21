WORK PACKAGE sf:program/work/bridge-compact-product-polar-ungauged-bv-residual-descent  (state: ACTIVE, owner: bridge-1)

## Objective
Lift the parity-complete compact-product Einstein/extra polar decomposition and direct current to the ungauged Noether/BV complex and determine its final residual descent.

## Stop condition (what DONE means)
Import the terminal direct polar Lee--Wald completion and the certified polar polynomial Einstein square by hashes. Construct the ungauged metric--Maxwell field, gauge, identity and antifield chain maps realizing the polar Einstein inclusion and additional cofiber before gauge fixing. Prove nilpotency, chain-map and cyclic compatibility, classify exceptional ell=0,1 and global/large-gauge endpoints separately, and descend the direct current through every residual gauge and charge quotient on the declared compact phase space. Export the exact residual cohomology dimensions and descended pairing/radical, or the first exact obstruction with its missing carrier. Include independent chain and pairing verifiers, gauge/charge mutations, schema, receipt, report, Paper 92 and atlas updates.

## Current gate
final residual meaning of the polar additional current

## Forbidden
no gauge-fixed primary module called an ungauged BV map; no exceptional harmonics inferred from generic ell; no charged global direction deleted as gauge; no current before descent called a particle norm; no causal boundary, scattering or unitarity claim

## Activates (downstream this unlocks)
- a parity-complete residual Einstein/extra exact sequence
- a stronger external Lee--Wald bridge paper
- physical-boundary and quantum follow-ups

## Dependencies (verify state before starting)
- sf:program/work/bridge-compact-product-polar-direct-lee-wald-completion#ANY_TERMINAL — DONE (met)

## Additional item fields (schema superset — passed through)
- `allowed_paths`: ["bridge/","residual_atlas/","paper/92-extra-axial-lee-wald-bridge.md","paper/","reports/","notes/d-quotient-einstein-team-brief.md"]
- `resource_hint`: "UNGauged BV LIFT. Keep the direct current immutable and make the residual quotient explicit; stop at the first unavailable global carrier rather than deleting it."
- `stream`: "bridge"

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
