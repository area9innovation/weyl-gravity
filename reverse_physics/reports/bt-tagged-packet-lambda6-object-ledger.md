# BT tagged-packet lambda-six object ledger

Certificate:
`REVERSE_PHYSICS_BT_TAGGED_PACKET_LAMBDA6_OBJECT_LEDGER_V1`.

Dependencies: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`. Lifecycle: `CLASSIFIED`.

## Result

The complete hard tagged compact-packet probability at order `lambda^6` has
exactly three physical summands on the fixed BT carrier:

\[
 \boxed{
 q_{\rm tag}^{(6)}=
 2\operatorname{Re}\langle T_2,C_{4,\rm tree}\rangle_K
 +2\operatorname{Re}\langle T_2,
 I_s\otimes L_{4,\rm active\ loop}\rangle_K
 +2\operatorname{Re}\langle T_2,
 S_{2,s}\otimes A_{2,\rm active\ tree}\rangle_K.}
\]

The first term is the already certified finite, nonzero compact-packet
tagged/connected tree interference. The other two are missing: the
renormalized active four-point one-loop interference and the renormalized
order-two spectator self-energy multiplying the active tree on the same
packet carrier.

There is no independent order-`lambda^6` source-dressing, detector-dressing,
order-three norm, or pure forward-survival summand in this selected
experiment. Nonforward support does not, however, remove spectator dressing
when it multiplies an active transition. This classification identifies the
two missing dynamical objects. It does not yet compute the complete
coefficient.

## Fixed BT expansion

Use the fixed odd three-particle BT input and output packet projectors and
write

\[
 A_{\rm tag}(\lambda)
 =P_{\rm out}(U_T-1)P_{\rm in}
 =\lambda^2T_2+\lambda^3T_3+\lambda^4T_4+O(\lambda^5).
\]

The total-Fock-parity theorem gives

\[
 \Pi_FT_3\Pi_F=-T_3.
\]

Both projectors have odd three-particle range, so

\[
 P_{\rm out}T_3P_{\rm in}=0.
\]

Thus the order-three block itself vanishes on the selected experiment, not
merely its cross with `T2`. In particular there is no `T3^sharp T3` term at
probability order six.

At amplitude order four, exhaustive tagged support and coupling order leave:

\[
 T_4=C_{4,\rm tree}+I_s\otimes L_{4,\rm active\ loop}
 +S_{2,s}\otimes A_{2,\rm active\ tree}.
\]

Here `C4_tree` is the connected six-point finite-time tree and `L4` is the
renormalized active four-point one-loop block, including its counterterms.
The unique tagged two-plus-four partition has two ways to reach total
coupling order four: order zero on the spectator times order four on the
active block, or the renormalized order-two spectator two-point block `S2_s`
times the order-two active tree `A2`. The latter includes the spectator mass
and wave-function counterterms. Every other disconnected partition is off
support, normalized vacuum factors cancel, and the complete connected
order-four particle-number classification leaves only the three-to-three
tree.

Squaring the block gives

\[
 q^{(4)}=\langle T_2,T_2\rangle_K,
 \qquad q^{(5)}=0,
\]

and the displayed three-term `q6` ledger.

## Why pure survival is absent

The active incoming and outgoing packet supports are hard and nonforward:

\[
 P_{\rm out}P_{\rm in}=0
\]

in the active two-particle factor. A pure forward or survival coefficient
acts on the input support and therefore has zero pairing with the selected
click output. Survival is required for an exhaustive click/no-click
evolution, but it is not a summand in this nonforward click coefficient. A
spectator self-energy multiplying the nonforward active tree has the active
tree's output support and therefore does survive; it is the third term in the
ledger.

This is different from saying the full theory has no survival amplitude. It
says only that its support cannot interfere with `T2` in the declared tagged
click.

## Why source and detector dressing are not extra summands

The selected scalar experiment is defined by pulling the entire BT experiment
through the same public formal map:

\[
 P_\phi=R_t^\dagger P_{\rm BT}R_t,
 \qquad
 E_\phi=R_t^\dagger E_{\rm BT}R_t.
\]

On the finite detector ideal,

\[
 R_t^\dagger R_t=R_tR_t^\dagger=1
\]

coefficientwise, and the finite trace is cyclic. Hence

\[
 \boxed{\operatorname{tr}(P_\phi E_\phi)
 =\operatorname{tr}(P_{\rm BT}E_{\rm BT}).}
\]

Expanding the left side produces apparent source and detector correction
terms. They cancel order by order because they are the expansion of one exact
similarity. Adding them separately to the fixed-BT ledger would double count
the same representation change.

The compact-source theorem extends the finite-rank effects by trace-norm
limits on the common Gaussian packet core. This is sufficient for the
selected shift-breaking scalar packet. It does not prove Eq. (19) for the
standard shift-invariant characteristic projector.

## The known tree term

For the same normalized spectator packet `f`, the computed tree cross is

\[
 q_{\rm tree\ cross}^{(6)}[f,f]
 =\frac{25\sqrt2\lambda^6\Delta\Omega}
 {1024\pi^2\kappa^2\operatorname{Area}}
 \operatorname{Re}C_{ff}(T).
\]

It is finite on compact hard support, and a nonempty positive packet family
exists for every fixed `T>0`. It is one summand of `q6`, not its final value.

## What is known about the missing disconnected terms

The certified ultraviolet hard law supplies the scale-dependent asymptotic
part of the physical two-to-two loop interference:

\[
 \frac{d\sigma_{\rm virt,log}}{d\Omega}
 =\frac{5\lambda^6}{256\pi^4s}(L_s+L_t+L_u),
 \qquad L_X=\log\frac{\mu_R^2}{|X|}.
\]

At the tagged central invariants

\[
 s=\frac{64}{25}\kappa^2,
 \qquad t=u=-\frac{32}{25}\kappa^2,
\]

the logarithm is

\[
 L_*=\log\frac{25\mu_R^2}{64\kappa^2}
 +2\log\frac{25\mu_R^2}{32\kappa^2},
\]

and its central click density is

\[
 q_{\rm loop,log}^{(6)}
 =\frac{125\lambda^6\Delta\Omega}
 {16384\pi^4\kappa^2\operatorname{Area}}L_*.
\]

This is boundary data, not either missing object. It does not supply finite
terms, the finite-time active-loop packet kernel, the spectator two-point
kernel, their shared counterterm scheme ledger, or exact normalization on the
common tagged packet. The complete active-loop calculation must reproduce
this hard scale derivative as a consistency check. A separate declared pole,
residue, or finite-time condition must fix the spectator two-point term.

## The next calculation

Compute both renormalized disconnected order-four terms on the exact same
finite-time packet carrier used by the tagged three-body experiment:

1. classify the local scalar counterterms and allowed scheme freedom;
2. fix active scattering and spectator pole/residue or finite-time
   renormalization conditions;
3. construct the active loop and spectator two-point kernels on the common
   packet/time carrier;
4. contract both order-four terms with the certified leading tagged tree;
5. verify the active loop scale derivative against the hard logarithm above;
   and
6. add both crosses to the certified compact connected-tree cross.

Only that complete sum can promote `q6` from `CLASSIFIED` to
`COEFFICIENT_COMPUTED`.

## Claim boundary

The result classifies the complete object ledger. It does not compute the
active loop, spectator self-energy packet term, finite terms,
scheme-dependent constants, complete `q6` value or sign, endpoint-inclusive
scattering, an all-time operator, general Eq. (19), gravity or metric
BV--BRST transfer, a restored gravitational QME, or anything
`LORENTZIAN-CAUSAL`. No literature-priority claim is made.

## Verification receipt

- Tier 0: the changed Python files byte-compile and the four structured JSON
  files parse in the capped edit check (peak RSS `14,572 KB`); the scoped diff
  passes `git diff --check`. Paper 05 compiles twice, with its final pass
  taking `0.48 s`, peak RSS `50,608 KB`, and producing 57 pages (`646,664`
  bytes). Paper 06 compiles twice, with its final pass taking `0.48 s`, peak
  RSS `51,000 KB`, and producing 53 pages (`633,679` bytes). No new overfull
  boxes are introduced; only the previously recorded paragraphs remain.
- Tier 1: the exact producer passes 26/26 checks, the independent verifier
  passes 28/28 checks, and 13 tests including 12 adversarial mutations pass.
  Their elapsed times and peak RSS values are respectively `0.45 s` and
  `68,572 KB`, `0.43 s` and `69,376 KB`, and `0.35 s` and `70,404 KB`.
  Every scientific rail runs sequentially under a 500 MB virtual-memory cap.
- Tier 2: all imported inputs are unchanged and content addressed. Both rails
  verify their hashes and passing states; no predecessor producer is rerun.
- Tier 3 is not run because this is a `CLASSIFIED` reduced-mode ledger, not a
  freeze, release, shared-algebra change, QME restoration, residual transfer,
  or Lorentzian claim.
- The Science Forge fold accepts 1,507 nodes including the work item and
  append-only DONE event, with zero invalid items and zero malformed events.

Commands:

```text
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_tagged_packet_lambda6_object_ledger.py --write --check
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_tagged_packet_lambda6_object_ledger.py
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_tagged_packet_lambda6_object_ledger
```

CLOSE-OUT: DONE — the `q6` ledger is complete. Its two missing coefficients
are the active renormalized four-point one-loop packet cross and the
spectator-self-energy-times-active-tree packet cross.

EVIDENCE:
`reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_PACKET_LAMBDA6_OBJECT_LEDGER_V1.json`
