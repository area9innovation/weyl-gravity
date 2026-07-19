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

The obstruction now has a constructive exact reduction in
[`GENERIC_BACKGROUND_GHOST_ENDO_DUHAMEL_REDUCTION.json`](certificates/GENERIC_BACKGROUND_GHOST_ENDO_DUHAMEL_REDUCTION.json).
For the positive Euclidean operator,
`H=H0+W` with `H0=(-Box I+Ric)-(1/2)grad div` and `W=-2 Ric`.
The Endo base has the exact finite-interval heat kernel
`K_H0(t)=K_F(t)-grad grad' integral_t^(3t/2) K_Delta0(s) ds`, and its
nonzero-mode determinant differs from `det F` only by the local scalar
zeta-scaling term. Through cubic curvature order the remaining ghost work is
therefore the finite set of one-, two- and three-Ricci insertion traces. The
zero-external-momentum angular numerator of the three-insertion row is now
computed exactly in
[`GENERIC_BACKGROUND_GHOST_N3_ADIABATIC_CARRIER.json`](certificates/GENERIC_BACKGROUND_GHOST_N3_ADIABATIC_CARRIER.json):
its scalar-flat `tr(Ric^3)` coefficient is `503/648` before the `W` and
Tr-log factors and `-503/243` afterwards. Its radial integral is scaleless and
IR singular, so the nonzero-momentum triangle, the curved-Endo one- and
two-insertion traces, and hence the generic ghost form-factor coefficients
remain open.

The one- and two-insertion architecture is now closed exactly in
[`GENERIC_BACKGROUND_GHOST_N1_N2_HODGE_RESOLVENT_REDUCTION.json`](certificates/GENERIC_BACKGROUND_GHOST_N1_N2_HODGE_RESOLVENT_REDUCTION.json).
Proper-time integration gives
`G_H0=G_F-(1/3)d Delta_0^-2 delta`; cyclicity then leaves exactly two `n=1`
and three `n=2` minimal vector/scalar resolvent carriers with coefficients
`(1,-1/3)` and `(-1/2,1/3,-1/18)`. This closes the nonminimal reduction, not
the traces: second- and first-curvature-order minimal kernels are still
required respectively.

The generic nonexceptional-momentum triangle is now reduced exactly in
[`GENERIC_BACKGROUND_GHOST_N3_TRIANGLE_KERNEL.json`](certificates/GENERIC_BACKGROUND_GHOST_N3_TRIANGLE_KERNEL.json).
Expanding the three Endo longitudinal projectors gives eight sectors with
multiplicities `(1,3,3,1)` and twenty exact Feynman-simplex/Wick rows. This is
the complete labelled-Ricci parametric tensor kernel, not yet the repository
five-carrier decomposition. The zero-derivative sector can feed `I10`, while
the longitudinal sectors can feed `I24`, `I25`, `I28`, and `I29`; the frozen
`K_munu` crosswalk/projection remains open in this intermediate receipt; the
pure-vector one-/two-insertion sum is evaluated separately below.

The scalar-flat crosswalk and tensor projection are now completed in
[`GENERIC_BACKGROUND_GHOST_N3_FIVE_CARRIER_PROJECTION.json`](certificates/GENERIC_BACKGROUND_GHOST_N3_FIVE_CARRIER_PROJECTION.json).
The eleven raw `I10/I24/I25/I28/I29` orientations have exact TT evaluation
rank ten; the CPT-IV relation is fixed by removing the symmetric `I28`
coordinate.  Every projected channel is stored as a rational
Feynman-simplex numerator over the common `Delta^4`, and unseen exact
momentum/alpha fixtures replay all 125 TT amplitudes.  This closes only the
parametric `n=3` ghost projection.

