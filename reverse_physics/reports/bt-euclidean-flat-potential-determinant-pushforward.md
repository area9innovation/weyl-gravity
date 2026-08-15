# BT flat-potential determinant pushforward

**Certificate:**
`REVERSE_PHYSICS_BT_EUCLIDEAN_FLAT_POTENTIAL_DETERMINANT_PUSHFORWARD_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

## Result

The residual-boundary formulation now has a global flat coordinate system.
It removes the moving surface element, the separate positive-ground-state
norm, and the directed-tree factor in favor of one spectral determinant.

Let

\[
 \mathcal H=\left\{u\in\mathbb R^N:\sum_xu_x=0\right\},\qquad
 H(u)=-\Delta+\operatorname{diag}(u),
\]

and let \(\ell _0(u)\) be the lowest eigenvalue of \(H(u)\).  Connectivity
makes it simple and gives a strictly positive eigenvector \(\Omega(u)\).
The constant-vector Rayleigh quotient is zero, so \(\ell _0(u)\leq0\).  Put

\[
 c(u)=-\ell _0(u),\qquad
 r(u)=u+c(u){\bf1},\qquad
 K(u)=H(u)-\ell _0(u)I.
\]

Then \(K(u)\succeq0\) and \(K(u)\Omega(u)=0\).  The map \(u\mapsto r(u)\)
is an analytic bijection from the flat space \({\cal H}\) onto the principal
boundary of the Schrödinger spectrahedron.  Its inverse simply subtracts the
arithmetic mean of \(r\).

Most importantly, the exact normalized BT law becomes

\[
 \boxed{
 d\nu(u)=\frac1Z
 \frac{\exp\!\left[-\bigl(\|u\|_2^2+N\ell _0(u)^2\bigr)/
                         (2\lambda^2)\right]}
      {\det{}'\!\left(H(u)-\ell _0(u)I\right)}\,du . }
\]

Here \(\det'\) is the product of the \(N-1\) positive eigenvalues.  The
field observable has not disappeared: it is

\[
 \psi(u)=\log\Omega(u)-\frac1N\sum_x\log\Omega_x(u).
\]

Thus the continuum gate is now an explicit random diagonal Schrödinger
problem on a linear carrier: control the lowest Fourier coefficient of the
logarithm of the positive ground state under a Gaussian-confined inverse-
pseudodeterminant ensemble.

This is an exact reformulation, not the missing volume-uniform estimate.

The most direct convexity shortcut is also decided negatively.  Already on
the three-vertex path at \(\lambda=2/5\), the full negative logarithm of this
density has a strictly negative directional second derivative.  Thus the new
coordinates do not restore global Brascamp--Lieb convexity.

## Why the surface and tree factors collapse

Normalize \(a_x=\Omega_x^2/\|\Omega\|_2^2\).  Hellmann--Feynman
differentiation gives, for \(h\in{\cal H}\),

\[
 Dc(u)[h]=-\langle a,h\rangle.
\]

Since \(Dr[h]=h+Dc[h]{\bf1}\), its Gram determinant on \({\cal H}\) is

\[
 1+N\|a-N^{-1}{\bf1}\|_2^2=N\|a\|_2^2.
\]

Therefore the Euclidean surface Jacobian of the boundary graph is

\[
 \mathcal J_{\rm graph}
 =\frac{\sqrt N\,\|\Omega^2\|_2}{\|\Omega\|_2^2}.
\]

The predecessor coarea theorem gives

\[
 \mathcal J_H=\sqrt N\,\|\Omega^2\|_2\,\tau,
\]

where \(\tau\) is the directed-tree density.  For the symmetric matrix
\(K\), the adjugate formula and the directed matrix-tree theorem give the two
expressions

\[
 \operatorname{cof}_iK
 =\det{}'(K)\frac{\Omega_i^2}{\|\Omega\|_2^2}
 =\Omega_i^2\tau.
\]

Hence

\[
 \det{}'(K)=\|\Omega\|_2^2\tau,
 \qquad
 \frac{{\cal J}_{\rm graph}}{{\cal J}_H}
 =\frac1{\det{}'(K)}.
\]

Finally, \(u\perp{\bf1}\) implies

\[
 \|r(u)\|_2^2=\|u\|_2^2+N\ell _0(u)^2,
\]

which yields the displayed density.

This does not contradict the earlier tilt-Jacobian cancellation.  That result
pulls the boundary law back to the log-field chart, where all coarea factors
cancel.  The present result instead uses the centered diagonal potential as
the independent flat variable; its nontrivial change of variables is exactly
the inverse pseudodeterminant.

## Exact four-cycle fixture

For \(C_4\), take

\[
 \Omega=(1,2,1,1/2),\qquad
 r=(1/2,-1,1/2,2).
\]

Then

\[
 c=\frac12,qquad
 u=(0,-3/2,0,3/2),\qquad
 \ell _0=-\frac12.
\]

The four principal cofactors of \(K\) are

\[
 5,\quad20,\quad5,\quad\frac54.
\]

Their sum is the pseudodeterminant,

\[
 \det{}'K=\frac{125}{4}
 =\left(1^2+2^2+1^2+(1/2)^2\right)\,5
 =\|\Omega\|_2^2\tau.
\]

The boundary-graph and residual-coarea Jacobians are respectively

\[
 \mathcal J_{\rm graph}=\frac{34}{25},\qquad
 \mathcal J_H=\frac{85}{2},
\]

so their ratio is exactly

\[
 \frac{{\cal J}_{\rm graph}}{{\cal J}_H}
 =\frac4{125}=\frac1{\det{}'K}.
\]

At \(\lambda=2/5\),

\[
 \frac{\|u\|_2^2+4\ell _0^2}{2\lambda^2}
 =\frac{275}{16}.
\]

Thus the unnormalized flat density at this fixture is exactly
\((4/125)e^{-275/16}\).  The independent verifier reconstructs the graph,
both Schrödinger matrices, the ground-state equation, every cofactor, and
both Jacobians without importing producer helpers.

## Exact obstruction to global convexity

Take the three-vertex path and the positive ground vector

\[
                 \Omega=(5,1,100).
\]

Its residual and centered potential are

\[
 r=(-4/5,103,-99/100),
 \qquad
 u=(-10361/300,20779/300,-5209/150),
\]

and the lowest eigenvalue of \(-\Delta+\operatorname{diag}(u)\) is

\[
                         \ell _0=-10121/300.
\]

Differentiate along the mean-zero potential direction \(h=(1,0,-1)\).  Let

\[
 \mathcal V(u)=
 \frac{\|u\|_2^2+3\ell _0(u)^2}{2\lambda^2}
 +\log\det{}'\!\left(H(u)-\ell _0(u)I\right)
\]

be the negative logarithm of the flat density, modulo its normalization.
Exact rational eigenvalue perturbation and the bordered inverse of \(K\)
give

\[
 D_h^2\ell _0=-\frac{1948370375}{18663338844}.
\]

The Gaussian-confined part has positive curvature

\[
 D_h^2{\cal V}_{\rm Gauss}
 =\frac{28994309146675}{298613421504}
 \approx97.0965,
\]

while the logarithmic pseudodeterminant contributes

\[
 D_h^2\log\det{}'K
 =-\frac{3352883248182475}{31186439208324}
 \approx-107.511.
\]

Therefore

\[
 \boxed{
 D_h^2{\cal V}
 =-\frac{5196641386825675}{498983027333184}<0. }
\]

No floating-point sign decision is used.  The producer obtains the jet from
the rational ground-state pseudoinverse.  The independent verifier instead
builds the bivariate characteristic polynomial
\(\det(H(u+th)-zI)\), implicitly differentiates its lowest root twice, and
differentiates \(-\partial_z\det(H-zI)=\det'K\).  The two exact rational
answers agree.

This obstruction is scoped.  It rules out a global-log-concavity or direct
Brascamp--Lieb proof in the new potential coordinates.  It does not rule out
a nonconvex integration-by-parts identity, localization, determinant
cancellation against the ground-state resolvent, or the actual moment bound.

## What this changes

The previous surface formulation left three coupled geometric objects: a
Gaussian surface weight, a moving surface element, and a reciprocal tree
Jacobian.  They are now one ordinary density on a fixed vector space.  This
makes the next analytic questions concrete:

1. differentiate the lowest eigenvalue and the pseudodeterminant in the flat
   potential variable;
2. derive a nonconvex integration-by-parts or localization estimate, since
   global convexity is now exactly obstructed;
3. control the ground-state resolvent strongly enough to bound the lowest
   Fourier coefficient of \(\log\Omega\);
4. only after the one-mode theorem, sum dyadic shells for the actual
   interacting \(H^{-1}\) moment.

The first term in the effective potential has genuine Gaussian confinement:
\(-\ell _0(u)\) is nonnegative and convex, so
\(\|u\|^2+N\ell _0(u)^2\) contains the strongly convex quadratic
\(\|u\|^2\).  The path fixture proves that the curvature of
\(\log\det'K(u)\) can overcancel it.  The next route must therefore preserve
the determinant and ground-state resolvent together rather than bound their
curvatures separately.

## Boundary

This result does not establish a volume-uniform determinant or resolvent
bound, the normalized lowest-mode moment, the interacting \(H^{-1}\) moment,
tightness, or a continuum measure.  Ordinary Osterwalder--Schrader positivity
at \(\lambda=0.4\) remains obstructed by the finite-volume predecessor.  No
Born rule, Krein reconstruction, or `LORENTZIAN-CAUSAL` statement follows.

## Verification

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_flat_potential_determinant_pushforward.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_flat_potential_determinant_pushforward.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_flat_potential_determinant_pushforward
```

