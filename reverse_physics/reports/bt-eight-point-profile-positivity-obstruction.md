# BT eight-point profile positivity obstruction

**Certificate:**
`REVERSE_PHYSICS_BT_EIGHT_POINT_PROFILE_POSITIVITY_OBSTRUCTION_V1`

**Lifecycle:** `CLASSIFIED`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Result

Retaining the two hard evaluations as independent profile channels does not
rescue an ordinary positive fourth jump.  After all four exact
fixed-invariant threshold functionals, their effects are

\[
 \kappa_{33}=-\frac{6699}{128},\qquad
 \kappa_{34}=-\frac{7149}{128}.
\]

These are not yet normalized fourth-event probabilities.  Their sign,
however, is already fixed.  There are eight external delta-prime derivatives,
so their common external sign is

\[
 (-1)^8=+1.
\]

The first three threshold scale is \(+6\), the existing selected-history chain
is

\[
 q_0q_1q_2
 =\frac1{48}\frac5{64}\frac{27}{400}
 =\frac9{81920}>0,
\]

and the remaining squared-amplitude, phase-space, Born-division, history-count,
and ordered-simplex factors are positive.  A later physical normalization can
change the magnitude but not turn these two negative effects into positive
ones.

## Positive profile cone

On the declared two-point profile algebra

\[
 {\cal A}_h=\mathbb Qe_{33}\oplus\mathbb Qe_{34},
 \qquad e_ie_j=\delta_{ij}e_i,
\]

the fourth effect is

\[
 K_4=
 \begin{pmatrix}
 -6699/128&0\\
 0&-7149/128
 \end{pmatrix}.
\]

It has rank two and inertia

\[
 (n_+,n_-,n_0)=(0,2,0).
\]

Every normalized positive profile state is

\[
 \omega_w(x)=wx_{33}+(1-w)x_{34},\qquad 0\leq w\leq1.
\]

Consequently

\[
 \omega_w(K_4)
 =\frac{450w-7149}{128}
 \in\left[-\frac{7149}{128},-\frac{6699}{128}\right]<0.
\]

Thus no convex recombination of these evaluation channels is a positive fourth
effect.  In particular, \(K_4\) cannot be \(J^\dagger J\) on a Hilbert
carrier.  The certified Hudson--Parthasarathy continuation has

\[
 D=\frac12\sum_eJ_e^\dagger J_e
\]

and therefore cannot accept this \(K_4\) as an ordinary completely positive
fourth jump.  This closes the direct evaluation-diagonal continuation of the
positive stochastic Møller column.

Merely adding off-diagonal entries on this same positive carrier cannot help:
every positive-semidefinite matrix has nonnegative diagonal entries.  A larger
channel recombination remains possible only if it derives additional terms
before the physical pullback, so that these certified kernels are pre-trace
components rather than the final Hilbert-space expectations.

## Exact minimal Krein lift

The negative effect does possess a canonical indefinite factorization.  At the
shared

\[
 \rho=\frac{819}{4000},
\]

the previously forced complement fibre has Gram matrix

\[
 G_{\rm miss}(\rho)=
 \begin{pmatrix}
 0&-\rho\\
 -\rho&-2
 \end{pmatrix}.
\]

It has inertia \((1,1,0)\), and its second basis vector \(f_2\) has the
particularly simple norm

\[
 f_2^TG_{\rm miss}f_2=-2.
\]

Take one copy of this fibre over each hard idempotent.  The resulting module

\[
 {\cal E}_h={\cal A}_h\otimes E_\rho
\]

has Gram \(\eta_h=G_{\rm miss}\oplus G_{\rm miss}\) and inertia
\((2,2,0)\).  Define the forward block

\[
 Be_{33}=\frac{\sqrt{6699}}{16}\,e_{33}\otimes f_2,
 \qquad
 Be_{34}=\frac{\sqrt{7149}}{16}\,e_{34}\otimes f_2.
\]

Then, exactly,

\[
 B^\sharp B=B^T\eta_hB
 =\begin{pmatrix}
 -6699/128&0\\
 0&-7149/128
 \end{pmatrix}
 =K_4.
\]

On the source plus target module, with metric
\(\eta_{\rm tot}=I_2\oplus\eta_h\), the block operator

\[
 {\cal K}_4=
 \begin{pmatrix}
 0&-B^\sharp\\
 B&0
 \end{pmatrix}
\]

obeys

