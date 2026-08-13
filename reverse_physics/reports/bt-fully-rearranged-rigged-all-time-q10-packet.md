# Fully rearranged BT rigged all-time q10 packet coefficient

Certificate:
REVERSE_PHYSICS_BT_FULLY_REARRANGED_RIGGED_ALL_TIME_Q10_PACKET_V1

Tags: LOCAL-ALGEBRAIC, EUCLIDEAN-SPECTRAL, REDUCED-MODE.
Lifecycle: COEFFICIENT_COMPUTED.

## Result

The complete selected fully rearranged BT probability now has a finite
all-time coefficient through \(q_{10}\) on the same smooth compact rigged
packet class used for the leading theorem.  The common external center time
is removed before the limit.  This is exactly the normalization missing from
the superseded finite-time tree--loop cross.

Write

\[
 H_+(s)=\pi\delta(s)+i\operatorname{PV}{1\over s}.
\]

The leading tree is the previously certified map

\[
 T_{4,\infty}=16\sum_C K_{C,\infty}\otimes R_C.
\]

The complete direct-auxiliary loop boundary is

\[
 \begin{split}
 T_{6,\triangle,\infty}
 &={8\over16\pi^2}\sum_{P=1}^{15}
 C_0(Q_{P,1}^2,Q_{P,2}^2,Q_{P,3}^2)S_P,\\
 T_{6,{\rm bb},\infty}
 &={4\over16\pi^2}\sum_{R=1}^{60}
 {B_{\overline{\rm MS}}(Q_R^2)\over K_R^2+i0}W_R,\\
 T_{6,\infty}&=T_{6,\triangle,\infty}+T_{6,{\rm bb},\infty}.
 \end{split}
\]

For every packet \(F\) in the declared domain, both
\(T_{4,\infty}F\) and \(T_{6,\infty}F\) belong to \(L^2(Y)\).  Therefore

\[
 \boxed{
 q_{10,\infty}[F]
 =2\operatorname{Re}
 \langle T_{4,\infty}F,T_{6,\infty}F\rangle}
\]

is a finite exact packet functional.  Its value and sign depend on the packet
and the renormalization coordinate.

## Why the normalization obstruction disappears at all time

The finite-time obstruction found that the tree cut root \(F_T\) and a
center-time-divided Dyson amplitude have different tapers.  Their large-time
boundaries are nevertheless identical:

\[
 A_{2,T}(s)\longrightarrow H_+(s),
 \qquad
 F_T(s)\longrightarrow H_+(s).
\]

The center-time-divided three-vertex triangle has two positive relative
gaps, and

\[
 A_{3,T}(s_1,s_2)\longrightarrow
 H_+(s_1)\otimes H_+(s_2).
\]

Thus the finite-\(T\) interpolation remains noncanonical, but its all-time
boundary is unambiguous.

The bubble-with-bridge has an even cleaner two-dimensional kernel.  Put

\[
 W_T(x,y)={F_T(-x-y)F_T(x)F_T(y)\over T}.
\]

Its inverse Fourier transform is the normalized common-overlap length of
three translated intervals:

\[
 {L_T(u,v)\over T}
 =\max\left(0,1-{\operatorname{diam}(0,u,v)\over T}\right).
\]

It is between zero and one and tends to one for fixed \(u,v\).  In frequency
space,

\[
 W_T(x,y)=T^2W_1(Tx,Ty).
\]

The elementary bound

\[
 |F_1(z)|\leq\min(1,2/|z|)
\]

proves \(W_1\in L^1(\mathbb R^2)\).  Split according to which of
\(|x|,|y|,|x+y|\) are at most one.  A one-small strip has an
\(O(r^{-2})\) tail; the all-large region has an \(O(r^{-3})\) generic tail
and an \(O(r^{-2})\) cancellation-strip tail.  Hence \(W_T\) is an
\(L^1\) approximate identity of mass \((2\pi)^2\):

