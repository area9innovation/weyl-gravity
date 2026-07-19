WORK PACKAGE sf:program/work/berger-pbw-component-jet-contract  (state: DONE, owner: observer)

## Objective
Positive Berger clock apparatus: activate the first prerequisite identified by BERGER_108_ROW_PBW_INPUT_OBSTRUCTION by freezing a canonical 108-row component/cotangent carrier and an executable differential coefficient-jet normal form importing the exact detector profiles and emitter switches.

## Stop condition (what DONE means)
all 108 rows and 108 nonzero pairing entries are ordered, unique and nondegenerate; coefficient normalization, multiplication and all four Berger derivations are deterministic and independently replayed; mutations reject row, pairing, profile-width, switch-radius and noncanonical-factor drift, OR the first exact obstruction is certified

## Forbidden
claiming that this interface is a scalar q1 or q2 payload; truncating the jet tower; treating profile jets as constants; choosing physical masses or couplings; promoting q1-q2 replay, backreaction, tangent-cone, Bridge 3, finite-parameter or quantum claims

## Dependencies (verify state before starting)
- BERGER_108_ROW_PBW_INPUT_OBSTRUCTION — free-text (verify manually)
- BERGER_QUANTITATIVE_DETECTOR_ROD_CHART — free-text (verify manually)
- BERGER_EXACT_NORMALIZED_EMITTER_SWITCH_PROFILES — free-text (verify manually)
- BERGER_PORTABLE_COUPLED_64_UNARY_PAIRING_36_SDR — free-text (verify manually)

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
