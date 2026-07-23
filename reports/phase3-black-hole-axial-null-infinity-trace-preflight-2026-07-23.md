# Phase 3 axial null-infinity trace preflight

Date: 23 July 2026

## Result

The repaired six-state axial Bach system now has an exact action-derived
radial-current matrix on the pilot match sphere.  In the state order

\[
(P,P',Q,Q',H_1,F),
\]

write

\[
F^r(y,\bar z)=\pi\alpha_{\rm W}\,z^\dagger\widehat J_6(\omega)y.
\]

The certificate derives \(\widehat J_6\) from the literal Lee--Wald current
and the repaired first-order flow; it does not type the matrix in as an
expected answer.  For real nonzero frequency,

\[
\widehat J_6^\dagger=-\widehat J_6,
\qquad
\det\widehat J_6=
\frac{195689447424}{15625(4\omega^2+1)}.
\]

Thus the radial pairing has rank six throughout the real pilot interval.  At
\(\omega=1/2\), the Hermitian boundary form
\(-i\widehat J_6\), after the declared permutation, has exact LDL pivots

\[
\left(-\frac{168}{5},\frac{192}{7},-\frac{27648}{5},
\frac{256}{75},\frac{12}{5},-\frac{3}{20}\right),
\]

and hence inertia \((3,3)\).  No positivity conclusion is drawn from this
match-sphere form.

## Correct endpoint split

With the convention \(e^{+i\omega v}\), the infinity columns separate as

\[
\mathscr I^-:\quad (XI0,XI1,EI0),
\qquad
\mathscr I^+:\quad (XI2,XI3,EI2).
\]

The second assignment follows from

\[
e^{i\omega v}e^{-2i\omega r}r^{-4i\omega}
=2^{-4i\omega}(1-2/r)^{4i\omega}e^{i\omega u}.
\]

At the future horizon, the regular subspace is selected by columns
\((XH0a,XH0b,EH0)\), i.e. indices \((0,1,4)\) in the frozen horizon basis.

This split corrects an ambiguity in the earlier raw-\(F^v\) experiment.  The
six formal infinity columns do not form one endpoint test space: the
rate-zero group is incoming data at past null infinity, while the
rate-\(-2i\omega\) group is outgoing data at future null infinity.
Cross-testing all six with one improper radial-density integral mixes two
different boundary components.

## Three different objects

The preflight now separates:

1. **Radial current.**  For exact, same-frequency on-shell solutions,
   \(F^r\) is independent of radius.  The connection matrix must preserve
   this form.
2. **Coordinate density.**  In the Schwarzschild \(t\) chart,
   \(F^u=F^t-B^{-1}F^r\) and \(F^v=F^t+B^{-1}F^r\).  An improper integral of
   the EF component \(F^v\) is a Cauchy-density diagnostic, not by itself a
   flux through \(\mathscr I^+\) or \(\mathscr I^-\).
3. **Wave-packet flux.**  A physical null trace must first superpose
   frequencies, then take the endpoint limit in a declared finite-energy or
   Schwartz topology, separately at \(\mathscr I^+\) and \(\mathscr I^-\).

For a common-radius connection convention \(B_H=B_I T\), conservation is

\[
T^\dagger H_I T=H_H.
\]

With outward endpoint normals the horizon sign reverses:

\[
T^\dagger H_I^{\rm out}T+H_H^{\rm out}=0.
\]

## Exact remaining dependency

A genuine null-infinity trace is not yet defined.  The first missing theorem
is a uniform joint \((r,\omega)\) estimate for the reconstructed endpoint
expansions and their frequency derivatives, followed by a
stationary-phase/integration-by-parts proof that the wave-packet trace exists
and has finite conserved Lee--Wald flux.  Fixed-frequency formal heads alone
do not control threshold behaviour, frequency derivatives, or interchange
of the spectral integral with the endpoint limit.

This is a completed preflight, not a scattering theorem.  It establishes the
exact radial form and the correct endpoint polarizations while refusing to
promote the raw EF density to a physical null trace.

## Verification

```text
python3 -m black_hole_programme.phase3.axial_null_infinity_trace_preflight.produce --check
python3 -m black_hole_programme.phase3.axial_null_infinity_trace_preflight.verify
python3 -m pytest -q black_hole_programme/phase3/axial_null_infinity_trace_preflight/tests
python3 residual_atlas/validate_fragment.py residual_atlas/phase3-black-hole-axial-null-infinity-trace-preflight-fragment-v1.json
```

CLOSE-OUT: DONE — exact six-state radial current and null-endpoint polarization preflight certified; the raw EF \(F^v\) diagnostic is rejected as a null-flux definition, and the first missing wave-packet trace estimate is stated fail-closed.

EVIDENCE: `black_hole_programme/phase3/axial_null_infinity_trace_preflight/certificate.json`; `black_hole_programme/phase3/axial_null_infinity_trace_preflight/verify.py`; `black_hole_programme/phase3/axial_null_infinity_trace_preflight/tests/test_preflight.py`.
