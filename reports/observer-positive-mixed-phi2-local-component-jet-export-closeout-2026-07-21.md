# Observer positive-mixed Phi2 local component-jet export close-out

The exact retained-harmonic to local Berger component-jet gate is closed.
The positive-mixed primitive reconstructs the four diagonal components
\(428/567,-29/21,-29/21,-6/7\), and all other local components vanish.  All
942 component-PBW jets consumed by the universal formulas through order five
are exported with their derivative paths.

Harmonic reconstruction, noncommuting-frame PBW commutators, reality and
\(K_{\rm Berger}\) covariance pass.  The export includes six nonzero
Levi--Civita connection coefficients and all nonzero covariant tensor jets
through the same order.  Exact specialization reduces 6,171
Phi2-dependent source terms to 20 normalized survivors, with 6,091
vanishing; 288 unaffected terms retain a canonical hash.  An independent
coarea-variation rail gives \(-\Phi_{2,00}/2=-214/567\).

The complete replacement-112 executable unary and every downstream
reduction or nonlinear observer claim remain NO_CERTIFIED_MAP.

CLOSE-OUT: DONE — the missing positive-mixed retained-to-local variational input and evaluated nonrod D3S coefficients are certified

EVIDENCE: closed_universe_observers/certificates/BERGER_POSITIVE_MIXED_PHI2_LOCAL_COMPONENT_JET_EXPORT.json

## Verification receipt

- Tier 0: Python compilation, JSON/schema parsing and scoped
  git diff --check — PASS.
- Tier 1 producer:
  python3 -m closed_universe_observers.generate_berger_positive_mixed_phi2_local_component_jet_export --write
  — PASS (1.29 s).
- Tier 1 independent rail:
  python3 -m closed_universe_observers.verify_berger_positive_mixed_phi2_local_component_jet_export
  — PASS (1.36 s).
- Tier 1 focused tests:
  pytest -q closed_universe_observers/tests/test_berger_positive_mixed_phi2_local_component_jet_export.py
  — PASS, 5 tests (4.52 s pytest time; 4.93 s process time).
- Tier 2 atlas generation, schema validation and independent verifier:
  python3 -m closed_universe_observers.atlas.generate_observer_atlas_fragment;
  python3 residual_atlas/validate_fragment.py closed_universe_observers/atlas/observer-atlas-fragment.json;
  python3 -m closed_universe_observers.atlas.verify_observer_atlas_fragment
  — PASS (0.70 s, 0.69 s, 1.55 s).
- Tier 2 direct atlas consumers:
  pytest -q closed_universe_observers/tests/test_observer_atlas_fragment.py
  — PASS, 46 tests (27.7 s wall time).
- Paper 09:
  pdflatex -interaction=nonstopmode -halt-on-error -output-directory=temporary
  09-relational-clocks-berger-d-cartan.tex, twice — PASS (0.88 s,
  1.03 s; output kept outside the worktree).
- Tier 3 is not run: this is a scoped coefficient-export gate, not a
  programme freeze, shared-core change, release or theorem-lifecycle
  promotion.
