# BT radial-convexity and unit-virial obstruction

**Certificate:**
`REVERSE_PHYSICS_BT_EUCLIDEAN_RADIAL_CONVEXITY_OBSTRUCTION_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

## Result

Two natural repairs of the BT low-temperature virial argument fail exactly.
On the four-dimensional period-six torus, let

\[
 d(x)=\sum_{i=1}^4\min(x_i,6-x_i)
\]

and, up to subtraction of the finite-volume mean, set

\[
 \psi_x=k_{d(x)}\log(101/100),
\]

where

\[
 (k_0,\ldots,k_{12})=(0,1,2,3,4,5,7,10,15,25,48,101,214).
\]

Every edge weight is rational:

\[
 w_{xy}=(101/100)^{k_{d(y)}-k_{d(x)}}.
\]

Direct exact enumeration of all \(6^4=1296\) sites gives

\[
 A>0,\qquad D=C_D\log(101/100),\qquad
 \left.\frac{d^2}{d\rho^2}A(\rho\psi)\right|_{\rho=1}
 =C_2\log(101/100)^2,
\]

with rational coefficients \(C_D>0\) and \(C_2<0\).  Moreover, the odd
alternating partial sum gives

\[
 \log(101/100)<\frac1{100}-\frac1{2\,100^2}
 +\frac1{3\,100^3}=\frac{29851}{3000000}.
\]

The exact rational comparison \(C_D(29851/3000000)<A\) therefore proves

\[
                         0<D<A.
\]

Thus the homogeneous inequality \(D\geq A\) is false, and the function
\(\rho\mapsto A(\rho\psi)\) is not convex on every positive radial ray.

## Meaning for the continuum programme

The predecessor had already ruled out the coefficient-two inequality.  This
fixture pushes the obstruction below coefficient one and also rules out the
convexity argument that would have implied \(D\geq A\) by integrating the
radial derivative.  The failure is a collective reciprocal-edge effect on a
layered background; checking only one vertex or an averaged distance shell is
not valid because the residual is squared before summation.

The result does **not** show that every positive constant fails.  A theorem
\(D\geq cA\) with \(0<c<1\) remains open, as does a Gibbs-weighted estimate
that never requires a pointwise homogeneous virial inequality.  The existing
affine virial and actual uniform action-density theorem are unchanged.

## Claim boundary

This is a method obstruction, not divergence of the actual interacting
\(H^{-1}\) moment.  It establishes no continuum measure, Born rule, Krein
reconstruction, or `LORENTZIAN-CAUSAL` statement.

## Verification

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_radial_convexity_obstruction.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_radial_convexity_obstruction.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_radial_convexity_obstruction
```

## Tier receipt

- Tier 0: Python compilation, schema/certificate/event JSON parsing, scoped
  `git diff --check`, exact staged-diff inspection, and the two-pass Paper 21
  build/log scan passed.  The PDF build took 3.4 seconds.
- Tier 1: producer replay passed in 0.12 seconds; the orbit-type independent
  verifier passed in 0.09 seconds; seven direct and mutation tests passed in
  0.20 seconds.  The Paper 21 claim-map producer and verifier also passed.
- Tier 2 was not run because no shared operator or transitive certificate
  input changed; both predecessor certificates are content-pinned imports.
- Tier 3 was not run because this is a scoped method obstruction, not a
  freeze, lifecycle promotion, shared-core change, or release.
