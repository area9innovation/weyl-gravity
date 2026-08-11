# BT six-point parent-jet interference

**Dependency tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

**Lifecycle:** `CLASSIFIED`

**Certificate:** `REVERSE_PHYSICS_BT_SIX_POINT_PARENT_JET_INTERFERENCE_V1`

## Result

The scalar six-point selected-history coefficient \(5/3072\) does not lift to
the constructed positive scalar second species jump on the same two parent
external-mass jets used at five points.  The complete 220-tree amplitude has
nonzero interference between the constant/linear parent jets and the two
spectator-complement profiles.  Its normalized raised two-species
endomorphism has nonzero off-diagonal entries and a strictly negative
characteristic discriminant throughout the physical outer-threshold region.
It therefore cannot be similar to a positive scalar multiple of \(I_2\).

This is the first exact amplitude-level obstruction to the higher identity-
species lift in the channel-resolved branching instrument.  The scalar tree
coefficient and the finite CPTP instrument remain correct as, respectively,
a scalar contraction and an abstract positive completion.  What fails is
their affiliation above the first jump.

## Amplitude before the scalar trace

Use the nested scaling

\[
 x_0=\delta\epsilon a_0,\quad
 x_1=\delta\epsilon a_1,\quad
 s_{01}=\delta\epsilon\tau_1,
 \qquad
 x_2=\delta a_2,\quad s_{012}=\delta\tau_2,
\]

with the remaining three external masses used as square-free spectator jets.
Let

\[
 S_1=a_3+a_4+a_5,
 \qquad
 S_2=a_3a_4+a_3a_5+a_4a_5.
\]

After taking the leading \(\delta\) coefficient and then
\(\epsilon\to0\), the six-point amplitude is

\[
 C_6=F_0+F_1S_1+F_2S_2,
\]

with no \(a_3a_4a_5\) component at amplitude level.  Put

\[
 A=(a_0-a_1)^2-2\tau_1(a_0+a_1)+2\tau_1^2.
\]

The two components relevant to the scalar square are

\[
 F_1=\frac{a_2^2 A}{8\tau_1^2\tau_2},
\]

\[
 F_2=\frac{a_2\{a_2A+2\tau_2[-A+3\tau_1^2]\}}
 {8\tau_1^2\tau_2^2}.
\]

The three singleton masks have the same \(F_1\), and the three complementary-
pair masks have the same \(F_2\).  Consequently

\[
 [a_3a_4a_5]C_6^2=6F_1F_2,
\]

which is exactly the strongly ordered scalar kernel used in the predecessor
threshold calculation.  Thus resolving the species does not alter the
\(5/3072\) scalar history weight.

## Unique parent-jet factorization

Recombine the inner daughter pair into the parent mass jet \(p\).  The outer
five-point amplitude has

\[
 H(p)=H_0+pH_1+O(p^2),
\]

\[
 H_0=L_0S_1+Q_0S_2,
 \qquad
 H_1=L_1S_1+Q_1S_2,
\]

where

\[
 L_0=-\frac{a_2^2}{4\tau_2},\qquad
 Q_0=\frac{a_2(2\tau_2-a_2)}{4\tau_2^2},
\]

\[
 L_1=\frac{a_2}{2\tau_2},\qquad
 Q_1=\frac{\tau_2+a_2}{2\tau_2^2}.
\]

Their profile matrix is invertible:

\[
 \det\begin{pmatrix}L_0&L_1\\Q_0&Q_1\end{pmatrix}
 =-\frac{3a_2^2}{8\tau_2^2}.
\]

On the spectator quotient relevant to
\([a_3a_4a_5]C_6^2\), the factorization
\(C_{6,{\rm rel}}=F_1S_1+F_2S_2=uH_0+vH_1\) is therefore unique.  Exact
reduction gives

\[
 u=\frac{2\tau_1(a_0+a_1)-(a_0-a_1)^2}{2\tau_1^2}
   =2Q_{\rm inner},
 \qquad
 v=\frac{a_2}{2}.
\]

At five points the corresponding second coefficient is
\(2L_{\rm inner}=-(a_0-a_1)^2/(2\tau_1)\).  At six points it has been replaced
by an outer-history variable: \(\partial v/\partial a_2=1/2\).  Thus even the
amplitude factorization is no longer an inner-local repetition of the
five-point splitting operator.

## The interference obstruction

For profiles \(f=lS_1+qS_2\) and \(g=l'S_1+q'S_2\), define the exact
square-free complement pairing

\[
 B(f,g)=[a_3a_4a_5]fg=3(lq'+ql').
\]

In the parent constant/linear basis,

\[
 \begin{aligned}
 B_{00}&=6L_0Q_0
 =-\frac{3a_2^3(2\tau_2-a_2)}{8\tau_2^3},\\
 B_{01}&=3(L_0Q_1+Q_0L_1)
 =\frac{3a_2^2(\tau_2-2a_2)}{8\tau_2^3},\\
 B_{11}&=6L_1Q_1
 =\frac{3a_2(\tau_2+a_2)}{2\tau_2^3}.
 \end{aligned}
\]

Unlike the four-point hard parent used at the first jump, both diagonal
self-pairings are nonzero.  The child covariant species Gram is

\[
 G=\begin{pmatrix}
 u^2B_{00}&uvB_{01}\\
 uvB_{01}&v^2B_{11}
 \end{pmatrix}.
\]

Away from \(B_{01}=0\), normalize by the parent hard cross component and raise
with \(J=\left(\begin{smallmatrix}0&1\\1&0\end{smallmatrix}\right)\).  The
result is

