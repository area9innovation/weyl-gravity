# Bateman--Turok real kernel and axis-compatible regulator gluing

**Result:** `COEFFICIENT_COMPUTED`

**Dependency:** `REDUCED-MODE`

**Certificate:**
[`REVERSE_PHYSICS_BT_REAL_VIRTUAL_AXIS_GLUING_V1`](../certificates/REVERSE_PHYSICS_BT_REAL_VIRTUAL_AXIS_GLUING_V1.json)

## Result

The ordinary independent-mass regulator line encounters an exact obstruction
at the first real-plus-virtual collinear order.  The complete real final-state
kernel can now be integrated over its splitting angle and summed over all
three identical final-particle pairs.  Its finite-part normalization changes
by

\[
 \Delta_c\frac{d\sigma_{\rm real}}{d\Omega}
 =\frac{3\lambda^6}{512\pi^4s}\log c.
\]

The certified one-loop virtual boundary logarithm cannot cancel this change
under any **axis-compatible** recombination rule: when one daughter mass
regulator is removed, the virtual parent regulator must reduce to a finite,
nonzero multiple of the surviving daughter regulator.  The physical pair
threshold has exactly this property, and its virtual logarithm has zero
constant response to the daughter mass-ratio rescaling.

This is a scoped obstruction, not a proof that Bateman--Turok theory is
inconsistent.  It says that an ordinary off-shell, independent-mass
prescription with physical parent/daughter matching does not define a
regulator-independent fivefold projector on this complete logarithmic
carrier.  A distributional normalization, degenerate incoming-state sum,
dressed state, or resummation may change the architecture.

## Full symbolic real kernel

Let the two particles in the shrinking final-state pair have masses
`x0=delta*a0`, `x1=delta*a1`, pair invariant `t=delta*tau`, and let
`a2,a3,a4` denote the two incoming and remaining outgoing spectator masses.
For the complete 25-graph tree amplitude

\[
 A_5=\frac{M_5}{8\lambda^3}=\delta^2 C+O(\delta^3),
\]

the new symbolic calculation keeps both the inner splitting fraction `zeta`
and the outer scattering ratio `chi=-T/S` arbitrary.  In the exact
square-free spectator jet it obtains

\[
 [a_2a_3a_4]C^2=
 \frac{3(a_0-a_1)^2
 \left((a_0-a_1)^2-2\tau(a_0+a_1)\right)}{8\tau^3}.
\]

Both `zeta` and `chi` cancel identically.  An independent verifier rebuilds
the same result from invariant Källén vertices rather than the producer's
dot-product graph representation.  Since the scalar kernel has no remaining
inner orientation dependence, the complete inner integral is simply
`integral dOmega_inner=4*pi`.  The result remains differential in the
nonsingular outer two-body solid angle.

The pair-invariant threshold integral is therefore the previously certified
exact function

\[
 H(r)=\frac{-5r^3+3r^2-3r+5+6r(r+1)\log r}{16(r-1)},
 \qquad r=\frac{x_1}{x_0},
\]

with

\[
 H(r)=-\frac5{16}
 +r\left(-\frac38\log r-\frac18\right)
 +O(r^2\log r).
\]

Thus the reduced finite part changes by `-(3/8)log(c)` under
`r -> c*r`.

## Physical sign and normalization

There are five delta-prime Wightman factors in the `2->3` Born trace.  Since

\[
 \delta'(p^2)=-\left.\partial_{m^2}\delta(p^2-m^2)\right|_{m^2=0},
\]

the fivefold projector contributes the sign `(-1)^5=-1`.  This sign is
invisible in Bateman--Turok's printed four-leg Eq. (13), where the fourth
power is positive, but it matters here.

Using

\[
 d\Phi_3=\frac{dt}{2\pi}
 d\Phi_2^{\rm outer}d\Phi_2^{\rm inner},\qquad
 \frac{d\Phi_2}{d\Omega}
 =\frac{\sqrt{\Lambda}}{32\pi^2P^2},
\]

the rational factor before the inner-angle integral is

\[
 64\;\frac1{2!3!}\;\frac1{2s}\;\frac1{2\pi}
 \;\frac1{32\pi^2}\;\frac1{32\pi^2}
 =\frac1{768\pi^5s}.
\]

