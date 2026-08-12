# BT tagged-connected compact-packet interference

Certificate:
`REVERSE_PHYSICS_BT_TAGGED_CONNECTED_COMPACT_PACKET_INTERFERENCE_V1`.

Dependencies: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`. Lifecycle:
`COEFFICIENT_COMPUTED`.

## Result

The finite-box factor `1/(2 E_s V)` is the measure of one momentum cell. It
does not make the tagged/connected tree interference vanish for a fixed
physical compact packet. As the box is refined, such a packet contains a
number of coherent modes proportional to `V`, and their double sum exactly
compensates the single-mode suppression.

For normalized incoming and outgoing positive spectator packets `f` and `g`,
put

\[
 c_{gf}=\langle g,f\rangle_\nu,
 \qquad
 C_{gf}(T)=\langle g,\mathcal W_{\kappa,T}f\rangle_\nu,
\]

where

\[
 d\nu(\mathbf p)=\frac{d^3\mathbf p}{2E_{\mathbf p}}
\]

is the public BT one-particle measure and `mathcal W` is the connected
ten-channel kernel after the common active-packet contraction. The exact
relative tree cross is

\[
 \boxed{
 \frac{q_{\rm cross}^{(6)}[g,f]}{q_{\rm tag}^{(4)}}
 =\frac{2\sqrt2\lambda^2}{3}
 \operatorname{Re}\!\left(\overline{c_{gf}}C_{gf}(T)\right).}
\]

For the same spectator packet, `g=f`, the identity overlap is one. At the
certified scaled tagged fixture this gives

\[
 \boxed{
 q_{\rm cross}^{(6)}[f,f]
 =\frac{25\sqrt2\lambda^6\Delta\Omega}
 {1024\pi^2\kappa^2\operatorname{Area}}
 \operatorname{Re}C_{ff}(T).}
\]

This is a dimensionless, box-independent compact-packet functional. It is not
a packet-independent number and it is not the complete order-`lambda^6`
probability.

## The compact positive spectator

Smear the public cross oscillators in the measure `dnu`. For a packet `f`,
the ghost-even positive combination is

\[
 u(f)=\frac{|\Omega,f\rangle+|\Upsilon,f\rangle}{\sqrt2}.
\]

The off-diagonal CCR gives

\[
 \langle u(g),u(f)\rangle_K=\langle g,f\rangle_\nu.
\]

Thus `||f||=1` makes `u(f)` a normalized Krein-positive one-particle state,
and the unchanged spectator identity contributes exactly one when the same
packet is prepared and detected. This is the continuum version of the raw
box identity contraction canceling its two external normalizers.

## The connected packet kernel

On the certified tagged carrier the six masks containing exactly one tag
label are

```text
R = {7,19,21,14,26,28},
```

and the remaining four are

```text
N = {11,13,25,22}.
```

The incidence theorem gives weight five on `R` and weight six on `N`. After
contracting the same normalized active preparation and detector used for the
leading tagged probability, define

\[
 \mathcal W_{\kappa,T}(k,p)=
 \operatorname{Re}\left(
 5\sum_{A\in R}\beta_{A,T}(k,p)
 +6\sum_{A\in N}\beta_{A,T}(k,p)\right),
\]

with

\[
 \beta_{A,T}=\frac{F_T(\delta_A)}{D_A},
 \qquad
 F_T(\delta)=\int_0^T e^{i\delta t}\,dt.
\]

Choose compact hard packet supports on which every oriented denominator obeys
`D_A>=d0>0`. Since `|F_T|<=T` and the total absolute incidence weight is

\[
 6\cdot5+4\cdot6=54,
\]

we have

\[
 |\mathcal W_{\kappa,T}(k,p)|\le\frac{54T}{d_0}.
\]

For support measures `mu_in` and `mu_out`, Cauchy--Schwarz therefore gives

\[
 |C_{gf}(T)|\le
 \frac{54T}{d_0}\sqrt{\mu_{\rm in}\mu_{\rm out}}.
\]

The kernel is bounded on a finite-measure product and hence
Hilbert--Schmidt. The compact packet functional is finite, and smooth packet
approximants converge in it.

## A nonzero physical packet exists

At the exact tagged fixture,

\[
 \mathcal W_{\kappa,T}(p_*,p_*)
 =W_\kappa(T)=\frac{w(\kappa T)}{\kappa^2}>0
\]

for every fixed `T>0`. The finite-time kernel is continuous there: the
resonant function `F_T(delta)` is entire in `delta`, and all denominators
remain nonzero on the hard tube. For each fixed positive `T`, continuity
therefore supplies a sufficiently small product neighborhood on which the
real kernel remains positive. Any nonzero, nonnegative normalized compact
packet supported there has

\[
 C_{ff}(T)>0.
\]

The tree interference consequently survives on genuine compact packets. This
is a local finite-time existence theorem, not a uniform statement as
`T -> infinity`.

## Why the single-mode limit was misleading

Partition a fixed compact spectator support into `N` equal cells of
`dnu`-measure `h`. The normalized cell indicators are

\[
 e_i=\frac{\mathbf1_{C_i}}{\sqrt h},
\]

and the uniform normalized packet is

\[
 f_N=\frac1{\sqrt N}\sum_{i=1}^Ne_i,
 \qquad \mu=Nh.
\]

For cell-sampled kernel values `W_ij`, the connected integral-operator matrix
is

\[
 B_{ij}=hW_{ij}.
\]

Consequently

\[
 \langle f_N,Bf_N\rangle
 =\frac hN\sum_{i,j=1}^N W_{ij}.
\]

For a constant kernel this is exactly

\[
 \frac hN N^2W=NhW=\mu W.
\]

There are now two inequivalent limits:

- A single box mode has `N=1` and
  `h=1/(2E_sV)=1/N_s`, so it gives `W/N_s` and vanishes as `1/V`.
- A fixed physical packet keeps `mu=Nh` fixed. Then `N` grows in proportion
  to `V`, and its matrix element stays `mu W` for the constant kernel.

For a continuous nonconstant kernel, the cell expression converges to

\[
 \frac1\mu\int_{S\times S}
 \mathcal W_{\kappa,T}(k,p)\,d\nu(k)d\nu(p),
\]

which is generally finite and nonzero. The off-diagonal cells are essential;
retaining only the diagonal would incorrectly reproduce a `1/V` loss.

The earlier finite-volume theorem remains correct for the family it studied.
What changes is its interpretation: holding one lattice label fixed while
`V` grows is not the continuum approximation of a fixed compact packet. It
is a sequence of increasingly sharp momentum states.

## What this changes physically

The resonant tree contribution is no longer merely a point kernel or a
single-box-mode artifact. It defines a finite compact-packet interference
functional and is strictly positive for a nonempty family of hard tagged
packets at every declared finite positive time.

This makes the remaining obstruction sharper. The tree term cannot be
dropped by taking a continuum box limit. It must be combined with the other
terms at the same perturbative order—or canceled by a dynamically derived
source/survival mechanism.

There is also a prior bookkeeping gate. An order-`lambda` correction to the
dressed source can interfere with the leading order-`lambda^2` tagged
amplitude at probability order `lambda^5`. Until that term is derived or
proved absent on the selected ghost-even packet, a calculation advertised as
the complete order-`lambda^6` probability would already have skipped the
first unresolved correction.

## Claim boundary

This result is the compact-packet tree cross functional only. It does not
establish a canonical packet or numerical rate, the complete
order-`lambda^6` probability, the possible order-`lambda^5` source term, the
active one-loop term, survival or virtual completion, forward/collinear or
KLN completion, an all-time operator, general Eq. (19), gravity or metric
BV--BRST transfer, or anything `LORENTZIAN-CAUSAL`. No literature-priority
claim is made.

## Verification receipt

- Tier 0: the changed Python files byte-compile and the four structured JSON
  files parse in the combined capped edit check (peak RSS `15,076 KB`); the
  scoped diff passes `git diff --check`. Paper 05 compiles twice, with its
  final pass taking `0.48 s`, peak RSS `50,700 KB`, and producing 56 pages
  (`643,367` bytes). Paper 06 compiles twice, with its final pass taking
  `0.49 s`, peak RSS `50,776 KB`, and producing 53 pages (`631,392` bytes).
  The new paragraphs introduce no overfull boxes; both papers retain only
  their previously recorded overfull paragraphs.
- Tier 1: the exact producer passes 29/29 checks, the independent verifier
  passes 30/30 checks, and 17 tests including 16 adversarial mutations pass.
  Their elapsed times and peak RSS values are respectively `0.28 s` and
  `64,480 KB`, `0.09 s` and `23,592 KB`, and `0.15 s` and `24,868 KB`.
  Every scientific rail runs sequentially under a 500 MB virtual-memory cap.
- Tier 2: all mathematical inputs are unchanged and content addressed. Both
  rails verify their hashes and passing states; no predecessor producer was
  rerun.
- Tier 3 was not run because no shared algebra, freeze, release, QME state,
  residual transfer, or Lorentzian claim changes.
- The Science Forge fold accepts 1,503 nodes including the work item and
  append-only DONE event, with zero invalid items and zero malformed events.

Commands:

```text
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_tagged_connected_compact_packet_interference.py --write --check
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_tagged_connected_compact_packet_interference.py
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_tagged_connected_compact_packet_interference
```

CLOSE-OUT: DONE — the normalized compact spectator carrier, exact tree-cross
functional, finite bound, positive packet witness, box refinement and fixed-
packet continuum limit are certified. The source correction is the next
physical gate.

EVIDENCE:
`reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_CONNECTED_COMPACT_PACKET_INTERFERENCE_V1.json`
