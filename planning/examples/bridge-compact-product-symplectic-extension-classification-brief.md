PULLED by agent bridge-1 — stream bridge — lease exclusive (acquired 2026-07-21T06:01:55Z, expires 2026-07-21T14:01:55Z)

WORK PACKAGE sf:program/work/bridge-compact-product-symplectic-extension-classification  (state: ACTIVE, owner: bridge-1)

## Objective
Classify corrected cyclic maps and invariant symplectic extension data on the certified parity-complete pre-residual solution sequence and noncyclic mapping-cofiber triangle.

## Stop condition (what DONE means)
Import EINSTEIN_WEYL_PARITY_COMPLETE_RESIDUAL_EXACT_SEQUENCE_MAXIMAL_V1 and the fixed-identity cyclic obstruction by exact hashes. Work only on the certified pre-residual H0 sequence and ungauged mapping-cofiber triangle; do not assume the absent moment-map-zero quotient functor. First solve the exact local polynomial chain-map equations for corrected nonidentity Einstein field inclusions compatible with both action pairings, generic axial/polar fibres and every exceptional/global endpoint. Independently classify cyclicity up to an admissible chain homotopy and compute the resulting extension cocycle. For every admissible extra lift, prove which Einstein--extra cross pairings, ranks, radicals and extension classes are basis invariant under X -> X+E, and decide whether a local cyclic split exists on the maximal declared carrier. If none exists, exhibit the first exact cohomological or polynomial obstruction; if one exists, give the normalized map/homotopy and prove independence under allowed redefinitions. Supply independent chain/cohomology/current verifiers, lift-shear, identity-map, charge and exceptional mutations, strict schema, receipt, report, Paper 92 update and atlas fragment.

## Current gate
corrected cyclic meaning of the maximal pre-residual Einstein/additional extension

## Forbidden
no after-residual sequence or quotient functor assumed; no chosen lift sign called invariant; no algebraic vector-space split called cyclic/local; no charged quotient hidden in a basis choice; no fixed identity map retried as though the obstruction were absent; no particle, positivity, scattering or unitarity claim

## Activates (downstream this unlocks)
- freeze of the parity-complete Lee--Wald bridge paper
- branch-resolved interaction and quantum consumers

## Dependencies (verify state before starting)
- sf:program/work/bridge-compact-product-parity-complete-residual-exact-sequence#ANY_TERMINAL — OBSTRUCTED (met)

## Additional item fields (schema superset — passed through)
- `allowed_paths`: ["bridge/","residual_atlas/","paper/92-extra-axial-lee-wald-bridge.md","reports/","notes/d-quotient-einstein-team-brief.md","planning/forge-requests/"]
- `resource_hint`: "INVARIANT EXTENSION AUDIT ON THE MAXIMAL CERTIFIED CARRIER. This directly addresses X -> X+E and the corrected-map/up-to-homotopy alternatives while the common residual quotient is still absent."
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
