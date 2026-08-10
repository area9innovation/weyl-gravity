# Bateman--Turok external projector and infrared-carrier mismatch

**Result:** `COEFFICIENT_COMPUTED`

**Dependency:** `REDUCED-MODE`

**Certificate:**
[`REVERSE_PHYSICS_BT_EXTERNAL_PROJECTOR_CARRIER_MISMATCH_V1`](../certificates/REVERSE_PHYSICS_BT_EXTERNAL_PROJECTOR_CARRIER_MISMATCH_V1.json)

## Result

The external four-mass phase-space projector can be applied exactly to the
complete cut-constructible logarithmic loop jet.  It gives

\[
 \frac{d\sigma_{\mathrm{virt,log}}}{d\Omega}
 =\frac{5\lambda^6}{256\pi^4s}(L_s+L_t+L_u).
\]

In the hard forward limit this is

\[
 \frac{5\lambda^6}{256\pi^4s}(3L-\ell)+O(t/s),
 \qquad \ell=\log(-t/s).
\]

This does **not** cancel or fail to cancel the real-emission ambiguity already
computed.  The two logarithms live on different carriers:

- the virtual logarithm is a ratio of hard Mandelstam invariants, `-t/s`;
- the real logarithm is a ratio of two external mass regulators, `x1/x0`.

Holding the hard invariants fixed and rescaling
`x1/x0 -> c*x1/x0`, the computed virtual hard log does not change.  The real
threshold finite part changes by `-(3/8) log(c)`.  Therefore the present
virtual jet has zero response where the real term has response `-3/8`.

The conclusion is narrow but decisive: applying the external phase projector
to the hard-region jet does not reach the virtual term that could perform a
real--virtual cancellation.  That term, if it exists, must come from a
nonanalytic external-mass boundary layer of the triangle and box integrals.

## Why the phase projector is simple

Bateman and Turok's four-point formula is

\[
 \frac{d\sigma}{d\Omega}
 =\left.
 \partial_{x_1}\partial_{x_2}\partial_{x_3}\partial_{x_4}
 \frac{|\mathbf p|\,|M|^2}
 {(16\pi)^2|\mathbf q|s}
 \right|_{x_i=0}.
\]

The exact reduced tree amplitude starts at external-mass degree two.  The
complete cut-constructible logarithmic loop amplitude also starts at degree
two.  Their interference therefore starts at degree four, exactly the degree
selected by the four derivatives.

Write the analytic phase density as

\[
 \Phi(x)=\Phi_0+\Phi_1(x)+\cdots,
 \qquad \Phi_0=\frac1{256\pi^2s},
\]

and the relevant interference as `I4(x)+higher degree`.  Then

\[
 [x_1x_2x_3x_4]\,\Phi I_4
 =\Phi_0[x_1x_2x_3x_4]I_4.
\]

Every derivative of the phase density raises the total degree above four and
drops out.  The same argument covers any analytic mass-dependent pullback of
the scattering angle or hard invariants.  A mutation with a degree-three
interference term makes a linear phase correction contribute, so the argument
depends essentially on the certified degree-two cancellations in both
amplitudes.

The predecessor gives

\[
 [x_1x_2x_3x_4],2\operatorname{Re}
 (M_{\rm tree}^{*}M_{\rm loop,log})
 =\frac{\lambda^6}{(4\pi)^2}\frac{16}{3}
   15(L_s+L_t+L_u).
\]

Multiplication by `Phi0` reduces the rational coefficient exactly:

\[
 \frac{15(16/3)}{16\cdot256}=\frac5{256}.
\]

## The two ratios are not the same variable

The triangle/box predecessor works in the hard region

\[
 s\,t\,(s+t)\ne0
\]

and takes an ordinary square-free Taylor jet in the four external masses.  Its
surviving logarithm is

\[
 \ell=\log(-t/s),
\]

where `s` and `t` are hard four-point channel invariants.

The five-point real threshold instead sends the invariant mass of a pair of
final particles to zero together with their two external mass regulators:

\[
 x_0=\epsilon,\qquad x_1=\rho\epsilon.
\]

After the other three mass derivatives, the nonanalytic term is

\[
 -\frac38x_0x_1\log\rho.
\]

Under `rho -> c rho` it shifts by

\[
 -\frac38x_0x_1\log c.
\]

The hard virtual logarithms contain no `rho`, so their shift is exactly zero.
No choice of overall phase-space normalization can turn zero response into a
nonzero one.  This comparison can therefore be made before the still-missing
full `2->3` normalization.

The phrase "a ratio logarithm remains" in the triangle/box report should be
read as a **hard kinematic ratio**, not an external-mass regulator ratio.  The
present certificate makes that distinction explicit.

## What calculation is actually next

The next object is not another multiplication by the external phase density.
It is a regions calculation of the triangle and box integrals with external
masses retained nonanalytically as the collinear boundary is approached.  The
required function class must allow terms such as

\[
 x_i x_j\log(x_i/x_j),
\]

which do not belong to the predecessor's ordinary Taylor carrier.  Only after
that boundary jet is computed under the same ratio prescription as the real
threshold can the following be assembled consistently:

1. all collinear pair boundaries of the full five-point phase space;
2. virtual boundary, hard, counterterm, and cut-free pieces;
3. one common subtraction prescription; and
4. the inclusive quotient trace and beyond-tree positivity test.

## Fail-closed boundary

This result does not establish:

- cancellation or noncancellation in the completed BT observable;
- a coefficient for the missing virtual mass-ratio logarithm;
- a complete NLO cross section, probability, or asymptotic-state map;
- a KLN, resummation, or dressed-state theorem;
- scheme independence of an off-shell finite part;
- positivity or unitarity beyond tree level;
- a tensor, BRST, or gravitational lift; or
- anything `LORENTZIAN-CAUSAL`.

Bateman--Turok Eq. (13) supplies the external phase-space projector.  The
projected hard coefficient and carrier comparison are this repository's
results.  No literature-priority claim is made.

## Verification

All rails are intended to run sequentially under a 500,000 KB virtual-memory
cap:

```text
ulimit -v 500000; python3 reverse_physics/bt_external_projector_carrier_mismatch.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_external_projector_carrier_mismatch.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_external_projector_carrier_mismatch
```

The producer uses exact rational arithmetic.  The independent verifier does
not import it: it reconstructs the normalization from the two predecessor
certificates and checks the phase-degree argument in an independent sparse
polynomial algebra.

Final scoped receipt (2026-08-10):

| Tier | Command | Time | Peak RSS | Result |
|---|---|---:|---:|---|
| 0 | `py_compile` producer, verifier, and test | 0.02 s | 14,660 KB | PASS |
| 0 | `json.tool` certificate | 0.02 s | 13,836 KB | PASS |
| 0 | `json.tool` schema | 0.02 s | 13,908 KB | PASS |
| 0 | scoped `git diff --check` | 0.00 s | 10,836 KB | PASS |
| 1 producer | exact coefficient and sparse phase-degree rail | 0.02 s | 15,992 KB | PASS, 13/13 |
| 1 independent | predecessor reconstruction and independent sparse product | 0.07 s | 23,716 KB | PASS, 15/15 |
| 1 new tests | projector/carrier tests and false-cancellation mutation | 0.26 s | 24,376 KB | PASS, 10/10 |

All commands ran sequentially under a 500,000 KB virtual-memory cap.  The
unchanged predecessor inputs were checked by their recorded SHA-256 hashes:
`4bfa9c3c0968e89c7f29de3ac74d0a197d419dfd50519757948fbf6467914e71`
for the triangle/box jet and
`e6b1872ca0fbcd6a51ccd8a44b018678678dc0121ede855911a8006b7af2a4a2`
for the real threshold.  Their expensive producers were not regenerated.

Tier 2 was unnecessary because no predecessor mathematical input, shared
operator, predecessor schema, or generated artifact changed; the new schema
was exercised by both new Tier 1 rails, and the inputs are consumed
content-addressedly.  Tier 3 was not run because this is not a freeze,
shared-core change, release, or explicit full-suite request.  The advisory
Science Forge shadow rail was not rerun: its immediately preceding attempt on
this same stream stalled at the 500,000 KB ceiling, and an advisory timeout is
not a pass.  The memory limit was not raised.  None of these skipped rails is
reported as passing.

CLOSE-OUT: SHORTFALL -- the hard-log external projector is complete, but its
logarithm has the wrong carrier to test the real threshold ambiguity.

EVIDENCE: `reverse_physics/certificates/REVERSE_PHYSICS_BT_EXTERNAL_PROJECTOR_CARRIER_MISMATCH_V1.json`

MISSING-DEP: nonanalytic virtual external-mass boundary jet on the real
threshold ratio prescription

## Successor update (2026-08-10)

[`REVERSE_PHYSICS_BT_EXTERNAL_MASS_BOUNDARY_LOG_JET_V1`](../certificates/REVERSE_PHYSICS_BT_EXTERNAL_MASS_BOUNDARY_LOG_JET_V1.json)
has now computed the missing boundary carrier from an external unitarity cut.
The projected result is
`3*lambda^6*(L1+L2+L3+L4)/(128*pi^4*s)`.  This closes the virtual
boundary-log calculation on the real threshold's hard fixture.  The remaining
gate is the full real splitting-fraction integral and a declared regulator map
between one recombined virtual mass and two real daughter masses; cancellation
is still not claimed.

## Physical hard-log successor (2026-08-10)

[`REVERSE_PHYSICS_BT_UV_HARD_SCATTERING_LAW_V1`](../certificates/REVERSE_PHYSICS_BT_UV_HARD_SCATTERING_LAW_V1.json)
uses a different response of the same projected logarithm: common hard-energy
dilation at fixed nonforward angle.  Its three channel logs cancel the
beta-function scale derivative of the Born rate exactly and resum to the
positive `1/[s*log(s)^2]` hard law.  This does not alter the mass-ratio carrier
mismatch or supply the missing inclusive endpoint cancellation proved open in
this report.