\[
 W_T(x,y)\longrightarrow
 (2\pi)^2\delta(x)\delta(y).
\]

This proves that the center-time-intensive switched bubble tends to the full
renormalized covariant bubble--bridge distribution, including its local
MSbar term.

## Exact bridge-shell audit

The apparent sixty bridge poles reduce to ten unordered \(3|3\) momentum
masks.  In the all-incoming order

\[
 [p_0,p_1,p_2,-k_0,-k_1,-k_2],
\]

mask \(7\) is the hard momentum \(P=p_0+p_1+p_2\).  Its six species tensors
annihilate the selected source \(u_0\).  The other nine masks are exactly the
nine exchange channels:

| mask | bridge | \(K^2\) | \(N_{ia}\) |
|---:|:---:|---:|---:|
| 14 | \(q_{00}\) | \(-1024/425\) | \(864/425\) |
| 22 | \(q_{01}\) | \(3456/10625\) | \(-16992/10625\) |
| 25 | \(-q_{02}\) | \(-32256/10625\) | \(-4608/10625\) |
| 13 | \(q_{10}\) | \(-1152/425\) | \(-96/85\) |
| 21 | \(q_{11}\) | \(-32/85\) | \(168/85\) |
| 26 | \(-q_{12}\) | \(224/425\) | \(-72/85\) |
| 11 | \(q_{20}\) | \(0\) | \(-384/425\) |
| 19 | \(q_{21}\) | \(-1568/625\) | \(-4008/10625\) |
| 28 | \(-q_{22}\) | \(-32/625\) | \(13608/10625\) |

The same exact chart derivative used at leading order gives

\[
 \partial_tK_R^2=\partial_tq_{ia}^2=-2N_{ia}\ne0
\]

for every nonhard bridge mask.  Only mask \(11=q_{20}\) crosses shell.
All six roles over that mask have positive source weight.

The bubble factor is harmless on this packet because

\[
 |Q_R^2|\ge {32\over625}
\]

for all sixty roles.  Orienting each bridge as
\(K_R=\pm q_{ia}\), write

\[
 K_R^2=D_{ia}\delta_{ia}.
\]

The common noncritical coordinate changes \(t\) to \(\delta_{ia}\).
Consequently \(1/(K_R^2+i0)\) acts as a parameter-dependent Hilbert-transform
PV term plus a smooth coarea delta evaluation.  It is never evaluated
pointwise on shell.  Both pieces send a smooth compact source packet
continuously into \(L^2(Y)\).

## Triangle control

No new triangle singularity is introduced by the limit.  The fifteen
covariant triangle kernels already obey the exact margins

\[
 \min |Q_{P,j}^2|={32\over625},
 \qquad
 \min|\lambda_K|={80896\over903125}.
\]

After shrinking the common packet inside these open margins, every \(C_0\)
is smooth and bounded.  The center-time-divided six-ordering boundary is the
certified covariant \(C_0/(16\pi^2)\).  The finite tensor sum is therefore a
bounded Hilbert--Schmidt packet kernel.

## Common Born rule and RG identity

Every \(S_P\), \(W_R\), and tree residue is fixed by total ghost parity.
The scalar distributions act only on momentum.  Hence

\[
 q_{10,\infty}^{\rm public}[F]
 =q_{10,\infty}^{\rm Hilbert}[F]
\]

on the selected positive carrier.

In the declared MSbar coordinate,

\[
 \partial_{\log\mu}T_{6,{\rm bb},\infty}
 ={5\over4\pi^2}T_{4,\infty},
\]

so

\[
 \partial_{\log\mu}q_{10,\infty}
 ={5\over2\pi^2}q_{8,\infty}.
\]

Together with

\[
 \partial_{\log\mu}\lambda
 =-{5\lambda^3\over16\pi^2},
\]

this gives

\[
 \partial_{\log\mu}
 \left(\lambda^8q_{8,\infty}
 +\lambda^{10}q_{10,\infty}\right)
 =O(\lambda^{12}).
\]

