# BT nearest-neighbour pair-block response at one loop

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`, `REDUCED-MODE`

Lifecycle: `COEFFICIENT_COMPUTED`

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_PAIR_BLOCK_RESPONSE_ONE_LOOP_V1`

## Result

The smallest genuine block repairs the long-wave sign that obstructs the
single-site response calculation, at the first nontrivial perturbative order.
For the full-Gibbs annealed nearest-neighbour pair response,

\[
 \beta^{\rm pair}_L(\lambda)
 =b^{\rm pair}_{2,L}\lambda^2+O_L(\lambda^4).
\]

On the periodic \(6^4\) lattice, exact rational conditional normalization,
background averaging, and momentum summation give

\[
 \boxed{
 b^{\rm pair}_{2,6}
 =\frac{956585197}{10069092633600}>0.
 }
\]

The sign persists in the infinite-volume coefficient. With

\[
 f(t)=e^{-2t}I_0(2t),\qquad
 W_4=\int_0^\infty f(t)^4dt,\qquad
 I_4=\int_0^\infty f(t)^2f'(t)^2dt,
\]

the exact reduction is

\[
 \boxed{
 b^{\rm pair}_{2,\infty}
 =-\frac{32629}{1517824}+\frac{W_4}{14}
  +\frac{39I_4}{1568}
 >\frac1{10000}>0.
 }
\]

This is a real change of research status: coefficientwise pair conditioning
survives the obstruction that killed coefficientwise single-site conditioning.
It is not yet a nonperturbative response theorem or the interacting
\(H^{-1}\) estimate.

## The pair update

Take \(B=\{o,o+e_\mu\}\), condition on the quotient background, and replace
the two block coordinates by their joint conditional mean. Average the eight
nearest-neighbour pairs containing each site and divide by eight, so each site
has total update rate one.

In the free bilaplacian theory the block precision and covariance are

\[
 K_{BB}=\begin{pmatrix}72&-16\\-16&72\end{pmatrix},\qquad
 K_{BB}^{-1}=
 \begin{pmatrix}9/616&1/308\\1/308&9/616\end{pmatrix}.
\]

The normalized free axial relaxation symbol is

\[
 \widehat R^{\rm pair}_0(k)
 =\frac{\omega(k)^2(44-\omega(k))}{2464}.
\]

Its low-momentum coefficient is \(44/2464=1/56\), improving the
single-site value \(1/72\).

## Conditional one-loop calculation

Scale \(\psi=\lambda\phi\). For the directed differences incident at a site,
put

\[
 A_x=\sum d,\qquad B_x=\sum d^2,\qquad C_x=\sum d^3.
\]

Then

\[
 S_\lambda=S_0+\lambda S_1+\lambda^2S_2+O(\lambda^3),
\]

with

\[
 S_1=\frac12\sum_xA_xB_x,
 \qquad
 S_2=\sum_x\left(\frac18B_x^2+\frac16A_xC_x\right).
\]

Only the sixteen residual sites in the pair and its one-edge neighbourhood
depend on the two internal fields. Subtracting the background-only value
leaves a 314-term cubic interaction \(U_1\) and a 701-term quartic
interaction \(U_2\).

Write the free block field as its conditional center plus a two-component
innovation \(u\). The second conditional-center coefficient is

\[
 m_{2,a}
 =\frac12\mathbb E_u[u_aU_1^2]-\mathbb E_u[u_aU_2]
  -\mathbb E_u[u_aU_1]\mathbb E_u[U_1].
\]

Differentiating the product in the last term requires two independent
innovations sharing the same external Gaussian background. Retaining this
replica subtraction is essential: it is the pair analogue of retaining the
conditional normalizer. The order-\(\lambda\) marginal reweighting vanishes
by Gaussian integration by parts, translation invariance, and constant-shift
invariance, exactly as in the certified single-site calculation.

The same subtraction makes the Green reduction genuinely affine rather than
an ansatz. Written as

\[
 \frac12\kappa(u_a,U_1,U_1)-\operatorname{Cov}(u_a,U_2),
\]

the cubic-square term must contain one innovation contraction from the
external \(u_a\) and another connecting the two \(U_1\) vertices. After the
response derivative, at most two external-background legs remain. Their
Gaussian average therefore contains at most one Green covariance; no hidden
quadratic Green kernel has been discarded.

For a response row, the coefficient of the axial \(\omega\) term is half its
second spatial moment. A quarter of pair orientations are parallel to the
external axis and three quarters are transverse, so

\[
 b^{\rm pair}_{2,L}
 =\frac12\left(\frac14M_{\parallel,L}
                   +\frac34M_{\perp,L}\right).
\]

The producer derives the resulting 202-term Green kernel from the action
jets. Its coefficients sum to zero, making the answer independent of the
additive Green-function gauge.

## Why annealing is load-bearing

At the all-zero external background, the two exact second-moment
coefficients are

\[
 M^{\rm vac}_{\parallel,2}=-\frac{7349}{379456},\qquad
 M^{\rm vac}_{\perp,2}=-\frac{7979}{379456}.
\]

Thus

\[
 b^{\rm pair,vac}_2=-\frac{15643}{1517824}<0.
\]

