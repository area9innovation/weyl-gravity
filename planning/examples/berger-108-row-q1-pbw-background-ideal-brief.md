WORK PACKAGE sf:program/work/berger-108-row-q1-pbw-background-ideal  (state: OBSTRUCTED, owner: observer)

## Objective
Positive Berger clock apparatus: compose the pinned scalar 64-row unary with all apparatus/emitter scalar blocks in the repaired noncommuting coefficient-jet algebra, or certify the first remaining exact obstruction to a nilpotent 108-row q1 PBW matrix.

## Stop condition (what DONE means)
a canonical sparse 108x108 scalar PBW q1 is exported and independently passes nilpotency/cyclicity with background identities and mutations, OR an exact free-jet witness proves that the current dependencies do not determine the quotient in which a required q1-squared path vanishes, while preserving the certified on-shell covariant identity and naming the minimal background-specialization ideal

## Forbidden
declaring background equations zero inside the free jet algebra without a content-addressed specialization/crosswalk; importing finite Peter-Weyl modes as support-local PBW rows; inferring scalar coefficients from row ranges; changing physical masses/couplings; promoting q2, backreaction, tangent-cone, Bridge 3, finite-parameter or quantum claims

## Dependencies (verify state before starting)
- BERGER_108_ROW_COMPONENT_JET_CONTRACT — free-text (verify manually)
- BERGER_PORTABLE_COUPLED_64_UNARY_PAIRING_36_SDR — free-text (verify manually)
- BERGER_84_ROW_NORMALIZED_PROFILE_MIXED_UNARY — free-text (verify manually)
- BERGER_108_ROW_POLARIZATION_EMITTER_UNARY_FIRST_RECOIL — free-text (verify manually)
- BERGER_GLOBAL_DETECTOR_INDEXED_RODS — free-text (verify manually)

## Standing constraints
# Standing constraints for programme agents (included in every work package)

- This tree is the READ-authority. Follow the repo AGENTS.md exactly:
  shared-master discipline (explicit pathspec, never `git add .`, never
  force-push, preserve other teams' dirty files), the quantum claim boundary
  (LOCAL-ALGEBRAIC / EUCLIDEAN-SPECTRAL / REDUCED-MODE / LORENTZIAN-CAUSAL tags;
  never promote one implicitly), exact rational/algebraic arithmetic in every
  canonical form/rank/cocycle test, and the receipts requirement.
- Do NOT commit on an agent's behalf — the coordinator integrates by pathspec.
  Do NOT edit generated views, IR graphs, gate/receipt files, or another team's
  certificates, snapshots, or history.
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
- Report at the end: deliverables, gate results, deviations from the work item,
  and anything `stop_condition` required that you could not meet (honest
  shortfall, never silent narrowing).

## Orientation
Read tools/science-forge/views/agent_context.md, docs/structure-finding-thesis.md, docs/math-roadmap.md, and lib/math/COMPLETENESS.md before starting.
