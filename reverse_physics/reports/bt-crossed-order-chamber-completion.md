# BT crossed-order chamber completion

Certificate: REVERSE_PHYSICS_BT_CROSSED_ORDER_CHAMBER_COMPLETION_V1

Lifecycle: CLASSIFIED

Dependencies: LOCAL-ALGEBRAIC, REDUCED-MODE

## Result

The certified physical vacuum intertwiners do not transfer the full
two-sided Hudson--Parthasarathy unitary. They cover only the chronological
vacuum-output chamber. Once those same vectors are allowed as incoming
states, the HP creation terms produce orthogonal time-order chambers that
have no certified physical Källén map.

The smallest ancestry-matched, no-spectator closure contains 388
history-chamber sheets rather than the 76 vacuum-ordered sheets. Exactly 312
crossed sheets are missing physical affiliation. This replaces the vague
phrase "arbitrary incoming continuum" by a first finite and computable domain
problem.

## The conserved HP grading

Let \(L\) be the rooted-comb level operator and let \(N_F\) be Boson number on
the 75-edge noise Fock space. Define

\[
 Q_{\rm HP}=N_F-L.
\]

For every insertion edge \(e\),

\[
 J_e\,dA_e^\dagger:
 (N_F,L)\longmapsto(N_F+1,L+1),
\]

whereas

\[
 -J_e^\dagger dA_e:
 (N_F,L)\longmapsto(N_F-1,L-1).
\]

The drift \(D=\frac12\sum_eJ_e^\dagger J_e\) preserves both numbers.
Consequently

\[
 [Q_{\rm HP},U_a]=0
\]

on the finite-particle adapted core. This is an auxiliary system--noise
grading. It is not the BT boost charge, ghost parity, or a spacetime
conservation law.

The vacuum path lies in \(Q_{\rm HP}=0\): at rooted-comb level \(k\), it has
exactly \(k\) ancestral edge quanta. The full \(Q_{\rm HP}=0\) sector is
larger; here we first take the smallest subspace having exactly the ancestral
edge set and no additional spectators.

## Why the vacuum chamber is not two-sided

The certified maps have sources

\[
 {\cal O}_k=\{0<t_1<\cdots<t_k<a\}
\]

with one copy for every rooted-comb history. This is exactly the order
generated from a vacuum input by adapted forward creation.

It is not invariant when used as an incoming space. Suppose an incoming
level-one vector already contains its parent-edge quantum at a late time
\(t_1\). The level-one HP coefficient can create a child-edge quantum at an
earlier time \(t_2<t_1\). The resulting two-quantum vector has the correct
ancestral edge set, but lies in the reversed chamber rather than
\(t_1<t_2\). The coefficient has squared norm \(q_1=5/64\), so this leakage
is not a null boundary effect.

At general level \(k\), a new edge time has \(k+1\) possible positions among
the existing ancestral times. Only the last position remains in the vacuum
chronology. The other \(k\) positions are crossed chambers.

External-label permutation covariance does not repair this. The existing
seven-point certificate explicitly keeps the chronologically attached
daughter distinct from the pre-existing cluster. Relabeling final external
legs inside one chronological chamber does not turn an incoming pre-existing
quantum into a later emitted quantum.

## Minimal chamber closure

Let \(c_k\) be the number of time-order chambers required per rooted history.
Insertion in every possible position gives

\[
 c_0=1,\qquad c_{k+1}=(k+1)c_k,
\]

and hence

\[
 c_k=k!.
\]

The adjoint annihilation term removes the current ancestral edge and returns
one of the \(k!\) parent chambers. Therefore all factorial chambers form a
reducing no-spectator path space. The insertion recurrence also proves
minimality: any reducing subspace containing the canonical chambers must
contain every chamber produced in the next level.

The exact multiplicities are:

| level \(k\) | rooted histories | chambers/history | completed sheets | already affiliated | missing crossed |
|---:|---:|---:|---:|---:|---:|
| 0 | 1 | 1 | 1 | 1 | 0 |
| 1 | 3 | 1 | 3 | 3 | 0 |
| 2 | 12 | 2 | 24 | 12 | 12 |
| 3 | 60 | 6 | 360 | 60 | 300 |
| **total** | 76 |  | **388** | **76** | **312** |

Retaining the two physical jet species changes the multiplicity from 152 to
776. The difference is 624 species-resolved continuum copies.

Starting directly from canonical incoming chambers exposes 12 reversed
level-two sheets and 120 of the level-three crossed sheets. Closing those
new level-two chambers under the third creation generates the remaining 180,
giving all 300 noncanonical level-three sheets.

## Exact finite leakage witness

The certificate includes a three-state exact witness with basis

\[
 (\text{late parent},\text{canonical child},\text{reversed child}).
\]

For \(q_1=5/64\), let

\[
 B=\begin{pmatrix}
 0&0&0\\
 0&0&0\\
 \sqrt5/8&0&0
 \end{pmatrix},
 \qquad K=B-B^T.
\]

The Cayley transform

