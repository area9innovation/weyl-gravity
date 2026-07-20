# Observer Berger replacement 112-row unary theory close-out

The forced four rows do complete the centered rod-background orbit, but the
resulting generator is not a symmetry of the certified diagonal positive
eight-scalar action.  In the exact eight-background basis its symmetric part
has rank four, with diagonal entries
\(\pm2\cot(\sqrt{58}/24)\).

The canonical cotangent lift acts by \(-A^T\).  Therefore the isolated
eight-rod scalar-wave Hessian already has normalized principal commutator
\[
 [K_{\rm Berger},q_1]_{\rm principal}=-(A^T+A),
\]
again of rank four.  No unconstructed lower-order or cross-sector row can
cancel this principal defect.

Deleting either new rod/cotangent pair leaves background rank seven.
Replacing \(A\) by its skew part preserves the diagonal action but loses
background closure with rank-four defect.  No positive diagonal kinetic
rescaling can help because \(A\) has nonzero diagonal entries.

The smallest unexcluded repair keeps the 112 rows but replaces the identity
rod kinetic matrix by the exact positive mixing
\(H=B^{-T}B^{-1}\).  It satisfies \(A^TH+HA=0\), but is a changed action:
its stress, \(\Phi_2\), complete unary and quotient all require recomputation.

CLOSE-OUT: OBSTRUCTED — the certified diagonal eight-rod action fails the required K_Berger-equivariant unary gate at exact principal rank four

EVIDENCE: `closed_universe_observers/certificates/BERGER_REPLACEMENT_112_UNARY_THEORY_K_EQUIVARIANCE_OBSTRUCTION.json`

## Verification receipt

- Tier 0: changed Python and structured-data inputs parsed successfully;
  scoped `git diff --check` — PASS.
- Tier 1 producer:
  `python3 -m closed_universe_observers.generate_berger_replacement_112_unary_theory_obstruction --write`
  — PASS (10.43 s exact audit before output).
- Tier 1 independent rail:
  `python3 -m closed_universe_observers.verify_berger_replacement_112_unary_theory_obstruction`
  — PASS (20.18 s).
- Tier 1 tests:
  `python3 -m pytest -q closed_universe_observers/tests/test_berger_replacement_112_unary_theory_obstruction.py`
  — PASS, 5 tests (0.40 s).
- Tier 2 atlas generation:
  `python3 -m closed_universe_observers.atlas.generate_observer_atlas_fragment`
  — PASS (0.64 s).
- Tier 2 independent atlas verifier:
  `python3 -m closed_universe_observers.atlas.verify_observer_atlas_fragment`
  — PASS (1.37 s).
- Tier 2 direct consumers:
  `python3 -m pytest -q closed_universe_observers/tests/test_observer_atlas_fragment.py closed_universe_observers/tests/test_berger_replacement_112_unary_theory_obstruction.py`
  — PASS, 60 tests (24.51 s).
- Paper 09:
  `pdflatex -interaction=nonstopmode -halt-on-error 09-relational-clocks-berger-d-cartan.tex`
  run twice from `paper/` — PASS (0.62 s, 0.56 s; 17 pages).  `latexmk`
  was unavailable in the environment, so it was not counted as a pass.
- Tier 3 is not run: this is a scoped obstruction, not a freeze, theorem
  promotion, shared-core change or release.
