# BT tagged-packet lambda-five parity selection

Certificate:
`REVERSE_PHYSICS_BT_TAGGED_PACKET_LAMBDA5_PARITY_SELECTION_V1`.

Dependencies: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`. Lifecycle:
`COEFFICIENT_COMPUTED`.

## Result

The complete probability-order-`lambda^5` coefficient of the covariantly
dressed hard tagged packet experiment is exactly zero:

\[
 \boxed{q_{\rm tag}^{(5)}=0.}
\]

The reason is structural, not a fitted cancellation. Let

\[
 \Pi_F=(-1)^N
\]

be total fluctuation Fock parity. The exact theory is covariant under changing
the signs of the coupling and every fluctuation field. The leading
order-`lambda^2` tagged output and the complete order-`lambda^3` correction
therefore lie in opposite total-particle-parity sectors. The public
cross-Krein inner product pairs only equal particle number, so their cross
term vanishes.

Consequently the tagged packet probability has the sharpened form

\[
 q_{\rm tag}(\lambda)
 =\lambda^4q_4+\lambda^6q_6+O(\lambda^8),
\]

with every odd coefficient zero for the declared covariant source/detector
family. The leading coefficient remains

\[
 q_4=\frac{3\Delta\Omega}{32\pi^2s\operatorname{Area}}.
\]

The theorem removes a skipped-order concern. It does not compute `q6`.

## Which parity is used

`Pi_F` is ordinary total Fock-number parity for the scalar or BT fluctuation
quanta. It is not either of the two other gradings used in this programme:

- it is not BT ghost parity, which exchanges `Omega` and `Upsilon`;
- it is not the continuous `SO+(1,1)` charge, under which the two species have
  opposite weights.

The distinction matters. The present zero follows from orthogonality of even
and odd total particle number. It does not use a one-sided `SO+(1,1)` charge
radical and does not assume Eq. (19).

## Exact coupling/field covariance

Write

\[
 X=\Box\phi,\qquad Y=(\partial\phi)^2.
\]

The perfect-square action is

\[
 S_\lambda[\phi]=-rac12\int(X+\lambda Y)^2.
\]

Under

\[
 \phi\mapsto-\phi,\qquad\lambda\mapsto-\lambda,
\]

we have `X -> -X`, `Y -> Y`, and therefore

\[
 X+\lambda Y\mapsto-(X+\lambda Y),
 \qquad S_\lambda[\phi]=S_{-\lambda}[-\phi].
\]

The exact BT composites have the same covariance. For example,

\[
 \Omega_\lambda=\lambda^{-1}e^{\lambda\phi}
\]

obeys

\[
 \Omega_{-\lambda}[-\phi]=-\Omega_\lambda[\phi].
\]

Using

\[
 \Upsilon_\lambda
 =e^{-\lambda\phi}
 \left(\Box\phi+\lambda(\partial\phi)^2\right)
\]

gives the same sign. The `1/lambda` background changes sign together with the
coupling, so the statement is about fluctuations around the correspondingly
transformed broken background.

In operator language,

\[
 \Pi_F U(\lambda)\Pi_F=U(-\lambda).
\]

If

\[
 U(\lambda)=\sum_n\lambda^nU_n,
\]

then

\[
 \Pi_FU_n\Pi_F=(-1)^nU_n.
\]

Covariantly transported source and detector projectors obey the same
coefficient rule.

## Vertex and graph check

The expanded action has:

- an order-`lambda` cubic interaction containing three fluctuation fields;
- an order-`lambda^2` quartic interaction containing four fluctuation fields.

For a graph with `V3` cubic vertices, `V4` quartic vertices, `I` internal
edges and `E` external fluctuation legs,

\[
 3V_3+4V_4=2I+E,
 \qquad d_\lambda=V_3+2V_4.
\]

Modulo two,

\[
 E\equiv V_3\equiv d_\lambda\pmod2.
\]

Thus an odd coupling order changes total Fock parity and an even coupling
order preserves it. The producer enumerates 261 nonnegative graph-count
fixtures in its declared range; the independent verifier checks a larger
range. Every row obeys the identity.

## The dressed source correction

The normalized leading compact packet source is

\[
 \psi_0=rac{|\Upsilon^3;f\rangle+|\Omega^3;f\rangle}{\sqrt2}.
\]

Its pulled squeezed vacuum contains only even particle-number changes, so
`psi0` is total-Fock-odd. The already derived order-`lambda` composite map is
quadratic and its canonical lift is cubic. Hence the first dressed-source
correction has the opposite parity:

\[
 \Pi_F\psi_0=-\psi_0,
 \qquad
 \Pi_F\psi_1=+\psi_1.
\]

No endpoint coefficient is needed for this classification. Endpoint and
oscillatory data can change `psi1` within the even sector, but cannot give it
an odd component without breaking the exact covariance.

## The complete lambda-five cross term

Write the selected outgoing click vector as

\[
 Y(\lambda)=\lambda^2y_2+\lambda^3y_3+O(\lambda^4).
\]

The leading piece contains the active four-point tagged transition:

\[
 y_2=A_2\psi_0,
 \qquad \Pi_Fy_2=-y_2.
\]

The complete next coefficient includes every first correction:

\[
 y_3=A_3\psi_0+A_2\psi_1
      +\text{first detector correction},
 \qquad \Pi_Fy_3=+y_3.
\]

Because the cross-Krein metric commutes with `Pi_F` and `Pi_F` is
Krein-self-adjoint,

\[
 \langle y_2,y_3\rangle_K
 =\langle\Pi_Fy_2,\Pi_Fy_3\rangle_K
 =-\langle y_2,y_3\rangle_K=0.
\]

Therefore

\[
 q_{\rm tag}^{(5)}
 =2\operatorname{Re}\langle y_2,y_3\rangle_K=0.
\]

Equivalently, the covariantly named experiment satisfies

\[
 q(\lambda)=q(-\lambda),
\]

so all odd perturbative coefficients vanish.

## Scope of the covariance

The preparation and detector must be transformed as the same covariant
family when `lambda` changes sign. This is the natural comparison for the
BT-pulled scalar source: under simultaneous sign reversal, each three-BT-
particle branch gains the same overall minus sign and its projector is
unchanged.

If one instead holds an explicitly parity-breaking detector or external
spurion fixed while reversing only `lambda`, the evenness conclusion does not
follow. No such insertion occurs in the declared tagged packet experiment.

The regulator and counterterms must also preserve the exact discrete
covariance. This is an assumption of the finite perturbative coefficient, not
a claim about every possible renormalization prescription.

## What remains at lambda six

The first unresolved correction is now genuinely probability order
`lambda^6`. Its object ledger contains at least:

- the certified nonzero compact tagged/connected tree interference;
- active four-point tree/one-loop interference;
- parity-even order-`lambda^2` source and detector corrections;
- the matching survival or virtual contribution;
- any forward/collinear completion required by the chosen detector.

These are different objects and cannot be replaced by one another. In
particular, the parity theorem says only that the intervening odd order is
zero; it supplies none of the missing even-order coefficients.

## Claim boundary

This result does not establish the complete `lambda^6` coefficient, the
active loop, second-order source/detector transport, survival or KLN
completion, an all-time operator, general Eq. (19), gravity or metric
BV--BRST transfer, all-order positivity, or anything `LORENTZIAN-CAUSAL`. No
literature-priority claim is made.

## Verification receipt

- Tier 0: the changed Python files byte-compile and the four structured JSON
  files parse in the capped edit check (peak RSS `14,880 KB`); the scoped diff
  passes `git diff --check`. Paper 05 compiles twice, with its final pass
  taking `0.48 s`, peak RSS `50,820 KB`, and producing 56 pages (`644,878`
  bytes). Paper 06 compiles twice, with its final pass taking `0.50 s`, peak
  RSS `50,640 KB`, and producing 53 pages (`632,570` bytes). The edits add no
  overfull boxes; only the previously recorded paragraphs remain.
- Tier 1: the exact producer passes 26/26 checks, the independent verifier
  passes 28/28 checks, and 15 tests including 14 adversarial mutations pass.
  Their elapsed times and peak RSS values are respectively `0.32 s` and
  `66,972 KB`, `0.43 s` and `70,204 KB`, and `0.50 s` and `72,008 KB`.
  Every scientific rail runs sequentially under a 500 MB virtual-memory cap.
- Tier 2: all imported inputs are unchanged and content addressed. Both rails
  verify their hashes and passing states; no predecessor producer is rerun.
- Tier 3 is not run because no shared algebra, freeze, release, QME state,
  residual transfer or Lorentzian claim changes.
- The Science Forge fold accepts 1,505 nodes including the work item and
  append-only DONE event, with zero invalid items and zero malformed events.

Commands:

```text
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_tagged_packet_lambda5_parity_selection.py --write --check
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_tagged_packet_lambda5_parity_selection.py
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_tagged_packet_lambda5_parity_selection
```

CLOSE-OUT: DONE — the complete tagged packet probability coefficient at
order `lambda^5` is exactly zero by total-Fock-parity covariance. The complete
even order `lambda^6` ledger is the next physical gate.

EVIDENCE:
`reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_PACKET_LAMBDA5_PARITY_SELECTION_V1.json`
