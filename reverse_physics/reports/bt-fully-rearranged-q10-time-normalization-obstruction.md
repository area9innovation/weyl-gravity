# Fully rearranged BT q10 time-normalization obstruction

**Certificate:**
`REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_TIME_NORMALIZATION_OBSTRUCTION_V1`

**Tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.
**Lifecycle:** `CLASSIFIED`.

## Result

The displayed selected-packet \(q_{10}\) interference does not yet belong to
one consistently normalized finite-time experiment.  Its leading tree factor
is a relative-duration cut root after the independent external center-time
volume has been cancelled, whereas its two third-order loop factors still
integrate three unrestricted vertex times over \([0,T]^3\).

This is an exact normalization obstruction, not an infrared estimate.  It
supersedes the finite-time \(q_{10}\) value and RG identity at their common-time
normalization step.  It does not supersede the graph exhaustion, support
zeros, species tensors, fixed-\(T\) distributional loop constructions, or the
leading all-time \(q_8\) theorem.

## Where the extra time occurs

The fully rearranged packet has equal fixed incoming and outgoing total
four-momentum.  Hence the total external frequency of every six-leg graph is

\[
 \Omega=0.
\]

For one ordering of three vertices, let \(t\) be the earliest vertex time and
\(u,v\) the two successive gaps.  The full switched sector is

\[
 \begin{split}
 I_{3,T}(\Delta_1,\Delta_2)
 &=\int_{u,v\ge0\atop u+v\le T}
 (T-u-v)e^{i\Delta_1u+i\Delta_2v}\,du\,dv\\
 &=T A_{3,T}(\Delta_1,\Delta_2),
 \end{split}
\]

where

\[
 A_{3,T}=\int_{u,v\ge0\atop u+v\le T}
 \left(1-{u+v\over T}\right)
 e^{i\Delta_1u+i\Delta_2v}\,du\,dv.
\]

Thus every triangle ordering and every chronological sector of the
bubble-with-bridge contains one exact external center-time factor \(T\).
The factor is present before any large-\(T\) estimate.

The analogous two-vertex sector is

\[
 I_{2,T}(\delta)=\int_0^T(T-\tau)e^{i\delta\tau}\,d\tau
 =T A_{2,T}(\delta),
\]

\[
 A_{2,T}(\delta)=\int_0^T
 \left(1-{\tau\over T}\right)e^{i\delta\tau}\,d\tau.
\]

The certified leading cut root instead uses

\[
 F_T(\delta)=\int_0^T e^{i\delta\tau}\,d\tau.
\]

These are not the same finite-time kernel.  The zero-defect witness is

\[
 A_{2,T}(0)={T\over2},\qquad F_T(0)=T.
\]

More generally, after removing the common \(i^n\delta^nT^{n+1}\), their
Taylor coefficients are respectively

\[
 {1\over n!(n+1)(n+2)},
 \qquad
 {1\over n!(n+1)}.
\]

The independent verifier reconstructs all coefficients through degree eight
by separate beta-simplex integrals.

## Correction of the bubble forest identity

The local MSbar derivative remains exact:

\[
 \partial_{\log\mu}b_{\mu,\mathbf Q}(t_A-t_B)
 =2\delta(t_A-t_B).
\]

But collapsing \(t_A=t_B=t\) leaves a two-time square, not the already
center-time-cancelled tree cut root:

\[
 2\int_{[0,T]^2}dt\,dt_C\,
 e^{i((q_A^0+q_B^0)t+q_C^0t_C)}d_E(t-t_C).
\]

Since \(q_A^0+q_B^0=-q_C^0\), changing to
\(\tau=t-t_C\) gives the overlap length \(T-|\tau|\).  Its two time
orientations therefore carry the taper \(1-|\tau|/T\); an oriented positive
branch carries \(A_{2,T}\), not \(F_T\).  Consequently

\[
 \partial_{\log\mu}T_{6,{\rm bb},T}
 ={5\over4\pi^2}T_{4,T}
\]

is superseded as a finite-time identity between the previously named
kernels.  The correct structural statement relates
\(T_{6,{\rm bb},T}/T\) to the center-time-anchored collapsed tree kernel.
Its species coefficient is retained, but the scalar time kernel must be
matched before an RG cancellation is claimed.

## What survives

The following predecessor results are independent of the mismatch and remain
available:

- the triangle and bubble-with-bridge exhaust the normal-ordered connected
  direct-auxiliary order-\(g^3\) six-leg graphs;
- all 202 externally disconnected partitions remain off the fully
  rearranged support;
- the full three-time triangle and renormalized bubble-with-bridge are
  well-defined fixed-\(T\) distributions on their declared compact packets;
