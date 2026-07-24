# Phase 3 axial QNM contour-seed preflight

## Disposition

`UNVALIDATED-NUMERIC — NONCERTIFYING PREFLIGHT`

Dependency tag: `REDUCED-MODE`.

This report records a reproducible numerical seed and proposed contour for the
Schwarzschild axial \(\ell=2\) scalar Regge--Wheeler problem.  It is not a QNM,
root-count, \(\beta\), Smith-type, Fredholm-pole, or EP2 certificate.  None of
the printed digits is enclosed.  The finite continued fraction, endpoint
series, ODE integration and contour quadrature all lack validated remainder
bounds.

## Frozen convention and scalar equation

The repository uses \(e^{+i\omega t}\), so temporal damping is
\(\operatorname{Im}\omega>0\).  For \(M=1\),

\[
D=\left(1-\frac2r\right)\frac{d}{dr}=\frac{d}{dr_*},
\qquad
Ly=D^2y+\left(\omega^2-V_2\right)y=0,
\]

\[
V_2=\left(1-\frac2r\right)
\left(\frac6{r^2}-\frac6{r^3}\right).
\]

The future-horizon and outgoing-infinity factors are respectively

\[
e^{+i\omega r_*},
\qquad
e^{-i\omega r_*}.
\]

With \(x=1-2/r\), the Leaver ansatz used by the preflight is

\[
y=e^{-i\omega r}r^{-2i\omega}x^{2i\omega}
\sum_{n\ge0}a_nx^n.
\]

Direct substitution gives

\[
\alpha_n=(n+1)(n+1+4i\omega),
\]

\[
\beta_n=-2n^2-2n-16i\omega n
        +32\omega^2-8i\omega-3,
\]

\[
\gamma_n=(n-1)(n+1+8i\omega)
         -16\omega^2+8i\omega-3,
\]

and

\[
\alpha_na_{n+1}+\beta_na_n+\gamma_na_{n-1}=0.
\]

## Two independent numerical rails

### Finite backward continued fraction

The depth-400 finite backward approximant gives the conjugate pair

\[
\omega=
\pm0.373671684418041835793492003281\ldots
+0.088962315688935698280460927210\ldots\,i.
\]

The negative-real branch is the repository-frequency image of the usually
tabulated positive-frequency mode under the opposite time convention.

Changes relative to depth 400 are:

| Depth | Absolute change |
|---:|---:|
| 40 | \(9.16299\times10^{-10}\) |
| 60 | \(1.01587\times10^{-11}\) |
| 80 | \(2.35466\times10^{-13}\) |
| 120 | \(4.42621\times10^{-16}\) |
| 180 | \(2.11106\times10^{-19}\) |
| 260 | \(4.82132\times10^{-23}\) |

This is truncation convergence, not a minimal-solution tail enclosure.

### Matched Riccati shooting

An independent 45-decimal rail constructs a horizon Frobenius series and a
separately derived infinity asymptotic series, then transports their
logarithmic derivatives with `mpmath` Taylor ODE integration to \(r_m=4\).
It does not use the continued-fraction recurrence in its mismatch evaluation.

| Outer radius | Series order | Numerical root |
|---:|---:|---|
| 30 | 24 | \(-0.3736716832967196733+0.0889623135070310430i\) |
| 40 | 34 | \(-0.3736716844136960168+0.0889623156834933966i\) |
| 45 | 38 | \(-0.3736716844183182527+0.0889623156887353735i\) |

The respective distances from the depth-400 continued-fraction value are

\[
2.45318\times10^{-9},
\qquad
6.96453\times10^{-12},
\qquad
3.41398\times10^{-13}.
\]

These are observations only.  The infinity series has no enclosed remainder,
and the requested Taylor-ODE tolerance is not a ball bound.

## Proposed contour

For the negative-real branch, use the provisional circle

\[
c=-0.373671684418041835793492
  +0.088962315688935698280461i,
\qquad
R=0.025,
\]

\[
D_{\rm seed}=\{\omega:|\omega-c|<R\}.
\]

Its imaginary extent is

\[
[0.06396231569,\ 0.11396231569],
\]

inside the currently declared coefficientwise strip
\(|\operatorname{Im}\omega|<1/4\).

Clearances after subtracting the radius are:

| Excluded point or candidate | Clearance |
|---|---:|
| \(0\) | \(0.3591156354\) |
| \(i/4\) | \(0.3818951505\) |
| \(i/2\) | \(0.5305020303\) |
| \(i\) | \(0.9596929420\) |
| positive-real mirror seed | \(0.7223433688\) |

For the depth-260 finite continued-fraction proxy \(F\), 256 contour samples
give

\[
\min_{\partial D_{\rm seed}}|F|=0.5109321991,
\qquad
\max_{\partial D_{\rm seed}}|F|=0.6362565519,
\]

