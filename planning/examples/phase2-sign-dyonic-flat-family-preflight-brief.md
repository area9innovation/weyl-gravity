WORK PACKAGE sf:program/work/phase2-sign-dyonic-flat-family-preflight  (state: PROPOSED, owner: phase2-sign-1)

## Objective
Certify the stationary compact dyonic Einstein-Maxwell/Weyl-Maxwell product family and its exact symmetry/parity disposition as the P2-C sign-robustness base.

## Stop condition (what DONE means)
At k1=0 and fixed nonzero magnetic Chern N, independently derive beta=kappa N^2/(4 q_min^2), k2=1/(beta(1+tau^2)), P=2 q_min/(N kappa(1+tau^2)), E=tau P, alpha_B=alpha_crit(1+tau^2), alpha_crit=3N^2/(4 q_min^2) from the incidence equations and flux quantization. Freeze the metric, bundle connection, electric-charge convention, stabilizer lifts and global H=partial_t. State explicitly that this varies coupling and background, not one fixed-alpha_B theory. Because F wedge F is nonzero for tau!=0, prove whether parity remains a block symmetry only after an accompanying duality/charge action; otherwise certify a combined mixed-parity carrier. Export exact certificate, schema, verifier, tests, report and atlas fragment.

## Current gate
Stationary dyonic compact-family and symmetry preflight

## Forbidden
no pure-magnetic off-wall dS2/AdS2 branch used as a comparable positive-frequency family; no inherited axial/polar split assumed; no fixed-coupling family claim; no sign computation yet

## Dependencies (verify state before starting)
- sf:program/work/bridge-phase1-einstein-extra-contribution-freeze — DONE (met)

## Additional item fields (schema superset — passed through)
- `stream`: "bridge"
- `priority`: 0
- `allowed_paths`: ["bridge/phase2/dyonic_flat_family_preflight/","reports/phase2-sign-dyonic-flat-family-preflight-2026-07-22.md","residual_atlas/phase2-sign-dyonic-flat-family-preflight-fragment-v1.json","planning/forge-requests/phase2-dyonic-parity-duality.json"]
- `resource_hint`: "Exact rational one-parameter family. The parity/duality disposition is load-bearing and may itself be the first structural result."
- `input_commit`: "4a212883aefa5525cc847d0c12763c74c1c3411a"

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

## Close-out footer — COPY VERBATIM at the END of your report
The transition is chosen MECHANICALLY from these two literal lines; a missing
`CLOSE-OUT:` or (for a DONE) `EVIDENCE:` line makes `s-f work close` REFUSE. Paste and fill:

```
CLOSE-OUT: DONE — <one-line rationale>
EVIDENCE: <path to a receipt / certificate / gate that backs it>
```

Markers: `DONE` (objective met) | `OBSTRUCTED` (blocked, cannot proceed) | `SHORTFALL`
(substantive work landed, stop-condition not fully met — keeps the item ACTIVE; add a
`MISSING-DEP: <typed need>` line to fold to BLOCKED). A `DONE` close REQUIRES an `EVIDENCE:` line.
Deliver with `s-f work close --item <id> --agent <you> --report <file> --now <T>` (report+close in
one) — NOT report-then-`yield`, which releases the lease and folds the item back to READY without a
terminal transition (the coordinator overview then flags it as a lagging terminal disposition).

## Orientation
Read tools/science-forge/views/agent_context.md, docs/structure-finding-thesis.md, docs/math-roadmap.md, and lib/math/COMPLETENESS.md before starting.