At the normalized symmetric nonexceptional point `x1=x2=x3=1`, the eleven
simplex integrals are now evaluated exactly in
[`GENERIC_BACKGROUND_GHOST_N3_SYMMETRIC_POINT_SIMPLEX_INTEGRATION.json`](certificates/GENERIC_BACKGROUND_GHOST_N3_SYMMETRIC_POINT_SIMPLEX_INTEGRATION.json).
They reduce to rational combinations of the single scalar master
`J_triangle=4 Cl2(pi/3)/sqrt(3)`.  Exact rational divergence witnesses with
checked open-edge and punctured-corner flux prove the four moment reductions;
an independent quadrature replay guards against the false logarithm branches
produced by naive iterated symbolic integration.  This is one coefficient-
bearing kinematic fixture, not the generic functions of `(x1,x2,x3)`.

At generic positive nonexceptional kinematics, the integrands themselves now
have an exact homogeneous barycentric reduction in
[`GENERIC_BACKGROUND_GHOST_N3_BARYCENTRIC_FACTORIZATION.json`](certificates/GENERIC_BACKGROUND_GHOST_N3_BARYCENTRIC_FACTORIZATION.json).
Ten of eleven numerators contain one exact `Delta` factor, so their common
pole order drops from four to three.  All raw orientations except `I10_123`
vanish on every open simplex edge; their exact edge/vertex orders and positive
corner-integrability margins are stored.  The `I28` quotient relation holds
pointwise.  This identifies the only direct edge-restriction source but does
not yet compute rational IBP primitives, their corner flux, bubble/log
coefficients, or the generic integrated functions.

The combined pure-vector `n=1+n=2` slice
is now exact; the three longitudinal `D_W` towers are resummed into the
normalized scalar Schur operator
`S_L(W)=(2/3)I+(1/3)delta(F+W)^-1 d`. Its relative determinant kernel, a
possible local zeta multiplicative term, the physical fourth-order kernel,
and the integrated repository functions and coefficients remain open.

The infinite-dimensional regularization gate is now sharpened in
[`GENERIC_BACKGROUND_GHOST_SCHUR_SCHATTEN_SPLIT.json`](certificates/GENERIC_BACKGROUND_GHOST_SCHUR_SCHATTEN_SPLIT.json).
Writing `S_L=I+K`, the order-`-2` correction lies in every Schatten `S_p`
with `p>2`, so `det_3(I+K)` is canonical and contains the trace-class tail.
Only the finite `R(K)` and `R(K^2)` rows require the common regulator.  The
canonical local residues are exact:
`Wres(K)=(4 pi)^-2 integral (R^2+4 Ric^2)/9`,
`Wres(K^2)=(4 pi)^-2 integral (R^2+2 Ric^2)/27`, and
`Wres(log S_L)=(4 pi)^-2 integral (5 R^2+22 Ric^2)/54`. Conversion to a zeta
pole or scale coefficient still requires a declared reference-operator order
and trace normalization. See
[`GENERIC_BACKGROUND_GHOST_SCHUR_WODZICKI_RESIDUE.json`](certificates/GENERIC_BACKGROUND_GHOST_SCHUR_WODZICKI_RESIDUE.json).

