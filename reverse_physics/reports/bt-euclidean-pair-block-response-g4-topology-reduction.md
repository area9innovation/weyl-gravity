# BT pair-block response at fourth order: six-topology reduction

**Dependency boundary:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`,
`REDUCED-MODE`

**Lifecycle:** `CLASSIFIED`

**Certificate:**
`REVERSE_PHYSICS_BT_EUCLIDEAN_PAIR_BLOCK_RESPONSE_G4_TOPOLOGY_REDUCTION_V1`

## Result

The complete normalized order-\(\lambda^4\) pair response does not require
evaluating all seven cumulant rows or all 27 connected Wick adjacency types.
Momentum conservation and removal of the bilaplacian zero mode reduce the
calculation to exactly six topology types:

- three contractions internal to \(Dm_4\), of loop ranks zero, one, and two;
- one two-loop \(Dm_3\)-\(S_1\) contraction;
- one two-loop \(Dm_2\)-\(S_2\) contraction;
- one two-loop \(Dm_2\)-\(S_1\)-\(S_1\) contraction.

Every term involving \(Dm_1\) is exactly zero. This is stronger than a
variance or power-counting improvement: those terms need never be generated.

The exact coefficient is still open. What is now fixed is the complete and
minimal Fourier object that must be evaluated.

## 1. Starting ledger

The predecessor certificate proved

\[
\begin{aligned}
 T_4={}&\mathbb E_0[Dm_4]-\kappa_0(Dm_3,S_1)
 -\kappa_0(Dm_2,S_2)+\frac12\kappa_0(Dm_2,S_1,S_1)\\
 &-\kappa_0(Dm_1,S_3)+\kappa_0(Dm_1,S_1,S_2)
 -\frac16\kappa_0(Dm_1,S_1,S_1,S_1).
\end{aligned}
\]

Here \(Dm_i\) has background degree at most \(i\), while \(S_j\) is
homogeneous of degree \(j+2\). Joint cumulants retain only Wick multigraphs
connected at the level of these composite vertices.

Exhaustive labeled pairing gives:

| row | raw pairings | connected pairings | connected adjacency types |
|---|---:|---:|---:|
| \(Dm_4\) | 5 | 5 | 3 |
| \(Dm_3,S_1\) | 18 | 18 | 3 |
| \(Dm_2,S_2\) | 18 | 12 | 1 |
| \(Dm_2,S_1,S_1\) | 120 | 90 | 4 |
| \(Dm_1,S_3\) | 15 | 15 | 1 |
| \(Dm_1,S_1,S_2\) | 105 | 96 | 3 |
| \(Dm_1,S_1,S_1,S_1\) | 945 | 810 | 12 |
| **total** | **1226** | **1046** | **27** |

The producer constructs every labeled pairing rather than inserting these
counts as expected answers. The independent verifier uses a separate
pairing generator and cut-based bridge test.

## 2. Bridge-zero-mode theorem

Consider a connected vacuum Wick multigraph with one local response vertex
and any number of translation-summed action vertices. Suppose an edge is a
non-self bridge. Removing it divides the graph into two components. Sum the
momentum-conservation equations over either component. Every internal edge
cancels with its opposite orientation, leaving only the bridge momentum.
Consequently that momentum is zero.

The free periodic bilaplacian covariance is

\[
 G_L(k)=\begin{cases}
 \omega(k)^{-2},&k\ne0,\\
 0,&k=0.
 \end{cases}
\]

The bridge propagator therefore vanishes. Every topology containing such a
bridge is exactly zero.

Self-loops are not bridges. An edge belonging to a parallel-edge family is
also not a bridge. Marking a graph momentum-admissible means only that this
particular zero-mode theorem does not kill it; it is not an assertion that
its vertex factor is nonzero.

## 3. Exact elimination

Of the 27 connected adjacency types:

- 21 contain a non-self bridge and vanish;
- 6 are momentum-admissible;
- the surviving labeled-pairing multiplicities are
  \(1,1,3,6,12,36\).

The consequences by row are:

- all three \(Dm_4\) self-contraction types survive;
- only the degree-three, triple-cross-edge \(Dm_3,S_1\) type survives;
- the unique \(Dm_2,S_2\) type survives;
- only one of four \(Dm_2,S_1,S_1\) types survives;
- all sixteen adjacency types across the three \(Dm_1\) rows vanish.

The disappearance of \(Dm_1\) is the higher-order form of the zero-mode
mechanism behind the one-loop marginal cancellation. A degree-one local
response insertion has only one incident edge; that edge is necessarily a
bridge.

## 4. Six-term Fourier formula

Let \(N=L^4\), and use

\[
 \phi_x=N^{-1/2}\sum_k e^{ikx}\phi_k.
\]

Let

\[
 \Gamma_n=D^nS_{n-2}\big|_{\phi=0}
\]

be the symmetric action vertex, and let

\[
 F_{i,r}=D_{\rm background}^r(Dm_i)\big|_{0}
\]

be the symmetric degree-\(r\) response vertex. Polynomial Taylor
coefficients are therefore \(\Gamma_n/n!\) and \(F_{i,r}/r!\).

The complete coefficient is

\[
\begin{aligned}
T_4={}&F_{4,0}
+\frac1{2N}\sum_kF_{4,2}(k,-k)G(k)\\
&+\frac1{8N^2}\sum_{k,l}
 F_{4,4}(k,-k,l,-l)G(k)G(l)\\
&-\frac1{6N^2}\sum_{k,l}
 F_{3,3}(k,l,-k-l)\Gamma_3(-k,-l,k+l)
 G(k)G(l)G(k+l)\\
&-\frac1{4N^2}\sum_{k,l}
 F_{2,2}(k,-k)\Gamma_4(-k,k,l,-l)G(k)^2G(l)\\
&+\frac1{4N^2}\sum_{k,l}
 F_{2,2}(k,-k)
 \Gamma_3(-k,l,k-l)\Gamma_3(k,-l,l-k)
 G(k)^2G(l)G(k-l).
\end{aligned}
\]

The prefactors include both the labeled Wick multiplicities and the vertex
factorials. For example, the final live topology has multiplicity 36;
division by \(2!(3!)^2\) gives \(1/2\), and the outer cumulant coefficient
\(1/2\) gives the displayed \(1/4\).

All sums may include zero momenta because any summand containing \(G(0)\) is
defined to be zero.

## 5. Why the exact fixture is \(L=6\)

The response coefficient is extracted from the second spatial moment of a
range-two local kernel. On an \(L=4\) torus, unwrapped quadratic coordinates
alias across the periodic boundary. The earlier suggestion to begin with
coordinate-space \(L=4\) is therefore superseded.

The exact target is the already certified \(6^4\) fixture:

- the range-two response support is nondegenerate;
- every \(\omega(k)\) is rational;
- sixth-root phases lie in \(\mathbb Q(\sqrt{-3})\);
- conjugation makes the final answer rational.

The evaluator should stream the \((k,l)\) sums. An \(N\)-by-\(N\) covariance
matrix or a degree-four coordinate tensor is unnecessary and violates the
memory architecture established by this reduction.

## 6. Failed preflights and their meaning

A calibrated Gaussian preflight was attempted only as an orientation tool.
With 400 samples its global reweighting variance was much larger than the
certified one-loop signal \(956585197/10069092633600\). It therefore supplied
no usable fourth-order evidence.

Two attempts to materialize the degree-four local response tensor in a
66-coordinate basis reached the enforced 500000 KiB ceiling. They stopped
without a result. This is a method obstruction, not a physics obstruction:
the six-term momentum formula avoids that tensor entirely.

## 7. Status and next calculation

Established:

- exhaustive enumeration of all raw and connected pairings;
- the bridge-zero-mode theorem;
- exact elimination of 21 of 27 connected adjacency types;
- exact vanishing of every \(Dm_1\) marginal row;
- the complete six-term, maximum-two-loop Fourier formula;
- selection of \(L=6\) as the first nondegenerate exact fixture.

Still open:

- the five local response vertices appearing in the formula;
- the rational \(L=6\) coefficient and its sign;
- its large-volume hard/soft asymptotics;
- a uniform remainder or fixed-coupling pair-response theorem;
- response-to-Witten transfer and the actual interacting \(H^{-1}\) bound.

The next implementation should evaluate the five local response vertices on
plane-wave backgrounds using exact two-variable conditional Gaussian
arithmetic, then stream the six sums in \(\mathbb Q(\sqrt{-3})\). A separate
modular or position-space contraction must verify the result before any
coefficient lifecycle promotion.

Nothing here establishes a continuum measure, Born rule, Krein
reconstruction, new physical dimension, or Lorentzian-causal statement.
