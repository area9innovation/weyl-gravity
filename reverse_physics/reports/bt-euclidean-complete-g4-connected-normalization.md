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

The surviving connected components have loop ranks exactly \(0,1,2\); none
has rank three or higher.  Thus the unresolved object is a finite sum of
explicit zero-, one-, and two-loop lattice kernels.  This is a genuine
reduction from the standalone expected-Hessian norm, but it is not an
evaluation or bound of those kernels.  The complete labeled table and an
independent pairing enumerator are in the certificate and verifier.

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
square-root pieces are individually much larger and nearly opposite.  This
motivates an exact-cancellation search.  It is not evidence for a certified
zero, sign, asymptotic scaling, interacting moment, or continuum limit.

## Next calculation

The connected Wick topologies of the boxed formula are now exhaustively
classified.  The first decisive test is exact rational evaluation of their
zero-, one-, and two-loop sums on $L=4$, where all dispersions and selected
cosine values are rational.  If the sum vanishes, the task is to find the
vertex or Ward identity that explains the cancellation for every volume.  If
it does not, its first nonzero connected topology determines the correct
hard/one-soft/all-soft bound.

No exact $M_4$ cancellation, whole-lattice power decision, nonperturbative
score theorem, interacting $H^{-1}$ moment, continuum identification, Born
rule, Krein reconstruction, or `LORENTZIAN-CAUSAL` statement is established.

## Verification

```text
ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_connected_normalization.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_complete_g4_connected_normalization.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_complete_g4_connected_normalization
cc -std=c11 -O2 -Wall -Wextra -Werror reverse_physics/bt_euclidean_complete_g4_preflight.c -lm -o /tmp/bt-complete-g4-preflight
```

## Verification receipt

Tier 0: Python compilation and the strict C build passed in 0.04 s and 0.15 s
(16,328 KB and 41,452 KB maximum RSS).  Tier 1: generation, independent
verification, and 10 unit/mutation tests passed in 0.05 s, 0.12 s, and 0.26 s
(21,732 KB, 30,092 KB, and 31,344 KB maximum RSS).  The paper claim-map and
independent verifier passed in 0.15 s (30,516 KB maximum RSS).  The planning
import accepted 1,616 nodes with no invalid item or malformed event in 7.19 s
(225,952 KB maximum RSS under `GOMEMLIMIT=300MiB`).  Two bounded LaTeX passes
completed in 1.58 s (53,732 KB maximum RSS).  The prose advisory remained
non-certifying and reported the pre-existing parenthetical and abstract-word
budget findings.  Tier 3 was not run because no shared core algebra, freeze,
release, theorem lifecycle, exact cancellation, weighted estimate, or
continuum lifecycle changed.

The advisory `ci/science-forge-shadow.sh` rail exited zero by design but did
not pass: its Forge 0.0.2 binary and current stdlib hashes disagree, the bridge
audit fails closed at substrate diagnostic `E9118`, and the July corpus census
baseline records 976 certificates versus 1,666 now present.  Diagnostics are
in `/tmp/sf-shadow.cBDj0k`.  These are reported external substrate/baseline
findings, not evidence for or against this certificate; the scoped planning
import above is the applicable fail-closed event/schema check.
