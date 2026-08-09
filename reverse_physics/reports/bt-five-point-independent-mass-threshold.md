# Bateman--Turok independent-mass threshold obstruction

**Result:** `COEFFICIENT_COMPUTED`

**Dependency:** `REDUCED-MODE`

**Certificate:**
[`REVERSE_PHYSICS_BT_FIVE_POINT_INDEPENDENT_MASS_THRESHOLD_V1`](../certificates/REVERSE_PHYSICS_BT_FIVE_POINT_INDEPENDENT_MASS_THRESHOLD_V1.json)

## Result

The five-point collinear boundary does not possess an ordinary independent
five-mass derivative.  After three exact spectator-mass derivatives, the two
remaining masses produce a logarithmically divergent mixed slope.  A finite
part can be assigned, but its value changes when the ratio-cutoff
normalization is rescaled.

This turns the previous common-ray warning into an exact obstruction on the
declared reduced carrier.  It does not establish that the completed
Bateman--Turok observable is ambiguous: a virtual contribution or physical
renormalization condition may cancel or fix the finite part.

## Arbitrary-mass amplitude coefficient

Let

\[
 x_i=\delta a_i,\qquad t=s_0=\delta\tau,
\]

with the nonsingular cyclic invariants held at the real limiting values used
by the predecessor.  The complete normalized 25-tree amplitude has

\[
 A_5=\delta^2 C(a_0,\ldots,a_4;\tau)+O(\delta^3)
\]

for arbitrary mass ratios.  The producer derives `C` directly from the
published cubic and quartic dot-product vertices.  The verifier independently
uses invariant Källén triangles and a Laurent recurrence for the double
propagators.  Both prove that the order-zero and order-one terms vanish.

The full coefficient is recorded canonically in the certificate.  The
important simplification occurs after squaring and selecting the three
spectator masses:

\[
 [a_2a_3a_4]C^2
 =\frac{3(a_0-a_1)^2
 \bigl((a_0-a_1)^2-2\tau(a_0+a_1)\bigr)}{8\tau^3}.
\]

The spectator projection is therefore exact before any threshold integral is
performed.  Higher homogeneous terms in the amplitude contribute one or more
additional powers of the common scale and cannot change the leading
two-mass obstruction below.

## Exact threshold integral

Write the two remaining masses as

\[
 x_0=\epsilon,\qquad x_1=r\epsilon,qquad r=m^2>0,
\]

and scale the pair invariant as `t=epsilon u`.  The physical lower endpoint is

\[
 u_+=(1+m)^2.
\]

Including the inner two-body Källén density and taking the upper endpoint to
infinity in the homogeneous region gives

\[
 H(r)=\int_{u_+}^{\infty}du\,
 \frac{3(1-r)^2((1-r)^2-2u(1+r))}{8u^4}
 \sqrt{(u-(1+m)^2)(u-(1-m)^2)}.
\]

The producer rationalizes the root with `q=tanh(y/2)`.  The independent rail
uses `z=exp(-y)`.  Both reduce the integral to a rational function and obtain

\[
 H(r)=
 \frac{-5r^3+3r^2-3r+5+6r(r+1)\log r}{16(r-1)},
 \qquad H(1)=0.
\]

The fixed physical upper limit differs from infinity by terms of higher
homogeneous order; it cannot alter this leading threshold function.

## Why the independent derivative does not exist

Near the axis `r=0`,

\[
 H(r)=-\frac5{16}
 +r\left(-\frac38\log r-\frac18\right)
 +O(r^2\log r).
\]

Thus the candidate mixed coefficient obtained from the slope quotient is

\[
 B_\varepsilon=\frac{H(\varepsilon)-H(0)}{\varepsilon}
 =-\frac38\log\varepsilon-\frac18
 +O(\varepsilon\log\varepsilon),
\]

which diverges to positive infinity.  Equivalently, the spectator-projected
threshold function contains

\[
 -\frac38 x_0x_1\log(x_1/x_0).
\]

It therefore has no ordinary joint quadratic jet at the two-mass corner.  As
the other three derivatives were already taken exactly, the reduced
collinear contribution supplies no ordinary fivefold mixed mass derivative.

This conclusion is stronger than observing different values along two rays.
Any polynomial of degree at most two is annihilated on the four rays
`r=(0,1,4,9)` by weights `(-10,15,-6,1)`.  The exact threshold values give

\[
 \Delta=\frac{45}{4}-30\log2+\frac{135}{16}\log3.
\]

Using four terms of the positive atanh series for each logarithm gives the
fully rational enclosure

\[
 -\frac{13144501}{47029248}
 <\Delta<
 -\frac{716497}{2612736}<0.
\]

No floating-point sign decision or transcendence theorem enters this
certificate.

## Finite-part ambiguity

One may subtract the logarithmic divergence.  For a ratio-cutoff
normalization `c>0`, define

