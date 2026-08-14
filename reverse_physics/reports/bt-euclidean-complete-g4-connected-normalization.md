# Complete BT order-g4 connected normalization

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_CONNECTED_NORMALIZATION_V1`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

Lifecycle:
`COMPLETE_G4_CONNECTED_REORGANIZATION_PROVED_CANCELLATION_DECISION_OPEN`

## Result

The standalone second-chaos norm is not yet the right object to estimate.
It contains a large normalization-aligned multiple of the quadratic score
$A$.  That multiple cancels only after the signed cross is recombined with
the nonnegative $D$ norm.

The complete coefficient should instead be kept in the connected form

\[
 \boxed{
 M_4=\mathbb E_0[B^2+2AC-2ABW_1]
     +\operatorname{Cov}_0\!\left(A^2,\frac12W_1^2-W_2\right).}
\]

This identity does not decide $M_4$, but it removes every fully disconnected
vacuum factor before estimation and identifies the cancellation that a
diagramwise bound would destroy.

## Why the earlier sufficient bound is badly conditioned

Set

\[
 R_0=\frac12W_1^2-W_2,
 \qquad z_2=\mathbb E_0R_0,
\]

and write the square-root coefficient as

\[
 E=C-\frac12W_1B+HA,
 \qquad
 H=\frac18W_1^2-\frac12W_2-\frac12z_2.
\]

Its mean is not zero:

\[
 \boxed{\mathbb E_0H=-\frac18\mathbb E_0[W_1^2].}
\]

Consequently, with $H_c=H-\mathbb E_0H$,

\[
 E=E_c-\frac18\mathbb E_0[W_1^2]A,
 \qquad E_c=C-\frac12W_1B+H_cA,
\]

and because $A$ is pure second chaos,

\[
 \Pi_2E=\Pi_2E_c-\frac18\mathbb E_0[W_1^2]A.
\]

The displayed summand is extensive.  The third chaos of $W_1$ is the cubic
part of $S_1$.  The certified exact fixture has $V_3(2,2,4)=-16$; fixed
ultraviolet boxes around it give

\[
 \mathbb E_0[W_1^2]\geq\|\Pi_3W_1\|_0^2\geq cN.
\]

There is also a direct nonzero polynomial fixture: on $L=4$, put the selected
cosine along an inert axis and use the three-mode transverse field from the
cubic certificate.  Momentum support gives $U_{32}=0$, while
$U_{30}=-1024$, so $W_1$ is not the zero polynomial.

The aligned contribution to the cross is

\[
 -\frac14\mathbb E_0[W_1^2]\|A\|_0^2.
\]

The $W_1^2A^2/4$ part of $\|D\|^2$ contains the opposite disconnected piece
plus the connected covariance.  Thus these extensive terms cancel exactly,
but only in the complete $M_4$.  A separate bound or triangle inequality on
the aligned summand is therefore obstructed as formulated.  This does not
prove that the norm of the fully combined $\Pi_2E$ is large: $\Pi_2E_c$ may
itself contain a canceling $A$ component.

## Exact algebra fixture

For the standard-Gaussian polynomial fixture used by the expected-Hessian
certificate,

\[
 \mathbb E[W_1^2]=25,\quad
 \mathbb E[H]=-\frac{25}{8},\quad
 \|D\|^2=\frac{653}{2},\quad
 2\langle A,E\rangle=\frac{527}{2}.
\]

The disconnected pieces are $+25/2$ and $-25/2$.  The direct, connected-
covariance, and square-root forms all give

\[
 M_4=590.
\]

This checks the rearrangement only; it is not BT lattice data.

## Exhaustive connected-pairing audit

Write \(U_{nr}\) for the coefficient of \(t^r\) in
\(S_{n-2}(\eta+t h)\).  Expanding the boxed connected formula produces 13
homogeneous monomials.  An exact labeled Wick enumeration applies two
filters before any estimate: covariance subtraction removes pairings with no
edge joining \(U_{31}^2\) to the \(R_0\) factor, and fixed-\(h\) momentum
support removes components whose external transfer cannot total zero.
\(U_{33}\) vanishes identically for \(L\geq4\).

This labeled table concerns the translation-invariant \(C_0\) contractions.
A component marked momentum-forbidden there can be revived when a covariance
is replaced by the real-cosine rank-one term.  It must not be read as a zero
of the full conditioned expectation.  A separate exact signed-source audit
now expands every choice in \(C=C_0-vh\otimes h\).  The viable conditioned
components still have loop ranks exactly \(0,1,2\), and none has rank three or
higher for any integer \(L\geq4\).  Thus the unresolved object remains a
finite sum of zero-, one-, and two-loop lattice kernels, but rank corrections
must be included.

## Controlled numerical preflight

The streaming C implementation independently evaluates $A,B,C,W_1,W_2$ on
free conditioned Gaussian fields using an $O(L^4)$ radix-two FFT.  It uses
fixed seeds and long-double online covariance accumulation.  The results are
supporting only:

| $L$ | samples | $\|D\|^2$ | signed cross | $M_4$ | standard error |
|---:|---:|---:|---:|---:|---:|
| 4 | 100,000 | 107.142 | -107.667 | -0.525 | 1.767 |
| 8 | 30,000 | 3315.554 | -3383.745 | -68.191 | 80.150 |

At both volumes $M_4$ is within one standard error of zero, while its two
square-root pieces are individually much larger and nearly opposite.  The
successor exact calculation finds
\(M_4(4)=-338835474713437/204838502400000\), within one reported standard
error of the \(L=4\) estimate.  The numerical rows remain supporting only.

## Next calculation

Certificate
`REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_L4_DECISION_V1` now closes the
first decisive test: \(M_4(4)\) is exactly negative and nonzero, so an
all-volume zero identity is obstructed.  Its sector ledger shows dominant
bulk and single-rank two-loop contributions of opposite sign.  The general-
volume successor now combines those contributions exactly for every
\(L\geq5\): five common integrands cancel, the factorized conditioning
remainder has a logarithm-squared bound, and 14 unfactorized two-loop kernels
remain for a joint hard/one-soft/all-soft estimate.

No large-volume sign or scaling decision, whole-lattice power-survival
theorem, nonperturbative score theorem, interacting $H^{-1}$ moment,
continuum identification, Born rule, Krein reconstruction, or
`LORENTZIAN-CAUSAL` statement is established.

## Verification

```text
ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_connected_normalization.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_complete_g4_connected_normalization.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_complete_g4_connected_normalization
cc -std=c11 -O2 -Wall -Wextra -Werror reverse_physics/bt_euclidean_complete_g4_preflight.c -lm -o /tmp/bt-complete-g4-preflight
```

## Verification receipt

The scope correction and conditioned rank audit are in the affected chain of
the exact \(L=4\) successor.  The regenerated predecessor, independent
verifier, and 12 unit/adversarial-mutation tests passed in 1.32 s, 1.10 s, and
2.32 s (22,072 KB, 30,424 KB, and 31,148 KB maximum RSS).  The two added
mutations independently reject promotion of the bulk table to all conditioned
contractions and a false rank-three conclusion.  Python compilation passed as
part of the successor Tier-0 rail; the Paper 21 claim-map check and verifier
each passed in 0.07 s.  The append-only planning import accepted 1,618 nodes
with no invalid item or malformed event in 7.80 s under
`GOMEMLIMIT=300MiB`.  Tier 3 was not run because the corrected table scope
preserves the connected identity and maximum-two-loop theorem and introduces
no freeze, release, shared-core change, continuum theorem, or lifecycle
promotion.  Full timings and the independent exact-evaluation receipt are in
the successor \(L=4\) decision report.
