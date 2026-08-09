# Bateman--Turok five-point collinear boundary layer

**Result:** `COEFFICIENT_COMPUTED`

**Dependency:** `REDUCED-MODE`

**Certificate:**
[`REVERSE_PHYSICS_BT_FIVE_POINT_COLLINEAR_LAYER_V1`](../certificates/REVERSE_PHYSICS_BT_FIVE_POINT_COLLINEAR_LAYER_V1.json)

## Result

The pointwise five-point result cannot simply be moved through three-body
phase-space integration.  A shrinking two-particle collinear window carries a
strictly nonzero contribution at total external-mass order five, exactly the
order at which the Bateman--Turok fivefold projector acts.

This is an obstruction to an interchange of operations, not a computation of
the physical `2->3` probability.  In particular, a common mass ray does not
isolate the mixed square-free coefficient `x0*x1*x2*x3*x4`.

Use the exact ray

\[
  (x_0,x_1,x_2,x_3,x_4)=\delta(1,4,9,16,25),
  \qquad t=s_0=\delta\tau,
\]

and hold the other cyclic invariants at

\[
  (s_1,s_2,s_3,s_4)=\left(\frac{32}{3},-8,16,-\frac83\right).
\]

For the complete normalized 25-tree amplitude
`A5=M5/(8 lambda^3)`, direct exact evaluation of the published dot-product
vertices gives

\[
 A_5(\delta,\tau)=\delta^2 C(\tau)+O(\delta^3),
 \qquad
 C(\tau)=-\frac{3(979\tau^2-5620\tau+5193)}{4\tau^2}.
\]

The independent verifier obtains the same function without constructing the
full rational amplitude.  It rewrites each cubic end as a Källén triangle,
builds the quartic vertex from pair channels, and solves every inverse double
propagator as a Laurent-series recurrence.  The order-zero and order-one
amplitude terms cancel exactly; the displayed order-two term remains.

## Why the phase-space boundary has order five

Factor three-body phase space through the selected pair `Q=q0+q1`, `Q^2=t`:

\[
 d\Phi_3(P;q_0,q_1,q_2)
 =\frac{dt}{2\pi}\,d\Phi_2(P;Q,q_2)\,d\Phi_2(Q;q_0,q_1).
\]

Up to a positive convention-dependent constant and the solid-angle element,
the inner two-body density is

\[
 J(t,x_0,x_1)=\frac{\sqrt{\lambda(t,x_0,x_1)}}{t},
\]

where

\[
 \lambda(a,b,c)=a^2+b^2+c^2-2ab-2ac-2bc.
\]

On the declared ray,

\[
 J(\delta\tau,\delta,4\delta)
 =\frac{\sqrt{(\tau-9)(\tau-1)}}{\tau}.
\]

The physical pair threshold is `tau=9`.  Since `dt=delta d tau`, the
normalized differential boundary slice scales as

\[
 dt\,J\,|A_5|^2
 =\delta^5 d\tau\,
   \frac{\sqrt{(\tau-9)(\tau-1)}}{\tau}|C(\tau)|^2
   +o(\delta^5).
\]

This is not just an order estimate.  On the compact above-threshold window
`10 <= tau <= 11`, both factors increase.  Indeed,

\[
 \frac{d|C|}{d\tau}
 =\frac34\frac{5620\tau-10386}{\tau^3}>0,
 \qquad
 \frac{dJ^2}{d\tau}=\frac{10\tau-18}{\tau^3}>0.
\]

At `tau=10`,

\[
 C(10)=-\frac{140679}{400},\qquad J(10)=\frac3{10}.
\]

Therefore the exact reduced slice obeys

\[
 \int_{10}^{11}d\tau\,J(\tau)|C(\tau)|^2
 \geq \frac{59371743123}{1600000}>0.
\]

Universal phase-space constants and the nonsingular outer two-body density
were deliberately omitted from this normalized inequality.  They are positive
and do not alter the scaling or the obstruction.

## The fixture is on a real scattering boundary

The hard invariants were not selected as an arbitrary complex point.  With
metric `diag(+1,-1,-1,-1)`, the all-incoming rational momenta

\[
\begin{aligned}
k_0&=(-2/3,0,0,-2/3),&k_1&=(-4/3,0,0,-4/3),\\
k_2&=(-2,0,0,2),&k_3&=(2,2,0,0),\\
k_4&=(2,-2,0,0)
\end{aligned}
\]

are individually null, sum to zero, and have cyclic invariants

\[
 (s_0,s_1,s_2,s_3,s_4)
 =\left(0,\frac{32}{3},-8,16,-\frac83\right).
\]

They represent `(-q0,-q1,-q2,p0,p1)` for a center-of-mass `2->3` process,
with `q0` and `q1` collinear.  The massive pair exists for every
`10 <= tau <= 11`: keeping the limiting momentum fraction `q0/Q=1/3`
requires the pair-rest-frame angle

\[
 \cos\theta_*=
 \frac{9-\tau}{3\sqrt{(\tau-9)(\tau-1)}},
\]

which lies strictly between `-1` and `1` on this window.  For sufficiently
small positive `delta`, both the incoming and outgoing threshold inequalities
are satisfied.  Choosing the pair transverse direction orthogonal to the beam
keeps the hard invariants equal to the displayed values up to `O(delta)`, which
does not change `C(tau)`.

