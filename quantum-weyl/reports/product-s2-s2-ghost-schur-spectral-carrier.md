# Product \(S^2\times S^2\) ghost Schur spectral carrier

## Result

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

On the compact product

\[
S^2(k_1)\times S^2(k_2),\qquad k_1,k_2>0,
\]

the scalar harmonics are labelled by \((\ell,m)\), with

\[
a=k_1\ell(\ell+1),\qquad b=k_2m(m+1),\qquad
\lambda=a+b,qquad d_{\ell m}=(2\ell+1)(2m+1).
\]

The exact normalized longitudinal Schur eigenvalue is

\[
s_{\ell m}=\frac23+\frac13
\sum_{i\in\operatorname{active}}
\frac{a_i}{\lambda-2k_i}.
\]

Only factor gradients which are actually present are included. Thus the
constant scalar is absent, a pure first-factor harmonic has one active exact
component, and a mixed harmonic has two. This is the complete spectral
measure for the Schur carrier on the declared product background. For
\(k_1\ne k_2\) it sees the tracefree-Ricci anisotropy which is invisible on
the round four-sphere.

## The priming correction is coupled

The modes \((1,0)\) and \((0,1)\) expose a subtlety which a naive primed
determinant misses. On the active factor,

\[
\lambda-2k_i=0,
\]

so the minimal vector determinant has a zero while the separately written
Schur factor has a pole. Their polynomially continued product is finite:

\[
\frac{\lambda-2k_i}{\lambda}
\left(\frac23+\frac13\frac{\lambda}{\lambda-2k_i}\right)
=1-\frac{4k_i}{3\lambda}
\longrightarrow \frac13.
\]

There are three harmonics on each factor. The correct prescription is
therefore to evaluate the regular vector and Schur determinants on their
common complement and multiply by the exceptional correction

\[
3^{-6}.
\]

Deleting the vector zeros and scalar rows independently would lose this
factor. An independent verifier constructs the full one- or two-dimensional
exact-vector matrices \(H=A+\tfrac12d\delta\) and
\(H_0=F+\tfrac12d\delta\), and reproduces every stored paired ratio directly
as \(\det H/\det H_0\).

## Exact checks

The checked \(k_1=1,k_2=2\) fixture includes regular and exceptional modes,
factor-exchange covariance, and an exact rectangular cutoff product. The
Einstein specialization \(k_1=k_2=k\) gives

\[
s_{\ell m}=\frac{\lambda-4k/3}{\lambda-2k}
=\frac{\Delta_0-R/3}{\Delta_0-R/2},\qquad R=4k,
\]

in agreement with the generic Schur certificate.

The principal spectral symbol

\[
K_{-2}(x,\xi)=\frac23\frac{\operatorname{Ric}(\xi,\xi)}{|\xi|^4}
\]

and the exact product curvature data replay

\[
\operatorname{Wres}(K^2)
=\frac{8(k_1^2+k_1k_2+k_2^2)}{27k_1k_2}.
\]

For \((k_1,k_2)=(1,2)\), this is \(28/27\).

## Claim boundary and next gate

The bivariate infinite sums have not yet been analytically continued. In
particular, the certificate does not compute the infinite
\(\det_3\) value, the finite weighted rows \(R(K)\) and
\(\operatorname{FP}R(K^2)\), or the full coupled ghost determinant. The next
gate is to analytically continue those product spectral sums with the
exceptional factor retained, then add the remaining BV sectors. This is not
a generic-background form-factor, complete \(\Gamma_1/Q_1\), Lorentzian QME,
state, particle, positivity, scattering, or unitarity result.

## Receipts

```bash
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.product_s2_s2_ghost_schur_spectral_carrier --check
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.verify_product_s2_s2_ghost_schur_spectral_carrier
PYTHONPATH=quantum-weyl python3 -m unittest \
  quantum-weyl/spectral/euclidean/tests/test_product_s2_s2_ghost_schur_spectral_carrier.py
```

| Tier | Scope | Elapsed | Result |
| --- | --- | ---: | --- |
| 0 | Python compile, Draft 2020-12 schema validation, scoped `git diff --check` | under 1 s | PASS |
| 1 | producer replay, independent exact matrix verifier, six direct tests | 0.5 s | PASS |
| 2 | active-frontier chain, generated atlas and independent validator, Paper 12 claim map and table verifier | 8.2 s | PASS |
| publication | two-pass main TeX and three-pass supplement TeX; warnings/errors scan | 3.3 s | PASS |

Tier 3 was not run.  This change adds one content-addressed special-background
spectral leaf and its direct consumers; it does not alter shared core algebra,
promote a lifecycle state, freeze a theorem, or prepare a release.  The
affected certificate chain is the smallest deterministic suite capable of
falsifying the new claim.  The infinite bivariate sums are recorded as
`NOT_COMPUTED`, not as a timeout or pass.
