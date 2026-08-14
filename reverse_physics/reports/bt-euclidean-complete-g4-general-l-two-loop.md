# General-volume BT order-g4 two-loop reduction

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_GENERAL_L_TWO_LOOP_V1`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

Lifecycle:
`GENERAL_L_TWO_LOOP_FORMULA_AND_FACTOR_TADPOLE_CANCELLATION_PROVED_REMAINING_KERNEL_BOUND_OPEN`

## Result

The large positive bulk and negative rank-one sectors seen at \(L=4\) must
not be estimated separately.  For every integer \(L\geq5\), an exact affine
momentum-flow enumeration puts both sectors on one common scale.  It starts
from 96 source-conserving oriented topology flows.  Forty-eight require an
identically zero Gaussian momentum and therefore vanish.  The other 48 combine into 21
distinct integrands; five cancel exactly, leaving 16.

The important cancellation is stronger than a reduction in bookkeeping.
Define

\[
 X_L=\sum_{q\ne0,-p}
 \frac{K_3(p,q,-p-q)^2}
 {\omega_q^2\omega_{p+q}^2},
 \qquad
 Y_L=\sum_{q\ne0}
 \frac{K_4(p,-p,q,-q)}{\omega_q^2}.
\]

Here \(p=(1,0,0,0)\) is the lowest axial lattice momentum and the normalized
kernels \(K_3,K_4\) are those of the certified lattice action.  Before the
bulk/rank reorganization, the conditioning-sensitive two-loop sector contains
terms proportional to \(Y_L^2\), \(X_LY_L\), and \(X_L^2\).  After every bulk
propagator pinned to \(\pm p\) is placed on the same
\(\omega_p^{-2}\) scale as a rank-one conditioned covariance, the complete
factorized sector becomes

\[
 \frac{1}{N\omega_p^2}
 \left[(72Y_L^2-72Y_L^2)
       +(-216X_LY_L+216X_LY_L)
       +162X_L^2\right].
\]

Thus all power-sized quartic tadpoles cancel before absolute values.  The
surviving conditioning-scale contribution is the positive bubble square

\[
 \boxed{R_L=\frac{162X_L^2}{N\omega_p^2}.}
\]

Fourteen two-loop integrands remain outside this factorized sector.  The
successor seven-kernel certificate pairs them exactly under global momentum
inversion, proves a positive two-sided bound for the paired quartic vertex,
and isolates one negative \(L^2\) carrier.  Their combined hard, one-soft, and
all-soft power coefficient is the active fixed-order gate.

## Why the formula is valid for every L at least five

Every external real-cosine or rank-one endpoint contributes signed momentum
\(\pm p\).  The independent graph audit finds that every connected component
source is \(m p\) with \(|m|\leq4\).  For \(L\geq5\), modular conservation in
\(\mathbb Z_L^4\) is therefore equivalent to the integer equation \(m=0\).
Two chord momenta \(q,r\) solve the remaining flow equations, and every edge
is an affine form

\[
 a q+b r+c p,\qquad a,b,c\in\mathbb Z.
\]

The certificate records every kernel argument, propagator constraint, exact
rational coefficient, parent term, and rank-insertion count.  The \(L=4\)
lattice has additional \(m=\pm4\) resonances and remains governed by its
separate exact certificate; the factorized normalization nevertheless agrees
exactly with that ledger.

## Exact L=4 normalization check

Direct rational evaluation gives

\[
 X_4=\frac{56533}{7560},\qquad
 Y_4=\frac{98953}{3360}.
\]

Consequently

\[
 \frac{72Y_4^2}{N\omega_p^2}
  =\frac{9791696209}{160563200},\qquad
 \frac{108X_4Y_4}{N\omega_p^2}
  =\frac{5594109949}{240844800},
\]

which match the opposite bulk/rank entries in the exact \(L=4\) ledger.  The
surviving square is

\[
 R_4=\frac{3195980089}{361267200}
    \simeq8.84658249905.
\]

This check fixes the factors \(72,108,162\); it does not promote the
generic-source atlas across the special \(L=4\) resonances.

## Rigorous logarithmic bound for the surviving square

The certified cubic identity gives \(K_3=V_3/6\) and

\[
 |V_3(p,q,-p-q)|
 \leq4\omega_p\min(\omega_q,\omega_{p+q}).
\]

Therefore

\[
 0\leq X_L
 \leq\frac49\omega_p^2
       \sum_{q\ne0}\frac1{\omega_q^2}.
\]

Choose centered integer representatives \(n\) for lattice momenta.  The
chord bound \(\sin(\pi |n_j|/L)\geq2|n_j|/L\) yields
\(\omega_n\geq16|n|_2^2/L^2\).  The max-norm shell \(m\) has at most

\[
 (2m+1)^4-(2m-1)^4=64m^3+16m
\]

points.  Using \(H_R\leq1+\log R\) and
\(\sum_{m=1}^R m^{-3}\leq3/2\), with
\(R=\lfloor L/2\rfloor\), gives the explicit estimate

\[
 \sum_{q\ne0}\frac1{\omega_q^2}
 \leq N\left(\frac{11}{32}+\frac14\log R\right).
\]

Since

\[
 256\leq N\omega_p^2\leq16\pi^4,
\]

we obtain

\[
 X_L\leq
 \frac{64\pi^4}{9}
 \left(\frac{11}{32}+\frac14\log R\right)
\]

and

\[
 0\leq R_L\leq\frac{81}{128}
 \left[
 \frac{64\pi^4}{9}
 \left(\frac{11}{32}+\frac14\log R\right)
 \right]^2.
\]

Thus \(R_L=O((1+\log L)^2)\).  On the already certified tuned refinement
branch, \(g_L^2\log L\to8\pi^2/5\), so \(g_L^4R_L\) is bounded.  This closes
only the factorized conditioning sector.  It is not a bound for the remaining
14 integrands or for the full coefficient.

## What remains

The earlier barrier was the apparent cancellation of two individually huge
bulk and rank-one sums.  That cancellation is now performed exactly wherever
it factorizes through \(X_L,Y_L\).  The remaining problem is narrower.
Certificate
`REVERSE_PHYSICS_BT_EUCLIDEAN_COMPLETE_G4_SEVEN_KERNEL_REDUCTION_V1`
reduces the 14 entries to seven inversion pairs and proves that one negative
nested carrier alone has magnitude at least \(cL^2\).  Estimate the seven
kernels jointly, retaining their cancellation within common hard, one-soft,
and all-soft regions.  Lower-loop terms must then be recombined before
deciding the large-volume sign or scaling of \(M_4\).

No whole-\(M_4\) asymptotic theorem, nonperturbative annealed score estimate,
actual interacting \(H^{-1}\) moment, tightness, continuum identification,
Born rule, Krein reconstruction, or `LORENTZIAN-CAUSAL` result is established.

## Verification

```text
ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_general_l_two_loop.py --check
ulimit -v 500000; python3 reverse_physics/bt_euclidean_complete_g4_general_l_two_loop_decision.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_complete_g4_general_l_two_loop.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_complete_g4_general_l_two_loop
```

## Verification receipt

Tier 0: Python compilation of the producer, decision builder, independent
verifier, tests, and Paper 21 claim-map scripts passed in 0.05 s (21,876 KB
maximum RSS).  Every changed JSON and schema parsed with `jq`, and the scoped
diff passed `git diff --check`.  Two bounded LaTeX passes completed in 0.73 s
and 0.74 s (54,108 KB maximum RSS).

Tier 1: the deterministic affine-flow producer, decision builder, independent
verifier, and 11 unit/adversarial-mutation tests passed in 0.10 s, 0.03 s,
0.18 s, and 0.29 s (22,116 KB, 20,472 KB, 30,488 KB, and 31,112 KB maximum
RSS).  Mutations cover an integrand coefficient, affine flow, cancellation
count, factorized formula, Green bound, dependency tags, the remaining-kernel
boundary, the interacting \(H^{-1}\) boundary, and schema closure.  The Paper
21 claim-map generator check and independent verifier each passed in 0.07 s
(31,220 KB and 27,872 KB maximum RSS).

Tier 2: the independent verifier reconstructs the complete affine atlas from
hard-coded action terms and its own labeled-pairing, component, spanning-tree,
and exact rational coefficient logic.  It reproduces all 21 precombination
integrands, five zero sums, 16 survivors, and the two coefficient-81 bubble
squares.  A separate exact \(L=4\) dispersion calculation reproduces
\(X_4,Y_4\), both canceled factors, and \(R_4\).  The append-only planning
import accepted 1,619 nodes with no invalid item or malformed event in 8.48 s
(222,612 KB maximum RSS under `GOMEMLIMIT=300MiB`).

Tier 3 was not run: Paper 21 remains a `WORKING_DRAFT`, this bounded
`LOCAL-ALGEBRAIC`/`EUCLIDEAN-SPECTRAL` certificate does not freeze or release
the programme, no shared core algebra changed, and no quantum lifecycle,
continuum theorem, or paper-theorem lifecycle was promoted.