\[
 \operatorname{FP}_c=
 \lim_{\varepsilon\to0}
 \left[B_{c\varepsilon}+\frac38\log\varepsilon\right].
\]

Then

\[
 \operatorname{FP}_c=-\frac18-\frac38\log c.
\]

The reference choice `c=1` gives `-1/8`, while `c=4` shifts it by
`-3/4 log 2`.  Both remove the same divergence.  Hence locality of the
subtraction alone does not pick a value; an additional physical condition is
required.

This is the concrete real-emission datum the loop calculation must meet.  A
four-leg virtual logarithm with the opposite coefficient could cancel the
ambiguity, or a common renormalization prescription could fix it.  Without
that calculation, neither outcome is certified.

## Mutation and fail-closed boundary

The verifier rejects a certificate that promotes the finite part from
`REGULATOR_NORMALIZATION_DEPENDENT` to `CANONICAL`.  It also requires the full
five-body projector and physical rate to remain unconstructed.

This result does not establish:

- that Bateman--Turok theory remains ambiguous after real--virtual completion;
- a value for the physical five-mass distribution;
- a completed `2->3` probability or cross section;
- absence of a KLN, resummation, or dressed-state cancellation;
- positivity or unitarity beyond tree level;
- a tensor/BRST gravitational lift; or
- anything `LORENTZIAN-CAUSAL`.

The action, delta-prime projection, and stated collinear obstruction are from
[Bateman--Turok v1](https://arxiv.org/abs/2607.00096v1).  The arbitrary-mass
amplitude reduction, threshold function, logarithmic obstruction, and
finite-part shift are this repository's results.  No literature-priority
claim is made.

## Verification

```text
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 \
  reverse_physics/bt_five_point_independent_mass_threshold.py --check
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 \
  reverse_physics/verify_bt_five_point_independent_mass_threshold.py
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 \
  -m unittest -v reverse_physics.tests.test_bt_five_point_independent_mass_threshold
```

Final scoped receipt (wall time measured with `/usr/bin/time`, 2026-08-09):

| Tier | Command | Time | Peak RSS | Result |
|---|---|---:|---:|---|
| 0 | `python3 -m py_compile` on producer, verifier, and test | 0.03 s | 15,420 KB | PASS |
| 0 | `python3 -m json.tool` on certificate and schema | 0.11 s | 14,080 KB | PASS |
| 1 producer | dot-vertex producer `--check` | 6.03 s | 86,640 KB | PASS, 12/12 |
| 1 independent | invariant-vertex and `z=exp(-y)` verifier | 9.14 s | 95,328 KB | PASS, 11/11 |
| 1 new tests | independent-mass threshold tests | 34.63 s | 95,804 KB | PASS, 11/11 |
| affected predecessors | collinear-layer, five-point-jet, and off-shell-obstruction tests | 13.09 s | 73,552 KB | PASS, 31/31 |

Both symbolic integrations ran sequentially under a 500,000 KB virtual-memory
cap.  The retained paths peaked below 96 MB.  No unrestricted multivariate
expansion was attempted.

The advisory command `env -u SF_PROGRAM ci/science-forge-shadow.sh` completed
in 6.16 s with exit 0 but is **not** recorded as a pass.  It reported the
known Forge binary/stdlib hash mismatch, the bridge audit's Python environment
without `sympy`, and corpus drift (1493 certificates versus the 2026-07-19
baseline of 976).  Those findings neither promote nor falsify this scoped
result.  Its 325,936 KB peak includes the advisory's concurrent census and is
not part of the sequential symbolic architecture.

The affected coefficient chain was run because the independent-mass
threshold changes the interpretation of the preceding boundary certificate.
Tier 3 was not run because this is not a freeze, shared-core change, release,
or explicit full-suite request.  Skipped Tier 3 work is not reported as a
pass.

CLOSE-OUT: SHORTFALL -- the reduced real threshold has no ordinary mixed
five-mass derivative and its finite part is normalization-dependent; the
four-leg virtual jet is the next object that can cancel or fix it.

EVIDENCE: `reverse_physics/certificates/REVERSE_PHYSICS_BT_FIVE_POINT_INDEPENDENT_MASS_THRESHOLD_V1.json`

MISSING-DEP: renormalized four-leg loop jet on the same mass prescription

## Successor checkpoint

The ultraviolet-algebraic part of that dependency is now closed by
[`REVERSE_PHYSICS_BT_PERFECT_SQUARE_RG_SEPARATRIX_V1`](../certificates/REVERSE_PHYSICS_BT_PERFECT_SQUARE_RG_SEPARATRIX_V1.json):
the PS coupling locus is exactly preserved by Holdom's published one-loop beta
functions, and its counterterm closes on the PS action.  The successor also
proves that those RG data and the published on-shell cuts do not determine the
finite independent-external-mass top jet.  Thus the missing dependency is now
the explicit finite bubble, triangle, and box interference jet, not UV
renormalizability of the one-coupling locus.
