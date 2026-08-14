# BT residual spectrahedral pushforward

**Certificate:**
`REVERSE_PHYSICS_BT_EUCLIDEAN_RESIDUAL_SPECTRAHEDRAL_PUSHFORWARD_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

**Lifecycle:** `REFORMULATION_PROVED`

## Result

The normalized low-mode problem now has an exact alternative coordinate
system.  It does not yet have the required volume-uniform bound.

Let \(G\) be a finite connected graph, let \(\Omega_x>0\), and quotient by
constant rescaling.  Fix the representative by

\[
                    \sum_x\log\Omega_x=0.
\]

With the graph-Laplacian convention

\[
 (\Delta\Omega)_x=\sum_{y\sim x}\Omega_y-d_x\Omega_x,
 \qquad r_x=\frac{(\Delta\Omega)_x}{\Omega_x},
\]

define

\[
 K(r)=-\Delta+\operatorname{diag}(r),\qquad
 \mathcal C_G=\{r:K(r)\succeq0\}.
\]

The residual map is an analytic bijection from the mean-zero log-field
carrier onto the smooth boundary of the convex spectrahedron
\(\mathcal C_G\).  Its inverse takes a boundary potential \(r\), extracts the
unique positive ground state of \(K(r)\), fixes its geometric mean to one,
and takes its logarithm.

This turns the formerly implicit orthogonal-mode partition factor into an
explicit surface and matrix-tree Jacobian.  The interacting \(H^{-1}\)
moment is still open, but its normalization problem is no longer hidden in an
unspecified fiber integral.

## Ground-state identity

The defining equation immediately gives \(K(r(\Omega))\Omega=0\).  More is
true.  For every real vector \(v\),

\[
 v^TK(r(\Omega))v
 =\sum_{\{x,y\}\in E}\Omega_x\Omega_y
 \left(\frac{v_x}{\Omega_x}-\frac{v_y}{\Omega_y}\right)^2\geq0.
\]

Connectivity makes the kernel one-dimensional, spanned by the strictly
positive vector \(\Omega\).  Conversely, the lowest eigenvector at every
boundary point of \(\mathcal C_G\) is simple and strictly positive.  This
proves both directions of the correspondence.  Simplicity also makes the
boundary smooth and the inverse ground vector analytic.

The statement is finite dimensional.  It does not itself supply an
all-volume estimate or a continuum limit.

## Differential and directed-tree Jacobian

Write \(\psi=\log\Omega\).  Differentiating the residual gives

\[
 J_\psi=Dr(\psi)
 =-\operatorname{diag}(\Omega)^{-1}K(r)
   \operatorname{diag}(\Omega).
\]

Thus \(J_\psi\mathbf1=0\).  The boundary normal is proportional to
\(\Omega^2=(\Omega_x^2)_x\), and

\[
                     (\Omega^2)^TJ_\psi=0.
\]

Moreover, \(-J_\psi\) is the directed weighted Laplacian with edge weight
\(w_{xy}=\Omega_y/\Omega_x\).  The directed matrix-tree theorem implies that

\[
       \tau_\psi=\frac{\operatorname{cof}_i(-J_\psi)}{\Omega_i^2}
\]

is independent of the deleted vertex \(i\).  The Euclidean Jacobian of the
map from \(\mathbf1^\perp\) to \((\Omega^2)^\perp\) is therefore

\[
       \mathcal J_H(\psi)
       =\sqrt N\,\|\Omega^2\|_2\,\tau_\psi.
\]

Equivalently, this is the product of the \(N-1\) nonzero singular values of
the residual derivative.

The reversible weights make the tree factor more explicit.  Reorienting each
undirected spanning tree toward the deleted root gives

\[
 \tau_\psi=
 \sum_T\frac{\prod_{\{x,y\}\in T}\Omega_x\Omega_y}
               {\prod_x\Omega_x^2}.
\]

This has a useful sign consequence.  Under any multiplicative field tilt
\(\Omega_x(t)=\Omega_xe^{t h_x}\), every tree term is the exponential of an
affine function of \(t\).  Hence \(\log\tau(t)\) is convex.  The other factor
\(\log\|\Omega(t)^2\|_2\) is also a log-sum-exp, so

\[
                       \log\mathcal J_H(t)
\]

is convex along every field direction.  Thus the exact entropy Jacobian has
a controlled curvature sign even though the BT action itself does not.  This
does not, by itself, control the surface geometry or the normalized marginal.

For the periodic lattices there is also a global all-field bound.  If \(G\)
is vertex transitive, let \(\kappa(G)\) be its number of spanning trees.
Automorphism symmetry makes the average tree degree at every vertex equal to
\(2(N-1)/N\).  With \(\sum_x\psi_x=0\), AM--GM over the tree monomials gives

\[
                         \tau_\psi\geq\kappa(G).
\]

The same gauge condition gives
\(\|\Omega^2\|_2=(\sum_xe^{4\psi_x})^{1/2}\geq\sqrt N\).  Consequently

\[
                 \mathcal J_H(\psi)\geq N\kappa(G),
\]

with equality at the constant field.  Thus the reciprocal entropy Jacobian
cannot enhance a nonconstant field relative to the vacuum value.  The
remaining risk lies in the joint Gaussian surface geometry and ground-state
observable, so this is still not a normalized moment bound.

## Exact normalized pushforward

In \(\psi=\lambda\phi\) coordinates, the finite-volume BT Gibbs measure is

\[
 d\mu_L(\psi)=Z_L^{-1}
 \exp\!\left[-\frac{\|r(\psi)\|_2^2}{2\lambda^2}\right]d\psi.
\]

Finite-dimensional coarea and the diffeomorphism give the exact pushforward

\[
 d\nu_L(r)=Z_L^{-1}
 \frac{\exp[-\|r\|_2^2/(2\lambda^2)]}
 {\sqrt N\,\|\Omega(r)^2\|_2\,\tau(r)}
 d\mathcal H^{N-1}(r),
 \qquad r\in\partial\mathcal C_G.
\]

The continuum-normalized Fourier observable becomes

\[
 \widehat\Phi_L(k)=\frac1{\lambda N}\sum_x
 \log\Omega_x(r)e^{-2\pi i k\cdot x/L}.
\]

Consequently, the next estimate is a precise random-ground-state problem:
control the lowest Fourier coefficient of the logarithm of the positive
ground state jointly with the reciprocal directed-tree Jacobian.  This is an
exact normalized marginal formulation, not a moment estimate.

## Rational four-cycle fixture

On the four-cycle take

\[
 \Omega=(1,2,1,1/2),\qquad
 r=(1/2,-1,1/2,2),\qquad A=11/4.
\]

The four rooted tree cofactors of \(-J\) are

\[
                      (5,20,5,5/4)=5\Omega^2.
\]

The four undirected spanning-tree monomials are
\((1/2,1/2,2,2)\), whose sum is the same tree density \(5\).
Since \(C_4\) has four spanning trees, the nonconstant fixture has
\(\tau=5>4\) and \(\mathcal J_H=85/2>16=N\kappa(C_4)\), as required by the
global minimum theorem.

For the integer basis \(e_0-e_3,e_1-e_3,e_2-e_3\) of the mean-zero carrier,
the domain Gram determinant is \(4\), the image Gram determinant is \(7225\),
and hence

\[
                  \mathcal J_H^2=\frac{7225}{4},
                  \qquad \mathcal J_H=\frac{85}{2}.
\]

The independent verifier reconstructs the graph Laplacian, residual,
Schrodinger matrix, differential, tangent normal, four cofactors, and both
Gram determinants without importing the producer's helpers.

## Foundations consequence

This separates three dependency layers.

1. The graph matrices, sum-of-squares identity, cofactors, and rational
   fixture are finite exact algebra.
2. Perron--Frobenius simplicity, analytic dependence of the ground vector,
   and coarea are finite-dimensional analysis.
3. The desired estimate is an all-volume theorem for a logarithmic ground
   state under a tree-weighted surface measure.

The classification is only `USED_BY_DISPLAYED_PROOF`.  No weakest-base,
necessity, equivalence, or independence claim has been proved.

## Next gate and boundaries

The next calculation is the variation of all three factors under a
lowest-mode multiplicative tilt of the ground state: the Gaussian residual
norm, the boundary surface element, and the directed-tree Jacobian.  A
uniform ratio bound would control the normalized one-mode marginal; a
controlled bad-volume sequence could obstruct it.  Only then should the
analysis pass to dyadic shells.

This result does not establish the normalized lowest-mode bound, the actual
interacting \(H^{-1}\) moment or its divergence, tightness, a continuum
measure, a Born rule, a Krein reconstruction, or anything
`LORENTZIAN-CAUSAL`.  It makes no literature-novelty claim for the finite
ground-state transform or matrix-tree identity.

## Verification

Run sequentially:

```text
ulimit -v 500000; python3 reverse_physics/bt_euclidean_residual_spectrahedral_pushforward.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_residual_spectrahedral_pushforward.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_residual_spectrahedral_pushforward
```