Here `64` comes from `|M5|^2=64 lambda^6 A5^2`.  Integrating the inner solid
angle gives `1/(192*pi^4*s)` for one labeled pair.  Combining it with the
fivefold sign and the reduced `-(3/8)log(c)` shift gives

\[
 \Delta_c\frac{d\sigma_{\rm real,pair}}{d\Omega}
 =\frac{\lambda^6}{512\pi^4s}\log c.
\]

The outgoing projector contains `1/3!`, and the three-particle final state has
three unordered pair boundaries.  Summing those regions gives the displayed
`3/512` coefficient.  This is also a check that the sign is physically
sensible: `H(0)=-5/16`, so the leading fivefold-projected real boundary has a
positive sign.

## Axis-compatible parent/daughter gluing

Let `G(x,y)` be the virtual parent mass-squared regulator assigned to two real
daughter regulators.  The declared ordinary class is

\[
 G(x,y)=x\,g(y/x),\qquad g\text{ continuous at }0,
 \quad 0<|g(0)|<\infty.
\]

This is the minimal axis-compatibility condition: when the second daughter
regulator is removed, the parent reduces to a finite nonzero multiple of the
surviving daughter's regulator.  For fixed `c>0`, continuity at the axis gives

\[
 \frac{G(x,cy)}{G(x,y)}
 =\frac{g(cr)}{g(r)}\longrightarrow1,
 \qquad r=y/x\longrightarrow0.
\]

Consequently

\[
 \Delta_c\log\frac{-\mu^2}{G}=0
\]

at constant order.  The same is true for every continuous cut-free term and
every local analytic counterterm.  The hard Mandelstam-ratio logarithm already
had zero daughter-ratio response, while the complete external-boundary result
is

\[
 \frac{d\sigma_{\rm virt,boundary}}{d\Omega}
 =\frac{3\lambda^6}{128\pi^4s}
 \sum_{i=1}^4\log\frac{-\mu^2}{X_i}.
\]

Therefore the complete logarithmic virtual response is zero on this gluing
class, whereas the real response is nonzero.

The physical threshold is an explicit member:

\[
 G_{\rm thr}(x,y)=(\sqrt{x}+\sqrt{y})^2,
\]

for which

\[
 \frac{G_{\rm thr}(x,cy)}{G_{\rm thr}(x,y)}
 =\frac{(1+\sqrt{cr})^2}{(1+\sqrt r)^2}\longrightarrow1.
\]

The independent rail makes the substitution `r=u^2`, `c=v^2`, reducing this
limit to exact rational substitution at `u=0`.

## Decisive mutation and meaning

Cancellation can be manufactured if the axis condition is abandoned.  For
one pair, take

\[
 G_{\rm mut}(x,y)=x^{11/12}y^{1/12}.
\]

Then the virtual logarithm shifts by
`-lambda^6*log(c)/(512*pi^4*s)`, exactly opposing the real per-pair shift.  But
`G_mut(x,0)=0`: removing an already vanishing daughter also removes the parent
regulator, so it does not extend the ordinary parent state continuously to the
axis.  The verifier requires this mutation to remain outside the theorem's
class.  This demonstrates both that the obstruction is nontrivial and that it
is not an unrestricted no-go theorem.

In normal language: the real calculation remembers how quickly one tiny
daughter mass is taken to zero relative to the other.  A physically recombined
virtual particle does not remember that ratio once the smaller daughter has
disappeared.  Their regulator dependences therefore live in different
variables and cannot cancel under ordinary threshold matching.

## Claim boundary and next architecture

Established on the declared carrier:

- the general collinear real kernel, including exact splitting-fraction and
  outer-ratio independence;
- the complete inner-angle factor;
- all three identical final-pair boundaries;
- the real finite-part response with its BT sign and physical normalization;
- the complete logarithmic virtual response under every axis-compatible
  gluing; and
- exact noncancellation of those normalization responses.

Not established:

- a complete NLO quotient trace or physical probability;
- failure of distributional, dressed-state, enlarged-degenerate-state, or
  resummed constructions;
- initial-state collinear completion;
- positivity or unitarity beyond the published tree result;
- a tensor/BRST or Weyl-gravity lift; or
- anything `LORENTZIAN-CAUSAL`.

