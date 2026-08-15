# BT tuned-branch remainder compensation

## Result

The completed fourth-order calculation now gives a precise answer about the
method, although not yet about the interacting continuum theory. On the
fixed-physical-volume tuned refinement branch, the exact zero-fiber-score
moment cannot be approximated uniformly by its complete truncation through
order \(g^4\).

Let

\[
 F_L(g)=\mathbb E_{\nu_{L,g}}[s_{L,g}(\eta)^2]\geq0
\]

be the annealed squared zero-fiber score. At fixed volume its certified
expansion starts as

\[
 F_L(g)=g^2M_2(L)+g^3M_3(L)+g^4M_4(L)+\cdots.
\]

This report uses only `LOCAL-ALGEBRAIC` and `EUCLIDEAN-SPECTRAL` inputs.

## The cubic coefficient vanishes exactly

Under background inversion, the first score coefficient
\(A=D_hS_1\) is even, the next coefficient \(B=D_hS_2\) is odd, and the
first background-density coefficient \(W_1\) is odd. Therefore

\[
 M_3=\mathbb E_0[2AB-A^2W_1]=0.
\]

This is a parity identity, not a numerical cancellation.

## The tuned quartic truncation becomes negative without bound

The leading coefficient is

\[
 M_2=N\omega_p^2 C_L,
 \qquad C_L=\frac{5}{16\pi^2}\log L+O(1).
\]

On the certified tuned branch,
\(g_L^2\log L\to8\pi^2/5\). Since
\(N=L^4\) and \(\omega_p=4\sin^2(\pi/L)\), this gives
\(g_L^2M_2=O(1)\).

The complete quartic theorem gives

\[
 \frac{M_4}{N\omega_p}\longrightarrow c_*=c_4+c_7.
\]

The exact outward bounds are

\[
 c_4<-\frac{1613}{100000},\qquad
 c_7<\frac{8051597}{500000000},
\]

so

\[
 c_*<-\frac{13403}{500000000}<0.
\]

Meanwhile \(g_L^4N\omega_p\) grows like
\(L^2/\log^2L\). Hence the complete quartic truncation

\[
 T_L=g_L^2M_2+g_L^4M_4
\]

tends to minus infinity.

## Positivity forces a large omitted sector

Define the exact complement at the tuned coupling by

\[
 Q_L=F_L(g_L)-g_L^2M_2(L)-g_L^4M_4(L).
\]

This definition does not assume convergence of an infinite perturbation
series. Since \(F_L(g_L)\geq0\),

\[
 Q_L\geq-g_L^2M_2-g_L^4M_4,
\]

and therefore

\[
 Q_L\to+\infty,
 \qquad
 \liminf_{L\to\infty}
 \frac{Q_L}{g_L^4N\omega_p}
 \geq-c_*>
 \frac{13403}{500000000}.
\]

So the missing all-order sector is not a small correction. It must compensate
the negative quartic term on the same leading power scale. A uniformly bounded
remainder, or a remainder little-o of \(g_L^4N\omega_p\), is impossible.

## What this means

This is a rigorous barrier for the proof strategy, not a proof that the exact
score diverges. Higher orders may cancel the negative quartic term and leave
the full positive moment bounded. In fact, such a cancellation is now
mathematically mandatory if the desired continuum estimate is true.

The next calculation must therefore keep the whole positive score square
together. A block-spin, conditional Ward, or other nonperturbative estimate
must retain the background Gibbs weight and perform the forced resummation
before taking absolute values. The target remains

\[
 F_L(g_L)\leq C N\omega_p^2.
\]

The certificate does not establish this estimate, an interacting
\(H^{-1}\) bound, a continuum measure, a Born rule, a Krein reconstruction, or
any Lorentzian causal statement.

## Verification

```text
ulimit -v 500000; python3 reverse_physics/bt_euclidean_tuned_remainder_compensation.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_tuned_remainder_compensation.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_tuned_remainder_compensation
```

Tier 0 checks parse the producer, verifier, test, schema, and generated
certificate and inspect the scoped diff. Tier 1 runs the commands above,
including mutations of the gap, parity identity, lifecycle boundary, and
dependency tags. The affected Paper 21 claim-map and PDF checks form the
direct-consumer rail. Tier 3 is unnecessary because this result obstructs a
method and does not promote a continuum or release theorem.

On 2026-08-15 the producer check passed in 0.03 s at 20,472 KB peak, the
independent verifier in 0.08 s at 29,192 KB, and all seven focused and mutation
tests in 0.10 s at 30,812 KB. The RG and complete-\(M_4\) predecessor verifiers
passed in 0.08 s and 0.20 s. Two bounded `pdflatex` passes each took about
0.72 s at 53,712 KB and produced a 57-page PDF. The Paper 21 generator check
and independent authority/hash/boundary verifier passed. Tier 2 did not rebuild
unchanged coefficient producers because their content-addressed certificates
were imported by hash. Tier 3 was not run under the method-obstruction
criterion above.

The advisory Science Forge shadow rail was also invoked. It did not complete:
the external `cbp` helper aborted under the 500 MB cap after printing only the
rail header. This advisory invocation is recorded as incomplete and supplies
no verification evidence; the independent certificate and paper rails above
are the claim-bearing checks.
