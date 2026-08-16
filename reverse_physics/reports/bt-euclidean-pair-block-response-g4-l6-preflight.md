# BT pair-block fourth-order response: calibrated \(L=6\) preflight

**Dependency boundary:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`,
`REDUCED-MODE`

**Lifecycle:** `CLASSIFIED` — numerical supporting evidence only

**Certificate:**
`REVERSE_PHYSICS_BT_EUCLIDEAN_PAIR_BLOCK_RESPONSE_G4_L6_PREFLIGHT_V1`

## Result

The bounded-memory plane-wave evaluator observes

\[
 T_{4,6}=0.00082163614113613>0
\]

in binary64 arithmetic. The six terms in the exact topology reduction are

\[
\begin{array}{c|r}
\text{term}&\text{binary64 value}\\ \hline
F_{4,0}&+0.0005033754906226740\\
F_{4,2}&+0.002164969456075357\\
F_{4,4}&-0.0010564679600843152\\
-F_{3,3}\Gamma_3&+0.000011171944528325162\\
-F_{2,2}\Gamma_4&-0.0016602526411414497\\
+F_{2,2}\Gamma_3^2&+0.0008588398511355388
\end{array}
\]

This is not yet an exact or rigorous sign theorem. It determines what the
exact rail should expect and shows that the result is not a cancellation in
the last few floating-point bits.

## Calibration

Before evaluating fourth order, the same local response-vertex code computes

\[
 F_{2,0}+\frac1{2N}\sum_kF_{2,2}(k,-k)G(k)
 =0.00009500212499864366.
\]

The certified exact value is

\[
 {956585197\over10069092633600}
 =0.00009500212499862486\ldots,
\]

so the absolute binary64 discrepancy is \(1.88\times10^{-17}\). The same
fast compiled rail also reproduces the two exact zero-background values

\[
 F_{2,0}=-{15643\over1517824},\qquad
 F_{4,0}={41416831\over82278203392}.
\]

This calibration checks the conditional two-variable Gaussian, the
quadratic response derivative, the pair-orientation weights, the free
conditional-center filter, the Fourier normalization, and the complete
one-loop momentum sum. It does not independently prove the fourth-order
terms.

## Cancellation scale

The sum of absolute term magnitudes is approximately

\[
 0.00625507684358836,
\]

and the observed result is about 13.1 percent of that value. Thus ordinary
roundoff at binary64 scale is not plausibly responsible for the observed
sign. This remains an error heuristic, not an outward-rounded bound.

At \(\lambda=2/5\), the first two nonzero perturbative contributions would
both be positive on this fixture:

\[
 b_{2,6}\lambda^2>0,\qquad T_{4,6}\lambda^4>0.
\]

This statement is only about the displayed truncation. No conclusion about
the all-order response at \(\lambda=2/5\) follows.

## OOM resolution

The exhaustive run streamed all \(1296^2\) momentum pairs and used only
3172 KiB peak resident memory under the 500000 KiB virtual-memory ceiling.
It took 2330.4 seconds with eight OpenMP threads.

Two earlier coordinate-tensor attempts reached the memory ceiling because a
dense degree-four response tensor over 66 local coordinates was being
materialized. The six-topology Fourier architecture eliminates that object.
The previous OOM was therefore a representation failure, not a physics
obstruction.

## Exact next gate

The coefficient cannot be promoted from `CLASSIFIED` on this evidence. The
same streaming computation must be repeated on an independent rigorous rail:

1. finite-field arithmetic over primes admitting sixth roots of unity,
   followed by rational reconstruction and a conjugate-root check; or
2. outward-rounded complex-ball arithmetic producing a final interval whose
   lower endpoint is strictly positive.

That rail must reproduce the exact one-loop fixture and record all six
fourth-order terms separately. Only then can the finite-volume coefficient
be promoted and the large-volume hard/hard, hard/soft, and soft/soft analysis
begin.

Nothing here proves a volume-uniform remainder, fixed-coupling response,
heat-bath gap, Witten estimate, interacting \(H^{-1}\) bound, continuum
measure, Born rule, Krein reconstruction, new physical dimension, or
Lorentzian-causal result.
