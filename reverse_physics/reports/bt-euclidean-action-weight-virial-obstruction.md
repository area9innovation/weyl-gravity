# BT action-weight threshold and radial-virial obstruction

**Date:** 2026-08-14

**Certificate:** `REVERSE_PHYSICS_BT_EUCLIDEAN_ACTION_WEIGHT_VIRIAL_OBSTRUCTION_V1`

**Dependencies:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

**Lifecycle:** `OBSTRUCTION_PROVED`

## Result

The quarter-power action weight suggested by the first lowest-mode Schur
family is not a global candidate. A second exact family makes the full
lowest-mode Schur curvature decay faster relative to its action: every
pointwise weight exponent below one half fails. The half-action weight is the
first exponent not obstructed by this family.

The obvious companion estimate for integrating that weight also fails. An
exact rational background has radial derivative

\[
 D(\psi)=\psi\mathbin\cdot\nabla A(\psi)<2A(\psi).
\]

Thus the coefficient-two virial shortcut to a uniform mean action-density
bound is unavailable. Neither obstruction disproves the interacting
\(H^{-1}\) estimate. They replace the next gate by a volume-normalized
half-action-density inequality together with either a weaker positive virial
constant or a direct annealed moment estimate.

## A complete mean-zero symmetry block

Work in the spatially constant sector of the \(6^4\) lattice. Set

\[
 k(a)=a(-2,1,1,-2,1,1),\qquad x=2^{3a},\qquad a\geq1.
\]

Use

\[
 h=(2,1,-1,-2,-1,1),\qquad
 u=(0,1,1,0,-1,-1),\qquad
 g=(1,-1,1,-1,1,-1).
\]

Here \(h,u\) span the lowest time-circle eigenspace and \(g\) is the
alternating mode. Together with

\[
 p=(1,0,-1,1,0,-1),\qquad
 m=(1,-1,0,1,-1,0),
\]

they form a basis of the five-dimensional mean-zero sector; the exact Gram
determinant is \(3456\).

The center is invariant under shift by three and reflection \(i\mapsto-i\).
The mode \(h\) is shift-odd and reflection-even. Among the complete basis,
only \(g\) has the same two symmetry characters. Consequently every other
mixed Hessian entry with \(h\) vanishes, and the two-mode \((h,g)\) Schur
complement is the full effective curvature of this chosen lowest mode.

## Exact Schur asymptotic

Per spatial site, direct differentiation gives

\[
\begin{aligned}
 H_{hh}&=16x^2-8x-4x^{-1}+8x^{-2},\\
 H_{hg}&=32x^2-16x-32x^{-1}+16x^{-2},\\
 H_{gg}&=64x^2-32x+32x^{-1}+32x^{-2},
\end{aligned}
\]

and

\[
 \det H=1152\left(2x-1-x^{-2}+x^{-3}\right).
\]

Therefore

\[
 \kappa(x)=H_{hh}-\frac{H_{hg}^2}{H_{gg}}
           =\frac{\det H}{H_{gg}}
\]

satisfies

\[
 0<\kappa(x)<\frac{48}{x}\quad(x\geq8),\qquad
 \lim_{x\to\infty}x\kappa(x)=36.
\]

Direct enumeration of selected fixtures on all \(6^4\) sites independently
reconstructs the common spatial factor \(216\) and the vanishing mixed
entries.

## The half-action threshold

At the same center, the action per spatial site is

\[
 A(x)=4x^2-8x+6-4x^{-1}+2x^{-2}.
\]

For any fixed real weight exponent \(p\),

\[
 \kappa(x)A(x)^p\sim36\,4^p x^{2p-1}.
\]

It follows that

\[
 \lim_{x\to\infty}\kappa(x)A(x)^{1/4}=0,
\]

and, more generally, every \(p<1/2\) is obstructed. At the threshold,

\[
 \lim_{x\to\infty}\kappa(x)A(x)^{1/2}=72.
\]

This does not invalidate the predecessor certificate: its exact family and
its limit \(18\) remain correct. It invalidates only the inference that the
quarter power was a viable global exponent.

For the full lattice, \(A_{\rm total}/N=A(x)/6\), the free curvature in the
declared mode is \(12\) per spatial site, and

\[
 C(x)=\frac{\kappa(x)}{12}\sqrt{1+\frac{A(x)}6},
 \qquad \lim_{x\to\infty}C(x)^2=6.
\]

The scale-compatible candidate is therefore

\[
 \frac{\kappa_h(\psi)}{\kappa_h(0)}
 \sqrt{1+\frac{A(\psi)}N}\geq c>0,
\]

uniformly in volume. This family does not obstruct it, but no global theorem
is claimed. Action density matters because a half weight in total action
typically contributes \(\sqrt N\) after Gibbs averaging and therefore does
not directly give a volume-uniform covariance estimate.

## Exact failure of the coefficient-two virial shortcut

Take

\[
 k=(-1,-1,0,0,2,0),\qquad \psi=k\log(101/100).
\]

All exponentials are rational. Exact arithmetic gives

\[
 A=\frac{12274143260801}{10406040100000000},\qquad
 T=\frac{614597925020801}{2601510025000000},
\]

where \(D=(\log(101/100))T\). For \(u=1/100\), the alternating Taylor bound

\[
 \log(1+u)<u-\frac{u^2}{2}+\frac{u^3}{3}
\]

gives the completely rational certificate

\[
 \frac DA
 <\frac{18346362659795930651}{9205607445600750000}
 <2.
\]

Spatial replication multiplies both \(D\) and \(A\) by \(216\), so this is a
full \(6^4\) obstruction as well. It rules out only the constant two. A
universal inequality \(D\geq cA\) for some explicit \(0<c<2\) remains open
and would still be enough for a uniform action-density moment via Gibbs
integration by parts.

## Continuum disposition

The first volume-uniform interacting estimate is still open. The next exact
calculation is now sharply formulated:

1. prove or obstruct positivity of the orthogonal Hessian block needed to
   define the lowest-mode Schur complement globally;
2. prove or obstruct the normalized half-action-density curvature bound;
3. prove or obstruct a weaker positive radial virial constant;
4. if both pointwise routes fail, estimate the normalized low-mode marginal
   or the action density directly under the Gibbs measure.

No result here establishes tightness, a continuum Euclidean measure, a Born
rule, Krein reconstruction, analytic continuation, or anything
`LORENTZIAN-CAUSAL`.

## Verification

Run sequentially under the repository memory ceiling:

```text
python3 reverse_physics/bt_euclidean_action_weight_virial_obstruction.py --check
python3 reverse_physics/verify_bt_euclidean_action_weight_virial_obstruction.py
python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_action_weight_virial_obstruction
```
