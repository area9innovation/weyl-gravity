# BT expected-Hessian axial symbol

**Certificate:**
`REVERSE_PHYSICS_BT_EUCLIDEAN_EXPECTED_HESSIAN_AXIAL_SYMBOL_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`,
`REDUCED-MODE`

## Result

The full interacting Gibbs/Witten numerator has a much smaller exact
description than its nonlinear definition suggests.  Let

\[
 A(\psi)=\frac12\sum_x r_x^2,
 \qquad
 r_x=\sum_{y\sim x}e^{\psi_y-\psi_x}-2D,
\]

and let

\[
 H_L(z)=\mathbb E_\mu[\partial_{\psi_0}\partial_{\psi_z}A].
\]

The pointwise Hessian has range two.  Translation and hypercubic symmetry
therefore leave only four expected coefficients: (a) at the origin, (b)
at a nearest neighbour, (c) at axial distance two, and (d) at mixed
distance two.  Constant-shift invariance fixes the row sum.  For an axial
momentum this collapses the whole symbol to

\[
 \boxed{
 \widehat H_L(p)=\alpha_L\omega(p)+c_L\omega(p)^2,
 \qquad
 \alpha_L=-(b_L+4c_L+6d_L),
 }
\]

where (omega(p)=2(1-cos p)).  At the vacuum,

\[
 (b,c,d)=(-16,1,2),\qquad \alpha=0,
\]

and the bilaplacian (omega^2) is recovered.  Away from the vacuum there is
no algebraic identity forcing (alpha_L=0).

## Local formulas

Put (t_{xy}=e^{\psi_y-\psi_x}), (s_x=\sum_y t_{xy}=q+r_x).  Direct
differentiation gives

\[
 H_{x,x+e}=-(q+2r_x)t_{x,x+e}
 -(q+2r_{x+e})t_{x+e,x},
\]

\[
 H_{x,x+2e}=t_{x+e,x}t_{x+e,x+2e},
\]

and

\[
 H_{x,x+e+f}
 =t_{x+e,x}t_{x+e,x+e+f}
 +t_{x+f,x}t_{x+f,x+e+f}.
\]

The last two expressions are positive.  Translation symmetry and Jensen's
inequality give (c_L\geq1) and (d_L\geq2).

An exact rational (C_6\times C_6) fixture uses the positive profile
((1,2,1,1/2,1,1)) along one axis.  Independent differentiation of the
complete sparse Hessian gives

\[
 b=-\frac{133}{12},\qquad
 c=\frac{59}{48},\qquad
 d=\frac73,\qquad
 \alpha=\frac32.
\]

This fixture proves that the (p^2) coefficient is not identically zero as a
local algebraic expression.  It is not a Gibbs expectation or an
infinite-volume theorem.

## Uniform actual-Gibbs bounds

At (lambda=2/5), the certified affine virial theorem gives

\[
 \frac1N\mathbb E_\mu A\leq\frac{1222}{25},
 \qquad
 \mathbb E_\mu r_x^2\leq\frac{2444}{25}.
\]

Since (t_{xy}\leq s_x), (uv\leq(u+v)^2/4), and
((q+r)^2\leq2q^2+2r^2), these imply

\[
 |b_L|\leq\frac{5964}{5},\qquad
 1\leq c_L\leq\frac{2022}{25},\qquad
 2\leq d_L\leq\frac{4044}{25},
\]

and

\[
 |\alpha_L|\leq\frac{62172}{25}.
\]

Gibbs integration by parts supplies the positive score-covariance identity

\[
 \mathbb E_\mu[\operatorname{Hess}A]
 =\lambda^{-2}\mathbb E_\mu[\nabla A\otimes\nabla A]
\]

on the mean-zero carrier.  Hence

\[
 0\leq\widehat H_L(p)\leq\frac{14052}{5}\,\omega(p).
\]

At the smallest nonzero momentum, positivity also gives

\[
 \alpha_L\geq-c_L\omega(2\pi/L).
\]

Because (c_L) is uniformly bounded, every large-volume accumulation point
of (alpha_L) is nonnegative.

