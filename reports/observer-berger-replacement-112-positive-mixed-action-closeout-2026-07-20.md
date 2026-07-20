# Observer Berger replacement 112 positive-mixed action close-out

The exact positive form \(H=B^{-T}B^{-1}\) passes the changed-action unary
gate.  Under \(R=B\psi\) and \(R^+=B^{-T}\psi^+\), the action and odd pairing
become eight canonical positive scalar BV pairs.  The coefficient-space
generator is the standard skew complex structure, so both principal and
lower-order \(K_{\rm Berger}\) commutators vanish.

The changed stress was recomputed.  It is homogeneous and time independent,
with sparse source coefficients \(29/36,1/8,1/8,5/9\).  Its Noether defect
and retained cokernel projection vanish, and the exact sparse
\(\Phi_2\) primitive is \(428/567,-29/21,-29/21,-6/7\).

The complete action-derived 112-row unary passes nilpotency, cyclicity,
reality, pairing and the support-local rod Green-parent gates.  The existing
leading detector preparation and response map is unchanged and remains rank
two at coordinate level.  Full 112-row cohomology and gauge-reduced response,
apparatus \(q_2,q_3\), \(\mathcal Z_2\), memory, redshift, recoil and quantum
claims remain `NO_CERTIFIED_MAP`.

CLOSE-OUT: DONE — the exact positive-mixed changed action supplies the certified replacement 112-row unary base

EVIDENCE: `closed_universe_observers/certificates/BERGER_REPLACEMENT_112_POSITIVE_MIXED_ACTION_UNARY.json`

## Verification receipt

- Tier 0: changed Python and structured-data inputs parse; scoped
  `git diff --check` — PASS.
- Tier 1 producer:
  `python3 -m closed_universe_observers.generate_berger_replacement_112_positive_mixed_action --write`
  — PASS (19.68 s before the cache-only optimization).
- Tier 1 independent rail:
  `python3 -m closed_universe_observers.verify_berger_replacement_112_positive_mixed_action`
  — PASS (8.57 s).
- Tier 1 tests:
  `python3 -m pytest -q closed_universe_observers/tests/test_berger_replacement_112_positive_mixed_action.py`
  — PASS, 5 tests (18.36 s after producer-result caching).
- Tier 2 atlas generation:
  `python3 -m closed_universe_observers.atlas.generate_observer_atlas_fragment`
  — PASS (0.71 s).
- Tier 2 independent atlas verifier:
  `python3 -m closed_universe_observers.atlas.verify_observer_atlas_fragment`
  — PASS (1.52 s).
- Tier 2 direct consumers:
  `python3 -m pytest -q closed_universe_observers/tests/test_observer_atlas_fragment.py closed_universe_observers/tests/test_berger_replacement_112_positive_mixed_action.py`
  — PASS, 60 tests (47.18 s).
- Paper 09:
  `pdflatex -interaction=nonstopmode -halt-on-error -output-directory=<temporary> 09-relational-clocks-berger-d-cartan.tex`
  run twice from `paper/` — PASS (0.85 s, 0.72 s; 18 pages).  The
  generated PDF was deliberately kept outside the worktree because it is not
  in this ticket's allowed paths.
- Tier 3 is not run: this is a scoped carrier gate, not a programme freeze,
  shared-core change or release.
