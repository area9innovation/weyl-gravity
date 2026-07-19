# Generic-background physical Hessian n=3 five-carrier projection

## Result

The same-gauge rank-nine physical Hessian is now operational through the
complete three-linear term

\[
\frac16\operatorname{Tr}\left[(H_0^{-1}H_1)^3\right].
\]

The exact sparse engine constructs the full Feynman-parameter numerator,
solves the eleven raw scalar-flat carrier coordinates in the section that
removes the symmetric `I28` null direction, and interpolates every coordinate
at generic external boxes.  The certificate contains 5,755 exact terms in
the channels

```text
I10_123
I24_123 I24_213 I24_312
I25_123 I25_213 I25_312
I28_123 I28_132 I28_231
I29_123
```

The formula digest is

```text
7c91744da094939e86e96a6807b8f406c01b1e4b2991ef235e11dea2c2b3b3fe
```

and both unseen exact momentum fixtures have zero defects in all eleven
channels.

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

## Why the physical interpolation is Laurent

The first polynomial interpolation attempt reused the ghost rule
`3-d/2`.  It failed exactly on a mixed `I24` row.  That failure is retained as
the architecture diagnostic: the physical `H1` vertex contains spacetime
Riemann tensors, while the scalar-flat carrier section reconstructs each
linearized Riemann tensor from a transverse-traceless Ricci tensor using

\[
h_i=\frac{2\,\operatorname{Ric}_i}{x_i}.
\]

There can therefore be one inverse external box per curvature leg.  After
clearing the uniform denominator `x1*x2*x3`, a carrier with `d` explicit
derivatives has homogeneous numerator degree

\[
6-\frac d2.
\]

Thus the maximum box degree is six rather than three.  The degree-six space
has 28 monomials.  The 28 deterministic momentum fixtures have rank 28
modulo `1000003`; a nonzero determinant modulo a prime proves the integral
evaluation determinant is nonzero over the rationals.  All interpolation
coefficients and residuals are then solved exactly over `Q`.

The common box denominator is a coordinate feature of the declared
scalar-flat TT `K/Ricci` crosswalk.  This certificate does not interpret it
as a new physical pole.

## Exact architecture

The imported physical vertex is quadratic in the incoming loop momentum.
Instead of expanding raw tensor graphs, the implementation uses exact sparse
polynomials in

```text
alpha1 alpha2 l0 l1 l2 l3
```

and performs matrix multiplication, the rank-nine trace, all four Wick
orders, and the carrier solve in that algebra.  Its uniform representation is

\[
(4\pi)^{-2}\sum_A
I_A\frac{N_A(\alpha_1,\alpha_2;x_1,x_2,x_3)}
{x_1x_2x_3\,\Delta^4},
\]

where every numerator has alpha degree at most nine.  Fixture coordinates are
content-addressed under ignored `build/` storage by the engine version and
the hashes of the physical-Hessian and carrier dependencies.  The cache is a
runtime optimization only; the independent verifier recomputes an unseen
fixture without it.

## Claim boundary

This closes the full-alpha-polynomial and five-carrier-projection subgate for
the three-`H1` physical triangle.  It does **not**:

- integrate the generic alpha-simplex rows;
- import the curvature-squared `H2` physical Hessian;
- compute the mixed `H1-H2` trace rows;
- assemble the five complete repository third-curvature form factors;
- fix finite `C2` or dressed `R(g_hat)^2` normalizations;
- supply complete renormalized `Gamma1` or `Q1`;
- authorize residual transfer; or
- establish a Lorentzian QME, Hadamard, particle, positivity, scattering, or
  unitarity theorem.

The next physical gate is therefore generic integration of these eleven rows
in the existing scalar-triangle master basis, in parallel with acquisition of
the `H2` layer.

## Receipts

```text
28 exact training fixtures, checkpointed           PASS  993.47 s
emit + two unseen exact fixtures                    PASS   67.48 s
fresh no-cache unseen verifier                      PASS   28.76 s
exhaustive replay from content-addressed cache      PASS   11.83 s
six scoped unit tests                               PASS    1.74 s
stored strict-schema/certificate rail               PASS    1.00 s
```

Reproduction commands:

```bash
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.generic_background_physical_hessian_n3_five_carrier_projection \
  --check
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.verify_generic_background_physical_hessian_n3_five_carrier_projection
PYTHONPATH=quantum-weyl python3 -m unittest \
  spectral.euclidean.tests.test_generic_background_physical_hessian_n3_five_carrier_projection
```

The first command is the exhaustive certificate rail.  The fast per-commit
rail uses `--check-stored`; it validates the strict schema, row grading,
formula digest, lifecycle boundary, and dependency references without
replaying the 28 exact fixture coordinates.  Tier 3 is not required because
this result advances a scoped Euclidean parametric carrier and does not
promote a QME or Lorentzian lifecycle state.