## Verification receipt

- Tier 0 passed: the three Python files compile, the schema, certificate, and
  sequence-38 planning event parse, the generated certificate is current, and
  the scoped diff check is clean.  Scientific Python commands ran under a
  500 MB virtual-memory cap.
- The producer passed all 19 declared checks in 0.04 s at 22 MB maximum
  resident memory.
- The independent verifier passed in 0.11 s at 31 MB.  It uses an implicit
  bivariate characteristic-polynomial jet for the negative-curvature witness,
  independently of the producer's bordered-pseudoinverse jet.  It also checks
  undeclared exact path, triangle, and five-cycle fixtures in addition to the
  certified four-cycle fixture.
- Eleven direct and adversarial mutation tests passed in 0.13 s at 31 MB.
- Tier 2 predecessor checks passed for the residual-spectrahedral pushforward
  (15/15 in 0.15 s) and the induced-tilt Jacobian cancellation (16/16 in
  0.11 s).
- The append-only planning import read 1,641 nodes with zero invalid items and
  zero malformed events in 1.83 s at 15 MB under a 300 MiB Go memory limit.
- The 2.51 s advisory Science Forge shadow rail failed closed on the existing
  Forge binary/standard-library mismatch (`E9118`) and reported corpus
  baseline drift (1,758 certificates versus 976).  Its wrapper exited zero;
  the bridge audit itself is recorded as failed, not passed.
- Paper 21 is not changed at this checkpoint.  The certificate and this report
  are the scoped human and machine-readable publications, while concurrent
  foundations work remains outside this commit.
- Tier 3 was not run because this is a finite-graph reformulation and method
  obstruction, not the requested interacting \(H^{-1}\) lifecycle promotion,
  a freeze, release, shared-core change, or Lorentzian claim.