The pair's internal edge alone does not repair the sign. The reversal to the
positive \(6^4\) and infinite-volume values comes from fluctuations of the
actual free background together with conditional normalization. This is why
a uniform-background or unnormalized block calculation would give the wrong
research decision.

## All-volume numerator

Let

\[
 x_\mu=2(1-\cos k_\mu),\qquad e_1=\sum_\mu x_\mu=\omega(k),
 \qquad e_2=\sum_{\mu<\nu}x_\mu x_\nu.
\]

Exact Laurent, sign-orbit, hypercubic, and Chebyshev reduction gives

\[
 b^{\rm pair}_{2,L}=\frac{12493}{1517824}
 +\frac1{L^4}\sum_{k\ne0}\frac{Q(x(k))}{\omega(k)^2},
\]

where

\[
\begin{aligned}
Q={}&\frac3{56}e_1-\frac{39}{1568}e_1^2+\frac1{112}e_2
 -\frac{97}{137984}e_1^3+\frac{572}{137984}e_1e_2\\
&+\frac{51}{551936}e_1^4-\frac{126}{551936}e_1^2e_2
 -\frac1{551936}e_1^5+\frac2{551936}e_1^3e_2.
\end{aligned}
\]

The expanded polynomial has 125 monomials. The exact \(6^4\) sum gives the
boxed positive rational value above. Binary64 orientation checks, which are
diagnostics only, give

| \(L\) | \(b^{\rm pair}_{2,L}\) |
|---:|---:|
| 5 | \(9.1384\times10^{-6}\) |
| 6 | \(9.5002\times10^{-5}\) |
| 8 | \(1.7940\times10^{-4}\) |
| 12 | \(2.4127\times10^{-4}\) |
| 16 | \(2.6350\times10^{-4}\) |
| 24 | \(2.7959\times10^{-4}\) |
| 32 | \(2.8526\times10^{-4}\) |

## Exact positive infinite-volume bound

Brillouin-zone integration by parts and the Bessel representation give

\[
 \int\frac{e_2}{\omega^2}=2W_4,
 \qquad
 \int\frac{e_2}{\omega}=6I_4.
\]

The remaining polynomial moments are

\[
 \int\omega=8,\quad \int\omega^2=72,\quad
 \int\omega^3=704,\quad \int e_2=24,\quad
 \int\omega e_2=240.
\]

Substitution produces the displayed large-volume formula. Both \(W_4\) and
\(I_4\) have lower bounds from positive walk expansions. For \(N=100\), take
the first 101 return terms for \(W_4\). Using

\[
 I_4=1-4\bigl(G(0)-G(e_1+e_2)\bigr),
\]

take the first 101 potential-kernel terms and bound the omitted positive tail
by the return tail

\[
 \frac{121}{784N}.
\]

The exact rational substitution is strictly greater than \(1/10000\). No
floating-point value enters this sign decision.

## Meaning and next gate

In ordinary language, updating one site at a time creates a small wrong-way
long-distance effect. Updating the smallest connected pair lets its internal
edge and the surrounding fluctuations cancel that defect. The cancellation
is strong enough to leave a rigorously positive margin even on an infinite
lattice, at one loop.

That breaks a proof-method barrier, not the continuum barrier itself. The
remainder \(O_L(\lambda^4)\) has not been bounded uniformly, and nothing here
fixes the sign at the programme's \(\lambda=2/5\). The next calculation is the
complete order-\(\lambda^4\) pair coefficient and its large-volume
power/logarithm. In parallel, a nonperturbative pair-fiber response inequality
could bypass the series. A response-to-Witten Schur bridge and all dyadic
Fourier shells are still required before the actual interacting \(H^{-1}\)
estimate is proved.

This result does not establish a fixed-coupling pair response, perturbative
convergence, heat-bath gap, global Poincare or Witten theorem, normalized
lowest-mode bound, interacting \(H^{-1}\) bound, tightness, continuum
identification, restored ordinary OS positivity, new physical dimension,
Born rule, Krein reconstruction, or anything `LORENTZIAN-CAUSAL`.

Paper 21 is not changed because no reconstruction or continuum lifecycle
state is promoted.

## Verification

Run sequentially under the memory ceiling:

```text
ulimit -v 500000; python3 reverse_physics/bt_euclidean_pair_block_response_one_loop.py --check
ulimit -v 500000; mise x python@3.12 -- python3 reverse_physics/verify_bt_euclidean_pair_block_response_one_loop.py
ulimit -v 500000; mise x python@3.12 -- python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_pair_block_response_one_loop
```

The final producer passed 22/22 checks in 14.35 seconds at 168,368 KiB peak
RSS. The nonimporting verifier passed 17/17 checks in 14.94 seconds at
159,352 KiB. All 15 focused and mutation tests passed in 34.05 seconds at
300,528 KiB. The planning import folded 1,699 nodes with zero invalid items
and zero malformed events in 6.58 seconds at 201,440 KiB.

Three exploratory commands are not counted as passes: the default Python
lacked SymPy, and two inline derivation scripts contained syntax errors and
stopped before calculation. Each was corrected and replayed from the start.
The Science Forge shadow rail was not rerun because no registered shadow input
changed; that skip is not a pass. Tier 3 is not triggered because no actual
\(H^{-1}\), continuum, freeze, release, shared-core, or Lorentzian lifecycle
state is promoted.