- their species tensors remain total-\(\kappa\) fixed; and
- the common-Born identity will apply after one common scalar time
  normalization is supplied.

The exact scalar \(R_t\)-similarity cancellation is also retained as an
algebraic statement.  It cannot repair a mismatch between two different
time-normalized amplitudes.

The leading all-time result

\[
 q_{8,\infty}[F]
 =16\left\|\sum_{i,a}K_{ia,\infty}F\right\|^2>0
\]

is unaffected.  It was derived directly from the relative-duration cut root
and explicitly did not transfer \(q_{10}\).

## The route through the barrier

The corrected temporal kernels have good rigged limits.  In tempered
distributions,

\[
 A_{2,T}(s)\longrightarrow
 H_+(s)=\pi\delta(s)+i\operatorname{PV}{1\over s},
\]

and

\[
 A_{3,T}(s_1,s_2)\longrightarrow
 H_+(s_1)\otimes H_+(s_2).
\]

For the bubble spectral representation, put

\[
 W_T(x,y)={1\over T}F_T(-x-y)F_T(x)F_T(y).
\]

Its inverse Fourier kernel is the length of the common overlap of three
translated copies of \([0,T]\), divided by \(T\).  It tends to one at every
fixed pair of relative times, and therefore

\[
 W_T(x,y)\longrightarrow(2\pi)^2\delta(x)\delta(y)
\]

in \(\mathcal S'(\mathbb R^2)\).

These limits show that removing the center time does not destroy the
all-time boundary.  They do not yet justify passing the limit through the
triangle loop momentum or the renormalized bubble/bridge distributions.

The next calculation is therefore not to divide the old \(q_{10}\) formula
after the fact.  It is to derive the order-\(g^5\) normalized Born trace with
one external center time removed before its tree and loop sides are split.
An equivalent construction may use matched anchored order-\(g^2\) and
order-\(g^3\) amplitudes.  Only that object can support a finite-time RG
identity and an all-time \(q_{10}\) packet theorem.

## Claim boundary

No matched finite-time or all-time \(q_{10}\), sign, finite-coupling
probability, bounded whole-carrier operator, Møller/LSZ/\(S\) operator,
Eq. (19), gravity/BV--BRST/QME transfer, or `LORENTZIAN-CAUSAL` statement is
established.

## Verification receipt

- Tier 0: the new Python and JSON files parse; the scoped diff is checked;
  Papers V and VI are compiled twice under the 500 MB cap.
- Tier 1: the producer passes 31/31 exact checks, the independent verifier
  passes 41/41 checks, and 23 focused tests pass, including 21 certificate
  mutations.  The focused tests take 1.61 seconds; their peak resident memory
  is 24,432 KiB.
- Tier 2: the direct time-normalization predecessor chain is replayed
  sequentially under the 500 MB cap.  Its producers pass
  25/25, 26/26, 30/30, 31/31, 41/41, 33/33, 36/36 and 31/31 checks; its
  independent verifiers pass 24/24, 23/23, 32/32, 45/45, 65/65, 54/54,
  37/37 and 41/41 checks.  The eight focused test packages run 227 tests with
  no failures.  The largest observed resident set is 79,432 KiB.  No
  classical, shared-core, freeze, release, QME, or Lorentzian state changes,
  so Tier 3 is not required.
- Papers V and VI compile twice in 0.53/0.53 and 0.52/0.54 seconds, with
  respective peaks of 50,972 and 50,896 KiB.  Paper V is 84 pages and Paper
  VI is 72 pages.  Their six and two old overfull boxes remain; this edit adds
  none.
- Science Forge records an append-only `OBSTRUCTED` transition.  The existing
  Go coordinator folds 1,591 nodes with zero invalid items and zero malformed
  events.  `s-f work check` itself remains fail-closed because the Forge
  compiler reports the known `sanitize_thread` compile-time-name defect; that
  failed advisory command is not counted as a pass.  The obstruction is the
  deliverable; the corrected normalized Born cut is a new work item rather
  than an implicit promotion.

Commands:

```text
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_fully_rearranged_q10_time_normalization_obstruction.py --write --check
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_fully_rearranged_q10_time_normalization_obstruction.py
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_fully_rearranged_q10_time_normalization_obstruction
```

CLOSE-OUT: OBSTRUCTED -- the previous selected \(q_{10}\) tree-loop cross
mixes center-time conventions.  Its graph and species ledger survives, and a
matched anchored temporal boundary is now exact, but the normalized Born cut
must be derived before \(q_{10}\) is a physical coefficient.

EVIDENCE:
`reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_TIME_NORMALIZATION_OBSTRUCTION_V1.json`
