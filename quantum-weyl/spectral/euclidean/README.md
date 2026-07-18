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
`REPOSITORY_FULL_BV_MULTIPLICITY_LEDGER` receiver schema. Classical carrier
row counts are explicitly not treated as determinant multiplicities.
The complete local gauge-fixed BV anomaly basis is now available on the
regular Bach locus, so these numbers define candidate coordinates along
`omega C2`, `omega E4`, and `omega C dual C`. This remains a standard background-anomaly result,
not a computation of the repository BV Slavnov breaking: the elliptic
operator, auxiliary/fourth-order Jacobian, measure, zero modes, and regulated
Slavnov action still require a matched certificate.

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