The ordinary axis-compatible independent-mass route should therefore stop.
The next calculation must change architecture explicitly: derive a
distributional extension from the generalized Born rule, include degenerate
incoming/dressed states, or resum the collinear sector before evaluating the
positive quotient trace.

The action, delta-prime prescription, `1/n!` projectors, and dot-product
vertices are from
[Bateman--Turok v1](https://arxiv.org/abs/2607.00096v1).  The full symbolic
real kernel, normalization ledger, regulator-gluing class, and scoped
noncancellation theorem are repository results.  No literature-priority claim
is made.

## Verification

```text
ulimit -v 500000; python3 reverse_physics/bt_real_virtual_axis_gluing.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_real_virtual_axis_gluing.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_real_virtual_axis_gluing
```

Both symbolic rails run sequentially under the 500,000 KB virtual-memory cap.

Final scoped receipt (2026-08-10):

| Tier | Command | Time | Peak RSS | Result |
|---|---|---:|---:|---|
| 0 | `py_compile` producer, verifier, and test | 0.02 s | 14,692 KB | PASS |
| 0 | `json.tool` certificate | 0.02 s | 13,948 KB | PASS |
| 0 | `json.tool` schema | 0.02 s | 13,748 KB | PASS |
| 1 producer | dot-vertex three-spectator symbolic kernel and gluing ledger | 10.90 s | 71,228 KB | PASS, 20/20 |
| 1 independent | invariant-Källén graph kernel and rational threshold map | 11.12 s | 74,180 KB | PASS, 14/14 |
| 1 new tests | normalization and false-cancellation mutations | 22.57 s | 74,636 KB | PASS, 10/10 |

No symbolic processes overlap, and the cap was never raised.  The first test
attempt redundantly ran the independent symbolic kernel even after a strict
schema mutation had already failed; it was terminated by the execution rail
before completing and is not a pass.  The verifier now fails closed
immediately on invalid schema, after which the complete test suite passes in
under 23 seconds.

Tier 2 predecessor regeneration is unnecessary because all mathematical
inputs are unchanged and content-addressed; both new rails independently
rebuild the consumed kernel.  Tier 3 is not required because this result is
neither a freeze, release, nor shared-core change.  A skipped higher tier is
not a pass.

The advisory `s-f work check` could not run because the concurrently changed
Science Forge source failed to rebuild its `sfc` binary.  It is not recorded
as a pass.  The repository's explicit-path manual fallback was used: the
scoped diff, path list, structured files, and exact staged content are audited
before commit without touching the unrelated shared-tree edits.

CLOSE-OUT: OBSTRUCTED -- the ordinary independent-mass,
axis-compatible regulator architecture does not cancel its first complete
final-state collinear logarithmic response.

EVIDENCE: `reverse_physics/certificates/REVERSE_PHYSICS_BT_REAL_VIRTUAL_AXIS_GLUING_V1.json`

NEXT: change infrared architecture before attempting the quotient-trace
positivity test.

## Paper adoption (2026-08-10)

The result is now incorporated into the programme papers without enlarging its
claim boundary:

- Paper 05 records the coefficient and gluing obstruction as a
  certificate-backed successor remark, replaces the stale statement that the
  scalar loop question is merely deferred, and points the next scalar step to
  a changed infrared/asymptotic-state architecture.
- Paper 06 records only the non-transfer boundary: the scalar result changes
  none of its Einstein--Weyl tree theorems, but any gravitational
  Bateman--Turok completion must construct and verify its own infrared gluing
  on the BRST quotient.

Both PDFs were rebuilt through at least two passes under the 500,000 KB
virtual-memory cap.  The
final Paper 05 pass took 0.38 s and 50,572 KB; the final Paper 06 pass took
0.45 s and 50,772 KB.  Neither log contains undefined references or rerun
warnings.  Paper 06 has no overfull boxes; Paper 05 retains only three small
pre-existing overfull boxes (at most 4.21 pt).  The focused certificate suite
passed 10/10 in 21.62 s at 74,580 KB.  PDF text extraction independently
confirmed the coefficient, dependency tag, axis-compatible scope, and
non-transfer language in the rendered artifacts.

Paper 19 was not changed: it already contains unrelated uncommitted work and
the scalar quantum result is not part of its galactic-rotation theorem chain.
