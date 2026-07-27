# Complete massive axial Jost crosswalk

This `REDUCED-MODE` package closes the endpoint-analytic gate left by the
complete first-jet calculation.  It works with the full coupled axial
\(Q,Z\) system and proves:

- a two-dimensional horizon-ingoing Jost plane analytic in
  \((\omega,m)\);
- a two-dimensional infinity-outgoing Jost plane analytic in
  \((\omega,m)\);
- exclusion of an opposite-Jost admixture by Frobenius and sectorial
  Volterra uniqueness;
- invariance of the first spin-two divisor derivative under the
  same-sign spin-one mixing, because the spin-one factor is a local unit;
- the endpoint-normalized identity
  \[
  b_{\rm B}(\omega_n)
  =\frac{3i\omega_n}{2}\,
    \partial_m a_{\rm phys}(\omega_n,0);
  \]
- the nonzero signed squared-mass QNM velocity
  \[
  \omega_n'(0)=\frac{2i}{3\omega_n}\kappa_n.
  \]

The infinity proof is two-stage.  The exact common phase
\[
\phi_\sigma=e^{\sigma i kx}r^{\sigma i m/k},
\qquad k^2=\omega^2-m,
\]
leaves an \(O(r^{-2})\) scalar residual.  The remaining \(2\times2\)
coupling matrix is also \(O(r^{-2})\).  Successive scalar and matrix
Volterra equations therefore converge uniformly on a smaller parameter
polydisc along the already certified exterior-complex-scaled ray.  Their
normalization excludes the opposite exponential.

At the horizon, \(m f\) and the complete coupling matrix are \(O(f)\).
The two indicial exponents are \(\pm2i\omega\), each with multiplicity two.
The certified QNM disk avoids all Frobenius resonances, so the selected
matrix Frobenius series converges analytically.

This package does **not** construct a global weighted exterior Fredholm
domain, a retarded contour deformation, a complete QNM expansion, or a
real causal source.

Reproduce with:

```bash
python3 black_hole_programme/phase4/axial_massive_jost_crosswalk_v1/produce.py
python3 black_hole_programme/phase4/axial_massive_jost_crosswalk_v1/verify.py
python3 -m unittest \
  black_hole_programme.phase4.axial_massive_jost_crosswalk_v1.test_jost_crosswalk
```
