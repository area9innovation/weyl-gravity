# BT compact-wavepacket Hamiltonian probability

Certificate:
`REVERSE_PHYSICS_BT_COMPACT_WAVEPACKET_HAMILTONIAN_PROBABILITY_V1`.

Dependencies: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`. Lifecycle:
`COEFFICIENT_COMPUTED`.

## Result

The detector strength for the selected compact dressed scalar packet is no
longer an independently fitted number.  On one compact incoming/outgoing
neighborhood crossing the isolated positive-energy channel `B=11`, it is the
explicit finite-time integral operator obtained from the public BT two-quartic
Hamiltonian.  Its leading amplitude is bounded, its click effect is an adjoint
square, and a stated small-coupling condition makes the complementary no-click
effect positive.

For a normalized incoming packet `F` in the declared positive scalar source,
the resulting probability is

\[
 q_{\rm click}=16\lambda^8\|K_{B,T}F\|^2,
 \qquad q_{\rm no}=1-q_{\rm click}.
\]

This closes the fixed-strength placeholder for this finite-time, single-channel
packet experiment.  It does not prove general BT Eq. (19), a ten-channel or
all-time scattering probability, a loop theorem, or a gravity result.

## Full five-dimensional phase measure

Fix the total center-of-momentum four-vector to
`P=(16/5,0,0,0)`.  Three planar stereographic directions
`n(0),n(a),n(b)` determine the positive energies

\[
 E_0=\frac{8(1+ab)}{5ab},\qquad
 E_1=\frac{8(1+a^2)}{5a(a-b)},\qquad
 E_2=\frac{8(1+b^2)}{5b(b-a)},
\]

and `E0+E1+E2=16/5`.  A common orientation is represented by
`Rz(v) Rx(u) Rz(t)`.  Direct differentiation gives

\[
 \det\frac{\partial(E_0,E_1)}{\partial(a,b)}
 =-\frac{128(1+ab)}{25a^2b^2(a-b)^2}.
\]

The stereographic ZXZ Haar density is

\[
 dR=\frac{16|u|\,dt\,du\,dv}
 {(1+t^2)(1+u^2)^2(1+v^2)}.
\]

For labeled massless three-body phase space the invariant energy-orientation
form is `dE0 dE1 dR/8`.  The normalization is consistent with
`vol(SO(3))=8 pi^2` on one regular Euler chart and integrates over the energy
triangle to the standard total phase volume `P^2/(256 pi^3)`.  Consequently

\[
 d\mu=\frac{\rho(a,b,t,u,v)}{(2\pi)^5}
       \,da\,db\,dt\,du\,dv,
\]

where

\[
 \rho=
 \frac{256|(1+ab)u|}
 {25a^2b^2(a-b)^2(1+t^2)(1+u^2)^2(1+v^2)}.
\]

This is a chart density, not a value frozen at one point.  The producer
recovers the former fixture `rho=54/2125`.  The independent verifier instead
forms the full `9 x 5` chart Jacobian and the four conservation gradients using
rational automatic differentiation.  Exact coarea determinants agree with
the displayed formula at that fixture and three further points not used to
derive it:

\[
 \rho^2=\frac{576}{390625},\quad
 \frac{88510464}{152587890625},\quad
 \frac{10312216477696}{3243658447265625}.
\]

No floating-point rank or canonical-form calculation enters this check.

## A regular isolated shell neighborhood

The earlier shell fixture used an Euler-coordinate boundary for the incoming
frame.  A common rational rotation `Rx(15/16)` moves it into two regular chart
centers without changing any Lorentz invariant:

\[
 x_0=(2,-2,0,15/16,0),\qquad
 y_0=(2,-2,105/73,2,1/3).
\]

At this pair, channel `B=11` has

\[
 q_B=\left(1,\frac9{17},\frac{34436}{40885},
                -\frac{4152}{40885}\right),
 \qquad q_B^2=0,
 \qquad q_B^0=1,
\]

while the other nine unordered three-three channel invariants are nonzero.
Continuity therefore supplies compact regular neighborhoods `X,Y` and a
nonzero detector kernel `chi` supported where this channel alone crosses its
shell, `q_B^0>0`, and

\[
 D_B=q_B^0+|\mathbf q_B|\ge d_0>0.
\]

We normalize the detector acceptance by `|chi|<=1`.  This normalization is an
explicit hypothesis; omitting it would invalidate the stated operator bound.

## The finite-time Hamiltonian packet operator

Set

\[
 \delta_B=q_B^0-|\mathbf q_B|,
 \qquad
 q_B^2=\delta_BD_B,
 \qquad
 F_T(\delta)=\int_0^T e^{i\delta\tau}\,d\tau.
\]

The certified interaction-picture BT Hamiltonian cut replaces the covariant
pole on this sequential record by

\[
 \beta_{B,T}(y,x)=
 \chi(y,x)\frac{F_T(\delta_B(y,x))}{D_B(y,x)}.
\]

Thus

\[
 (K_{B,T}F)(y)=\int_X\beta_{B,T}(y,x)F(x)\,d\mu(x)
\]

maps `L2(X,dmu)` to `L2(Y,dmu)`.  Since
`|F_T(delta)|<=T`, the support hypotheses give

\[
 |\beta_{B,T}|\le\frac{T}{d_0},\qquad
 \|K_{B,T}\|_{\rm HS}^2
 \le\frac{T^2\mu(X)\mu(Y)}{d_0^2}.
\]

In particular the operator is Hilbert--Schmidt and hence bounded and compact.
At the exact shell center `F_T(0)=T` and `D_B=2`; choosing nonzero `chi` and a
packet supported sufficiently near that center makes `K_{B,T}` nonzero.

## Positive click and no-click effects

On the certified four-dimensional positive ghost-even species frame, the
single-channel residue is

\[
 R_+=\frac14
 \begin{pmatrix}
 1&0&0&0\\
 0&1&1&0\\
 0&1&1&1\\
 0&1&1&1
 \end{pmatrix},
 \qquad G=R_+^TR_+.
\]

Its spectrum is

\[
 0,\quad\frac1{16},\quad
 \frac{2-\sqrt3}{8},\quad
 \frac{2+\sqrt3}{8},
\]

and the declared source vector has `G` expectation `1/16`.  The complete
leading selected-record amplitude is

\[
 A_{B,T}=16\lambda^4K_{B,T}\otimes R_+.
\]

Define

\[
 E_{\rm click}=A_{B,T}^*A_{B,T},\qquad
 E_{\rm no}=I-E_{\rm click}.
\]

The first operator is positive by construction.  The Hilbert--Schmidt bound
and the largest eigenvalue of `G` imply `E_no>=0` whenever

\[
 32(2+\sqrt3)\lambda^8
 \frac{T^2\mu(X)\mu(Y)}{d_0^2}\le1.
\]

The two effects then sum exactly to the identity.  This condition is
sufficient, not claimed optimal.

## Scalar affiliation and the meaning of “physical”

The incoming packet is a compact three-particle kernel on the previously
certified Gaussian image domain.  Hilbert--Schmidt kernels admit finite-rank
approximants, and their adjoint-square effects converge in trace norm.  The
same bounded energy multipliers used in the compact-source certificate pull
these approximants back coefficientwise through the formally two-sided
`R_t` on the declared detector ideal.  This affiliates the selected positive
BT experiment to an explicitly dressed perfect-square scalar source.

Because the amplitude begins at order `lambda^4`, an unknown order-`lambda`
correction to the source can first modify the displayed probability at order
`lambda^9`.  The `lambda^8` coefficient above is therefore protected at its
declared leading order.

Here “physical” means a normalized positive two-outcome experiment for a
selected dressed scalar preparation, with its strength derived from the BT
Hamiltonian.  It does not mean a symmetry-selected universal source, the
general projector identity in Eq. (19), a complete scattering operator, or a
metric-gravity observable.

## Failed exploratory routes

Two direct SymPy attempts to simplify the full five-symbol coarea determinant
exhausted the imposed 500 MB virtual-memory budget.  They ended with
`MemoryError` after about 41 seconds (`455268 KB` maximum RSS) and 40 seconds
(`456896 KB` maximum RSS), respectively.  A third expanding symbolic energy
route was stopped before comparable growth.  These attempts are recorded as
failed diagnostics, not as evidence.  The landed route replaces global
expression expansion by analytic factorization plus exact low-memory rational
automatic differentiation.

The exploratory inline commands were not retained as reusable producers and
are therefore not counted as verification receipts.

## Verification receipts

All successful rails were run sequentially with `ulimit -v 500000` and Python
`/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3`:

- producer and byte-drift check: `27/27`, pass, `0.49 s`, `70136 KB` maximum
  RSS;
- independent Fraction/coarea verifier: `26/26`, pass, `0.08 s`, `24148 KB`
  maximum RSS;
- ten tests, including nine fail-closed mutations: pass, `0.23 s`, `24484 KB`
  maximum RSS;
- final Paper 6 TeX pass: pass, `0.51 s`, `50620 KB` maximum RSS.  The log
  retains only the two overfull boxes already present before this edit; the new
  paragraph introduced none;
- direct Science Forge `import-program`: pass with `1481` nodes, `0` invalid
  items and `0` malformed events, `18.94 s`, `279580 KB` maximum RSS.  The Go
  runtime could not reserve its startup arena under `ulimit -v 500000`, so this
  non-symbolic planning check was rerun without that virtual-address cap while
  resident memory was measured.

The advisory `ci/science-forge-shadow.sh` rail also ran.  It exited zero by
design but is not recorded as a pass: the external Forge binary and current
stdlib have a pre-existing hash mismatch, the bridge audit stopped at Forge
error `E9118`, and the corpus census reported `1580` certificates against the
old `976` baseline.  Those external advisory findings neither verify nor
falsify this certificate and cause no lifecycle promotion.

After the final capped science rerun, Git's cached-diff check itself failed to
start its threaded `lstat` helper under the same virtual-memory limit.  The
read-only command was rerun outside that cap as
`git -c core.preloadindex=false diff --cached --check` and passed.  The failed
Git invocation is not counted as a science or edit-check pass.

Tier 0 consists of JSON parsing, Python compilation, TeX compilation after the
paper edit, `git diff --check`, and inspection of the exact staged diff.  Tier
1 is the three scoped rails above.  Tier 2 is satisfied by checking the pinned
predecessor hashes and their certified `checks.ok` fields; no predecessor
operator, schema, or generated input was changed.  Tier 3 is not run because
this package neither freezes the programme nor promotes a QME, residual, or
Lorentzian lifecycle state.

## Open gates

The next physical gate is to glue the ten compact channel-record operators
using a positive partition of unity and to classify pairwise and higher
simultaneous-shell intersections.  The distinct Eq. (19) route still needs a
source-affiliated ghost-conjugate orbit branch or a different physical
projector; the public regular perturbative branch remains obstructed at order
`lambda`.

This certificate does not establish:

- a canonical packet, duration, detector, acceptance region, rate, or cross
  section;
- coherent ten-channel gluing or intersection terms;
- the complete connected finite-time amplitude;
- an exact all-orders probability, Møller operator, LSZ map, or all-time
  `S`-operator;
- infrared removal in the ordinary massless Fock representation;
- the standard shift-invariant scalar projector or general BT Eq. (19);
- loop/KLN completion or all-order positivity;
- gravity, BV/BRST transfer, or anything `LORENTZIAN-CAUSAL`;
- literature priority.

CLOSE-OUT: DONE — an explicit BT-Hamiltonian compact-packet integral replaces the fitted detector strength for one leading finite-time physical-scalar channel, with exact measure, operator, positivity, scalar-affiliation and boundary certificates.
EVIDENCE: reverse_physics/certificates/REVERSE_PHYSICS_BT_COMPACT_WAVEPACKET_HAMILTONIAN_PROBABILITY_V1.json
