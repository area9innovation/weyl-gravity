# BT annealed signed-response one-loop coefficient

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`, `REDUCED-MODE`

Lifecycle: `COEFFICIENT_COMPUTED`

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_ANNEALED_RESPONSE_ONE_LOOP_V1`

## Result

Actual Gibbs averaging repairs most of the wrong-sign vacuum response, but
not all of it at the first nontrivial order.  If

\[
 \widehat R_L(pe_1)
 =\beta_L(\lambda)\omega(p)-a_L(\lambda)\omega(p)^2,
\]

then the full conditional normalization and background marginal give

\[
 \beta_L(\lambda)=b_{2,L}\lambda^2+O_L(\lambda^4).
\]

On the periodic \(6^4\) lattice the coefficient is exactly

\[
 \boxed{
 b_{2,6}=-\frac{849547889}{1849425177600}<0.
 }
\]

Consequently \(\beta_6(\lambda)<0\) for every sufficiently small nonzero
coupling.  This refutes the hoped-for statement that full-Gibbs annealing
makes \(\beta_L\) nonnegative at every finite volume.  It does not imply a
negative heat-bath spectral gap: at a fixed lattice the positive
\(\omega^2\) term can still dominate every available nonzero momentum.

The calculation also gives an exact formula for every nondegenerate
hypercubic volume \(L\geq5\).  Its large-volume sign is reduced to two
positive one-dimensional Bessel moments but is not yet certified.

## Correct distance-two path coefficient

For an axial endpoint \(y=o+2e\) with intermediate site \(v=o+e\), the
fiber-dependent Hessian path weight is

\[
 t_{v,o}t_{v,y}=e^{z+\psi_y-2\psi_v}.
\]

The factor \(e^z\) must remain inside the conditional covariance.  Thus

\[
 D_yM_o
 =-\frac{e^{\psi_y-2\psi_v}}{\lambda^2}
   \operatorname{Cov}_{q_\xi}(z,e^z)<0.
\]

For a mixed endpoint, the same formula is summed over its two intermediate
sites.  This corrects the displayed prefactor in the predecessor while
preserving its strict sign, range-two support, vacuum formula, and symmetry
reduction.

## Conditional perturbation with the marginal retained

Scale \(\psi=\lambda\phi\).  For an edge difference \(d\), write the
residual jet at a site as

\[
 r=\lambda A+\frac{\lambda^2}{2}B
   +\frac{\lambda^3}{6}C+O(\lambda^4),
 \qquad
 A=\sum d,\quad B=\sum d^2,\quad C=\sum d^3.
\]

The action becomes

\[
 S_\lambda=S_0+\lambda S_1+\lambda^2S_2+O(\lambda^3),
\]

with

\[
 S_1=\frac12\sum A B,
 \qquad
 S_2=\sum\left(\frac18B^2+\frac16AC\right).
\]

At the chosen site, put \(\phi_o=m_0(\eta)+u\).  The free innovation \(u\)
is independent of the off-site background and is Gaussian with variance
\(1/72\).  Expanding the normalized conditional mean gives

\[
 m_1=-\mathbb E_u[uS_1],
\]

and

\[
 m_2=rac12\mathbb E_u[uS_1^2]-\mathbb E_u[uS_2]
     -\mathbb E_u[uS_1]\mathbb E_u[S_1].
\]

The background density also changes at order \(\lambda\).  Its apparent
contribution to the order-\(\lambda^2\) response is zero rather than being
discarded: \(D m_1\) is linear, and Gaussian integration by parts gives

\[
 \mathbb E_0[(D m_1)S_1]
 =\sum_{ij}\ell_j C_{ji}\,
   \mathbb E_0[\partial_iS_1]=0.
\]

Translation invariance makes the last expected derivative independent of
the site, while constant-shift invariance makes its sum over sites zero.
This is the precise reason the full marginal can be retained without a
global polynomial expansion.

The symmetry
\(S_{-\lambda}(\phi)=S_\lambda(-\phi)\) makes \(\beta_L\) even in
\(\lambda\), so the remainder after \(b_{2,L}\lambda^2\) is
\(O_L(\lambda^4)\).

## Exact one-loop Fourier numerator

Let

\[
 x_\mu=2(1-\cos k_\mu),\qquad
 e_1=\sum_\mu x_\mu=\omega(k),\qquad
 e_2=\sum_{\mu<\nu}x_\mu x_\nu.
\]

The sparse conditional jet, centered Gaussian moments, and hypercubic
symmetrization reduce the whole coefficient to