\[
35.52309265
\le |F'/F|
\le44.55670564,
\qquad
\operatorname{mean}|F'/F|=40.12327389.
\]

The sampled winding and trapezoidal log-derivative diagnostic are one at
32, 64, 128 and 256 nodes.  This is not an argument-principle proof: the
finite continued fraction is a rational approximant, can have truncation
poles, and has not been identified with a ball-valued analytic Jost
determinant on the closed disk.

No numerical \(b/a\) value is reported.  The globally normalized intrinsic
tangent \(b\), including endpoint normalization and the exact factor-frame
crosswalk, has not been implemented.  Even the proxy value
\(1/\min|F|\simeq1.95721\) is normalization-dependent and is not a Jost
bound.

## Exact missing work for validated endpoint balls

1. Freeze by content hash the scalar \(U\), time and boundary convention,
   projective cocycle or extension matrix, and factor-frame normalization.
2. On every complex-frequency contour panel, construct a horizon Frobenius
   ball recurrence after factoring \(x^{2i\omega}\).  Uniformly exclude and
   bound its divisors
   \[
   (n+1)(n+1+4i\omega).
   \]
   This must resolve the \(\omega=i(n+1)/4\) frame events rather than merely
   sample around them.
3. Construct an infinity-outgoing ball initializer after factoring
   \(e^{-i\omega r}r^{-2i\omega}\).  Its leading recurrence divisor is
   \(2i\omega(n+1)\), so the closed domain must exclude zero.  A truncation is
   insufficient: prove a uniform Volterra or asymptotic remainder on the
   complex contour, or use a hyperboloidal or complex-scaled compactification
   with a certified outgoing endpoint germ.
4. Declare every logarithm and complex-scaling branch and prove the radial
   path avoids \(r=0\), \(r=2\), reconstruction walls and branch cuts for
   every frequency ball.
5. Propagate correlated complex balls or Taylor models for \(Y_H,Y_+\) to a
   fixed match radius.  Enclose ODE residuals and endpoint remainders, control
   wrapping, and prove a nonzero lower bound for the Evans determinant on
   every boundary panel.
6. Differentiate recurrences and transport analytically in frequency to
   enclose \(a'\); finite differences are insufficient.  Certify the contour
   quadrature of \(a'/a\) in a single integer ball.
7. Implement the intrinsic tangent columns \(X_H,X_+\), including
   differentiated endpoint normalizations, and prove
   \[
   b=\det(X_H,Y_+)+\det(Y_H,X_+)
   \]
   agrees with the factor-adapted triangular entry up to the declared
   analytic unit and \(a\)-multiple.
8. Enclose \(b/a\) and its contour quadrature with the same correlated
   frequency model.  Only then may exclusion of zero from the moment be used.
9. Satisfy the repository validation protocol: reproduce the exact real-axis
   anchors and conjugation laws, meet the residual and boundary tolerances,
   and run a genuinely independent validated rail, such as a validated
   hyperboloidal-Chebyshev determinant or a Leaver minimal-solution
   calculation with rigorous tail enclosure.  Any disagreement, timeout or
   skipped anchor is fail-closed.

## Reproducibility artifacts

The deterministic but noncertifying scripts and their captured output live in
`black_hole_programme/phase3/axial_qnm_contour_seed_preflight_v1/`.
Their pre-materialization hashes are:

```text
qnm_leaver_preflight.py
5137ed8e82159f7af3cb6492952a2f6c5608f22a33f7383f70142656f71b61ed
qnm_leaver_preflight.json
e4ad8e8eee8870a73d22ff6aba5240f1d3f8512cbd0c8fbe175a2dae0bb61e14

qnm_mpmath_shooting_preflight.py
bc38643e1f15c7562ca9dc4bf5767b735a47f9a6246c9e01910f399e7ff18ad7
qnm_mpmath_shooting_preflight.json
d36f64d86681a262568ea18ff75152b2a1c956eb74b58fed607170c4e094eca4

qnm_contour_diagnostic.py
2be1187d40cbdce19c4ffe8482a9083f6c840854ffb1e906cbdd18a02f15c75f
qnm_contour_diagnostic.json
ead92864b8f8b0bfa40909c5f2d3e7e0c3788c9bfedb5694896746a0d5fef36f
```

The package receipt records the hashes again after repository
materialization.  No `certificate.json` is issued.

## Claim boundary

This preflight does not establish:

- the existence, uniqueness, simplicity or enclosure of a QNM;
- a nonzero boundary value of a Jost or Evans determinant;
- an argument-principle root count;
- a normalized \(b/a\), a nonzero contour moment or \(\beta_n\);
- either local Smith branch;
- a connection-level or Fredholm exceptional point;
- a Green-resolvent pole or generalized ringdown term;
- a Lorentzian-causal result.

CLOSE-OUT: NONCERTIFYING PREFLIGHT ONLY — a plausible contour and two
consistent numerical seeds are recorded for construction of validated
endpoint balls.