A Cramér--Rao integration-by-parts argument then gives a genuine interacting
mode lower bound.  For a unit real axial Fourier mode (h),

\[
 \operatorname{Var}_\mu\langle h,\psi\rangle
 \geq\frac{1}{17565\,\omega(p)},
\]

or, with (phi=\psi/\lambda),

\[
 \operatorname{Var}_\mu\langle h,\phi\rangle
 \geq\frac{5}{14052\,\omega(p)}.
\]

This is a lower bound on fluctuations.  It is not the upper bound needed for
the interacting (H^{-1}) tightness programme, and it does not by itself
prove an (H^{-1}) divergence.

## Finite-volume diagnostic

The independent local Metropolis sampler measured the local coefficients
directly under the full Gibbs measure:

| (L) | action density | (alpha_L) | (c_L) | (d_L) |
|---:|---:|---:|---:|---:|
| 6 | (0.49923(287)) | (0.09713(75)) | (1.007611(46)) | (2.016151(124)) |
| 8 | (0.49258(192)) | (0.09553(59)) | (1.007472(31)) | (2.015887(97)) |

The parentheses are blocked standard errors.  The exact action-recompute
residuals are below (6\times10^{-11}).  The two-volume stability is strong
evidence that the full expected-Hessian numerator develops an ordinary
(p^2) term at (lambda=0.4), but it is not a proof that the infinite-volume
limit exists or is nonzero.

The expensive observation reproduction is deliberately separated from the
fast commit rail:

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_hessian_symbol_experiment.py --reproduce
```

The stored (L=6,8) observation is binary64 evidence, not an exact
certificate.

## What changed in the research picture

The hoped-for exact interacting continuation of the vacuum (p^4)
cancellation does not occur pointwise and is not supported by the full-Gibbs
data.  But (alpha_L) is only the expected or “diamagnetic” twist curvature.
The true helicity modulus/free-energy curvature also contains a subtractive
integrated-current variance.  Those two objects must be combined before
claiming a physical stiffness or Witten coercivity.

The earlier conditional-background score is also a different measure and a
different observable.  Its tentative (p^4) scaling cannot be disproved by
this full-measure (p^2) observation, and neither result may be silently used
as the other.

The next calculation is therefore exact and focused: derive the uniform-twist
free-energy identity, including the paramagnetic current term, and decide
whether the complete twist response stays positive, cancels, or degenerates
with volume.  A positive response would motivate a Witten coercivity route;
a cancellation would explain how the conditioned (p^4) behavior survives.

No literature-novelty claim is made without a dedicated review.  No
interacting (H^{-1}) bound or divergence, continuum measure, Born rule,
Krein reconstruction, or `LORENTZIAN-CAUSAL` result is established.

## Verification

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_expected_hessian_axial_symbol.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_expected_hessian_axial_symbol.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_expected_hessian_axial_symbol
ulimit -v 500000; python3 reverse_physics/bt_euclidean_hessian_symbol_experiment.py --smoke
```

## Verification receipt

- Tier 0 and the scoped Tier 1 rails are recorded in the certificate and
  commit handoff.
- Tier 2 does not rebuild the unchanged, content-addressed affine
  action-density and Riemannian Witten inputs.
- Tier 3 is not run because this checkpoint promotes no (H^{-1}), continuum,
  freeze, release, shared-core, or Lorentzian lifecycle.
- All Python rails use a 500 MB virtual-memory limit.  The full (L=6,8)
  observation used about 22 MB and 20 MB peak resident memory in the recorded
  runs; it is not part of the fast per-commit rail.
- The planning importer accepted 1,679 nodes with zero invalid items and zero
  malformed events in 15.66 s under `GOMEMLIMIT=300MiB` and `GOGC=50`.
- The 3.20 s advisory Science Forge shadow wrapper exited zero, but its bridge
  audit failed closed because the referenced external `bp2transformer`
  verifier lacks `sympy`; it also reported corpus drift (1,823 certificates
  versus the July baseline of 976).  These advisory findings are recorded as
  failures/drift, not passes.
