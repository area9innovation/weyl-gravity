# BT centered conditional-fiber domination obstruction

**Certificate:**
`REVERSE_PHYSICS_BT_EUCLIDEAN_CENTERED_FIBER_DOMINATION_OBSTRUCTION_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

**Lifecycle:** `OBSTRUCTION_PROVED`

## Result

A lowest-mode conditional fiber cannot be controlled pointwise by comparing
every orthogonal background with its value at mode coordinate zero. On the
fixed periodic (6^4) lattice, an exact family of backgrounds
(eta_n\perp h) and shifts (t_n) satisfies

\[
 \frac{A(\eta_n+t_nh)}{A(\eta_n)}
 \leq \frac{9}{4\,4^n}\longrightarrow0,
 \qquad |t_n|=n\log2\longrightarrow\infty.
\]

Consequently no constants (c>0) and finite (C) can give

\[
                 A(\eta+t h)\geq cA(\eta)-C
\]

for every centered orthogonal fiber. The corresponding pointwise centered
Boltzmann ratio is unbounded.

This does not decide the integrated marginal. A half-period lattice
translation proves exactly that the full marginal is even. The next live
route is therefore annealed or background-recentered control, not a pointwise
comparison with (t=0).

## Fixed-volume family

Use a field constant on the three spatial directions of the (6^4) lattice.
The six spatial neighbor weights are then one and cancel six units of the
degree-eight subtraction. At each of the (216) spatial sites the action is
the degree-two time-cycle action

\[
 A(k;x)=\frac12\sum_{j=0}^5
 \left(x^{k_{j-1}-k_j}+x^{k_{j+1}-k_j}-2\right)^2,
 \qquad x=2^n.
\]

Choose

\[
 h=(2,1,-1,-2,-1,1),
 \qquad
 a=(-1,-1,1,-3,3,1).
\]

Both vectors have zero mean, (a\cdot h=0),
(\lVert h\rVert^2=12), and

\[
                         (-\Delta_6)h=h.
\]

Set

\[
 \eta_n=n\log2\,a,
 \qquad t_n=-n\log2.
\]

The shifted coefficient vector is

\[
                    a-h=(-3,-2,2,-1,4,0).
\]

The construction remains inside the mean-zero carrier, and the background is
orthogonal to the selected lowest mode for every (n).

## Exact Laurent actions

The background action per spatial site is

\[
\begin{aligned}
 A_a(x)={}&\tfrac12x^{12}+x^{10}+\tfrac12x^8-2x^6
 -\tfrac12x^4-4x^2+10-6x^{-2}\\
 &-\tfrac12x^{-4}-x^{-6}+\tfrac32x^{-8}+\tfrac12x^{-12}.
\end{aligned}
\]

The shifted action is

\[
\begin{aligned}
 A_{a-h}(x)={}&\tfrac12x^{10}+2x^8+x^6-2x^5-3x^4-3x^3
 +\tfrac12x^2-x+12-2x^{-1}\\
 &+\tfrac12x^{-2}-4x^{-3}-4x^{-4}-2x^{-5}+x^{-6}
 +x^{-7}+x^{-8}+x^{-9}+\tfrac12x^{-10}.
\end{aligned}
\]

These are exact Laurent polynomials generated from all six residual rows, not
asymptotic numerical fits.

## All-(n) comparison

One background residual is

\[
                         x^6+x^4-2\geq x^6
                         \qquad(x\geq2),
\]

so

\[
                          A_a(x)\geq\frac12x^{12}.
\]

The six shifted residuals obey

\[
\begin{array}{lll}
 |x^3+x-2|\leq\frac54x^3,&
 |x^4-2+x^{-1}|\leq x^4,&
 |-2+x^{-3}+x^{-4}|\leq2,\\
 |x^5+x^3-2|\leq\frac54x^5,&
 |-2+x^{-4}+x^{-5}|\leq2,&
 |x^4-2+x^{-3}|\leq x^4.
\end{array}
\]

Therefore

\[
 A_{a-h}(x)
 \leq\frac{25}{32}x^6+x^8+\frac{25}{32}x^{10}+4.
\]

For (x\geq2), division by (x^{10}) gives the exact coefficient

\[
 \frac{25}{512}+\frac14+\frac{25}{32}+\frac1{256}
 =\frac{555}{512}<\frac98.
\]

It follows that

\[
 A_{a-h}(x)\leq\frac98x^{10},
 \qquad
 \frac{A_{a-h}(x)}{A_a(x)}\leq\frac9{4x^2}.
\]

Multiplication by the spatial factor (216) leaves the ratio unchanged.
Because the two leading powers differ, the family also rules out every fixed
relative bound (A(\eta+t h)\geq cA(\eta)-C) with (c>0).

## Exact (n=1) fixture

At (x=2), per spatial site,

\[
 A_a=\frac{25038513}{8192},
 \qquad
 A_{a-h}=\frac{1970877}{2048},
 \qquad
 \frac{A_{a-h}}{A_a}=\frac{2627836}{8346171}.
\]

The action gap is (17155005/8192>0). The independent verifier enumerates
all (6^4=1296) sites and all eight neighbors, reproducing the factor (216)
without using the producer's spatial reduction.

## What survives after the obstruction

Translation by three time sites preserves the lattice action, the mean-zero
hyperplane, Lebesgue measure, and the subspace orthogonal to (h). It sends
(h) to (-h). Hence

\[
 m_h(t)=Z^{-1}\int_{\eta\perp h}
             e^{-A(\eta+t h)/\lambda^2}\,d\eta
       =m_h(-t).
\]

Thus the normalized first moment vanishes. Evenness does not bound the second
moment and does not imply (m_h(t)\leq m_h(0)). The exact bad backgrounds are
also assigned very small Gibbs weight at their centered values, so their
existence does not establish divergence of the integrated marginal.

The useful conclusion is methodological but exact: a successful theorem must
pair, recenter, or average the background-dependent fiber minima. The already
certified uniform expectation of the action density is available for such an
annealed estimate.

## Foundations consequence

The vectors, Laurent coefficients, rational fixture, all-(n) comparison, and
translation symmetry are finite exact algebra. Interpreting translation as a
change of variables in the fiber integral is finite-dimensional analysis. A
volume-uniform marginal or (H^{-1}) estimate remains an unsupplied analytic
layer. No weakest-base reversal is claimed.

## Boundaries

This certificate does not establish divergence of the normalized lowest-mode
second moment, failure of every conditional-fiber or transport method,
failure of the interacting (H^{-1}) estimate, tightness, a continuum
Euclidean measure, a broader reflection-positivity theorem, a Born rule, a
Krein reconstruction, or anything `LORENTZIAN-CAUSAL`.

## Verification

Run sequentially:

```text
ulimit -v 500000; python3 reverse_physics/bt_euclidean_centered_fiber_domination_obstruction.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_centered_fiber_domination_obstruction.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_centered_fiber_domination_obstruction
```
