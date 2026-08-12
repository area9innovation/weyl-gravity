# BT fully rearranged physical packet probability

Certificate:
`REVERSE_PHYSICS_BT_FULLY_REARRANGED_PHYSICAL_PACKET_PROBABILITY_V1`.

Dependencies: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`. Lifecycle:
`COEFFICIENT_COMPUTED`.

## Result

There is a nonempty class of finite-time three-particle detectors for which
the globally certified connected BT column is the **complete leading
transition amplitude**, not merely the connected part of an unknown answer.

Choose compact incoming and outgoing packet supports `X` and `Y` around the
exact rational centers below. They are separated from every momentum support
of a disconnected six-leg distribution. Consequently

\[
 P_Y(U_T-I)P_X=\lambda^4 A_{YX}+O(\lambda^5),
 \qquad A_{YX}=P_YA_{\rm full}P_X,
\]

with no disconnected order-`lambda^4` remainder. Since `P_Y P_X=0`, neither
the identity nor a forward/survival amplitude enters the first nonzero click
coefficient:

\[
 q_{Y\leftarrow X}
 =\lambda^8\langle\Psi_{\rm in},A_{YX}^*A_{YX}\Psi_{\rm in}\rangle
 +O(\lambda^9).
\]

For the declared dressed scalar source this is

\[
 \boxed{
 q_{Y\leftarrow X}=16\lambda^8
 \left\|\sum_{B=1}^{9}P_YK_{B,T}P_XF\right\|^2+O(\lambda^9),
 }
\]

and the global theorem gives

\[
 q_{Y\leftarrow X}^{(8)}
 \leq\frac{81}{200\pi^6}\lambda^8T^2.
\]

This is the first complete leading physical three-to-three packet
coefficient in this line of work. “Complete leading” is deliberately scoped:
it means that every connected and disconnected contribution at the first
nonzero order has been accounted for on this detector. It does not mean an
all-order or all-time probability.

## Exact detector witness

Use the already certified regular chart centers

\[
 x_0=(2,-2,0,15/16,0),\qquad
 y_0=(2,-2,105/73,2,1/3).
\]

The incoming momenta are

\[
 \begin{split}
 p_0&=(6/5,6/5,0,0),\\
 p_1&=(1,-3/5,124/2405,384/481),\\
 p_2&=(1,-3/5,-124/2405,-384/481),
 \end{split}
\]

and the outgoing momenta are

\[
 \begin{split}
 k_0&=(6/5,6/85,-32328/40885,36792/40885),\\
 k_1&=(1,-1563/2125,80904/1022125,-137548/204425),\\
 k_2&=(1,1413/2125,727296/1022125,-46412/204425).
 \end{split}
\]

Exact Fraction arithmetic verifies

\[
 p_i^2=k_a^2=0,
 \qquad \sum_i p_i=\sum_a k_a=(16/5,\mathbf0).
\]

All external energies are at least one. The six same-side pair invariants are

\[
 96/25,\ 96/25,\ 64/25
\]

on each side, so no same-side pair is collinear.

More directly, put all external momenta in incoming convention,

\[
 \ell=(p_0,p_1,p_2,-k_0,-k_1,-k_2).
\]

For every subset `S` of size one, two, or three, compute the Euclidean square
of its momentum sum. The exact minima are

\[
 \begin{array}{c|c}
 |S|&\displaystyle\min_S\left|\sum_{i\in S}\ell_i\right|_E^2\\ \hline
 1&2\\
 2&32/625\\
 3&17794/10625.
 \end{array}
\]

All are strictly positive. Continuity therefore supplies compact
neighborhoods `X` and `Y` on which all the same subset sums remain separated
from zero. This one statement simultaneously excludes soft components,
identity spectators, collinear on-shell three-point components, and every
independent three-leg momentum delta.

The nine individual incoming--outgoing momentum distances are also recorded
exactly. Their minimum is `32/625`, explicitly confirming that no outgoing
particle is an unchanged incoming spectator, even after relabeling.

## Exhaustive disconnected classification

A disconnected six-leg graph partitions the six external labels among two or
more connected components. The producer enumerates all set partitions rather
than listing only expected graph topologies:

\[
 B_6=203,
 \qquad B_6-1=202
\]

disconnected partitions. Their ten possible component-size profiles are

\[
\begin{gathered}
1+1+1+1+1+1,\quad1+1+1+1+2,\quad1+1+1+3,\\
1+1+2+2,\quad1+1+4,\quad1+2+3,\quad1+5,\\
2+2+2,\quad2+4,\quad3+3.
\end{gathered}
\]

Every profile has at least one component containing at most three external
legs.

In momentum space, each connected component carries its own conservation
distribution

\[
 \delta^{(4)}\!\left(\sum_{i\in S}\ell_i\right),
\]

possibly multiplied or differentiated by vertex, propagator, or external-jet
factors. For every possible small component `S`, the exact detector margins
above keep its argument away from zero. Hence at least one factor in every
disconnected partition pairs to zero with the detector.

This includes the potentially delicate profiles:

- `2+4`: the two-leg component is an identity spectator delta or an
  impossible same-time orientation;
- `3+3`: both components have their own three-leg conservation deltas; all
  twenty three-subset sums are nonzero on the selected support;
- profiles containing a singleton: the one-leg conservation distribution is
  supported only at zero momentum.

No assumption about the numerical value or phase of the lower connected
four-point block is required. Its disconnected embedding is killed by the
spectator delta before that block is evaluated.

Vacuum components have a separate but immediate disposition. A nontrivial
vacuum bubble has positive coupling degree. If it multiplies the identity
external graph, `P_Y P_X=0` kills it; if it multiplies the first connected
six-leg graph, its coupling degree is strictly greater than four. Empty
external blocks omitted from the Bell-partition enumeration therefore cannot
restore a selected order-`lambda^4` transition.

## Why derivatives do not restore disconnected terms

The generalized BT projector differentiates independent external mass
parameters before taking the massless boundary. Derivative vertices and
delta-prime external measures can also differentiate distributions. None of
these operations invalidate the support argument, because

\[
 \operatorname{supp}(\partial^\alpha T)
 \subseteq\operatorname{supp}(T).
\]

Derivatives can change the order of a distribution on its support, but cannot
move it into a compact detector region disjoint from that support. Therefore
the annihilation applies to the complete generalized-Born external-mass jet,
not merely to an ordinary on-shell amplitude evaluated at one point.

## Why the connected term is the first one

For the public cubic and quartic vertices,

\[
 d_\lambda=E+2L-2
\]

for every connected graph. A connected six-leg tree therefore begins at

\[
 d_\lambda=6-2=4.
\]

The predecessor already proves that its three topology families are exactly
`V4^2`, `V3^2 V4`, and `V3^4`, and that their complete species output is the
positive-even four-plane. The global successor proves the unit-weight sum is
Hilbert--Schmidt across the full momentum phase space, including `q_B=0`.

Combining those results with the disconnected support theorem gives

\[
 P_Y(U_T-I)P_X=\lambda^4P_YA_{\rm full}P_X+O(\lambda^5).
\]

The `O(lambda^5)` boundary is conservative and includes the already declared
possible order-`lambda` correction to the dressed scalar preparation. For the
bare six-leg connected graph series itself, loop counting advances from
`lambda^4` to `lambda^6`.

## Complete leading click probability

Let `F` be the normalized compact incoming packet and use the positive-even
source `u_0`. The hard species residue is dark and the other nine residue
images coincide, so

\[
 A_{YX}(F\otimes u_0)
 =4\lambda^4
 \left(\sum_{B=1}^{9}P_YK_{B,T}P_XF\right)\otimes u_0.
\]

Consequently

\[
 q_{Y\leftarrow X}^{(8)}
 =16\lambda^8
 \left\|\sum_{B=1}^{9}P_YK_{B,T}P_XF\right\|^2\geq0.
\]

Restricting the globally Hilbert--Schmidt column cannot increase its norm.
The predecessor's global estimate therefore yields

\[
 q_{Y\leftarrow X}^{(8)}
 \leq\frac{81}{200\pi^6}\lambda^8T^2.
\]

Because `P_Y P_X=0`, the usual orthogonal-detector lemma applies: if

\[
 P_YU_TP_X=\lambda^4A_{YX}+\lambda^5A_5+\cdots,
\]

then the order-`lambda^8` coefficient of its adjoint square is exactly
`A_YX^* A_YX`. Unknown higher amplitudes and the forward/survival coefficient
do not enter it.

On the inherited contraction domain one may define the operational binary
effects

\[
 E_{\rm click}=A_{YX}^*A_{YX},\qquad
 E_{\rm no}=I-E_{\rm click}.
\]

They are positive and sum to the identity. As before, the second effect is an
operational leading detector complement, not an identification of the BT
forward graph.

## Meaning of “the physical”

This result reaches a clean and defensible version of the physical route:

- a concrete dressed scalar preparation;
- a nonempty open class of momentum-resolving detectors;
- the actual unit-weight BT tree amplitude;
- every connected and disconnected contribution at its first nonzero order;
- a nonnegative, dimensionless normalized-packet transition coefficient;
- no dependence on an unknown forward graph at that order.

It is stronger than a connected amplitude or a detector-modified toy model.
It is still weaker than a complete scattering theory. The result is at fixed
finite time, for selected fully rearranged supports, and at leading order.

It does not establish detector-overlap sectors, higher perturbative orders,
the all-time limit, general Eq. (19), loop/KLN completion, gravity, BV/BRST
transfer, or anything `LORENTZIAN-CAUSAL`.

## Next gate

For this selected experiment, the leading physical coefficient is complete.
The next physical extension is to relax the support separation and compose
the lower connected blocks on spectator-overlap strata. That is needed for an
all-channel detector theorem, but it is not needed for the fully rearranged
transition proved here.

The alternative Eq. (19) route remains a distinct nonregular projector
problem. The existing regular same-carrier architecture is obstructed, so any
successful Eq. (19) construction must be localized/on-shell, doubled,
singular/unbounded, or nonperturbative.

## Verification receipts

All scientific commands run sequentially under `ulimit -v 500000` with
Python `/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3`:

- producer: `28/28`, pass, `0.34 s`, `64296 KB` maximum RSS;
- independent verifier: `28/28`, pass, `0.10 s`, `23640 KB` maximum RSS;
- thirteen tests, including twelve decisive mutations: pass, `0.16 s`,
  `24620 KB` maximum RSS.

Papers 5 and 6 compiled twice with `pdflatex -interaction=nonstopmode
-halt-on-error` under the same memory cap. Their final passes took `0.48 s`
and `0.50 s`, at `50756 KB` and `50532 KB` maximum RSS; no new overfull boxes
were introduced. The append-only planning fold imported `1493` nodes with
zero invalid items and zero malformed events in `5.93 s` at `281872 KB`
maximum RSS.

Tier 0 covers Python/JSON parsing, TeX compilation, staged-diff inspection,
and `git diff --check`. Tier 1 is the producer, independent verifier, and
mutation suite. The content-pinned predecessor chain supplies the affected
Tier-2 gate. Tier 3 is not required because this is a reduced-mode leading
coefficient theorem, not a freeze, shared-core change, QME promotion, or
Lorentzian result.

CLOSE-OUT: DONE — the exact support theorem, coefficient certificate,
independent verifier, mutation suite, Papers 5/6, and append-only planning
transition establish the complete leading fully rearranged physical packet
probability.

EVIDENCE:
`reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_PHYSICAL_PACKET_PROBABILITY_V1.json`