\[
 N=\frac{JG}{B_{01}}
 =\begin{pmatrix}
 ua_2/2 & \dfrac{a_2(\tau_2+a_2)}{\tau_2-2a_2}\\[6pt]
 -\dfrac{u^2a_2(2\tau_2-a_2)}{\tau_2-2a_2}&ua_2/2
 \end{pmatrix}.
\]

Its characteristic discriminant is

\[
 \Delta_N=-\frac{4u^2a_2^2(\tau_2+a_2)(2\tau_2-a_2)}
 {(\tau_2-2a_2)^2}.
\]

For the physical outer domain \(\tau_2>a_2>0\), this is strictly negative
whenever \(\tau_2\ne2a_2\).  Hence \(N\) has a non-real conjugate eigenpair.
An allowed parent-fibre basis change acts on \(N\) by similarity and cannot
change that characteristic polynomial.  A common tree phase, delta-prime
sign, or nonzero real normalization only multiplies both eigenvalues and does
not turn \(N\) into a positive scalar matrix.

At \(\tau_2=2a_2\), \(B_{01}=0\): the parent hard cross normalization vanishes.
This surface is fail-closed and is not a scalar-jump limit.  The unnormalized
profile pairing itself remains nondegenerate, since

\[
 B_{00}B_{11}-B_{01}^2=-\frac{81a_2^4}{64\tau_2^4}.
\]

## Meaning for the branching construction

The earlier finite GKSL instrument remains a valid positive process matching
the first three scalar history probabilities.  Its first jump is still the
certified physical \((1/48)I_2\) map.  The result changes the status of the
second jump: the chosen \(\sqrt{5/64}\,I_2\) species factor is a positive
completion, but it is not the amplitude-derived BT species map on this
carrier.  The seven-point species tensor is not needed to falsify that
minimal identity lift because the obstruction already occurs at six points.

Retaining both gradings instead of tracing one of them gives the minimal
four-component parent-jet times spectator-profile carrier.  Its physical
pullback has a nondegenerate collapse-invisible kernel and a
Krein-orthogonal two-dimensional image with positive scalar raised Gram.
Certificate
`REVERSE_PHYSICS_BT_SIX_POINT_PROFILE_QUOTIENT_COMPLETION_V1` proves that its
projector reproduces the complete scalar amplitude pointwise and affiliates
the conditional \(5/64\) second rate on the quotient fibre.  Thus the present
obstruction is exact on the premature two-species restriction and is resolved,
not contradicted, by the grading-faithful enlargement.  The seven-point
species/profile tensor remains open.

## Verification

The producer reuses the exact cached Berends--Giele subset recursion but emits
all seven amplitude mask components before squaring.  The independent rail
uses invariant triangle vertices and explicitly enumerates all 220 trees.  At
three exact kinematic points crossed with three unrelated hard fixtures it
recovers every finite-\(\epsilon\) mask coefficient, then independently rebuilds
the strong limit, parent factorization, complement pairing, raised matrix,
and characteristic discriminant.

All symbolic Python jobs ran sequentially under `ulimit -v 500000`.  The new
valid rails stayed below 80 MB and the predecessor regression below 83 MB.  A deliberately malformed component mutation
was observed to drive a late symbolic simplifier to 405 MB; it was terminated
and replaced by an equivalent fail-fast serialized-claim gate.  That aborted
diagnostic is not recorded as a pass.

## Verification receipt

| tier | command or check | result | elapsed | peak RSS |
|---|---|---:|---:|---:|
| 0 | Python byte-compile of five changed modules and JSON parse of four structured artifacts | PASS | 0.03 s | 15,588 KB |
| 0 | `git diff --check` on scoped paths | PASS | below 0.3 s | negligible |
| 1 | producer exact reproduction | PASS, 29/29 | 6.37 s | 75,544 KB |
| 1 | explicit-220-tree independent verifier | PASS, 20/20 | 8.58 s | 78,996 KB |
| 1 | producer/verifier plus ten mutations | PASS, 12/12 | 15.30 s | 79,048 KB |
| 1 | predecessor six-point producer after optional component extension | PASS, 20/20 | 7.99 s | 80,576 KB |
| 1 | predecessor explicit-tree verifier after optional leading-component return | PASS, 17/17 | 6.03 s | 82,224 KB |
| 1 | predecessor six-point mutation and unit suite | PASS, 13/13 | 23.10 s | 82,344 KB |
| 1 | Paper V two-pass PDF build | PASS | 0.50 s / 0.42 s | 50,880 / 50,956 KB |
| 1 | Paper VI two-pass PDF build | PASS | 0.45 s / 0.45 s | 50,512 / 50,916 KB |
| coordination | `sfc work-event ... --transition OBSTRUCTED` | append-only event generated, seq. 1 | about 11 s | not measured |

Tier 2 is required only if the extracted component result changes a shared
mathematical input consumed by another certificate chain.  This package
retains the predecessor scalar kernel and coefficient and instead classifies
the previously uncomputed species lift.  Tier 3 is not required: there is no
freeze, release, shared-core algebra change, complete-probability promotion,
or Lorentzian theorem.  No skipped, aborted, or advisory check is counted as
a pass.  The full Science Forge import/shadow census was not rerun because its
recent observed footprint is approximately 481 MB and it cannot start under
the 500 MB virtual-memory rail; the scoped `work-event` transition did parse
the programme and emitted the content-addressed terminal event.  Its first
capped invocation failed during Go runtime address-space reservation before
changing state and is not a pass.
