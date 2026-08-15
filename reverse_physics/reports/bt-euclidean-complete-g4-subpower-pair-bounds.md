# BT complete-g4 exact subpower bounds for pairs 1, 2, and 5

Certificate:
REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_SUBPOWER_PAIR_BOUNDS_V1

Dependency tags: LOCAL-ALGEBRAIC, EUCLIDEAN-SPECTRAL

Lifecycle:
THREE_SUBPOWER_PAIR_BOUNDS_PROVED_FOUR_PAIR_POWER_GATE_OPEN

## Result

Three of the seven inversion-paired generic-volume two-loop kernels are now
removed from the power-scale problem. For every integer \(L\ge5\), pairs 1,
2, and 5 satisfy explicit \(O(\log^2L)\) bounds. Since
\(N\omega_p\asymp L^2\), each is \(o(N\omega_p)\), and therefore none can
cancel a nonzero coefficient at the power scale.

The unresolved leading-power calculation has consequently shrunk from all
seven pairs to pairs 3, 4, 6, and 7. This is a reduction of the open problem,
not a decision of the combined coefficient or of complete \(M_4\).

## Vertex estimates

For any conserved cubic momentum triple, the exact lattice vertex obeys

\[
 |K_3(a,b,c)|\le \frac23\omega_a\omega_b,
\]

with either two legs selectable. For a conserved quartic tuple, the directed-
edge partition definition gives four \(1|3\) and three \(2|2\) partitions.
Each block product is at most
\(64\prod_i\sqrt{\omega_{k_i}}\). Dividing the sum of seven products by
\(4!\) gives the all-leg estimate

\[
 |K_4(k_1,k_2,k_3,k_4)|
 \le \frac{56}{3}\prod_{i=1}^4\sqrt{\omega_{k_i}}.
\]

These constants are recomputed with exact rational arithmetic by the
independent verifier.

## Pairs 1 and 2

Write

\[
 G_2(L)=\sum_{k\ne0}\omega_k^{-2},\qquad
 G_2(L)\le N A_L,\qquad
 A_L=\frac{11}{32}+\frac14\log R,\quad R=\lfloor L/2\rfloor.
\]

For pair 1, selecting the two soft factors in each of the four cubic vertices
cancels every \(q\) and \(q+r\) propagator. What remains is

\[
 |I_1(L)|\le
 64\frac{\omega_p^2}{N}G_2(L)^2.
\]

For pair 2, the corresponding selection leaves one Green-square sum and the
shifted convolution

\[
 \sum_q\frac1{\omega_q\omega_{q+p}}\le G_2(L),
\]

where the last step is Cauchy--Schwarz and translation invariance. Hence

\[
 |I_2(L)|\le
 64\frac{\omega_p^2}{N}G_2(L)^2.
\]

Using \(N\omega_p^2\le16\pi^4\) yields, for \(j=1,2\),

\[
 \boxed{|I_j(L)|\le1024\pi^4 A_L^2.}
\]

## Pair 5 and the two-centre convolution

The cubic allocations use \(\omega_p\omega_q\) and
\(\omega_p\omega_r\). The all-leg quartic estimate then factorizes the
remainder into two copies of

\[
 J_L=\sum_{q\ne0,-p}
 \frac1{\sqrt{\omega_q}\,\omega_{q+p}^{3/2}}.
\]

Let \(\rho_2\) and \(\rho_\infty\) be the centered Euclidean and max-norm
distances on the momentum torus. Since
\(\omega_k\ge16\rho_2(k)^2/L^2\), it remains to bound a dimensionless
two-centre sum. If

\[
 m=\min\{\rho_\infty(q),\rho_\infty(q+p)\}\ge1,
\]

the summand is at most \(m^{-4}\). The union of the two max-norm shells has
at most

\[
 2\{(2m+1)^4-(2m-1)^4\}=128m^3+32m
\]

