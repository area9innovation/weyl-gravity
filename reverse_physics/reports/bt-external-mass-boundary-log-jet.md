# Bateman--Turok external-mass boundary logarithmic jet

**Result:** `COEFFICIENT_COMPUTED`

**Dependency:** `REDUCED-MODE`

**Certificate:**
[`REVERSE_PHYSICS_BT_EXTERNAL_MASS_BOUNDARY_LOG_JET_V1`](../certificates/REVERSE_PHYSICS_BT_EXTERNAL_MASS_BOUNDARY_LOG_JET_V1.json)

## Result

The nonanalytic external-mass part of the one-loop four-point amplitude is now
computed on the physical collinear family.  The same hard fixture as the real
independent-mass threshold is retained as a control.
For each external leg `i`, define

\[
 L_i=\log(-\mu^2/x_i).
\]

The complete boundary loop polynomial through the mass degree needed by the
BT projector is

\[
 E_{\rm boundary}=\sum_{i=1}^4 E_i,
\]

\[
 E_i=\left[
 -2x_i\sum_{j\ne i}x_j
 +10\sum_{\substack{j<k\\j,k\ne i}}x_jx_k
 \right]L_i.
\]

Interference with the exact degree-two tree amplitude gives the compact result

\[
 [x_1x_2x_3x_4]\,
 M_{\rm tree}^{\rm red}E_{\rm boundary}
 =12(L_1+L_2+L_3+L_4).
\]

Restoring the amplitude and phase-space normalizations,

\[
 \boxed{
 \frac{d\sigma_{\rm boundary,log}}{d\Omega}
 =\frac{3\lambda^6}{128\pi^4s}
 (L_1+L_2+L_3+L_4)}.
\]

This is the external-regulator response that the previous fixed-hard-channel
calculation could not see.  It includes the lower-point insertions and the
one-particle-irreducible triangle/box boundary pieces together.  It is not a
model of one selected diagram family: its cut contains the complete 25-graph
five-point tree.

The result still does not decide real--virtual cancellation.  The virtual
carrier has one recombined external mass and three spectator masses, while the
real carrier has two daughter masses and three spectators.  A regulator map
between those spaces and the full real splitting-fraction integral are still
missing.

## Why a five-point tree computes a four-point loop boundary

Take the discontinuity of the one-loop four-point amplitude in one external
virtuality.  Cutting the two internal lines separates the graph into

\[
 \text{cubic splitting vertex}\quad\times\quad
 \text{complete five-point tree}.
\]

This is a standard unitarity factorization, but it is especially useful here.
It automatically sums every bubble, triangle, box, and lower-point insertion
that possesses this external cut.  A direct expansion of the separate loop
integrands is unnecessary.

Use the same collinear variables as the real-threshold certificate:

\[
 y=\delta a_0,\qquad z=\delta a_1,
 \qquad P^2=\delta\tau,
 \qquad x_j=\delta a_j\quad(j=2,3,4).
\]

The fixed nonsingular cyclic invariants are

\[
 (s_1,s_2,s_3,s_4)=(32/3,-8,16,-8/3).
\]

For the normalized complete tree

\[
 A_5=\frac{M_5}{8\lambda^3},
\]

the exact 25-graph cancellation gives

\[
 A_5=\delta^2C(a_0,\ldots,a_4;\tau)+O(\delta^3).
\]

The two cut propagators are double poles.  Their mass derivatives act on the
ordinary two-body density and the cubic splitting vertex:

\[
 \frac{\sqrt{\Lambda(\tau,a_0,a_1)}}{\tau}
 \frac{\Lambda(\tau,a_0,a_1)}2
 =\frac{\Lambda(\tau,a_0,a_1)^{3/2}}{2\tau}.
\]

Therefore the boundary cut is

\[
 D=\left.
 \partial_{a_0}\partial_{a_1}
 \left[\frac{\Lambda^{3/2}}{2\tau}C\right]
 \right|_{a_0=a_1=0}.
\]

Exact differentiation gives

\[
 D=-\frac14\left[
 5a_2^2+5a_2a_3+5a_2a_4-a_2\tau
 +5a_3^2+5a_3a_4-a_3\tau
 +5a_4^2-a_4\tau
 \right].
\]

On the square-free external-mass carrier this reduces to

