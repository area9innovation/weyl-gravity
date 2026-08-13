# Fully rearranged BT q10 selected-packet assembly

**Certificate:**
`REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_SELECTED_PACKET_ASSEMBLY_V1`

**Tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`, `REDUCED-MODE`.
**Lifecycle:** `COEFFICIENT_COMPUTED` as an exact finite-time packet
functional in the declared normal-ordered MSbar auxiliary scheme.

## Result

The first correction to the fully rearranged selected probability is now
complete as an exact packet functional.  The fixed public auxiliary action has
one interaction coupling

\[
 g=\lambda^2,
 \qquad H_{\rm int}=gV_4,
\]

and no cubic vertex.  On the disjoint fully rearranged source and detector
supports, the one-vertex spectator transition vanishes.  Consequently

\[
 \boxed{
 A_{YX}=P_Y(U_T-I)P_X
 =g^2T_{4,T}+g^3T_{6,T}+O(g^4)
 =\lambda^4T_{4,T}+\lambda^6T_{6,T}+O(\lambda^8).}
\]

There is no fixed-auxiliary \(y_5\).  Squaring gives

\[
 q=\lambda^8q_8+\lambda^{10}q_{10}+O(\lambda^{12}),
 \qquad
 \boxed{q_{10}[F]=2\operatorname{Re}
 \langle T_{4,T}F,T_{6,T}F\rangle.}
\]

This replaces the earlier incomplete ledger
\(q_{10}=\lVert y_5\rVert^2+2\operatorname{Re}\langle y_4,y_6\rangle\)
by its complete fixed-frame value for the selected experiment.

## Why no graph or normalization term remains

The order-\(g^3\) ledger closes for four independent reasons.

1. Every one of the 202 externally disconnected six-label partitions carries
   a component momentum delta missed by the fully rearranged compact supports.
   The support argument is independent of coupling order.
2. A pure forward or survival coefficient remains on the incoming support,
   while \(P_YP_X=0\).  It therefore has zero selected click pairing.
3. A vacuum factor capable of multiplying the leading \(g^2\) transition at
   order \(g^3\) would have to be a one-vertex vacuum expectation.  It is zero
   for the declared normal-ordered quartic vertex.  A two-vertex vacuum bubble
   could only multiply the one-vertex spectator transition, which is already
   off the fully rearranged support; a pure vacuum factor multiplies the
   identity and is killed by \(P_YP_X=0\).
4. Every connected six-leg graph at \(g^3\) has three quartic vertices, three
   internal lines and one loop.  The frame-typed multigraph theorem gives four
   orbits.  Both tadpole orbits vanish in the declared normal-ordered massless
   scheme, leaving exactly the triangle and bubble-with-bridge.

Thus

\[
 \boxed{T_{6,T}=T_{6,\triangle,T}+T_{6,{\rm bb},T}.}
\]

The two finite-time predecessor certificates construct both summands,
including the bubble forest counterterm and its bridge-shell distribution.
There is no omitted original-\(\phi\) cubic graph: those graphs are the other
action-frame reorganization and cannot be added to the direct auxiliary list.

## Complete packet functional

On a common compact neighborhood of the same rational fully rearranged center,

\[
 T_{4,T}=16\sum_C K_{C,T}\otimes R_C,
\]

\[
 T_{6,\triangle,T}=8\sum_PJ_{\triangle,T,P}S_P,
 \qquad
 T_{6,{\rm bb},T}={4\over16\pi^2}\sum_RJ_{{\rm bb},T,R}W_R.
\]

Therefore the computed coefficient is

\[
 \boxed{
 \begin{split}
 q_{10}[F]=2\operatorname{Re}\Big\langle
 &\left(16\sum_CK_{C,T}\otimes R_C\right)F,\\
 &\left(8\sum_PJ_{\triangle,T,P}S_P
 +{4\over16\pi^2}\sum_RJ_{{\rm bb},T,R}W_R\right)F
 \Big\rangle .
 \end{split}}
\]

The common packet exists by intersecting and, if necessary, shrinking the
predecessor neighborhoods.  The tree map is bounded and both loop summands
are Hilbert--Schmidt there.  The functional is consequently finite.  It
retains the coherent complex triangle transient, bubble logarithm and bridge
PV/delta shell.  No packet-independent numerical value or sign is claimed.

## Why apparent scalar y5 dressing cancels

The selected scalar experiment is defined by pulling its source, detector and
effect through the same formal public map:

\[
 P_\phi=R_t^\dagger P_{\rm BT}R_t,
 \qquad E_\phi=R_t^\dagger E_{\rm BT}R_t.
\]

On the finite detector ideal, \(R_t^\dagger R_t=R_tR_t^\dagger=1\)
coefficientwise and the trace is cyclic.  Hence

\[
 \operatorname{tr}(P_\phi E_\phi)
 =\operatorname{tr}(P_{\rm BT}E_{\rm BT})
\]

at every formal order.  Expanding the pulled output can nevertheless produce
a nonzero apparent \(y_5\).  If

\[
 R=1+\lambda r_1+\lambda^2r_2+\cdots,
 \qquad R^\dagger R=1,
\]

then second-order isometry gives

\[
 r_2+r_2^\dagger+r_1^\dagger r_1=0.
\]

The dressing part of \(q_{10}\) is therefore

\[
 \lVert r_1^\dagger y_4\rVert^2
 +2\operatorname{Re}\langle y_4,r_2^\dagger y_4\rangle=0.
\]

The producer's exact Cayley fixture makes the cancellation visible:

\[
 y_5=(-2,1),\qquad \lVert y_5\rVert^2=5,
 \qquad 2\langle y_4,y_{6,{\rm dressing}}\rangle=-5.
\]

An independent verifier uses different exponential coefficients and obtains
the same zero.  Source and detector corrections are thus not missing physical
summands; adding them to the fixed-BT ledger would double-count one similarity.
This statement applies only to the selected shift-breaking pullback on the
finite ideal.  It does not construct the standard shift-invariant projector
of Eq. (19).

## Common-Born identity

The tree, triangle and bubble-with-bridge tensors are each fixed by total
ghost complement.  Their scalar time/momentum kernels commute with that
operation.  Hence the sum obeys

\[
 \kappa_3T_{6,T}\kappa_3=T_{6,T},
\]

and

\[
 T_{4,T}^\sharp T_{6,T}+T_{6,T}^\sharp T_{4,T}
 =T_{4,T}^*T_{6,T}+T_{6,T}^*T_{4,T}.
\]

Thus

\[
 \boxed{q_{10}^{\rm public}[F]=q_{10}^{\rm Hilbert}[F]}
\]

on the selected positive packet carrier.  Equality of the coefficient does
not determine its sign.

## Renormalization-group check

The triangle is scale independent.  The finite-time bubble forest identity is

\[
 \partial_{\log\mu}T_{6,{\rm bb},T}
 ={5\over4\pi^2}T_{4,T}.
\]

Therefore

\[
 \boxed{
 \partial_{\log\mu}q_{10}={5\over2\pi^2}q_8.}
\]

The independently certified beta function gives

\[
 \partial_{\log\mu}\lambda=-{5\lambda^3\over16\pi^2},
 \qquad
 \partial_{\log\mu}(\lambda^8q_8)
 =-{5\lambda^{10}\over2\pi^2}q_8+O(\lambda^{12}).
\]

Consequently

\[
 \boxed{
 \partial_{\log\mu}
 (\lambda^8q_8+\lambda^{10}q_{10})=O(\lambda^{12}).}
\]

This is a strong normalization check on the complete assembly.  A finite
quartic coupling redefinition changes the coordinate called \(q_{10}\) and
the coupling simultaneously.  The displayed standalone coefficient is the
declared normal-ordered MSbar coordinate, not a scheme-independent number.

## Boundary and next gate

The result establishes the selected finite-time reduced-mode probability jet

\[
 q[F]=\lambda^8q_8[F]+\lambda^{10}q_{10}[F]+O(\lambda^{12}),
\]

with \(q_8>0\), \(q_9=0\), finite exact \(q_{10}[F]\), public/Hilbert Born
agreement and order-\(\lambda^{10}\) RG invariance.  It does not establish a
packet-independent sign, finite-coupling positivity, overlap/forward sectors,
an all-time scattering operator, or a full-carrier zero-mode extension.

The next Eq. (19) test is now sharply posed: construct the order-\(\lambda^2\)
pushforward of the *standard shift-invariant* scalar characteristic projector
on this same compact packet ideal and compare its trace with the displayed
\(q_{10}\) functional.  The existing selected shift-breaking similarity is
not that theorem.  No result here transfers to metric BV--BRST gravity or is
`LORENTZIAN-CAUSAL`.

## Verification receipt

All Python and TeX commands ran sequentially under `ulimit -v 500000`.  The
repository-wide rail additionally used the sanitized
`PATH=/usr/local/bin:/usr/bin:/bin`.

| Tier | Command or rail | Result | Elapsed | Peak RSS |
|---|---|---:|---:|---:|
| 0/1 | exact producer `--write --check` | PASS, 33/33 | 0.62 s | 70,656 KiB |
| 1 | independent verifier with strict schema and different exponential dressing fixture | PASS, 54/54 | 0.07 s | 23,776 KiB |
| 1 | focused adversarial mutation suite | PASS, 53 tests | 0.15 s | 24,960 KiB |
| 2 | eight predecessor/new independent verifiers | PASS, 45/45, 28/28, 52/52, 29/29, 37/37, 45/45, 65/65 and 54/54 | 0.49 s total | 24,064 KiB maximum |
| 2 | combined affected tests | PASS, 277 tests | 2.69 s | 25,984 KiB |
| 0 | Paper V, two `pdflatex` passes | PASS | 0.52 s, 0.53 s | 51,152 KiB maximum |
| 0 | Paper VI, two `pdflatex` passes | PASS | 0.53 s each | 51,044 KiB maximum |
| 2 | Science Forge planning import/fold | PASS, 1,583 nodes; 0 invalid items; 0 malformed events | 6.00 s | 227,808 KiB |
| 3 | full `unittest discover` | **FAIL-CLOSED**, 3,443 tests: 31 failures, 9 skips | 707.358 s (11:48.39 wall) | 391,152 KiB |

The Tier-3 failures are the established historical certificate/hash drift in
older BT families plus the two `test_chain_imports` failures, including its
fifteen outside-reference findings.  Neither the new q10 module nor any of its
seven imported scientific predecessors appears in the thirty-one-failure
list.  The full rail is not called a pass and promotes no repository freeze.

The advisory Science Forge shadow rail completed in 1.95 s at 342,484 KiB.
It inventoried 1,631 certificates and 1,412 verifier files, but retained the
pre-existing Forge 0.0.2/stdlib mismatch, bridge-audit E9118 and baseline
corpus drift.  Advisory exit zero is not counted as certified success.

The rebuilt Paper V PDF has 82 pages, 763,719 bytes and SHA-256
`9e4acfb8dd8e4ac2eee103d0f8374f17866b10a21fa4f9f9853fd8c1706e5360`.
Paper VI has 70 pages, 727,279 bytes and SHA-256
`0a03fd12adaa2690a903c883cdb02820b834d2f44207d8b151cdddfbbf9a36bf`.
The final certificate SHA-256 is
`cd478d16440161adef9dcfde172359df3fdbe6abb5356043a29c77c80b718a0e`.
There are no undefined references.  All overfull-box warnings precede the new
passages and are unchanged in scope.

CLOSE-OUT: DONE -- the complete selected finite-time q10 packet functional,
dressing cancellation, common-Born identity and order-lambda10 RG cancellation
are exact in the declared normal-ordered direct-auxiliary scheme.

EVIDENCE:
`reverse_physics/certificates/REVERSE_PHYSICS_BT_FULLY_REARRANGED_Q10_SELECTED_PACKET_ASSEMBLY_V1.json`
