# Exact BT order-g4 decision on the 4^4 lattice

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_L4_DECISION_V1`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

Lifecycle:
`EXACT_L4_COMPLETE_G4_NEGATIVE_NONZERO_PROVED_ASYMPTOTIC_SCALING_OPEN`

## Result

The near-cancellation seen in the streaming preflight is not an exact Ward
identity.  For the \(4^4\) lattice, with the lowest real axial cosine removed
from the free background Gaussian, the complete connected coefficient is

\[
 \boxed{
 M_4(4)=-\frac{338835474713437}{204838502400000}
       \simeq -1.6541591094616253.}
\]

It is strictly negative and nonzero.  One exact finite-volume counterexample
therefore refutes the proposed identity \(M_4(L)=0\) for every volume.  It does
not determine the sign or scaling as \(L\to\infty\).

The coefficient evaluated is the complete connected expression

\[
 M_4=\mathbb E_0[B^2+2AC-2ABW_1]
     +\operatorname{Cov}_0\!\left(A^2,\frac12W_1^2-W_2\right),
\]

including the real-cosine rank-one correction in every Gaussian covariance.
No square-root-density term was bounded separately.

## What cancels and what remains

The exact rank/loop ledger is

| rank insertions | loop rank | contribution |
|---:|---:|---:|
| 0 | 0 | \(3/512\) |
| 0 | 1 | \(-1991996981/15173222400\) |
| 0 | 2 | \(4402010753794613/204838502400000\simeq21.4902\) |
| 1 | 0 | \(1/64\) |
| 1 | 1 | \(-456190061/18966528000\) |
| 1 | 2 | \(-33779866849/1445068800\simeq-23.3760\) |
| 2 | 0 | \(-29/512\) |
| 2 | 1 | \(183793/430080\) |
| 3 | 0 | \(-1/192\) |

The dominant translation-invariant two-loop sector is positive, while the
dominant single-rank two-loop sector is larger and negative at \(L=4\).  The
finite remainder is the sum of all nine displayed sectors.  This identifies
the next analytic object: the bulk and single-rank two-loop kernels must be
combined before any large-volume estimate.

## Correction to the preceding pairing table

The labeled table in
`REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_CONNECTED_NORMALIZATION_V1`
classifies translation-invariant \(C_0\) contractions.  A row marked
`VANISHES_BY_COMPONENT_MOMENTUM` there is a bulk zero, not necessarily a zero
of the conditioned expectation: replacing a propagator by the rank-one part
of

\[
 C=C_0-v\,h\otimes h
\]

adds fixed \(\pm p\) endpoints and can restore component momentum balance.

The predecessor certificate now records this scope explicitly.  A separate
exact audit exhausts every bulk/rank choice and every signed endpoint.  If a
component source is \(s_jp\), it is conserved for some integer \(L\geq4\) iff
all \(s_j\) vanish or the gcd of their nonzero absolute values has a divisor
at least four.  The viable conditioned loop ranks are still exactly
\(0,1,2\); no viable rank-three graph exists.  Thus the maximum-two-loop
conclusion survives, while the interpretation of the bulk zero labels is
narrowed.

## Primary exact evaluation

Use

\[
 \phi_x=N^{-1/2}\sum_k z_k e^{ikx},\qquad
 \mathbb E[z_kz_\ell]=\frac{\delta_{k,-\ell}}{\omega_k^2}
\]

before conditioning, with the zero mode omitted.  At \(L=4\), every phase is in
\(\{1,i,-1,-i\}\), every dispersion is an even integer, and
\(v=1/512\).  The homogeneous vertices are obtained directly from
\(S_1=ab/2\), \(S_2=ac/6+b^2/8\), and
\(S_3=ad/24+bc/12\).

Labeled Wick pairings are grouped by multigraph.  Each covariance edge is
expanded into its \(C_0\) and rank-one pieces.  A spanning forest solves the
vertex constraints; at most two chord momenta remain, so the largest exact
sum contains \(256^2\) states.  A common propagator denominator
\(2822400\) keeps the accumulation integral until the final rational
reduction.  The exhaustive producer uses bounded memory and takes about six
minutes; it is an affected-chain calculation, not the fast per-edit rail.

## Independent modular verification

The independent C++ verifier reimplements the calculation: it enumerates
labeled pairings, constructs the multigraphs, expands the conditioned
covariance, solves the \(\mathbb Z_4^4\) flows, and evaluates every term modulo
four distinct 61-bit primes.  It does not import the Python topology ledger.

Residue agreement alone would be probabilistic.  The verifier therefore also
rederives a common rational denominator and an absolute bound on every Wick
sum.  After clearing the claimed denominator, any discrepancy has absolute
value below a certified 227-bit integer.  The product of the four primes has
244 bits and exceeds twice that bound.  Agreement modulo all four primes
therefore forces the cleared integer discrepancy to be exactly zero.

Two normalization rails also agree.  The independent cubic formula gives

\[
 \mathbb E_0[A^2]=\frac{54853}{840}
                 \simeq65.3011904762,
\]

and the quartic contraction gives

\[
 \mathbb E_0[B^2]
 =\frac{57763797055217}{22404211200000}
 \simeq2.57825622779.
\]

The earlier streaming estimate \(M_4=-0.5252\pm1.7671\) differs from the exact
answer by less than one reported standard error.  That numerical agreement
is supporting only; exactness comes from the two arithmetic rails.

## Consequence and next calculation

An all-volume \(M_4=0\) identity is no longer a viable route.  The successor
certificate
`REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_GENERAL_L_TWO_LOOP_V1`
now supplies the general-\(L\) common-kernel formula for every \(L\geq5\).
After fixed-\(p\) bulk propagators and rank-one covariances are put on one
scale, all factorized power-sized tadpoles cancel and their remainder has an
explicit logarithm-squared bound.  Fourteen unfactorized kernels still require
a joint hard, one-soft, and all-soft estimate before the large-volume behavior
can be decided.

No large-volume sign or scaling theorem, whole-lattice power-survival result,
nonperturbative annealed score bound, interacting \(H^{-1}\) moment, tightness,
continuum identification, Born rule, Krein reconstruction, or
`LORENTZIAN-CAUSAL` statement is established.

## Verification

```text
ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_l4_decision.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_complete_g4_l4_decision.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_complete_g4_l4_decision
g++ -std=c++17 -O3 -Wall -Wextra -Werror reverse_physics/bt_euclidean_complete_g4_l4_modular_verify.cpp -o /tmp/bt-g4-l4-modverify
ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_l4_exact.py --check
```

## Verification receipt

Tier 0: Python compilation of the changed generators, verifiers, tests, and
paper scripts passed in 0.06 s (21,372 KB maximum RSS); every changed JSON
and schema parsed with `jq`.  The strict C++17 modular build passed in 2.32 s
(204,412 KB maximum RSS), and two bounded LaTeX passes completed in 0.74 s
and 0.73 s (53,880 KB maximum RSS).

Tier 1: the fast decision generator passed in 0.12 s (22,388 KB maximum RSS).
The independent verifier recompiled and ran the modular rail and passed in
5.09 s (204,592 KB maximum RSS).  All 10 unit and adversarial-mutation tests
passed in 5.37 s (204,188 KB maximum RSS).  A standalone run of the modular
executable passed in 1.31 s (29,908 KB maximum RSS).  The Paper 21 claim-map
generator check and independent verifier each passed in 0.07 s (31,140 KB
and 27,832 KB maximum RSS).

Tier 2: because the exact data are the mathematical input to the decision,
the bounded-memory primary producer was run exhaustively under the 500 MB
virtual-memory cap.  It passed in 343.71 s with 135,916 KB maximum RSS and
reproduced data SHA-256
`b7d7ce4abbfb8f3b6746df05085cecc2990df302b040b8790506e43f90a9db37`.
The separately implemented four-prime evaluator then supplied the independent
verification rail.  The affected predecessor generator, verifier, and 12
unit/mutation tests passed in 1.32 s, 1.10 s, and 2.32 s (22,072 KB, 30,424 KB,
and 31,148 KB maximum RSS).

The append-only planning import accepted 1,618 nodes with no invalid item or
malformed event in 7.80 s (248,552 KB maximum RSS under
`GOMEMLIMIT=300MiB`).  Tier 3 was not run because this is a finite-volume
`LOCAL-ALGEBRAIC`/`EUCLIDEAN-SPECTRAL` coefficient decision, not a freeze,
release, shared-core change, continuum theorem, or quantum lifecycle
promotion.
