# Generic-background ghost (n=3) pole-three relative IBP

> **Superseded frontier note.** The derivative and punctured-corner carriers
> isolated here have now been integrated exactly in
> [`generic-background-ghost-n3-pole3-integrated-functions.md`](generic-background-ghost-n3-pole3-integrated-functions.md).
> In the canonical primitives the only nonzero corner has equal angular
> weights, so its integrated contribution is rational; the two bubble-log
> ratios arise from the scalar-triangle derivative equations. The pole-four
> `I29` row remains open.

## Scope

This is an `EUCLIDEAN-SPECTRAL` result for the ten generic nonexceptional-
momentum ghost-triangle channels whose barycentric numerators contain one
exact factor of

\[
\Delta=\alpha_0\alpha_1x_1+\alpha_1\alpha_2x_2
       +\alpha_2\alpha_0x_3.
\]

It does not include the remaining pole-four (I_{29}) row.

## Exact reduction

In affine coordinates (A=\alpha_1), (B=\alpha_2),
(C=1-A-B), use

\[
 P=A(CU+BW),\qquad Q=B(CV-AW),
\]

with (U,V,W) of affine degree at most four.  This parameterization makes
the normal component vanish on all three open simplex edges.  The exact
polynomial identity is

\[
 N=\Delta(\partial_AP+\partial_BQ)
 -2(P\partial_A\Delta+Q\partial_B\Delta)
 +c_J\Delta^2+c_1AC\Delta+c_2AB\Delta.
\]

After division by (\Delta^3) and relative integration by parts, every one
of the ten rows is therefore reduced to

\[
 J_\triangle=\int_\triangle\frac1\Delta,
 \qquad
 M_{x_1}=\int_\triangle\frac{AC}{\Delta^2}
          =-\partial_{x_1}J_\triangle,
 \qquad
 M_{x_2}=\int_\triangle\frac{AB}{\Delta^2}
          =-\partial_{x_2}J_\triangle.
\]

The coefficients are exact rational functions of (x_1,x_2,x_3).  Four
stored primitives—(I_{10,123}), (I_{24,123}), (I_{25,123}), and
(I_{28,123})—generate the other six orientations by exact barycentric and
kinematic permutations.

The exact rank ledger is

| space | rank |
| --- | ---: |
| affine polynomials of degree at most seven | 36 |
| open-edge tangent IBP image | 27 |
| tangent image plus the three masters | 30 |
| tangent image plus masters and all ten targets | 30 |

Thus the ten targets add no direction beyond the scalar triangle and its two
independent first kinematic derivatives.

## Corner-flux theorem

Open-edge tangency does not imply vanishing flux through punctured corners.
Imposing the six vertex conditions

\[
 U_A=W_A=0,\qquad V_B=W_B=0,\qquad U_C=V_C=0
\]

reduces the tangent-plus-master rank to (26).  Each of the four orbit
representatives raises it to (27); exact permutation covers all ten rows.
The certificate stores a normalized rational dual witness for every orbit
representative at the rank-stable fixture
((x_1,x_2,x_3)=(2,3,5)):

\[
 \lambda(B_{\rm corner-zero})=0,
 \qquad \lambda(N)=1.
\]

The generic base rank and fixture base rank are both (26).  Hence the
normalized nonzero augmented minor at the fixture proves generic
non-membership in the declared corner-zero ansatz; this is not merely a
numerical rank guess.  A punctured-corner flux is unavoidable in this
primitive ansatz; this certificate alone does not determine whether the
integrated flux is logarithmic or rational.

At the time of this reduction the three local angular carriers had been
isolated exactly but not integrated.  The successor certificate shows their
equal-weight sum is rational, while the two independent bubble-log ratios
instead enter through the scalar-triangle differential equations.  This is
consistent with the standard scalar-triangle architecture in which triangle
derivatives couple to lower-topology bubble descendants; see Kol and Mazumdar,
[arXiv:1909.04055](https://arxiv.org/abs/1909.04055).

## Claim boundary

This certificate does **not** compute:

- the corner-log coefficients in a chosen bubble basis;
- the pole-four (I_{29}) reduction;
- all eleven fully integrated generic ghost functions;
- the generic physical fourth-order Hessian;
- the complete renormalized \(\Gamma_1\) or \(Q_1\);
- residual transfer or any Lorentzian/Hadamard/particle statement.

## Receipts and test tiers

The fast independent verifier uses two exact rational kinematic fixtures,
replays the four primitive identities, all ten permutation orbits, the
rank-stable normalized corner duals, dependency hashes, schema, digest and
claim boundary.  It is the Tier-1 commit rail.

The producer performs the full rational-function quotient solve and emits
the megabyte-scale exact certificate.  Its measured runtime is approximately
73 seconds and it is deliberately retained as the Tier-2 exhaustive command
rather than duplicated inside every unit test.  A separate fully symbolic
independent replay of every representative and permutation orbit passes in
approximately 154 seconds; it is a certificate-freeze rail, not a commit-loop
test.

```text
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.generic_background_ghost_n3_pole3_relative_ibp --check
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_generic_background_ghost_n3_pole3_relative_ibp
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_generic_background_ghost_n3_pole3_relative_ibp --exhaustive
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/spectral/euclidean/tests/test_generic_background_ghost_n3_pole3_relative_ibp.py
```

Primary artifact:

```text
quantum-weyl/spectral/euclidean/certificates/
GENERIC_BACKGROUND_GHOST_N3_POLE3_RELATIVE_IBP.json
```
