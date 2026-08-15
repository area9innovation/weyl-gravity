# Exact full-phase BT \(M_4\) decision at \(L=4\)

**Certificate:** `REVERSE_PHYSICS_BT_EUCLIDEAN_FULL_PHASE_G4_L4_DECISION_V1`

**Dependency tags:** `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

## Result

The complete full-cosine-sine order-\(g^4\) score coefficient does not cancel
at finite volume.  On the \(4^4\) torus, with the background Fourier modes
\(0,+p,-p\) removed,

\[
 \boxed{
 M_4^{\mathrm{full}}(4)
 =-\frac{2569186115493259}{716934758400000}
 \approx-3.5835703115. }
\]

The result is exact.  It refutes an identity
\(M_4^{\mathrm{full}}(L)=0\) at every volume.  It does not determine the
large-volume scaling or the sign of the resummed interacting observable.

## Two-dimensional fiber ledger

Let \(\zeta=t_c-it_s\) for the two free fiber coordinates, each with variance
\(v\).  Rotational invariance gives

\[
 \mathbb E\zeta^2=0,qquad
 \mathbb E|\zeta|^2=2v,qquad
 \mathbb E|\zeta|^4=8v^2.
\]

The order-\(g\) effective interaction simplifies to \(W_1=U_{30}\).  The
balanced \(U_{32}\) term would require a zero background leg, which is
removed, while its same-sign components average to zero.  Modulo constants,

\[
 W_2=U_{40}+vF_{42}-\frac v2|A|^2
 -\frac12\mathbb E_{\rm fiber}Q^2,
\]

where \(F_{42}\) has one \(+p,-p\) fiber pair and \(Q\) is the same-sign
two-fiber-leg cubic vertex.  Substitution into the complete vector formula
leaves eight connected families:

\[
\begin{aligned}
M_4^{\mathrm{full}}={}&
 \mathbb E[|B|^2+2A\cdot C-2U_{30}A\cdot B]\\
&+\operatorname{Cov}\!\left(
 |A|^2,
 \frac12U_{30}^2-U_{40}-vF_{42}
 +\frac v2|A|^2+\frac12\mathbb E_{\rm fiber}Q^2
 \right).
\end{aligned}
\]

At \(L=4\), the last \(Q^2\) covariance family vanishes exactly.  The other
seven terms are nonzero.

## Cancellation anatomy

The isolated cubic-current/quartic-score square is positive:

\[
 \mathbb E|B|^2
 =\frac{55147376933567}{11202105600000}
 \approx4.92295.
\]

It is not merely reduced but overcancelled by the signed density,
normalization, and higher-score terms.  The largest pieces are approximately

\[
 +40.7631,qquad -56.3988,qquad +17.8448,
\]

with the remaining score terms completing the exact negative remainder.  In
ordinary language, the noisy cubic blocks are real, but the Gibbs weighting
and the other perturbative orders coordinate them strongly enough to reverse
the finite-volume coefficient.

A negative coefficient is not a negative variance.  It means that the
fixed-order expansion is strongly nonuniform: higher orders must restore the
positivity of the exact observable.  This is diagnostic evidence against any
proof that truncates or bounds perturbative orders separately.

## Independent exact verification

The producer groups labeled Wick pairings by multigraph topology and performs
exact rational momentum sums.  A separately implemented C++17 verifier
reconstructs:

- all eight fixed-leg fiber families;
- every labeled Wick topology;
- the \(\mathbb Z_4^4\) momentum-flow equations;
- the propagator with \(0,+p,-p\) forbidden;
- every cubic, quartic, and quintic Gaussian-integer lattice kernel.

It evaluates each term modulo four distinct 61-bit primes.  Every term and
the total agree with the rational producer.  A deliberately coarse absolute
bound clears all possible denominators and bounds a hypothetical integer
difference by 226 bits.  The four-prime product has 244 bits and exceeds twice
that bound, so residue agreement proves equality rather than supplying a
probabilistic check.

The preliminary streaming Gaussian calculation gave
\(-4.12\pm2.26\), consistent with the exact value, but it is supporting only
and is not used in the proof.

## Boundary and next gate

The next exact task is the general-\(L\) affine atlas for these eight families.
Because the full-phase covariance is translation invariant, no rank-one
position-dependent sectors are needed: loop momenta simply exclude
\(0,+p,-p\).  Common kernels must be combined before absolute values to decide
whether the finite negative remainder retains the \(N\omega_p\) scale or
becomes subpower.

Even a large-volume fixed-order result will not establish the interacting
current susceptibility without a uniform remainder or a nonperturbative
bridge.  No interacting \(H^{-1}\) result, continuum measure, Born rule,
Krein reconstruction, or `LORENTZIAN-CAUSAL` claim is made.

## Verification

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_full_phase_g4_l4_exact.py --check
g++ -std=c++17 -O3 -Wall -Wextra -Werror reverse_physics/bt_euclidean_full_phase_g4_l4_modular_verify.cpp -o /tmp/bt-full-phase-g4-modverify
ulimit -v 500000; /tmp/bt-full-phase-g4-modverify
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_full_phase_g4_l4_decision.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_full_phase_g4_l4_decision
```

## Verification receipt

- Tier 0 passed: four Python files compile, the C++17 verifier builds with
  warnings as errors, the schema, data, certificate, and sequence-37 planning
  event parse, and the scoped diff check is clean.  All bounded executables ran
  under a 500 MB virtual-memory cap.
- The exact rational producer generated the data in 8.26 s and its drift check
  passed in 7.36 s, each at 115 MB maximum resident memory.  The lightweight
  certificate projection passed in 0.10 s at 23 MB.
- The standalone modular evaluator ran in 0.47 s at 18 MB.  The independent
  verifier, including a fresh warnings-as-errors C++ build, passed in 1.98 s at
  151 MB.
- Fourteen direct and adversarial mutation tests passed in 2.05 s at 152 MB.
- The full-phase coupling reconciliation and cubic-current predecessor
  verifiers passed in 0.16 s and 0.19 s respectively.
- The append-only planning import read 1,640 nodes with zero invalid items and
  zero malformed events in 7.24 s under a 300 MiB Go memory limit.
- The 2.34 s advisory Science Forge shadow rail failed closed on the existing
  Forge binary/standard-library mismatch (`E9118`) and reported corpus
  baseline drift (1,756 certificates versus 976).  Its advisory wrapper exited
  zero; the bridge audit itself is recorded as failed, not passed.
- Paper 21 remains deferred because its independent foundations
  authority/claim-map rail is stale at the unchanged parent (`authority hash
  drift: explorer_snapshot`).  This theorem is published through its
  certificate and report without taking ownership of that overlapping work.
- Tier 3 was not run because this is a finite-volume perturbative decision,
  not a continuum, reconstruction, freeze, or shared-core lifecycle promotion.
