# Phase 3 axial wave-packet null-trace audit

Date: 23 July 2026

## Outcome

The physics-specific nonstationary-phase mechanism is exact, but the current
infinity remainder certificate is two recurrence orders too shallow to
promote it from the displayed formal heads to exact Bach solutions.

The result is therefore a precise shortfall:

\[
\boxed{
\text{formal wrong-endpoint suppression is proved, but the exact remainder is only }C^1_\omega;
\ C^3_\omega\text{ is required.}
}
\]

No wave-packet phase space, null-flux Gram, scattering channel, stability or
CPT result is claimed.

## Exact scalar lemma

For (b\in C_c^N((1/2,3/4))) and a phase with constant nonzero frequency
derivative (L), repeated integration by parts gives

\[
 \left|\int e^{i\omega L}b(\omega)\,d\omega\right|
 \le |L|^{-N}\,\|\partial_\omega^N b\|_{L^1}.
\]

Every boundary term vanishes because the spectral amplitude has compact
support in the *open* pilot interval.  In the convention
(e^{+i\omega v}), the two wrong-endpoint phases are

\[
 XI0,XI1,EI0\text{ at fixed }u:
 e^{i\omega(u+2r_*)},
\]

and

\[
 XI2,XI3,EI2\text{ at fixed }v:
 e^{i\omega(v-2r-4\log r)}.
\]

Their frequency derivatives have magnitude comparable to (r) for fixed
(u) or (v) and sufficiently large radius.  The largest displayed metric
head grows as (r^2), so three integrations by parts make every finite head
vanish at its wrong null endpoint.

The producer checks every displayed XI0--XI3 metric coefficient and the two
Einstein-kernel heads.  All coefficients and their first three frequency
derivatives have exact rational upper bounds on ([1/2,3/4]); their only
real pole is at (omega=0), outside the allowed support.

## Correct matching traces at the formal-head level

The endpoint split remains

\[
\mathscr I^-: (XI0,XI1,EI0),\qquad
\mathscr I^+: (XI2,XI3,EI2).
\]

At fixed (v), the first basis carries the matching phase
(e^{i\omega v}).  At fixed (u), the second carries

\[
2^{-4i\omega}e^{i\omega u}(1-2/r)^{4i\omega},
\]

whose last factor converges uniformly to one.  After the declared
columnwise radiation rescaling, dominated convergence therefore defines
three formal trace coordinates at each endpoint for the finite heads.

This is not yet an exact-solution trace theorem.  In particular, a formal
fixed-frequency pairing is not renamed a physical wave-packet flux.

## Exact first missing estimate

The imported phase-normalized Volterra remainder satisfies

\[
 |K_{N,ij}(r,\omega)|\le C_{ij}r^{-p_{ij}},
 \qquad p_{\min}=3.
\]

For cross-rate entries, each (omega) derivative of

\[
 e^{\pm2i\omega r}r^{\pm4i\omega}
\]

costs one power of (r) (the logarithmic factor is subleading).  Thus the
absolute differentiated Volterra majorant behaves as

\[
r^{-(p-k)}(1+\log r)^k,
\]

and is integrable only when (p-k>1).  With (p=3):

* (k=0,1) are integrable;
* (k=2) first fails, with an (r^{-1}) majorant;
* the (k=3) estimate required for the largest (r^2) head is unavailable.

To control three frequency derivatives absolutely one needs

\[
p_{\min}\ge 5.
\]

The minimum repair is therefore two additional inverse-radius recurrence
orders: extend (H_0,H_1) through inverse order five, retain the
derivative-forced (F) coefficient through inverse order six, and rebuild
the differentiated envelope for (k=0,1,2,3).

## Flux disposition

Each formal matching trace has dimension three.  The exact null-flux Gram,
its radical, quotient dimension and inertia remain undefined because the
bounded exact-solution trace has not passed.  The two endpoints keep separate
outward-normal orientations, and negative frequencies are supplied only by
the real-field involution

\[
a_{\ell,-m}(-\omega)=(-1)^m\overline{a_{\ell m}(\omega)}.
\]

## Verification

```text
python3 -m black_hole_programme.phase3.axial_wavepacket_null_trace.produce --check
python3 -m black_hole_programme.phase3.axial_wavepacket_null_trace.verify
python3 -m black_hole_programme.phase3.axial_wavepacket_null_trace.mutations
python3 -m pytest -q black_hole_programme/phase3/axial_wavepacket_null_trace/tests
python3 residual_atlas/validate_fragment.py residual_atlas/phase3-black-hole-axial-wavepacket-null-trace-fragment-v1.json
```

CLOSE-OUT: SHORTFALL — the finite formal heads obey the exact three-fold nonstationary-phase suppression theorem, but the certified cross-rate Volterra remainder has only one absolutely integrable frequency derivative; two more recurrence orders are required before a physical null trace or flux Gram can be promoted.

EVIDENCE: `black_hole_programme/phase3/axial_wavepacket_null_trace/certificate.json`; `black_hole_programme/phase3/axial_wavepacket_null_trace/verify.py`; `black_hole_programme/phase3/axial_wavepacket_null_trace/mutations.py`.

MISSING-DEP: Extend the exact infinity recurrence by two inverse-radius orders and certify a cross-rate (p\ge5) Volterra envelope with frequency derivatives through order three.
