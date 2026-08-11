# BT complement/hard-profile parameter separation

**Certificate:** `REVERSE_PHYSICS_BT_COMPLEMENT_HARD_PROFILE_SEPARATION_V1`

**Lifecycle:** `CLASSIFIED`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Result

The hard-profile direction that survives all four eight-point thresholds is
not the \(\rho\)-dependent cross-Krein complement in another notation.  The
two structures vary independently on an exact shared fixture.

Both eight-point hard fixtures have

\[
 (a_0,a_1,\tau_1)=(1,4,10),
\]

and therefore the same first-emission parameter

\[
 \rho=\frac{(a_0-a_1)^2
 \{2\tau_1(a_0+a_1)-(a_0-a_1)^2\}}
 {4\tau_1^3}
 =\frac{819}{4000}.
\]

They consequently require the same cross-Krein complement and endpoint
coefficient.  Nevertheless their final eight-point responses differ by

\[
 \boxed{\frac{225}{64}\ne0}.
\]

Thus \(\rho\) alone cannot parameterize both the public-to-physical
compression and the fourth-jump profile.

## Exact commuting square that fails

The finite physical Møller column requires

\[
 G_{\rm miss}(\rho)=
 \begin{pmatrix}
 0&-\rho\\
 -\rho&-2
 \end{pmatrix}.
\]

At \(\rho=819/4000\), this matrix is the same for both hard fixtures.  It has

\[
 \operatorname{rank}G_{\rm miss}=2,
 \qquad
 \det G_{\rm miss}=-\frac{670761}{16000000}<0.
\]

The endpoint matching law likewise gives the same unique coefficient

\[
 c_1=\frac74+\frac\rho2=\frac{14819}{8000}.
\]

The eight-point fixtures differ only in their final adjacent invariant,

\[
 h=33\quad\hbox{or}\quad h=34,
\]

with every other hard entry and all soft data equal.  Their complete
all-threshold coefficients are

\[
 \kappa_4(33)=-\frac{6699}{128},
 \qquad
 \kappa_4(34)=-\frac{7149}{128}.
\]

Therefore

\[
 \rho(33)=\rho(34),\qquad
 G_{\rm miss}(33)=G_{\rm miss}(34),\qquad
 c_1(33)=c_1(34),
\]

but

\[
 \kappa_4(33)-\kappa_4(34)=\frac{225}{64}.
\]

Any proposed identification \(\kappa_4=f(\rho)\) is refuted by this exact
equal-input, unequal-output witness.

## Smallest justified architecture

The evidence fixes types, not dynamics.  A compatible successor must have:

- base data containing \(\rho\) and at least one additional hard-profile
  coordinate witnessed by \(h\);
- the rank-two cross-Krein fibre with Gram \(G_{\rm miss}(\rho)\); and
- a fourth-jump profile section allowed to vary with the additional hard
  coordinate.

This is not a proof that \((\rho,h)\) is a globally minimal coordinate system.
It proves only that a \(\rho\)-only base is insufficient and that at least one
additional hard-profile datum is necessary on the declared fixtures.

The result also prevents an attractive but incorrect shortcut: the new
eight-point direction cannot simply be named as the previously missing
cross-Krein fibre.  The complement is a rank-two fibre fixed at constant
\(\rho\), while the new obstruction is variation of the fourth response over
the hard kinematic base at that same \(\rho\).

## Consequence for Eq. (19)

A viable bridge must now derive both structures from BT dynamics:

1. the non-null rank-two complement needed by the public compression; and
2. a history-resolved fourth-jump section sensitive to the hard-profile
   coordinate.

An algebraic direct sum of these objects is easy to declare but does not
advance Eq. (19).  The next falsifiable step is to derive one exact operator
on the declared zero-mode, higher-composite, or eight-point quotient domain
that preserves the cross-CCR and charge grading, reproduces both fourth
coefficients at fixed \(\rho\), and restricts to the existing one-through-three
emission physical column.

## Claim boundary

Established exactly:

- the shared value \(\rho=819/4000\);
- the shared cross-Krein Gram and endpoint coefficient
  \(c_1=14819/8000\);
- the isolated hard change \(33\mapsto34\);
- the unequal fourth responses and difference \(225/64\); and
- failure of every \(\rho\)-only identification on this shared fixture.

Not established:

- a global dimension theorem for the BT kinematic base;
- a dynamically derived profile-valued jump or complement;
- a normalized fourth probability or Cox decision;
- a complete \(2\to6\) probability or spacetime Møller/LSZ operator;
- all-order Eq. (19), a gravity/BRST lift, or anything
  `LORENTZIAN-CAUSAL`.

## Verification receipt

All commands ran sequentially on 2026-08-11 with `ulimit -v 500000` and
Python 3.12.13 from
`/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3`.

- Tier 0 Python compilation passed for the producer, verifier, and mutation
  test (`0.02 s`, peak `14508 KiB`).
- Tier 0 JSON parsing passed for the work item, certificate, and schema
  (`0.10 s`, peak `14636 KiB`).
- `python3 reverse_physics/bt_complement_hard_profile_separation.py` passed
  `15/15` checks (`0.31 s`, peak `65612 KiB`).
- `python3 reverse_physics/verify_bt_complement_hard_profile_separation.py`
  passed `15/15` independent checks (`0.35 s`, peak `69908 KiB`).
- `python3 reverse_physics/tests/test_bt_complement_hard_profile_separation.py`
  passed `15/15` mutation tests (`4.50 s`, peak `70096 KiB`).
- Two-pass `pdflatex` builds of Paper V passed (`0.47 s`, `0.48 s`; peak
  `50820 KiB`, `50776 KiB`).  The second pass retains exactly the four
  pre-existing overfull boxes and introduces no new overfull box.
- Two-pass `pdflatex` builds of Paper VI passed (`0.47 s`, `0.48 s`; peak
  `50848 KiB`, `50640 KiB`) with no overfull box or undefined reference.

The producer hashes and consumes the unchanged predecessor certificates, so
the exact producer/verifier chain is the affected Tier 2 chain for this
parameter-separation claim.  A full Tier 3 repository rebuild was unnecessary:
no shared algebra, schema interface, freeze, lifecycle promotion beyond
`CLASSIFIED`, or Lorentzian claim changed.  The Science Forge advisory rail was
not rerun: its earlier same-session CBP helpers aborted and its census timed out
after `180.17 s`; that inconclusive advisory output is not evidence for this
claim.
