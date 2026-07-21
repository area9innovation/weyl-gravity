PULLED by agent quantum-qme-1 — stream quantum-qme — lease exclusive (acquired 2026-07-20T18:14:47Z, expires 2026-07-20T22:14:47Z)

WORK PACKAGE sf:program/work/quantum-parity-odd-third-curvature-carrier-manifest  (state: ACTIVE, owner: quantum-qme)

## Objective
Complete the parity-odd derivative-decorated third-curvature carrier manifest that is still missing from the one-loop effective-action architecture.

## Stop condition (what DONE means)
On the same declared four-dimensional scalar-flat Euclidean local algebra as the certified parity-even third-curvature manifest, enumerate the complete real parity-odd scalar carrier basis at third curvature order with arbitrary analytic form factors of the three labelled Laplacians.  Reduce modulo algebraic and differential Bianchi identities, Schouten identities, integration by parts, source-label permutations and the locally exact Pontryagin/transgression directions.  Compute source-generic stabilizers, effective labelled channels, all functional relations and the resulting exact quotient dimension.  Export canonical representatives, exact reduction witnesses, a strict schema and a method-distinct verifier using unseen algebraic-curvature/jet fixtures.  If the declared module cannot be made complete from current inputs, identify the first missing invariant-generation or syzygy operation and file a typed Forge/math request rather than sampling.

## Current gate
complete parity-odd derivative-decorated third-curvature quotient

## Forbidden
no parity-even basis reused by inserting epsilon without a completeness proof; no four-dimensional numerical tensor sampling called a canonical quotient; no coefficient, anomaly, QME, Lorentzian, state, particle or unitarity promotion; no conflation of the local Pontryagin anomaly class with every nonlocal parity-odd form factor

## Activates (downstream this unlocks)
- a coefficient-bearing parity-odd CPT receiver
- a complete even/odd third-curvature effective-action carrier table
- or an exact invariant-generation shortfall for Forge/Conflux

## Additional item fields (schema superset — passed through)
- `allowed_paths`: ["quantum-weyl/","reports/","paper/12-pure-weyl-one-loop-bv-anomaly.tex","paper/12-pure-weyl-one-loop-bv-anomaly-claim-map.json","notes/d-quotient-quantum-team-brief.md","notes/universe-building-roadmap.md","planning/forge-requests/"]
- `resource_hint`: "QUANTUM PROOF-FIRST INDEPENDENT RUNWAY.  Use exact invariant generation, canonical quotient reduction and holdout identities; this does not depend on selecting a compensator action."
- `notes`: ["The parity-even five-carrier manifest and its functional relation are already certified; this item fills the explicitly open odd half rather than repeating the even calculation.","The output is a carrier classification.  Coefficients require the physical Hessian and regulated trace substitution in a later item."]
- `input_commit`: "f4dcd59b9"
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