This anchors the local algebra to a real phase-space boundary.  It still does
not replace the missing angular and Dalitz integrations; the certificate is
intentionally tagged `REDUCED-MODE`.

## What this says about the previous pointwise zero

The predecessor certificate proved

\[
 [x_0x_1x_2x_3x_4]|A_5|^2=0
\]

at fixed nonzero channel invariants.  There is no contradiction.  The full
ordinary amplitude has degree-two terms with repeated virtualities, even
though its square-free jet begins at degree three.  On the common ray those
terms survive, and the moving integration boundary supplies the fifth power
of `delta` through `dt`.

Consequently:

1. the fixed-channel square-free calculation does not dominate the collinear
   boundary uniformly;
2. differentiating first at fixed `t` omits a moving-boundary contribution at
   the projector's total scaling order; and
3. one must define the independent five-mass blow-up or a distributional
   finite part before saying whether the mixed BT derivative is zero,
   nonzero, or prescription-dependent.

The third point is the live gate.  The common-ray coefficient cannot decide
it because terms such as `x0^2 x1 x2` and a genuinely square-free term have the
same common-ray degree.  The Källén square root and the threshold
`(sqrt(x0)+sqrt(x1))^2` also make an ordinary multivariate Taylor argument
inapplicable at the corner.

## Mutation

Flipping the relative sign between the cubic--quartic and three-cubic topology
families changes the `tau=10` boundary amplitude from

\[
 A_5=-\frac{140679}{400}\delta^2+O(\delta^3)
\]

to

\[
 A_5^{\rm mut}=\frac{15848}{75}+O(\delta).
\]

The independent Laurent rail detects this jump from valuation two to zero.
The cancellation is therefore tied to the perfect-square Feynman-rule sign,
not to the selected phase-space ray.

## Claim boundary

This certificate does not establish:

- a nonzero mixed five-mass distribution;
- a completed five-body Bateman--Turok projector;
- a physical integrated `2->3` probability or cross section;
- a KLN cancellation, resummation, or dressed asymptotic state;
- positivity beyond tree level;
- scheme or field-redefinition invariance;
- a tensor/BRST gravitational lift; or
- anything `LORENTZIAN-CAUSAL`.

The source action, Wightman `delta-prime` prescription, generalized
`n`-particle projection, and collinear caveat are from
[Bateman--Turok v1](https://arxiv.org/abs/2607.00096v1).  The phase-space
normalization convention is cross-checked against the Particle Data Group's
[Kinematics review](https://pdg.lbl.gov/2025/reviews/rpp2025-rev-kinematics.pdf).
The correlated boundary coefficient and lower bound are this repository's
result; no literature-priority claim is made.

## Verification

```text
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 \
  reverse_physics/bt_five_point_collinear_layer.py --check
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 \
  reverse_physics/bt_five_point_collinear_layer.py --check-full
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 \
  reverse_physics/verify_bt_five_point_collinear_layer.py
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 \
  -m unittest -v reverse_physics.tests.test_bt_five_point_collinear_layer
```

Final scoped receipt (wall time measured with `/usr/bin/time`, 2026-08-09):

| Tier | Command | Time | Peak RSS | Result |
|---|---|---:|---:|---|
| 0 | `python3 -m py_compile` on producer, verifier, and test | 0.03 s | 15,268 KB | PASS |
| 0 | `python3 -m json.tool` on certificate and schema | 0.05 s | 14,184 KB | PASS |
| 1 fast producer | producer `--check` | 3.98 s | 73,732 KB | PASS, 12/12 |
| 1 independent | Laurent verifier | 0.45 s | 68,208 KB | PASS, 11/11 |
| 1 plus predecessors | collinear-layer, five-point-jet, and off-shell-obstruction tests | 14.71 s | 73,484 KB | PASS, 31/31 |
| affected exact symbolic | producer `--check-full` | 28.48 s | 108,388 KB | PASS, 12/12 |

The symbolic jobs ran sequentially.  The retained computation has only
`delta` and `tau` as symbolic variables and used at most 108,388 KB; no
unrestricted multivariate expansion was attempted.

The advisory command `env -u SF_PROGRAM ci/science-forge-shadow.sh` completed
in 6.47 s with exit 0 but is **not** recorded as a pass.  It reported the known
Forge binary/stdlib hash mismatch, the bridge audit's Python environment
without `sympy`, and corpus drift (1492 certificates versus the 2026-07-19
baseline of 976).  Those findings neither promote nor falsify this scoped
result.  Its 333,060 KB peak includes the advisory's concurrent census and is
not part of the sequential symbolic architecture.

The affected coefficient chain was run because a new mathematical artifact
and independent verifier were introduced.  Tier 3 was not run because this is
not a freeze, shared-core change, release, or explicit full-suite request.
Skipped Tier 3 work is not reported as a pass.

CLOSE-OUT: SHORTFALL -- the collinear layer is nonzero at projector total
order, so a distributional independent-mass prescription is now the exact
missing dependency for the physical `2->3` probability.

EVIDENCE: `reverse_physics/certificates/REVERSE_PHYSICS_BT_FIVE_POINT_COLLINEAR_LAYER_V1.json`

MISSING-DEP: distributional five-independent-mass phase-space prescription
