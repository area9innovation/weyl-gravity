# Phase 3 validated-connection substrate preflight

**Work item:** `sf:program/work/phase3-validated-connection-substrate-preflight`  
**Result:** `BLOCKED_MISSING_VALIDATED_COUPLED_FUNDAMENTAL_FLOW`  
**Lifecycle:** `OBSTRUCTED`  
**Evidence class:** `REDUCED-MODE`; the displayed shooting data are explicitly
`UNCONTROLLED_NUMERIC_OBSERVATION`.

## Verdict

The landed Forge math library is not yet sufficient to certify the first
Schwarzschild connection matrix.  It contains two usable pieces:

1. outward-rounded real intervals and a validated **scalar** IVP integrator;
2. interval matrix arithmetic and Krawczyk-certified rational-centre linear
   solves, suitable for endpoint basis changes once the radial flow is
   enclosed.

The first missing primitive is narrower than the previously requested full
boundary-value stack:

> a validated real coupled linear IVP on a finite nonsingular interval, with a
> fundamental-matrix enclosure and explicit wrapping control.

The present scalar API

```text
ode_integrate(f: fn(Iv, Iv) -> Iv, ..., y0: Iv, ...) -> Option<OdeCert>
```

cannot represent the four-real-dimensional axial flow or the correlations
among the sixteen entries of its realified fundamental matrix.  Calling it
component by component would be unsound because each derivative depends on
the full coupled state.

The exact small successor request is
[`planning/forge-requests/phase3-validated-connection-substrate.json`](../planning/forge-requests/phase3-validated-connection-substrate.json).
It is an executable first child of the accepted broad M25 request; it does not
ask the Forge team to solve singular endpoints, Frobenius remainder bounds,
multiple shooting or the full BVP in the same package.

## Representative axial pilot

The audit exercised the certified parity-unified reconstruction equation at
the centre of the frozen downstream interval,

\[
\ell=2,\qquad M=1,\qquad \widehat\omega=\frac35
\in\left[\frac12,\frac34\right],
\]

on the finite radial box (3\le r\le4):

\[
(r^2-2r)F''+(2i\omega r^2+2r+2)F'
 +(6i\omega r-6)F=0.
\]

For its (2\times2) complex fundamental matrix (\Phi), the Wronskian
current takes the matrix form

\[
\Phi(r)^{T}J(r)\Phi(r)=J(3),\qquad
J(r)=\exp\!\left(\int_3^r\frac{c_1(s)}{c_2(s)}\,ds\right)
\begin{pmatrix}0&1\\-1&0\end{pmatrix}.
\]

An 80-decimal fixed-step RK4 observation gives current-defect maxima

| steps | maximum defect |
| ---: | ---: |
| 256 | `1.21971774170052827e-10` |
| 512 | `7.59764595265133410e-12` |
| 1024 | `4.74053594159205846e-13` |

The approximately fourth-order decrease is useful diagnostic evidence, but it
is not an enclosure.  A separate SciPy DOP853 implementation reproduces the
reported fundamental matrix to less than (2\times10^{-10}); this remains
agreement between two uncontrolled numerical methods, not proof.

## Why small shooting residuals are insufficient

Two independent controls make the gap concrete.

First, the declared exact outer conditioning-stress basis

\[
B_\infty=
\begin{pmatrix}1&1\\1&1001/1000\end{pmatrix}
\]

has exact infinity-norm condition number

\[
\kappa_\infty(B_\infty)=\frac{4004001}{1000}.
\]

The observed (512\to1024) fundamental-matrix change
`7.55252218716580651e-12` becomes a connection-matrix change
`8.72727952327667449e-9`, an observed amplification of about `1155.55`.
Thus endpoint matching needs a certified basis solve and flow enclosure
together; raw trajectory agreement is not stable evidence.

Second, the certificate contains two matrices whose entries print identically
to twelve significant digits.  One is normalized onto the Wronskian identity;
the other differs in one entry by (10^{-15}).  Their computed current defects
are respectively about (3.53\times10^{-81}) and
(3.07\times10^{-15}).  Printed agreement therefore cannot distinguish exact
current conservation from a small violation.

## Landed-kernel adoption gate

The physics-side Forge program `substrate_gate.forge` independently checks that:

* the scalar validated integrator encloses declared rational bounds on (e);
* `math/ivmat` certifies an ill-conditioned exact endpoint-basis solve;
* both native and C backends agree, and the C gate is sanitizer-clean.

This positive gate isolates the shortfall: the existing scalar and matrix
pieces work, but no API joins them into a correlated vector flow.

## Exact claim boundary

This preflight establishes a substrate capability obstruction at the pinned
Forge source hashes.  It does **not** establish:

* a rigorous enclosure of an axial trajectory or connection coefficient;
* endpoint Frobenius or infinity-series truncation bounds;
* horizon-to-infinity matching;
* a finite-flux channel, scattering matrix or pole;
* stability, positivity or a quantum conclusion.

The obstruction is not a no-go for validated matching.  It identifies the
smallest primitive that must land before the axial global pilot can honestly
promote shooting data.

## Verification receipt

| Rail | Command | Result | Elapsed |
| --- | --- | --- | ---: |
| producer replay | `python3 black_hole_programme/phase3/validated_connection_preflight/produce.py --check` | PASS | 1.20 s |
| independent verifier | `python3 black_hole_programme/phase3/validated_connection_preflight/verify.py` | PASS | 0.97 s |
| mutation rail | `python3 black_hole_programme/phase3/validated_connection_preflight/verify.py --self-test-mutation` | 3/3 rejected | 1.02 s |
| focused Python tests | `pytest -q black_hole_programme/phase3/validated_connection_preflight/tests` | 3 passed | 4.53 s |
| Forge C | `FORGE_LIB=/home/alstrup/area9/tango/forge/lib forge -test black_hole_programme/phase3/validated_connection_preflight` | 1 passed | 0.89 s |
| Forge native | `FORGE_LIB=/home/alstrup/area9/tango/forge/lib forge -emit-asm -test black_hole_programme/phase3/validated_connection_preflight` | 1 passed | 1.43 s |
| Forge C sanitizer | `FORGE_LIB=/home/alstrup/area9/tango/forge/lib forge -sanitize -test black_hole_programme/phase3/validated_connection_preflight` | 1 passed | 2.80 s |

Tier 2 and Tier 3 were not run: this item adds an isolated preflight and a
fail-closed request; it does not change a shared operator, imported classical
snapshot or paper theorem.

EVIDENCE:
`black_hole_programme/phase3/validated_connection_preflight/certificate.json`

CLOSE-OUT: OBSTRUCTED — scalar validated IVP and certified endpoint linear
algebra are usable, but the coupled fundamental-flow enclosure required by the
Phase-3 axial connection pilot is absent; a narrow executable Forge request is
filed.