sites. Therefore \(H_R\le1+\log R\) and
\(\sum_{m\ge1}m^{-3}<3/2\) give

\[
 \sum_{q\ne0,-p}
 \frac1{\rho_2(q)\rho_2(q+p)^3}
 \le176+128\log R,
\]

and consequently

\[
 J_L\le N B_L,\qquad
 B_L=\frac{11}{16}+\frac12\log R.
\]

The exact coefficient is
\(108(2/3)^2(56/3)=896\). Thus

\[
 |I_5(L)|\le896\frac{\omega_p^2}{N}J_L^2
 \le\boxed{14336\pi^4B_L^2}.
\]

## Consequence and next gate

All three terms are \(O(\log^2L)\), while \(N\omega_p\asymp L^2\).
On the certified tuned branch, \(g_L^4=O(\log^{-2}L)\), so each of these
three contributions is uniformly bounded. They have zero contribution to a
putative \(N\omega_p\) coefficient.

Pairs 3 and 6 are parity-sensitive and remain unbounded analytically. Pair 4
has the certified negative \(L^2\)-magnitude lower bound; pair 7 is positive
and power-capable. The next calculation is to symmetrize pairs 3 and 6 under
\(p\)-reflection before taking absolute values, then determine the common
power coefficient of pairs 3, 4, 6, and 7.

## Claim boundary

This certificate does not determine pairs 3 or 6, the combined four-pair
coefficient, the sign or scaling of complete \(M_4\), the nonperturbative
annealed score, or the actual interacting \(H^{-1}\) moment. It establishes
no continuum limit, Born rule, Krein reconstruction, or
LORENTZIAN-CAUSAL statement.

## Verification

    ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_subpower_pair_bounds.py --check
    ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_subpower_pair_bounds_decision.py --check
    ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_complete_g4_subpower_pair_bounds.py
    ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_complete_g4_subpower_pair_bounds

## Verification receipt

Tier 0: all six changed Python sources compiled in 0.05 s (21,876 KB maximum
RSS). Every changed JSON and schema parsed successfully, two bounded Paper 21
LaTeX passes completed in 0.83 s and 0.76 s (53,872 KB and 53,444 KB), and the
56-page PDF was regenerated. The scoped git diff check and exact staged diff
are checked immediately before commit.

Tier 1: the deterministic data producer and certificate builder checks passed
in 0.03 s each (20,700 KB and 20,268 KB). The independent verifier passed in
0.09 s (29,748 KB). Twelve unit and adversarial-mutation tests passed in
0.13 s (30,528 KB), covering coefficients, a representative momentum flow,
raw and shifted-convolution constants, the subpower set, pair-3 and combined-
power promotions, the actual \(H^{-1}\) boundary, dependency tags, and schema
closure. The generated Paper 21 claim-map check and independent verifier
passed in 0.06 s and 0.08 s (31,480 KB and 28,248 KB).

Tier 2: the independent verifier reloads the upstream seven-pair certificate,
checks its hashes, reconstructs all three momentum-exponent ledgers from the
stored kernel representatives, recomputes the rational vertex constants,
rederives the two-centre shell polynomial and convolution constants, checks the
normalization bounds, and enforces every open claim boundary. The append-only
sequence-18 planning event imported with 1,621 nodes, zero invalid items, and
zero malformed events in 7.00 s (246,852 KB under GOMEMLIMIT=300MiB).
Unchanged predecessor certificates were reused by content hash; no shared
operator, schema interface, or transitive classical/quantum certificate input
changed.

Tier 3 was not run: this is a bounded
LOCAL-ALGEBRAIC/EUCLIDEAN-SPECTRAL checkpoint, Paper 21 remains a
WORKING_DRAFT, the four-pair coefficient and complete-\(M_4\) decisions remain
open, and no freeze, release, shared-core algebra, quantum lifecycle,
continuum, Born, Krein, or Lorentzian claim was promoted.