The imported same-gauge physical Hessian is now operational through first
curvature order.  Its scalar-flat rank-nine momentum vertex has an exact
formal-adjoint completion, and one generic interior physical `n=3` simplex
fixture is evaluated in
[`GENERIC_BACKGROUND_PHYSICAL_HESSIAN_N3_TRIANGLE_FIXTURE.json`](certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_N3_TRIANGLE_FIXTURE.json).
For squared external momenta `(10,9,5)` and simplex point
`(7/15,1/5,1/3)`, all four Wick orders combine to the nonzero exact kernel
`-3532544138843839/319810083840000` before `(4 pi)^-2`.  This tests the
source-row Fourier map, adjunction, loop routing and Wick reduction at one
generic point.  The full alpha polynomial and five-carrier projection are
now exact, and the projected algebraic curvature-squared Hessian is imported
with its gauge-ordering crosswalk.  The integrated tensor triangle, `H2`
polarization and mixed `H1`-`H2` rows remain open generically.  A rational
equal-box TT fixture now performs the correct carrier comparison: all six
labelled `H1`-cubed triangle orderings plus all three polarized mixed bubbles
give the nonzero raw log coefficient `15707/216`.  Thus algebraic `H2` does
not cancel the corner identically.  The resolved largest-barycentric triangle
sectors and half-interval bubble sectors now carry one common Mellin minimal
subtraction, yielding the exact fixture scale row
`partial_log(mu^2) Gamma_MS=(4 pi)^-2 15707/216`.  A generic covariant
Volterra carrier now supplies six ordered triangle cells, three `H1-H2`
contact cells, their exact Schwinger measures, and one resolved-boundary
Mellin extension. The logarithmic residues at all six generic contact
endpoints are now evaluated and projected to 33 exact raw five-carrier rows;
left/right equality, two unseen fixtures and the symmetric `I28` quotient
section replay exactly. The symmetric-point triangle/contact incidence is now
assembled coefficientwise: `-1975/72+2704/27=15707/216`, so algebraic `H2`
does not cancel the symmetric `M14` divergence. Generic-box triangle corner
residues are now exact for all eleven channels, and their full incidence with
the contact rows is generically nonzero. Thus `M14` is disposed as a
Mellin-renormalized scale row. Finite local rows and complete form-factor
assembly remain open. See
[`generic-background-physical-hessian-symmetric-mixed-boundary-incidence.md`](../../reports/generic-background-physical-hessian-symmetric-mixed-boundary-incidence.md).

Replay with:

```bash
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.generic_background_ghost_cpt_obstruction --check
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_generic_background_ghost_cpt_obstruction
PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_generic_background_ghost_cpt_obstruction
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.generic_background_ghost_endo_duhamel_reduction --check
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_generic_background_ghost_endo_duhamel_reduction
PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_generic_background_ghost_endo_duhamel_reduction
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.generic_background_ghost_n1_n2_hodge_resolvent_reduction --check
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_generic_background_ghost_n1_n2_hodge_resolvent_reduction
PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_generic_background_ghost_n1_n2_hodge_resolvent_reduction
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.generic_background_ghost_longitudinal_schur_resummation --check
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_generic_background_ghost_longitudinal_schur_resummation
PYTHONPATH=quantum-weyl pytest -q quantum-weyl/spectral/euclidean/tests/test_generic_background_ghost_longitudinal_schur_resummation.py
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.generic_background_ghost_schur_schatten_split --check
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_generic_background_ghost_schur_schatten_split
PYTHONPATH=quantum-weyl pytest -q quantum-weyl/spectral/euclidean/tests/test_generic_background_ghost_schur_schatten_split.py
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.generic_background_ghost_n3_adiabatic_carrier --check
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_generic_background_ghost_n3_adiabatic_carrier
PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_generic_background_ghost_n3_adiabatic_carrier
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.generic_background_ghost_n3_triangle_kernel --check
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_generic_background_ghost_n3_triangle_kernel
PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_generic_background_ghost_n3_triangle_kernel
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_generic_background_ghost_n3_five_carrier_projection
PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_generic_background_ghost_n3_five_carrier_projection
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_generic_background_ghost_n3_symmetric_point_simplex_integration
PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_generic_background_ghost_n3_symmetric_point_simplex_integration
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_generic_background_ghost_n3_barycentric_factorization
PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_generic_background_ghost_n3_barycentric_factorization
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.generic_background_physical_hessian_n3_triangle_fixture --check
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_generic_background_physical_hessian_n3_triangle_fixture
PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_generic_background_physical_hessian_n3_triangle_fixture
```

Full regeneration of the five-carrier projection is an exact scientific-tier
check and takes roughly 163 seconds on the current workstation:

```bash
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.generic_background_ghost_n3_five_carrier_projection --check
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

The generic ghost one-/two-insertion gate now has an exact partial
evaluation. On the scalar-flat source complement the pure-vector physical
sum reduces to CPT-IV rows 1, 3 and 14,
`6 Gamma1 S1 - 2 Gamma3 S3 - 2 Gamma14 S14`, with an exact carrier
projection. The three remaining Hodge carriers contain
`D_W=delta W d`; its anisotropic principal symbol is outside the imported
minimal-potential CPT kernels. See
[`generic-background-ghost-n1-n2-vector-cpt-projection.md`](../../reports/generic-background-ghost-n1-n2-vector-cpt-projection.md).
The exact matrix determinant lemma and Hodge Ward identities now resum all
three towers to `S_L(W)`, with cubic weights `(-1/3,1/9,-1/81)`. The
finite/Fredholm relative identity is exact; a local zeta multiplicative term
is explicitly unevaluated. See
[`generic-background-ghost-longitudinal-schur-resummation.md`](../../reports/generic-background-ghost-longitudinal-schur-resummation.md).
The sharp trace-ideal continuation is recorded in
[`generic-background-ghost-schur-schatten-split.md`](../../reports/generic-background-ghost-schur-schatten-split.md):
the canonical `det_3` tail is defined and `Wres(K^2)` is computed, while `R(K)`, the
finite part of `R(K^2)`, and an unspecified zeta factorization remain open.
The successor
[`generic-background-ghost-schur-wodzicki-residue.md`](../../reports/generic-background-ghost-schur-wodzicki-residue.md)
computes `Wres(K)` and `Wres(log S_L)` and keeps the finite and
reference-specific scale rows fail-closed. The successor
[`generic-background-ghost-schur-weighted-trace-scale.md`](../../reports/generic-background-ghost-schur-weighted-trace-scale.md)
fixes the pole and scale response for the declared order-two weight. The
round-sphere benchmark
[`round-s4-ghost-schur-finite-weighted-traces.md`](../../reports/round-s4-ghost-schur-finite-weighted-traces.md)
then computes both reference finite rows exactly in digamma/trigamma form.
It also encloses the complete round-sphere `det_3` tail by exact rational
alternating-series and Euler--Maclaurin bounds and computes the selected
weighted modified determinant. Its finite-rank smoothing witness proves that
generic values require a full primed Green kernel or spectral measure; local
symbol data cannot determine them.

[`round-s4-ghost-schur-zeta-factorization.md`](../../reports/round-s4-ghost-schur-zeta-factorization.md)
then closes the zeta-to-weighted comparison on that same primed round-unit-
`S4` carrier. With `Q=Delta_0`, `A=Delta_0-4`, and `B=Delta_0-6`, the exact
local defect is
`m_Q(A,B)=-(1/4)(4^2-6^2)Wres(Q^-2)=5/3`, since
`Wres(Q^-2)=1/3`. Adding it to the selected weighted modified determinant
gives the zeta-factorized ratio `-2.3114788189487449608...`, independently
replayed from Hurwitz-zeta continuation. This is a special-background result.

The distinct generic convention is frozen in
[`generic-background-ghost-schur-weight-raised-zeta-factorization.md`](../../reports/generic-background-ghost-schur-weight-raised-zeta-factorization.md).
With `A=S_L Q` and `B=Q=Delta_0+Pi_0`, the order-minus-three/four BCH
weighted trace vanishes through four-dimensional residue order and
`m_Q^wr(S_L)=-(1/4)Wres(K^2)=-(4 pi)^-2 integral(R^2+2 Ric^2)/108`.
It specializes to `-1/3` on round `S4`, giving zeta ratio
`-4.3114788189487449608...`. The exact difference `2` from the preceding
`5/3` value records the change of factorization convention. The generic
finite rows remain a separate global Green/spectral problem.
