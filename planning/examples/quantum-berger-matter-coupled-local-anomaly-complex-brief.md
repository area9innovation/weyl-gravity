WORK PACKAGE sf:program/work/quantum-berger-matter-coupled-local-anomaly-complex  (state: ACTIVE, owner: quantum-qme)

## Objective
Construct the actual local BV anomaly complex for the declared gravity-clock(-Maxwell) Berger action, or prove that no admissible BV action morphism relates it to the pure-Weyl local anomaly complex. This replaces the now-obstructed identity-jet restriction by the matter-coupled theory the Berger sector really uses.

## Stop condition (what DONE means)
Import STRICT_ANOMALY_SECTOR_RESTRICTION_CHAIN_MAP_OBSTRUCTION_V1, including the exact antifield-row defect 961/1920, and the complete action-derived Berger gravity-clock(-Maxwell) BV rows by content hash. Classify the local ghost-number-one, form-degree-four anomaly candidates in the declared derivative/dimension/antifield bounds; compute the full BRST differential including matter equations and antifields; and either construct a chain morphism from a parent local complex whose defect cancels exactly or exhibit a basis-independent obstruction/nonexistence witness in a complete declared morphism class. Reduce cocycles modulo local counterterms and total derivatives, separating raw D, K_Berger=D-omega R, local Weyl and diffeomorphism dispositions. Produce exact certificates, independent verifiers, a candidate/completeness ledger and a receiver payload for the sector-restriction and Cartan tasks. A result may be ZERO, EXACT, NONTRIVIAL or NONDEFINED, but every verdict requires its corresponding primitive, separator or missing-carrier witness.

## Current gate
full matter-coupled Berger local-BV anomaly cohomology or exact action-morphism obstruction

## Forbidden
no reuse of the pure-Weyl metric-antifield row as the matter-coupled target; no AFN0 classification promoted to full BV cohomology; no subtraction of 961/1920 by hand; no background evaluation substituted for cochain restriction; no raw D used where only K_Berger is a symmetry; no local Euclidean result promoted to Lorentzian QME, Hadamard, positivity, particles or unitarity; no compensator theory conflated with the strict field-content theory

## Activates (downstream this unlocks)
- quantum-strict-anomaly-restriction-zero-charge-sectors
- quantum-restricted-d-cartan-anomaly-disposition
- a Berger sector-specific compensator-necessity verdict

## Dependencies (verify state before starting)
- sf:program/work/bridge-local-anomaly-zero-charge-sector-chain-maps#ANY_TERMINAL — OBSTRUCTED (met)

## Additional item fields (schema superset — passed through)
- `allowed_paths`: ["quantum-weyl/","bridge/anomaly_restriction/","d_quotient_classical/","closed_universe_observers/","reports/","residual_atlas/","paper/12-quantum-weyl-one-loop-qme.tex","paper/12-quantum-weyl-one-loop-qme-claim-map.json","notes/d-quotient-quantum-team-brief.md","notes/universe-building-roadmap.md","planning/forge-requests/"]
- `resource_hint`: "QUANTUM LOCAL-ALGEBRAIC. Reuse the landed anomaly, chain-map, variational and exact quotient layers where valid; do not start determinants or Lorentzian state work from this item."
- `notes`: ["The predecessor's 961/1920 result is an obstruction to the naive identity-jet map, not a verdict on the actual matter-coupled anomaly cohomology.","If the required Berger action rows are incomplete, emit one precise cross-stream request rather than reconstructing a competing classical action."]
- `input_commit`: "a9be01eab"
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
