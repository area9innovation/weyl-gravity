# BT normal-ordered tagged spectator reduction

Certificate:
`REVERSE_PHYSICS_BT_TAGGED_PACKET_NORMAL_ORDERED_SPECTATOR_REDUCTION_V1`.

Dependencies: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`. Lifecycle:
`COEFFICIENT_COMPUTED` for the spectator coefficient only.

## Result

On a declared normal-ordered, massless, unit-residue auxiliary BT carrier,
the order-`lambda^2` spectator two-point block is exactly zero:

\[
 \boxed{S_{2,s}=0.}
\]

The complete tagged order-`lambda^6` probability therefore reduces in this
scheme to

\[
 \boxed{
 q_{\rm tag}^{(6)}=
 2\operatorname{Re}\langle T_2,C_{4,\rm tree}\rangle_K
 +2\operatorname{Re}\langle T_2,
 I_s\otimes L_{4,\rm active\ loop}\rangle_K.}
\]

The connected-tree cross is already a computed nonzero compact-packet
functional. The active four-point one-loop packet cross is now the sole
missing coefficient in this declared scheme. The complete `q6` coefficient
is not computed.

This reduction is conditional in the scientifically important sense: it
declares a legitimate auxiliary renormalization convention. It does not say
that the public Letter uniquely imposes this convention. A calculation using
an unmatched finite two-point counterterm must reinstate the spectator term.

## Exact graph classification

The fixed auxiliary interaction is

\[
 {\lambda^2\over2}\Omega^2\Upsilon^2.
\]

Every vertex has coupling degree two. For a connected two-point graph with
quartic vertex count `V`, internal-line count `I`, and loop count `L`,

\[
 4V=2+2I,\qquad L=I-V+1,\qquad d_\lambda=2V.
\]

At coupling degree two these equations have the unique solution

\[
 (V,I,L)=(1,1,1).
\]

It is a one-vertex tadpole. There is no bubble, sunset, or
momentum-dependent two-point graph at this order. The next connected
two-point topology has `(V,I,L)=(2,3,2)` and begins at order `lambda^4`.

## Species contraction

The free auxiliary contraction is cross-only:

\[
 \langle\Omega\Omega\rangle=
 \langle\Upsilon\Upsilon\rangle=0,
 \qquad
 \langle\Omega\Upsilon\rangle=
 \langle\Upsilon\Omega\rangle\ne0.
\]

Removing two external fields from `Omega^2 Upsilon^2` gives, up to the common
tadpole integral, the exact species matrix

\[
 \begin{pmatrix}0&4\\4&0\end{pmatrix}.
\]

It is an off-diagonal mass mixing and has external-momentum degree zero.
Normal ordering `:Omega^2 Upsilon^2:` removes precisely this same-vertex
self-contraction as an operator identity, including at finite time. This is
stronger than setting a scaleless asymptotic integral to zero.

## Complete local counterterm basis

Modulo integration by parts, the ghost-parity-even,
`SO^+(1,1)`-neutral scalar operators of engineering dimension at most four
are

\[
 1,\qquad \Omega\Upsilon,\qquad
 \partial\Omega\partial\Upsilon,\qquad
 \Omega^2\Upsilon^2.
\]

Only the middle two are two-point counterterms. The one-vertex tadpole can
generate the mass structure `Omega Upsilon`, but no kinetic structure. The
declared conditions are:

1. normal order the auxiliary quartic interaction;
2. set the renormalized `Omega Upsilon` mass coefficient to zero; and
3. hold the cross-kinetic residue at its free value through order
   `lambda^2`.

They give `S2_s=0` on every packet in the common finite-time Fock domain.

## Why the scalar-frame wave-function pole is not added

The cubic-plus-quartic perfect-square coordinates have a certified
order-`lambda^2` field-renormalization pole. That fact is not in conflict with
the auxiliary result. The nonlinear formal `R_t` changes fields, sources,
effects, and counterterms together. For the selected experiment the entire
source and effect are pulled through the same two-sided similarity. Inserting
the scalar-coordinate wave-function correction once more into the fixed
auxiliary ledger would mix frames and double count the transformation.

This statement applies only to the selected covariant pullback. It is not
general Eq. (19) for the standard shift-invariant scalar projector.

## Remaining barrier

The sole missing `q6` object in this scheme is

\[
 I_s\otimes L_{4,\rm active\ loop}
\]

on the exact same compact active packet, finite duration, mass jet, and
detector normalization as the leading tree. Its coupling counterterm and
finite renormalization condition must be stated. Its hard limit must reproduce

\[
 {d\sigma_{\rm virt,log}\over d\Omega}
 ={5\lambda^6\over256\pi^4s}(L_s+L_t+L_u).
\]

The hard logarithm is a consistency condition, not the finite-time kernel.

## Claim boundary

This result does not compute the active loop, the complete `q6` value or
sign, the order-`lambda^4` auxiliary two-point sunset, an all-time scattering
operator, general Eq. (19), all-order positivity, infrared completion,
gravity or metric BV--BRST transfer, a restored gravitational QME, or
anything `LORENTZIAN-CAUSAL`. No literature-priority claim is made.

## Source boundary

The auxiliary action and formal Hamiltonian relation are imported from
Bateman and Turok, *Escape from Ostrogradsky via Hidden Ghost Parity*,
arXiv:2607.00096v1. The source archive is pinned by SHA-256 in
`BATEMAN_TUROK_HAMILTONIAN_SOURCE_V1`. The normal-ordered interacting scheme
and the graph/counterterm reduction above are this repository's declared
construction, not an attribution to that Letter.

## Verification receipt

- Tier 0: the changed Python files compile and all four structured JSON files
  parse under the memory cap in `0.03 s` with peak RSS `14,556 KB`; the scoped
  diff passes `git diff --check`. Paper 05 compiles twice, with its final pass
  taking `0.47 s`, peak RSS `50,652 KB`, and producing 57 pages (`647,036`
  bytes). Paper 06 compiles twice, with its final pass taking `0.50 s`, peak
  RSS `50,876 KB`, and producing 54 pages (`634,537` bytes). No new overfull
  boxes are introduced; only the previously recorded paragraphs remain.
- Tier 1: the exact producer passes 24/24 checks in `0.35 s` with peak RSS
  `65,564 KB`; the method-distinct verifier passes 28/28 checks in `0.39 s`
  with peak RSS `69,356 KB`; and 15 tests including 14 adversarial mutations
  pass in `0.44 s` with peak RSS `69,976 KB`. Every scientific rail runs
  sequentially under a 500 MB virtual-memory cap.
- Tier 2: imported inputs are content addressed; no mathematical predecessor
  is changed.
- Tier 3 is not required because this is a selected reduced-mode coefficient,
  not a freeze, release, shared-algebra change, QME restoration, residual
  transfer, or Lorentzian claim.
- The Science Forge fold accepts 1,509 nodes including the work item and
  append-only DONE event, with zero invalid items and zero malformed events.

Commands:

```text
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_tagged_packet_normal_ordered_spectator_reduction.py --write --check
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_tagged_packet_normal_ordered_spectator_reduction.py
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_tagged_packet_normal_ordered_spectator_reduction
```

CLOSE-OUT: DONE — the spectator cross is zero in the declared scheme; the
active four-point one-loop compact-packet cross is the sole remaining `q6`
coefficient.

EVIDENCE:
`reverse_physics/certificates/REVERSE_PHYSICS_BT_TAGGED_PACKET_NORMAL_ORDERED_SPECTATOR_REDUCTION_V1.json`