\[
 D_{\rm sf}=\frac14\left[
 \tau(a_2+a_3+a_4)
 -5(a_2a_3+a_2a_4+a_3a_4)
 \right].
\]

To check that the fixed fixture did not hide an angular function, the producer
then retains the splitting fraction `zeta` and outer ratio `chi=-T/S`
symbolically:

\[
 (s_1,s_2,s_3,s_4)
 =(1-\zeta,-\chi,1,\zeta(\chi-1)).
\]

A 32-slot square-free mass jet over `Q(tau,zeta,chi)` reproduces the same
`D_sf`, with both `partial_zeta D_sf` and `partial_chi D_sf` identically zero.
Thus the normalized two-body angular average equals the displayed polynomial;
no unintegrated virtual splitting function is being suppressed.

The producer obtains `C` from the published dot-product vertices.  The
independent verifier reconstructs all 25 graphs from invariant Källén
triangles and obtains the same `D` without importing the producer.

## Cut-to-log normalization

The normalization is fixed independently against Holdom's published off-shell
three-point logarithm.  For the cubic--quartic bubble, let `A_H` denote the
polynomial multiplying one external log in Holdom's formula.  A direct
double-pole cut gives

\[
 R_{\rm bubble}=-\frac13A_H.
\]

On the PS coupling locus

\[
 \lambda_3=-\lambda,
 \qquad \lambda_4=-\frac12\lambda^2,
\]

Holdom's coefficient is exactly one half of the physical cut coefficient,
apart from the universal `(4 pi)^-2`.  This control fixes both the sign and the
factor of two without using the desired four-point answer.

For the complete external four-point cut,

\[
 M_3M_5=(-2\lambda)(8\lambda^3)
 (\text{cubic}_{\rm red}A_5)
 =-16\lambda^4(\text{cubic}_{\rm red}A_5).
\]

The corresponding loop logarithm is consequently `-8 D` times
`lambda^4/(4 pi)^2`.  Crossing the selected external leg over all four legs
produces the polynomial `E_boundary` above.

## Four-mass projector

The universal low-degree tree identity is

\[
 (M_{\rm tree}^{\rm red})^{(2)}
 =\frac12\sum_{i<j}x_ix_j.
\]

Both this tree term and `E_boundary` have mass degree two.  Their interference
therefore begins at degree four.  As in the hard-log calculation, derivatives
of the analytic phase density cannot enter the fourfold top slot; only

\[
 \Phi_0=\frac1{256\pi^2s}
\]

contributes.

The square-free multiplication gives weight `12` to every external log.  The
physical interference contributes an additional factor

\[
 2\times4=8,
\]

from `Mtree=4 lambda^2 Mtree_red` and the complex-conjugate interference.
Thus

\[
 \frac{12\cdot8}{16\cdot256}=\frac3{128},
\]

which is the boxed rate coefficient.

## Regulator response and the remaining gluing problem

Under independent rescalings

\[
 x_i\longmapsto c_ix_i,
\]

the logarithms shift by `Li -> Li-log(ci)`, so

\[
 \Delta\frac{d\sigma_{\rm boundary,log}}{d\Omega}
 =-\frac{3\lambda^6}{128\pi^4s}
 \sum_i\log c_i.
\]

For a common rescaling this becomes

\[
 -\frac{3\lambda^6}{32\pi^4s}\log c.
\]

The real threshold has a different declared response,
`-(3/8) log(c_pair)`, before its omitted phase-space normalization.  These
numbers must not yet be compared:

- the virtual four-leg carrier contains a recombined parent mass and three
  spectator masses;
- the real five-leg carrier contains two daughter masses and three spectator
  masses;
- the real certificate fixes one splitting fraction through its hard
  invariant fixture rather than integrating the full inner two-body angle;
- identical-particle collinear pair multiplicities have not been assembled.

Choosing a relation between the parent regulator and the two daughter
regulators would change the apparent comparison.  That relation must be part
of a declared common infrared prescription, not chosen after seeing the
coefficients.

## What this establishes—and what it does not

Established:

- the complete external-mass logarithmic cut through the degree needed by the
  BT fourfold projector;
- its exact square-free loop polynomial;
- the projected rate coefficient `3/128` for each of four external logs; and
- the exact response to independent virtual regulator rescalings.

Not established:

- cancellation or noncancellation with the full real channel;
- universality away from the declared physical collinear family;
- the full splitting-fraction and inner-angle integral;
- a canonical four-to-five-leg regulator map;
- cut-free finite and counterterm contributions;
- a physical NLO probability or beyond-tree positivity theorem;
- a tensor, BRST, or gravitational lift; or
- anything `LORENTZIAN-CAUSAL`.

Bateman--Turok Appendix B supplies the vertices and Eq. (13) the external
projector.  Holdom's off-shell three-point logarithm is used only as an
independent normalization calibration.  The boundary coefficient is this
repository's result; no literature-priority claim is made.

## Verification

All symbolic processes are run sequentially under a 500,000 KB virtual-memory
cap:

```text
ulimit -v 500000; python3 reverse_physics/bt_external_mass_boundary_log_jet.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_external_mass_boundary_log_jet.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_external_mass_boundary_log_jet
```

Final scoped receipt (2026-08-10):

| Tier | Command | Time | Peak RSS | Result |
|---|---|---:|---:|---|
| 0 | `py_compile` producer, verifier, and test | 0.03 s | 15,188 KB | PASS |
| 0 | `json.tool` certificate | 0.02 s | 13,972 KB | PASS |
| 0 | `json.tool` schema | 0.02 s | 13,996 KB | PASS |
| 0 | scoped `git diff --check` | 0.00 s | 10,940 KB | PASS |
| 1 producer | dot-vertex cut plus symbolic `Q(tau,zeta,chi)` mass jet | 2.67 s | 71,332 KB | PASS, 20/20 |
| 1 independent | invariant-graph cut and independent symbolic mass jet | 2.29 s | 70,584 KB | PASS, 15/15 |
| 1 new tests | coefficient, angular-independence, and false-cancellation mutations | 9.50 s | 70,952 KB | PASS, 12/12 |

Every symbolic process ran sequentially under a 500,000 KB virtual-memory cap.
The exact splitting-fraction proof replaced an attempted unrestricted rational
field expansion that reached the cap without producing a result; that attempt
is not a pass and is not used.  The retained square-free architecture peaked
below 72 MB.

The unchanged predecessor inputs were accepted by exact SHA-256:

- five-point tree jet:
  `2ddecb1819a8cde12764dda5e097bab7c2ee9ffaacf66a3e4b1cd6567206b2c6`;
- independent-mass threshold:
  `e6b1872ca0fbcd6a51ccd8a44b018678678dc0121ede855911a8006b7af2a4a2`;
- hard-log projector/carrier result:
  `d3fdf83a77556906259acc798abd9b07958d2f328c7f422d31465f5f7c45562b`.

Tier 2 regeneration was unnecessary because no predecessor mathematical
input, schema, operator, or generated artifact changed; the new producer and
independent verifier consume those inputs content-addressedly.  Tier 3 was not
run because this is not a freeze, shared-core change, release, or explicit
full-suite request.  The advisory Science Forge shadow rail was not rerun
because its immediately preceding attempts on this stream stalled or aborted
at the same memory ceiling.  The cap was not raised, and no skipped or
incomplete rail is reported as passing.

CLOSE-OUT: SHORTFALL -- the full virtual external-mass logarithm is computed,
but the four-to-five-leg regulator gluing and full real splitting integral are
still required before a cancellation statement.

EVIDENCE: `reverse_physics/certificates/REVERSE_PHYSICS_BT_EXTERNAL_MASS_BOUNDARY_LOG_JET_V1.json`

MISSING-DEP: splitting-fraction-dependent real kernel plus an explicit common
parent/daughter regulator prescription

## Successor close-out (2026-08-10)

That gate is now resolved on the ordinary axis-compatible regulator class by
[`REVERSE_PHYSICS_BT_REAL_VIRTUAL_AXIS_GLUING_V1`](../certificates/REVERSE_PHYSICS_BT_REAL_VIRTUAL_AXIS_GLUING_V1.json).
The full real kernel is independent of splitting fraction and outer ratio;
after its inner-angle and identical-pair sum, its normalization shifts by
`+3*lambda^6*log(c)/(512*pi^4*s)`.  Every physical axis-compatible parent map,
including the pair threshold, gives zero constant virtual response.  Thus the
logarithmic terms do not cancel on that declared class.  Distributional,
dressed-state, enlarged-degenerate-state, and resummed architectures remain
open.
