# BT orthogonal Hessian block obstruction

**Certificate:**
`REVERSE_PHYSICS_BT_EUCLIDEAN_ORTHOGONAL_HESSIAN_BLOCK_OBSTRUCTION_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

## Result

The proposed global lowest-mode Schur-complement route is obstructed at its
first remaining gate.  On every four-dimensional periodic lattice whose side
length is divisible by four, an exact rational-weight background makes the
action Hessian strictly negative in a direction orthogonal to the entire
lowest axial Fourier eigenspace.

This is stronger than the earlier vanishing-curvature families.  Those
families showed that no positive field-independent curvature constant exists,
but their displayed Hessians remained positive.  The new family proves that
the orthogonal Hessian block itself is not globally positive semidefinite.
Consequently its inverse and the proposed Schur curvature are not globally
defined as positive covariance objects.

This remains a method obstruction.  It does not prove that the actual Gibbs
`H^-1` moment diverges.

## Exact period-four family

Let `L=4m`, use coordinates `psi=lambda*phi`, and put

\[
 k_x=\sum_{\mu=1}^4(-1)^{x_\mu},\qquad
 \psi_x=k_x\log(4/3).
\]

Define the period-four one-dimensional vector

\[
                 c=(1,0,-1,0)
\]

and the tensor-product direction

\[
                 v_x=\prod_{\mu=1}^4c(x_\mu).
\]

Both the center and direction have zero mean.  Flipping one coordinate changes
`k` by `-2*(-1)^x_mu`; every directed exponential weight is therefore exactly
`9/16` or `16/9`.

The calculation needs only the number of odd coordinates at a vertex.  On one
`4^4` cell, the residual classes are

| odd coordinates | vertices | residual |
|---:|---:|---:|
| 0 | 16 | `-7/2` |
| 1 | 64 | `-77/72` |
| 2 | 96 | `49/36` |
| 3 | 64 | `91/24` |
| 4 | 16 | `56/9` |

They give

\[
                    A=\frac{80458}{81}.
\]

For a direction `v`, write at each vertex

\[
 a_x=\sum_{y\sim x}w_{xy}(v_y-v_x),\qquad
 b_x=\sum_{y\sim x}w_{xy}(v_y-v_x)^2.
\]

Then

\[
                  \operatorname{Hess}A[v,v]
                  =\sum_x(a_x^2+r_xb_x).
\]

At the 16 all-even vertices, `a_x^2=81/4` and `b_x=9/2`, so their
total contribution is `72`.  At the 64 vertices with exactly one odd
coordinate, `a_x=0` and `b_x=32/9`, giving `-19712/81`.  Vertices with two
or more odd coordinates contribute zero.  Hence

\[
             \operatorname{Hess}A[v,v]
             =72-\frac{19712}{81}
             =-\frac{13880}{81}<0.
\]

The direction has norm squared `16`, is a negative-laplacian eigenvector with
eigenvalue `8`, and has free bilaplacian form `1024`.  Its nonlinear Hessian
Rayleigh quotient is `-1735/162`.

## Why this is the required orthogonal block

Every real lowest axial Fourier mode depends on only one coordinate.  The
inner product with `v` factorizes over the four coordinates and contains
three factors

\[
                  \sum_{j=0}^3c(j)=0.
\]

Thus `v` is orthogonal not just to one chosen lowest mode, but to all four
sine/cosine pairs spanning the eight-dimensional lowest axial eigenspace.
A negative quadratic form on this complement proves that the orthogonal
Hessian block is indefinite.

Repeating the period-four cell on `L=4m` multiplies the action, norm, and
Hessian by `m^4`.  Therefore

\[
 A_L=\frac{80458}{81}m^4,
 \qquad
 \operatorname{Hess}A_L[v,v]
 =-\frac{13880}{81}m^4.
\]

The sign obstruction persists on an unbounded volume sequence.  At
`lambda=2/5`, the two chain-rule factors cancel the `lambda^-2` in
`S_lambda(phi)=A(lambda*phi)/lambda^2`, so the same directional Hessian is
obtained in the `phi` variables.

## Consequence for the continuum programme

The affine virial theorem still proves a uniform actual Gibbs action-density
moment and its annealed half-action factor.  What fails is the proposed way of
turning that factor into covariance control: a globally positive orthogonal
block does not exist, so neither its positive inverse nor the associated
pointwise Schur complement is available everywhere.

The next live calculation is therefore the normalized low-frequency marginal
itself.  It should begin with one lowest axial coefficient and then pass to
dyadic Fourier shells.  A positive result must yield an actual, volume-uniform
`H^-1` second moment.  A negative result must exhibit a controlled volume
sequence for the normalized Gibbs expectation, not merely another bad
background.

The successor
`REVERSE_PHYSICS_BT_EUCLIDEAN_RESIDUAL_SPECTRAHEDRAL_PUSHFORWARD_V1`
now supplies exact normalized coordinates for this gate.  Positive fields
modulo scale are the positive ground states on the smooth boundary of
`{-Delta+diag(r)>=0}`, and the Gibbs measure becomes a Gaussian surface
weight divided by an explicit spanning-tree coarea Jacobian.  This exposes
the missing entropy factor but does not bound it; the lowest log-ground-state
Fourier marginal remains the live theorem.

## Boundaries

This certificate does not establish failure of every local, annealed, or
variational covariance method.  It does not establish divergence of the
actual interacting `H^-1` moment, absence of a continuum subsequence, a Born
rule, a Krein reconstruction, or anything `LORENTZIAN-CAUSAL`.

## Verification

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_orthogonal_hessian_block_obstruction.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_orthogonal_hessian_block_obstruction.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_orthogonal_hessian_block_obstruction
```