\[
 U_C=(1+K)(1-K)^{-1}
 =
 \begin{pmatrix}
 59/69&0&-16\sqrt5/69\\
 0&1&0\\
 16\sqrt5/69&0&59/69
 \end{pmatrix}
\]

is exactly orthogonal and sends the parent into the reversed chamber with
probability

\[
 \frac{1280}{4761}>0.
\]

This is not presented as the continuous HP cocycle. It independently proves
that the coefficient-level leakage is compatible with exact two-sided
unitarity and is not an artifact of a nonunitary truncation.

## What would produce the physical operator

Let \({\cal H}_{\rm ch}\) denote the 388-sheet chamber-complete path carrier.
The HP cocycle has a unitary restriction to this reducing no-spectator
carrier. A physical map

\[
 {\cal A}_{\rm ch}:{\cal H}_{\rm ch}
 \longrightarrow{\cal K}_{\rm phys,ch}
\]

would have to:

1. agree with \({\cal A}_{\le3}\) on the 76 canonical chambers;
2. map all crossed chambers into declared incoming/outgoing physical
   continuum ranges;
3. intertwine the HP creation and annihilation pairs;
4. preserve the nested Abel/Källén translations, species Gram, crossing
   convention, and generalized-Born domain.

If such a unitary affiliation exists, then

\[
 S_{\rm ch}={\cal A}_{\rm ch}
 U_a|_{{\cal H}_{\rm ch}}
 {\cal A}_{\rm ch}^*
\]

is a two-sided reduced-mode physical unitary with the already certified
vacuum column. The missing defect action would then be selected by the
pinned HP dynamics on this sector rather than chosen abstractly.

No such \({\cal A}_{\rm ch}\) is presently known. The first missing block is
the reversed two-time chamber for each of the 12 six-point histories. It
requires crossing one degenerate leg into the incoming side while retaining
both resolution variables and the full two-species signed Gram. This is
distinct from the vacuum fourth jump: it is a crossed two-emission problem,
not a new fourth forward emission.

The 388 sheets also exclude arbitrary spectators. Sectors with
\(Q_{\rm HP}\ne0\), non-ancestral edge configurations, non-strongly-ordered
kinematics, and spacetime asymptotic states remain additional gates.

## Claim boundary

Established exactly:

- conservation of \(Q_{\rm HP}=N_F-L\) on the finite-particle adapted core;
- non-invariance of the vacuum chronological carrier under two-sided HP
  action;
- the factorial chamber recurrence and its minimal reducing closure;
- the counts 76 canonical, 388 completed, and 312 missing crossed sheets;
- the first 12 reversed six-point sheets and 300 noncanonical seven-point
  sheets;
- an exact nonzero unitary-compatible reversed-chamber witness.

Not established:

- any crossed six- or seven-point physical intertwiner;
- physical affiliation of the 312 missing sheets;
- arbitrary incoming spectator sectors;
- a vacuum fourth jump or complete BT probability;
- a spacetime Møller, LSZ, AQFT, or S operator;
- all-order Eq. (19), gravity/BRST transfer, or anything
  LORENTZIAN-CAUSAL.

## Verification receipt

All scientific Python, SymPy and TeX commands ran sequentially on 2026-08-12
under ulimit -v 500000, using Python 3.12.13 at
/home/alstrup/.local/share/mise/installs/python/3.12.13/bin/python3.

- Python compilation passed in 0.02 s with 15,064 KiB peak RSS.
- The work item, append-only event, schema and certificate parsed as JSON;
  the timed parse took 0.02 s with 14,044 KiB peak RSS.
- The exact producer reproduced the certificate and passed 28/28 checks in
  0.32 s with 68,164 KiB peak RSS.
- The independent reconstruction passed 28/28 checks in 0.36 s with
  71,484 KiB peak RSS.
- The falsification suite passed 21/21 tests in 6.17 s (6.20 s including
  timing overhead), with 71,956 KiB peak RSS. Mutations covered history and
  chamber counts, completed and missing sheets, direct leakage, the HP gauge,
  the exact coefficient/skew/Cayley matrices, leakage probability, transfer
  gates, input hashes, scope boundaries, and prohibited physical promotions.
- Papers V and VI compiled twice. Their final passes took 0.46 s and 0.51 s,
  with at most 50,844 KiB peak RSS. Paper V retains its four pre-existing
  overfull boxes and introduces no new one; Paper VI has no warning, overfull
  box, or undefined reference. PDF text extraction found the chamber counts,
  leakage rate and non-transfer boundary in both rendered papers.
- The narrow Science Forge import-program check accepted all 1,435 nodes
  with zero invalid items and zero malformed events in 8.81 s, using
  269,748 KiB peak RSS under GOMEMLIMIT=256MiB, GOMAXPROCS=1 and a 60 s
  timeout.

The mathematical predecessors are unchanged and content-addressed, so this
new leaf does not trigger their full reconstruction chain. Tier 3 was not run
because no shared core, freeze, release, complete probability, Eq. (19),
gravitational transfer, or Lorentzian lifecycle state is promoted. No skipped
tier is reported as a pass.