\[
 {\cal K}_4^T\eta_{\rm tot}
 +\eta_{\rm tot}{\cal K}_4=0.
\]

It is therefore an exact Krein-skew fourth-order jet.  It is also minimal on
the two-point evaluation carrier: a rank-two negative pullback requires two
negative target directions, while one cross-Krein fibre has only one.  The
fibre module over the two hard points supplies exactly two.

This is the first explicit operator that simultaneously retains the hard base
and uses the forced complement fibre.  Its meaning is limited: it reconstructs
the exact negative profile effect, not a positive event.

## Consequence for the two routes

The ordinary physical route now has a scoped obstruction:

- the existing positive HP column cannot be extended diagonally by the exact
  fourth profile;
- no faithful positive mixture of the two hard channels repairs it; and
- changing only a positive normalization cannot repair its sign.

The indefinite route remains algebraically open:

- the exact Krein-skew lift exists;
- but it occupies negative directions and is not weak-ghost-symmetry data by
  itself;
- no BT zero-mode or higher-composite calculation has derived this block; and
- compatibility with the BT charge support and generalized-Born trace is
  unproved.

Accordingly, Eq. (19) or an off-diagonal dynamical trace is no longer merely
one attractive completion among many.  On this carrier it is the kind of
additional mechanism required to turn the exact tree data into a positive
fourth event.

## Claim boundary

Established exactly:

- the even eight-leg external orientation;
- the strictly negative rank-two profile effect;
- negativity of every nonzero positive diagonal profile average;
- obstruction to an ordinary CP/HP fourth jump on this carrier;
- the two-point cross-Krein module and its inertia;
- the exact pullback \(B^\sharp B=K_4\);
- the exact Krein-skew generator identity; and
- minimal negative index two for an injective two-channel lift.

Not established:

- a negative complete finite-resolution probability;
- a no-go for a larger channel recombination or dynamical quotient that
  changes the physical pullback by additional derived terms;
- a no-go for an Eq. (19) generalized-Born trace;
- the normalized magnitude of either fourth probability;
- a BT-derived or charge-compatible realization of the Krein block;
- a complete \(2\to6\) probability or spacetime Møller/LSZ operator;
- all-order Eq. (19), a gravity/BRST lift, or anything
  `LORENTZIAN-CAUSAL`.

## Literature state

The primary source remains Bateman and Turok,
[arXiv:2607.00096v1](https://arxiv.org/abs/2607.00096), submitted
2026-06-30.  Its cited companion proof of Eq. (19) was not present on arXiv
when checked on 2026-08-11.  The present certificate therefore does not claim
literature priority.

## Verification receipt

All commands ran sequentially on 2026-08-11 with `ulimit -v 500000` and
Python 3.12.13 from
`/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3`.

- Tier 0 Python compilation passed for the producer, verifier, and mutation
  tests (`0.03 s`, peak `14596 KiB`).
- Tier 0 JSON parsing passed for the work item, certificate, and schema
  (`0.10 s`, peak `14600 KiB`).
- `python3 reverse_physics/bt_eight_point_profile_positivity_obstruction.py
  --check` passed `20/20` exact checks (`0.41 s`, peak `68020 KiB`).
- `python3
  reverse_physics/verify_bt_eight_point_profile_positivity_obstruction.py`
  passed `20/20` independent checks (`0.37 s`, peak `70124 KiB`).
- `python3
  reverse_physics/tests/test_bt_eight_point_profile_positivity_obstruction.py`
  passed `20/20` falsification tests (`7.02 s`, peak `70388 KiB`).
- Two-pass `pdflatex` builds of Paper V passed (`0.50 s`, `0.54 s`;
  peak `50644 KiB`, `50296 KiB`).  The second pass retains exactly its
  four pre-existing overfull boxes and introduces no new one.
- After splitting the long certificate label, two-pass `pdflatex` builds of
  Paper VI passed (`0.58 s`, `0.53 s`; peak `50700 KiB`, `50840 KiB`)
  with no overfull box or undefined reference.

The producer imports every mathematical predecessor by content hash.  Its
exact reconstruction plus the independent matrix/sign verifier is the affected
Tier 2 chain for this new classification.  A Tier 3 full-repository rebuild was
unnecessary: no shared core algebra, freeze, release, lifecycle promotion
beyond `CLASSIFIED`, or Lorentzian claim changed.  The Science Forge advisory
was not rerun because its earlier same-session helpers aborted and its census
timed out after `180.17 s`; that inconclusive advisory output is not evidence
for this claim.
