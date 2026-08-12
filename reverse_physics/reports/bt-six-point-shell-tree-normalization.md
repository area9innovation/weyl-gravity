# BT six-point shell tree normalization

Certificate: `REVERSE_PHYSICS_BT_SIX_POINT_SHELL_TREE_NORMALIZATION_V1`

Dependencies: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`. Lifecycle:
`COEFFICIENT_COMPUTED`.

## Result

The public BT Hamiltonian fixes the coupling normalization of the finite-time
six-point shell, but it does not fix a detector-independent dimensionless
three-to-three probability.

Bateman--Turok Appendix B gives

\[
 V_3=-2i\lambda F_3,\qquad V_4=-4i\lambda^2F_4,
 \qquad P(K)=\frac{-i}{(K^2+i0)^2}.
\]

Ignoring only the displayed kinematic polynomials and propagator denominators,
the three six-point tree topology classes have factors

\[
 V_4^2P=+16i\lambda^4,
\]

\[
 V_3^2V_4P^2=-16i\lambda^4,
 \qquad
 V_3^4P^3=+16i\lambda^4.
\]

These are the (+,-,+) signs already used by the reduced 220-tree recursion.
The common amplitude factor is therefore (16i\lambda^4), and the reduced
Born density must be multiplied by (256\lambda^8).

## Coupling-normalized shell coefficient

The reduced fixed-channel residue norm was (9/8). Restoring the public tree
factor gives

\[
 \|h_{B,\mathrm{BT}}\|^2=256\lambda^8\frac98
 =288\lambda^8.
\]

The finite-time transverse shell consequently has norm

\[
 Q_{T,E}^{\mathrm{BT}}
 =\frac{288\pi\lambda^8T}{E}.
\]

At the exact fixture (E=1), the labeled outgoing shell measure is

\[
 \rho_{\rm out}=\frac{3}{320(2\pi)^5}
\]

per (da\,db\,du\,dv). The BT-normalized local coefficient is therefore

\[
 \rho_{\rm out}Q_{T,1}^{\mathrm{BT}}
 =\frac{27\lambda^8T}{320\pi^4}.
\]

Dividing by (3!\) would give (9\lambda^8T/(640\pi^4)) in an ordinary
identical-final-particle convention. That preflight is not substituted for a
generalized-Born trace.

## Why this is not yet a probability

The displayed coefficient has mass dimension (-2): (lambda) and the
outgoing shell density are dimensionless, while (T/E) has dimension
(-2). A dimensionless probability requires an incoming projector-cell
weight of dimension (+2), as well as a declared tangential detector
function.

The public Letter makes this reduction explicit only for its two-particle
center-of-mass example. There a finite-volume characteristic function gives

\[
 \operatorname{Prob}=\frac{\sigma}{\mathrm{Area}}.
\]

Its general (n)-particle projector contains a characteristic function
(\chi), but the Letter supplies no three-particle incoming cell, no
three-to-three flux convention, and no finite-volume cancellation for that
case. The arXiv record still contains only v1 as checked on 2026-08-12, and
the companion normalization/proof paper remains listed as forthcoming.

Thus the earlier effective strength splits into a fixed Hamiltonian part and
detector data:

\[
 g_{\rm tree}=16\lambda^4,
\]

up to the irrelevant common phase, while the incoming projector normalization
remains open. For a declared compact cell one would have

\[
 q_{\rm cell}=N_{\rm in,\chi}
 \frac{27\lambda^8T}{320\pi^4}
 \int_{\rm cell}da\,db\,du\,dv,
\]

where (N_{\rm in,\chi}) must have dimension (+2). This formula is a target
for the complete Eq. (18) trace, not a definition of its missing factor.

## Remaining gate

Choose a compact incoming three-particle characteristic cell and outgoing
tangential detector function. Then derive the full generalized-Born trace,
including both projector factorials and all finite-volume cancellations. The
result must reproduce the coefficient above locally and provide the missing
dimension-two input weight before the survival column is a physical detector
probability.

No global multichannel probability, Møller/LSZ/S operator, Eq. (19), loop
completion, gravity/BRST lift, or `LORENTZIAN-CAUSAL` theorem follows.

## Verification receipt

- Tier 0: all new Python and JSON files parse; the scoped diff passes
  `git diff --check`; Papers 5 and 6 compile twice.
- Tier 1: the producer passes 19/19 exact checks, the independent Gaussian-
  integer and dimensional verifier passes 21/21 checks, and all six mutation
  tests pass. The peak resident memory of each new rail is below 71 MB.
- Tier 2: the seven producers from full phase-space positivity through this
  normalization report 16/16, 12/12, 15/15, 16/16, 25/25, 23/23 and 19/19
  checks. Their independent verifiers report 14/14, 12/12, 15/15, 17/17,
  23/23, 27/27 and 21/21 checks. The combined 40-test chain passes in 3.783
  seconds with peak resident memory 86,068 KB.
- Tier 3 was not run: no shared core algebra, freeze, release, QME state, or
  Lorentzian claim changes.
- A freshly built Science Forge coordinator reports the planning directory
  `CLEAN`; the new work item and append-only DONE event conform. The paper
  prose rail remains advisory: Paper 5 retains its manuscript-wide historical
  parenthetical/abstract findings, while Paper 6 meets the parenthetical
  budget; neither finding certifies or falsifies this calculation.

Commands:

```text
ulimit -v 500000; python3 reverse_physics/bt_six_point_shell_tree_normalization.py --write --check
ulimit -v 500000; python3 reverse_physics/verify_bt_six_point_shell_tree_normalization.py
ulimit -v 500000; python3 -m unittest reverse_physics.tests.test_bt_six_point_shell_tree_normalization
```

CLOSE-OUT: DONE -- the BT Hamiltonian multiplier and local outgoing shell coefficient are fixed; the dimensionless probability is now isolated to a declared three-particle incoming projector-cell normalization absent from the public Letter.

EVIDENCE: `reverse_physics/certificates/REVERSE_PHYSICS_BT_SIX_POINT_SHELL_TREE_NORMALIZATION_V1.json`
