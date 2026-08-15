# BT separable-product gradient coercivity

**Certificate:**
`REVERSE_PHYSICS_BT_EUCLIDEAN_SEPARABLE_PRODUCT_GRADIENT_COERCIVITY_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`,
`REDUCED-MODE`

## Result

Every coordinate-separable positive continuum field retains the sharp free
BT Euler-gradient coefficient. On a flat periodic \(d\)-torus of common side
length \(\ell\), let

\[
 \psi(x_1,\ldots,x_d)=\sum_{i=1}^d\psi_i(x_i),
 \qquad \Omega=\prod_i e^{\psi_i},
 \qquad k_1={2\pi\over\ell}.
\]

For

\[
 R=\Delta\psi+|\nabla\psi|^2,
 \qquad
 E=\Delta R-2\operatorname{div}(R\nabla\psi),
\]

the exact theorem is

\[
                         \boxed{\|E\|_2^2\geq k_1^4\|R\|_2^2.}
\]

The constant is independent of the number of active coordinate profiles and
is sharp in the weak lowest-mode limit. Thus coherent ramps, walls, or other
large-amplitude paths assembled as a sum of independent one-coordinate
profiles cannot collapse the normalized Euler-gradient quotient.

This extends the earlier purely axial theorem. It remains a continuum
`REDUCED-MODE` result, not the all-field lattice or interacting \(H^{-1}\)
theorem.

## Product-space decomposition

Use normalized circle averages and put

\[
 u_i=\psi_i',\qquad R_i=u_i'+u_i^2,
 \qquad Z_i=\langle u_i^2\rangle,
 \qquad \widetilde R_i=R_i-Z_i.
\]

Then

\[
 R=\sum_iR_i,
 \qquad
\|R\|_2^2=\sum_i\|\widetilde R_i\|_2^2+\left(\sum_iZ_i\right)^2.
\]

Define

\[
 j_i=u_i''-2u_i^3,
 \qquad A_i=\sum_{j\ne i}Z_j.
\]

Direct expansion of the multidimensional Euler field gives the orthogonal
ANOVA decomposition

\[
 E=\sum_iF_i+\sum_{i<j}P_{ij},
\]

where

\[
 F_i=(j_i-2A_i u_i)',
 \qquad
 P_{ij}=-2\left(u_i'\widetilde R_j+u_j'\widetilde R_i\right).
\]

Each \(F_i\) belongs to the mean-zero one-coordinate sector, and each
\(P_{ij}\) belongs to a mean-zero two-coordinate sector. Distinct sectors are
orthogonal. In particular,

\[
 \|E\|_2^2\geq\sum_i\|F_i\|_2^2.
\]

The two-body transverse terms cannot cancel the one-body coercive part.

## One-body coercivity and the mean term

Put

\[
 X_i=\langle(u_i')^2\rangle,
 \qquad Y_i=\langle u_i^4\rangle.
\]

Since every periodic derivative \(u_i\) has mean zero,

\[
 -\langle j_i-2A_i u_i,u_i\rangle
 =X_i+2Y_i+2A_iZ_i=:Q_i.
\]

Poincare and Cauchy--Schwarz imply

\[
 \|F_i\|_2^2\geq k_1^2{Q_i^2\over Z_i},
\]

with zero profiles omitted. The familiar inequalities

\[
 X_i\geq k_1^2Z_i,
 \qquad (X_i+2Y_i)^2\geq X_i(X_i+Y_i)
\]

control the fluctuation part of \(R\).

It remains to control the square of the total residual mean. Rescale to
\(k_1=1\), write

\[
 X_i=Z_i+x_i,\qquad Y_i=Z_i^2+y_i,
 \qquad x_i,y_i\geq0,
\]

and put \(S=\sum Z_i\), \(X=\sum x_i\), \(Y=\sum y_i\). Then

\[
 \sum_iQ_i=S+2S^2+X+2Y.
\]

Cauchy--Schwarz across the coordinate index gives

\[
 \sum_i{Q_i^2\over Z_i}
 \geq{(S+2S^2+X+2Y)^2\over S}
 \geq S+S^2+X+Y.
\]

The last expression is exactly \(\|R\|_2^2\). Restoring scale gives the
boxed theorem.

## Exact two-profile fixture

On the \(2\pi\)-periodic four-torus take

\[
 u_1(x)=\sin x,\qquad u_2(y)=2\sin y,
 \qquad u_3=u_4=0.
\]

Exact normalized trigonometric moments give

\[
 \|R\|_2^2={87\over8}.
\]

The two one-body Euler norms are \(89/4\) and \(200\), while the two-body
sector has norm \(21\). Hence

\[
 \|E\|_2^2={973\over4},
 \qquad
 \|E\|_2^2-\|R\|_2^2={1859\over8}>0.
\]

The independent verifier reconstructs \(R\), \(E\), and all three
orthogonal pieces using exact two-variable Laurent--Fourier arithmetic rather
than the producer's moment formulas.

## Meaning for the remaining barrier

The preceding actual-Gibbs edge theorem showed that isolated enormous jumps
are locally rare. This theorem now rules out coherent accumulation when that
accumulation factorizes by coordinate. A genuine deterministic collapse must
therefore use irreducible mixed-coordinate structure—the same transverse
sector already identified by the weighted-current analysis.

The next analytic target is the first three-coordinate ANOVA component or a
nonseparable periodic family with controlled full-Witten Rayleigh quotient.
Deterministic coercivity alone still does not control the normalized Gibbs
cross-section entropy.

## Boundaries

This result does not establish a theorem for arbitrary nonseparable fields,
the all-field lattice gradient constant, background-marginal current
hyperuniformity, a Poincare inequality, Witten coercivity, an interacting
\(H^{-1}\) bound, a continuum measure, a Born rule, Krein reconstruction, or
anything `LORENTZIAN-CAUSAL`.

## Verification

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_separable_product_gradient_coercivity.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_separable_product_gradient_coercivity.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_separable_product_gradient_coercivity
```