\[
\begin{aligned}
 P(x)={}&\frac{e_1}{24}-\frac{5e_1^2}{288}+\frac{e_2}{144}
 +\frac{5e_1^3}{1296}+\frac{5e_1e_2}{1728}\\
 &-\frac{5e_1^4}{31104}-\frac{13e_1^2e_2}{31104}.
\end{aligned}
\]

For every nondegenerate periodic \(L^4\) lattice,

\[
 \boxed{
 b_{2,L}=-\frac{43}{5184}
 +\frac1{L^4}\sum_{k\ne0}\frac{P(x(k))}{\omega(k)^2}.
 }
\]

The first term is exactly the negative uniform-background coefficient.  The
sum is the annealed free-background correction.  At \(L=6\), every
one-axis value of \(x\) belongs to \(\{0,1,3,4,3,1\}\); the complete sum is
therefore rational and gives the boxed negative fraction above.

The producer does not assume this polynomial.  It constructs the forty-term
free conditional center, retains only the five conditional-jet components
that survive the Gaussian fiber, forms a 161-term covariance kernel, and
then performs exact Laurent, sign-orbit, hypercubic, Chebyshev, and
\(x_\mu=2(1-\cos k_\mu)\) reductions.  The resulting 69-monomial polynomial
is compared with the compact elementary-symmetric expression.

## Volume diagnostic and large-volume reduction

Direct binary64 evaluation of the exact formula gives:

| \(L\) | \(b_{2,L}\) |
|---:|---:|
| 5 | \(-5.2716058\times10^{-4}\) |
| 6 | \(-4.5935780\times10^{-4}\) |
| 8 | \(-3.9286792\times10^{-4}\) |
| 12 | \(-3.4438540\times10^{-4}\) |
| 16 | \(-3.2703584\times10^{-4}\) |

Only the \(L=6\) sign is certified exactly here.  The other rows are
orientation diagnostics.

Near zero momentum, \(P/\omega^2=O(|k|^{-2})\), which is integrable in four
dimensions.  The Riemann sums therefore converge to a Brillouin-zone
integral.  Put

\[
 f(t)=e^{-2t}I_0(2t),\qquad
 W_4=\int_0^\infty f(t)^4dt,
 \qquad
 I_4=\int_0^\infty f(t)^2f'(t)^2dt.
\]

The standard Laplace/Bessel representation of the hypercubic Green function
and Brillouin-zone integration by parts give

\[
 \boxed{
 b_{2,\infty}=-\frac{85}{5184}+\frac{W_4}{18}
              +\frac{5I_4}{288}.
 }
\]

The hypercubic Green-function Bessel representation is standard; see
[Guttmann, *Lattice Green functions in all dimensions*, 2010](https://arxiv.org/abs/1004.1435).
The particular BT combination and conditional-response reduction are derived
here.  No literature-novelty claim is made without a dedicated review.

## Meaning in ordinary language

The uniform surrounding field gave a small wrong-sign long-wave response.
The natural hope was that typical fluctuating surroundings would cancel it.
They cancel nearly all of it at weak coupling, but the exact \(6^4\)
calculation says a small wrong-sign remainder survives.

That matters because a proof demanding \(\beta_L\geq0\) at every volume
cannot work.  It does not yet settle the continuum estimate.  The remaining
question is whether the same negative remainder survives uniformly as the
lattice grows and whether higher orders or block conditioning change it.

## Next gate

Prove rational upper bounds such as

\[
 W_4<\frac{31}{200},\qquad I_4<\frac{54}{125},
\]

or any comparably strong certified interval.  The displayed limit formula
would then decide the large-volume one-loop sign.  A negative decision closes
single-site annealed signed contraction as a volume-uniform architecture and
redirects the programme to block conditional response or the direct
score/Witten route.

## Claim boundary

This coefficient does not prove that \(\beta_L\) is negative at
\(\lambda=0.4\), at arbitrary coupling, or nonperturbatively.  It does not
prove heat-bath instability, failure of block conditioning, a global
Poincare or Witten theorem, the normalized lowest-mode estimate, or the
interacting \(H^{-1}\) bound.  It establishes no continuum measure, ordinary
OS reconstruction, new physical dimension, Born rule, Krein reconstruction,
or `LORENTZIAN-CAUSAL` statement.

Paper 21 is not changed at this coefficient checkpoint because neither the
continuum nor reconstruction lifecycle is promoted.

## Verification

```text
ulimit -v 500000; python3 reverse_physics/bt_euclidean_annealed_response_one_loop.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_annealed_response_one_loop.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_annealed_response_one_loop
```
