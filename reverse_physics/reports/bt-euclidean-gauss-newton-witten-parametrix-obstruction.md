# BT Gauss--Newton Witten parametrix obstruction

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_GAUSS_NEWTON_WITTEN_PARAMETRIX_OBSTRUCTION_V1`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

## Result

The simplest residual-adapted inverse does not solve the BT Witten one-form
equation, even before a volume-uniform estimate is attempted.  Its failure is
not just one constant normalization: an asymmetric positive background mixes
a lowest cosine source into both the lowest sine and the orthogonal
checkerboard mode.

Write the finite-volume action on the mean-zero log-field carrier as

\[
 S(\psi)=\frac{\|r(\psi)\|^2}{2\lambda^2},
 \qquad J(\psi)=D_\psi r.
\]

For a constant lowest-mode one-form \(dT\), the natural pointwise
Gauss--Newton field is

\[
 v_G(\psi)=\lambda^2(J^*J)^{-1}dT.
\]

The first part of the action Hessian maps this field to the source exactly,
but that is not the complete Witten operator.  Since

\[
 \nabla^2S=\lambda^{-2}\left(
 J^*J+\sum_x r_x\nabla^2r_x\right),
\]

the exact image is

\[
 \boxed{
 \mathcal L_1v_G=dT+\mathcal L_0v_G
 +\lambda^{-2}\left(\sum_xr_x\nabla^2r_x\right)v_G.}
\]

The second term differentiates the background-dependent inverse metric in
configuration space.  The third is the curvature of the nonlinear residual
embedding.  Neither can be dropped.

## Vacuum calculation

On the four-cycle \(C_4\), use the orthogonal rational basis

\[
 b_1=(1,-1,0,0),\quad b_2=(1,1,-2,0),\quad
 b_3=(1,1,1,-3),
\]

whose Gram diagonal is \((2,6,12)\), and take
\(dT=(1,0,-1,0)\).  At the vacuum
\(\Omega=(1,1,1,1)\), with \(\lambda=2/5\), the full-residual candidate has

\[
 v_G=(1/50,1/50,0).
\]

The residual vanishes, so the embedding-curvature term is zero, and the
Gauss--Newton Hessian contribution is exactly \(dT\).  Nevertheless

\[
 \mathcal L_0v_G=-\frac1{50}dT,
 \qquad
 \boxed{\mathcal L_1v_G=\frac{49}{50}dT.}
\]

This does not contradict the exact free inverse.  Freezing the vacuum metric
produces a constant vector field and hence no derivative correction.  Here
\(v_G(\psi)\) is the globally background-adaptive field; its derivatives at
the vacuum are nonzero.

## Why the centered flat map is different

The exact flat-potential map uses

\[
 u=r-\bar r\mathbf1,
\]

not the full residual.  Away from the vacuum its metric differs by the exact
rank-one term

\[
 Dr^*Dr=Du^*Du+N\,d\bar r\otimes d\bar r.
\]

Thus the two parametrices must not be identified.  Replacing \(J\) by \(Du\)
does not repair the problem.  At the same vacuum the centered candidate gives

\[
                         \mathcal L_1v_{G,c}=\frac9{10}dT.
\]

The values of the two candidates coincide at the vacuum, but their second
configuration-space derivatives do not.

## Exact mode-mixing fixture

Now take the positive rational background

\[
                         \Omega=(1,1,2,2),
 \qquad r=(1,1,-1/2,-1/2).
\]

For the full-residual candidate, the Fourier coefficients of the defect
\(\mathcal L_1v_G-dT\) are

\[
 \begin{array}{c|c}
 \text{mode}&\text{exact coefficient}\\ \hline
 \text{lowest cosine}&55093/2653020\\
 \text{lowest sine}&-5349419/7959060\\
 \text{checkerboard}&79771/413100.
 \end{array}
\]

For the centered-map candidate they are

\[
 \begin{array}{c|c}
 \text{mode}&\text{exact coefficient}\\ \hline
 \text{lowest cosine}&362869/1687500\\
 \text{lowest sine}&-1395443/5062500\\
 \text{checkerboard}&130211/607500.
 \end{array}
\]

The nonzero sine and checkerboard entries are decisive.  Multiplying either
candidate by a field-independent scalar changes every output component by
the same factor and cannot remove components orthogonal to the source.

The producer obtains these values from complete three-variable exponential
Taylor jets and a finite Neumann inverse, all over the rationals.  The
independent verifier does not reuse that multivariate jet.  It follows each
coordinate axis separately with exact value/first/second-derivative dual
numbers and performs Gaussian elimination directly in that derivative
algebra.

## Meaning for the barrier

In plain language, locally inverting the stiffest part of the action was a
reasonable preconditioner, but the inverse itself bends as the field changes.
The Witten operator detects that bending, and a generic background scatters
the proposed lowest-mode solution into other modes.  A single renormalization
number cannot fix it.

This narrows the surviving route.  A positive construction must include the
configuration-space connection and residual-embedding curvature, or solve the
one-form equation nonlocally.  The exact checkerboard defect supplies a
concrete \(Q\)-sector source for the operator Schur problem.  It may be used to
build a corrected parametrix and prove a relative form bound, or to seed a
normalized low-Rayleigh construction.  A pointwise defect alone is not such a
sequence.

## Boundary

This is a method obstruction only.  It does not obstruct every corrected,
variational, or nonlocal Witten inverse.  It establishes neither volume-uniform
Witten Schur coercivity nor its failure, and gives no normalized lowest-mode
bound, interacting \(H^{-1}\) estimate, controlled divergence sequence,
tightness, or continuum measure.  It has no Born, Krein, or
`LORENTZIAN-CAUSAL` consequence.

Paper 21 is not changed at this checkpoint.  The result identifies the next
operator correction but does not change the open continuum or reconstruction
lifecycle state.

## Reproducibility

Run the exact scoped rails under the 500 MB Python cap:

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_gauss_newton_witten_parametrix_obstruction.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_gauss_newton_witten_parametrix_obstruction.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_gauss_newton_witten_parametrix_obstruction
```

The producer passed its 12 exact checks in 0.08 seconds at 21,456 KiB peak
RSS.  The method-distinct verifier passed in 0.05 seconds at 19,500 KiB, and
all ten focused and adversarial mutation tests passed in 0.32 seconds at
22,940 KiB.  Python compilation, JSON parsing, Draft 2020-12 schema checking,
certificate validation, scoped diff checking, and exact input-hash inspection
also passed.

The append-only planning import read 1,645 nodes with zero invalid items and
zero malformed events in 8.72 seconds at 184,100 KiB under the 300 MiB Go
limit.  Sequence 42 records this checkpoint without closing the active
continuum work item.

Tier 2 uses the exact hashes of the unchanged Witten one-form and flat
Piola/Ward certificates rather than rebuilding their producer chains.  Tier 3
is not applicable because no freeze, lifecycle promotion, shared-core change,
release, or theorem promotion occurs.

The read-only Science Forge shadow wrapper exited zero in advisory mode, but
its bridge audit remains a failure, not a pass: the existing Forge binary and
standard-library hashes disagree and compilation stops at `E9118`.  Its census
also reports drift, now 1,767 certificates against the stale 2026-07-19
baseline of 976.  Neither finding is used as scientific verification.
