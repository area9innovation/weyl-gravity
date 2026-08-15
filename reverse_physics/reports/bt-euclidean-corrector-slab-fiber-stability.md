# BT corrector-slab fiber stability

**Certificate:** `REVERSE_PHYSICS_BT_EUCLIDEAN_CORRECTOR_SLAB_FIBER_STABILITY_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

## Result

The localized slab that obstructs deterministic corrector-energy estimates
does not become a cheap configuration when the exact background marginal
integrates over the removed lowest cosine-sine plane.

Write the slab field as

\[
 \Omega_{t,s}=q_t2^{n_{t,s}},
\]

where the positive factors $q_t$ are arbitrary.  This is a strict relaxation
of the actual two-mode fiber, for which

\[
 q_t=\exp\left(a\cos\frac{2\pi t}{L}
              +b\sin\frac{2\pi t}{L}\right).
\]

On either active middle row, the four residuals have the form

\[
 r=b_0+\alpha\ell+\gamma r_0,
 \qquad \alpha,\gamma>0.
\]

Exact completion of squares gives

\[
 \sum_s r_{1,s}^2
 =\frac{1909}{100}+\frac{117}{25}\alpha
   +Q\left(\alpha,\gamma-\frac{33}{50}\right),
\]

\[
 \sum_s r_{2,s}^2
 =\frac{387}{50}+\frac{27}{25}\gamma
   +Q\left(\alpha-\frac{24}{25},\gamma\right),
\]

where

\[
 Q(x,y)=\frac{25}{4}x^2+\frac{21}{2}xy+\frac{25}{4}y^2
\]

has eigenvalues $1$ and $23/2$.  The two rows therefore retain at least
$2683/100$ residual square per spatial period.  Repetition over the other
coordinates proves, for every point of the two-mode fiber,

\[
 A(\eta_L+a h_c+b h_s)\geq\frac{2683}{800}L^3.
\]

This is stronger than a numerical minimization and stronger than a bound only
on the lowest-mode plane: it holds for every positive time-dependent row
factor.

## Actual integrated background density

In the logarithmic field coordinates, define

\[
 Z_\eta=\int_{\mathbb R^2}
 \exp\left[-\frac{A(\eta+a h_c+b h_s)}{\lambda^2}\right]da\,db.
\]

The exact background marginal has density proportional to $Z_\eta$.  The
certified all-phase curvature theorem gives

\[
 \operatorname{Hess}_{a,b}A\geq\kappa_L I_2,
 \qquad
 \kappa_L=\frac29N\omega_L^2\geq\frac{512}{9}.
\]

Strong convexity and the slab action floor imply a Gaussian upper bound on
$Z_{\eta_L}$.  At the zero background, integrating only over the square
$|a|,|b|\leq1/(2L)$ gives a matching elementary lower reference bound.
Together they yield

\[
 \frac{Z_{\eta_L}}{Z_0}
 \leq \frac{99\lambda^2}{896}L^2
 \exp\left[-\frac{(2683/800)L^3-15488/49}{\lambda^2}\right].
\]

At the simulated coupling $\lambda=2/5$, this becomes

\[
 \frac{Z_{\eta_L}}{Z_0}
 \leq\frac{99}{5600}L^2
 \exp\left[-\frac{2683}{128}L^3+\frac{96800}{49}\right].
\]

Thus fiber integration cannot turn this exact slab into a low-action marginal
escape.

## Boundary of the conclusion

This is a ratio of marginal densities at two specified backgrounds, not a
point probability.  It does not yet control a positive-radius neighborhood,
its entropy, every large-corrector environment, or the expectation of the
corrector structure factor.  The Gibbs hyperuniformity, current
susceptibility, annealed score, interacting $H^{-1}$ moment, and continuum
limit remain open.  No Born, Krein, or `LORENTZIAN-CAUSAL` promotion is made.

The next step is to make the two-row cone gap stable on a positive-radius block
event, count compatible bad blocks, and prove that a large corrector forces
enough such blocks before performing the Gibbs entropy sum.

## Verification

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_corrector_slab_fiber_stability.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_corrector_slab_fiber_stability.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_corrector_slab_fiber_stability
```

## Verification receipt

- Tier 0 passed: the three Python files compile and the schema, certificate and
  planning event parse as JSON.  Python and TeX ran under a 500 MB
  virtual-memory cap.
- The deterministic producer drift check passed in 0.03 s.
- The non-importing independent verifier passed in 0.08 s.  It reconstructs
  both residual-row polynomials, compares every completion coefficient,
  verifies positivity of the common quadratic form, and independently
  enumerates arbitrary rational row-factor fixtures on $L=8$ and $L=12$.
- Eleven direct and adversarial mutation tests passed in 0.13 s.
- The Paper 21 generator drift check and independent authority/boundary
  verifier passed in 0.15 s.  Two `pdflatex` passes completed in 3.32 s and
  produced a clean 61-page PDF.
- The planning import read 1633 nodes with zero invalid items and zero malformed
  events in 6.24 s.
- The 3.1 s advisory Science Forge shadow rail failed closed on the pre-existing
  Forge binary/stdlib mismatch (`E9118`) and reported corpus baseline drift
  (1744 certificates versus 976).  Its advisory wrapper exited zero; the bridge
  audit itself is recorded as failed, not passed.
- Tier 2 was not run because the three content-addressed inputs and their shared
  operators are unchanged; their hashes are checked independently.
- Tier 3 was not run because this is a single-family density comparison and
  working checkpoint, not a freeze, release, lifecycle promotion, or shared-core
  algebra change.  Neighborhood probability, Gibbs hyperuniformity, $H^{-1}$,
  and continuum gates remain explicitly open.
