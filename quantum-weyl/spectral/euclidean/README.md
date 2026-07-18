# Euclidean spectral coefficient gate

Dependency tag for every future result in this directory:
`EUCLIDEAN-SPECTRAL`.

The Branch C reduced-mode bootstrap still does not evaluate a determinant.
Separately, the exact standard conformal-spin-two determinant reconstruction
in [`coefficient_reconstruction.py`](coefficient_reconstruction.py) now gives

\[
a_2={87\over20},\qquad c_2={199\over30},\qquad p_2=0.
\]

from constant-curvature and Ricci-flat heat-kernel data, with an independent
conical-sphere check of \(c_2\). The odd zero is an exact parity Ward result
for the declared real tensor-Laplacian, parity-even heat-kernel regulator;
it is not assumed for an unmatched repository regulator. Its combined coefficient and local
one-generator \(D\)-descent receipt is
[`WEYL_GRAVITON_ANOMALY_COEFFICIENTS_D_DESCENT.json`](certificates/WEYL_GRAVITON_ANOMALY_COEFFICIENTS_D_DESCENT.json).
The companion
[`STANDARD_SPIN2_AUXILIARY_FOURTH_ORDER_MATCH.json`](certificates/STANDARD_SPIN2_AUXILIARY_FOURTH_ORDER_MATCH.json)
proves the exact TT Schur identity relating the physical second-order factor
pair to a local second-order/algebraic auxiliary quadratic form. It does not
fix the repository auxiliary measure or contour.
The
[`REPOSITORY_FULL_BV_MULTIPLICITY_PREFLIGHT.json`](certificates/REPOSITORY_FULL_BV_MULTIPLICITY_PREFLIGHT.json)
derives the standard bundle ranks `(5,1,5,3)`, their signed rank six, and the
covariant BV component decompositions. It localizes the remaining scalar
ghost multiplicity problem to one rank and provides the strict
`REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER` receiver schema and semantic
validator. The receiver enforces complete integration-row and factor
coverage, exact target ranks/signs, the scalar rank-two-to-rank-one map, and
nested proof hashes. Classical carrier row counts are explicitly not treated
as determinant multiplicities.
The complete repository Euclidean principal-symbol sequence is now certified
by `certificates/REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX.json`. The local
Ricci-flat carrier and factorwise `b4` calculation in
`certificates/REPOSITORY_NONCONFORMALLY_FLAT_OR_RICCI_FLAT_FULL_BV_OPERATOR_MEASURE_COEFFICIENT_MATCH.json`
fix `c=199/30`, while the independent round-`S4` calculation fixes
`a=87/20`. These coefficients feed the separately certified regulated
Slavnov insertion; they still do not establish a Lorentzian QME or global
determinant phase theorem.

The generic-background ghost applicability question is now decided exactly
in
[`GENERIC_BACKGROUND_DIFF_WEYL_GHOST_CPT_OBSTRUCTION.json`](certificates/GENERIC_BACKGROUND_DIFF_WEYL_GHOST_CPT_OBSTRUCTION.json).
Eliminating the algebraic Weyl-ghost row gives
`M_eff xi = Box xi + Ric(xi) + (1/2) grad div(xi)`, independently of the
covariant gauge parameter. Its unit-covector principal spectrum is
`(3/2,1,1,1)`, and generic tracefree Ricci curvature mixes the Hodge sectors.
It is elliptic but nonminimal, while its Einstein specialization reproduces
the accepted `Delta_0-R/3` scalar ghost factor. Thus the current
minimal-Laplace CPT kernels cannot receive the generic ghost block by direct
rank or endomorphism substitution. The next analytic input is a matched
nonminimal-vector determinant/CPT calculation or an exactly equivalent local
extension with its Jacobian; this is not an anomaly or Lorentzian no-go.

Replay with:

```bash
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.generic_background_ghost_cpt_obstruction --check
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_generic_background_ghost_cpt_obstruction
PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_generic_background_ghost_cpt_obstruction
```

The generic schema in this directory remains a promotion gate: a coefficient record is valid
only when it supplies an exact coefficient together with the action
normalization, signature, gauge, regularization, zero-mode policy, contour
policy, frozen classical commit, and proof certificate.

The schema fixes all Lorentzian causal, QME, and anomaly-cancellation claims
to `false`. A Euclidean local-effective-action coefficient cannot promote
any of those claims by itself.

Before emitting a record, the Euclidean package must separately certify:

- ellipticity of the complete gauge-fixed complex;
- exact field, ghost, and auxiliary multiplicities;
- conformal-Killing and all other zero-mode removals;
- the determinant measure and indefinite-direction contour;
- equivalence of auxiliary and fourth-order formulations;
- normalization relative to `S_W = alpha_C integral sqrt(g) C^2`;
- Euler and Pontryagin conventions.