This is an all-time selected-packet identity.  It does not reinstate the
superseded finite-time identity between differently tapered kernels.

## Meaning and boundary

The barrier has been crossed at the level actually supported by the
calculation: the selected fully rearranged physical packet has a complete
finite all-time perturbative jet

\[
 q_\infty[F]
 =\lambda^8q_{8,\infty}[F]
 +\lambda^{10}q_{10,\infty}[F]
 +O(\lambda^{12}).
\]

This is not a new spacetime dimension, a packet-independent number, or a
whole scattering theory.  It is a nontrivial loop-corrected probability
coefficient on a declared smooth packet experiment.

The result does not establish a canonical matched finite-time \(q_{10}\),
the sign of \(q_{10,\infty}\), finite-coupling positivity, a bounded
whole-carrier operator, Møller/LSZ/\(S\), forward or overlap completion,
general Eq. (19), gravity/BV--BRST/QME transfer, or anything
LORENTZIAN-CAUSAL.

## Verification receipt

- Tier 0: the new Python and JSON files parse, the schema validates, and the
  scoped diff is checked.  Papers V and VI compile twice under the 500 MB
  cap in 0.53/0.53 and 0.53/0.54 seconds, with respective peak resident sets
  of at most 51,008 and 51,128 KiB.  Paper V is 84 pages and Paper VI is 72
  pages.  Their six and two old overfull boxes remain; this edit adds none.
- Tier 1: the producer passes 46/46 exact checks, the independent verifier
  passes 56/56 checks, and 33 focused tests pass, including 31 certificate
  mutations.  The producer, verifier, and focused tests take 0.02, 0.07, and
  2.42 seconds, with respective peak resident sets of 17,024, 24,796, and
  24,996 KiB.
- Tier 2: the nine-package direct certificate chain is replayed sequentially
  under the 500 MB cap.  The time-normalization obstruction, all-time
  \(q_8\), triangle covariance, triangle time kernel, bubble covariance,
  bubble time kernel, common Born layer, superseded finite-time \(q_{10}\),
  and this all-time \(q_{10}\) package all pass their producers and
  independent verifiers.  The nine focused packages run 339 tests with no
  failures.  The largest observed resident set is 70,840 KiB.
- Tier 3 is required because the paper promotes a theorem.  The complete
  repository run is fail-closed: 3,556 tests run in 717.600 seconds, with 31
  failures and 9 skips, and exits nonzero.  The failures are in existing
  repository-wide drift/import rails; no failure is in the new all-time
  \(q_{10}\) package.  The run takes 11:58.64 wall-clock time and peaks at
  391,620 KiB with no swaps, within the hard cap.  This non-pass does not
  certify a repository freeze or release, and it does not negate the green
  scoped and transitive certificate chain.
- Science Forge records an append-only `DONE` transition.  The existing Go
  coordinator folds 1,593 nodes with zero invalid items and zero malformed
  events.  `s-f work check` itself remains fail-closed because the Forge
  compiler reports the known `sanitize_thread` compile-time-name defect;
  that failed advisory command is not counted as a pass.

Every scientific process above ran sequentially under the 500 MB hard
virtual-memory cap.

Commands:

~~~text
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/bt_fully_rearranged_rigged_all_time_q10_packet.py --write --check
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 reverse_physics/verify_bt_fully_rearranged_rigged_all_time_q10_packet.py
ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest -v reverse_physics.tests.test_bt_fully_rearranged_rigged_all_time_q10_packet
PATH=/usr/local/bin:/usr/bin:/bin; ulimit -v 500000; /home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3 -m unittest discover -v
~~~

CLOSE-OUT: DONE -- after external center time is removed, the complete
triangle-plus-bubble loop maps the selected rigged packet into \(L^2\), and
its interference with the leading tree gives a finite all-time
\(q_{10,\infty}\) coefficient.

EVIDENCE:
reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_RIGGED_ALL_TIME_Q10_PACKET_V1.json
