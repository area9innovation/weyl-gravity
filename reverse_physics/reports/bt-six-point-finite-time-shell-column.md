# BT six-point finite-time shell column

Certificate: `REVERSE_PHYSICS_BT_SIX_POINT_FINITE_TIME_SHELL_COLUMN_V1`

Dependencies: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`. Lifecycle:
`COEFFICIENT_COMPUTED`.

## Result

The exact isolated six-point pole has a square-integrable finite-time history
amplitude and an exactly normalized local survival completion. This is the
first continuous shell coordinate attached to the finite history-label
instrument. It remains a local reduced-mode column, not a global BT Møller
operator.

At the certified full-rank physical point, channel 11 has intermediate
momentum

\[
 q=\left(1,\frac9{17},-\frac4{85},-\frac{72}{85}\right),
 \qquad q^2=0.
\]

Its positive energy is exactly \(E=1\).

The standard labeled three-body Lorentz-invariant phase-space measure can be
pulled back without numerical approximation. The Euclidean coarea formula on
the nine outgoing spatial components gives

\[
 d\Phi_3=\frac{54}{2125(2\pi)^5}\,da\,db\,dt\,du\,dv.
\]

Since \(\partial_t s=-1152/425\), replacing \(t\) by the transverse shell
coordinate gives

\[
 d\Phi_3=\frac{3}{320(2\pi)^5}\,da\,db\,ds\,du\,dv.
\]

## Finite-time shell kernel

For an observation interval of length \(T\), let

\[
 F_T(\omega)=\int_0^T e^{i\omega t}\,dt.
\]

Near a positive-energy intermediate shell,
\(s=q^2=2E\omega+O(\omega^2)\). The corresponding shell amplitude is

\[
 \alpha_{T,E}(s)=\frac{F_T(s/(2E))}{2E}
 =\frac{2e^{isT/(4E)}\sin(sT/(4E))}{s}.
\]

The apparent value at \(s=0\) is removable at finite time:
\(\alpha_{T,E}(0)=T/(2E)\). Plancherel gives the exact norms

\[
 \int_{\mathbb R}|F_T(\omega)|^2d\omega=2\pi T,
 \qquad
 \int_{\mathbb R}|\alpha_{T,E}(s)|^2ds=\frac{\pi T}{E}.
\]

Thus \(|\alpha_{T,E}|^2/T\to(\pi/E)\delta(s)\), but every finite-\(T\)
amplitude is an ordinary \(L^2(ds)\) function.

## History norm and survival

For one fixed channel, the nine allowed histories have reduced Born vector

\[
 h_B=\sqrt2\,B e_B,\qquad \|h_B\|^2=\frac98.
\]

The shell-history amplitude \(A_{T,E}(s)=\alpha_{T,E}(s)h_B\) therefore
obeys

\[
 A_{T,E}^*A_{T,E}=Q_T,\qquad
 Q_T=\frac{9\pi T}{8E}.
\]

At the exact fixture, \(Q_T=9\pi T/8\). This reproduces the coefficient of
the duration-growing sequential history without using a distribution at
finite \(T\).

Multiplying by the frozen labeled final-state phase density gives

\[
 \frac{27T}{81920\pi^4}.
\]

This coefficient remains before the common BT tree multiplier, incoming flux,
tangential detector normalization, and generalized-Born convention. Dividing
by \(3!\) would give \(9T/(163840\pi^4)\) in the ordinary identical-final-state
convention, but that convention is not substituted for the missing BT
projector normalization.

Let \(g\) be a real effective local strength and put \(q=g^2Q_T\). The symbol
\(g\) includes the common tree multiplier, incoming flux, tangential detector
normalization and generalized-Born convention; those factors have not yet
been separately calibrated. In the perturbative domain \(0\le q\le1\),

\[
 M_g=\binom{\sqrt{1-q}}{gA_{T,E}}
\]

is an isometric column:

\[
 M_g^*M_g=1-q+g^2Q_T=1.
\]

The survival probability is \(1-q\), and the leading sequential probability
is \(q\). If \(V_{T,E}=A_{T,E}/\sqrt{Q_T}\), the skew rank-one block

\[
 K_T=\begin{pmatrix}0&-V_{T,E}^*\\V_{T,E}&0\end{pmatrix}
\]

obeys \(K_T^3=-K_T\). The column is the source column of the exact unitary
rotation with \(\sin\theta=g\sqrt{Q_T}\).

## Why the isolated history controls the long-time rate

For a constant regular amplitude on \(|s|<L\), the cross integral is

\[
 \int_{-L}^L\operatorname{Re}\alpha_{T,E}(s)\,ds
 =2\operatorname{Si}\!\left(\frac{LT}{2E}\right)
 \longrightarrow\pi.
\]

It remains order one, while the sequential norm grows as
\(9\pi T/(8E)\). Their ratio tends to zero. Therefore smooth regular-channel
interference cannot cancel the positive isolated-history rate. This does not
prescribe the global interference distribution or handle simultaneous channel
intersections.

## Remaining physical gate

The local labeled phase-space Jacobian is now fixed. A physical BT result must
still calibrate \(g\) from the two auxiliary quartic vertices, incoming flux and
generalized Born trace, supply the tangential detector normalization, extend
the column to compact wave packets in all five phase-space coordinates, and
glue the ten channel tubes where they overlap.

No global defect partial unitary, finite inclusive BT probability, complete
Møller/LSZ/S operator, Eq. (19), loop result, gravity/BRST lift, or
`LORENTZIAN-CAUSAL` theorem follows.

## Verification receipt

- Tier 0: the producer, verifier, test and schema files parse; both papers
  compile twice; the scoped diff passes `git diff --check`.
- Tier 1: the producer passes 23/23 checks, the independent verifier passes
  27/27 checks, and all six mutation tests pass. Peak resident memory is below
  75 MB for each new rail.
- Tier 2: the six-certificate chain from full phase-space positivity through
  this finite-time column passes sequentially. Its six producers report
  16/16, 12/12, 15/15, 16/16, 25/25 and 23/23 checks; its independent
  verifiers report 14/14, 12/12, 15/15, 17/17, 23/23 and 27/27 checks. The
  combined 34-test chain passes in 3.888 seconds with peak resident memory
  86,280 KB.
- Tier 3 was not run because this result neither changes shared core algebra
  nor promotes a freeze, release, QME state or Lorentzian claim.
- A freshly built Science Forge coordinator reports the complete planning
  directory `CLEAN`; the new work item and append-only DONE event both conform.
  The separate advisory shadow rail still reports its pre-existing toolchain
  lock mismatch and corpus-baseline drift, neither of which certifies this
  calculation.
- An initial symbolic five-variable independent coarea verifier exhausted the
  declared memory rail without a result. It was replaced by exact rational
  first-order automatic differentiation; the failed attempt is not counted as
  a pass.

Commands:

```text
ulimit -v 500000; python3 reverse_physics/bt_six_point_finite_time_shell_column.py --write --check
ulimit -v 500000; python3 reverse_physics/verify_bt_six_point_finite_time_shell_column.py
ulimit -v 500000; python3 -m unittest reverse_physics.tests.test_bt_six_point_finite_time_shell_column
```

CLOSE-OUT: DONE -- the isolated physical shell has an exact finite-time L2 history amplitude and normalized local survival column; BT calibration and global wave-packet gluing remain open.

EVIDENCE: `reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_FINITE_TIME_SHELL_COLUMN_V1.json`
