# Phase 3 axial global connection matrix v5

## Scope and terminal disposition

This gate attempted the first validated horizon-to-infinity connection matrix
for the repaired axial Bach system on Schwarzschild with `M=1`, `ell=2`, and
real `M omega` in `[1/2,3/4]`. It imports the certified horizon basis, the
practical `R=32` infinity initializer, and the exact block-triangular six-state
reconstruction.

The result remains **SHORTFALL**, not a black-hole theorem. The newly landed
affine moving-frame substrate closes the entire diagonal flow on the first
required frequency cell. The remaining failure is now isolated to uniform
parameter correlation in the forced lower block. Therefore no `6x3`
connection matrix, projection rank, or current identity is promoted.

## What the new substrate closed

For

\[
  M\omega\in[1/2,129/256],
\]

the eight-real carrier and four-real Einstein-kernel blocks were propagated
separately from `r=32` to `r=4` as 1,792 retained affine factors. Every local
Peano--Baker enclosure and Krawczyk frame solve closed. Factorwise
nonsingularity is certified, with maximum local correction widths

\[
  w_C=0.009978474438174208,
  \qquad
  w_K=0.00332335609866979.
\]

This supersedes the previous diagonal-rank shortfall. The old flattened
carrier control still widens from `0.0138` at `r=31` to
`2.56e15` at `r=4`, demonstrating why the factor representation is necessary.

A naïve unstructured twelve-real affine frame is refused at reset zero with
`IVLIN_AFFINE_FACTOR_RANK_UNCERTIFIED`. That refusal is expected: interval
realification loses the exact zero upper-right block. It is not evidence that
the mathematical factor is singular.

## Structured variation of constants

The lower lift was then implemented with exact block-triangular frames

\[
 C_k=\begin{pmatrix}C^c_k&0\\D_k&C^k_k\end{pmatrix}
\]

and local correction

\[
 L_k=(C^k_{k+1})^{-1}
 \left(G_kC^c_k+U^k_kD_k-D_{k+1}W^c_k\right).
\]

All 1,792 columnwise Krawczyk solves for the `4x8` matrices `L_k` close. The
remaining enclosure is nevertheless unusable. At reset 65 the rational
midpoint correction has maximum magnitude

\[
  2.9720385240453925\times10^{-11},
\]

while fixed-frame interval evaluation produces the run's maximum width

\[
  3.6880892110833354\times10^7.
\]

The reason is precise: `A(omega)`, the cumulative lower frame `D(omega)`, and
the local flow share the same frequency parameter, but the present fixed
rational-frame API replaces those occurrences by decorrelated interval boxes
before their cancellation.

## Missing dependency

The next reusable primitive is a parameter-dependent affine or Taylor-model
frame that retains the shared `omega` generator through local
variation-of-constants algebra. The same API should transport a correlated
rectangular column family so the six horizon columns can be carried and rank
tested without independent-vector wrapping.

The exact request is
`planning/forge-requests/phase3-ivlinode-parametric-affine-rectangular.json`.
It extends the successful affine API; it is not a request for another generic
ODE integrator or a black-hole-specific kernel.

## Verification disposition

Producer replay, JSON Schema validation, the independent certificate verifier,
seven negative mutations, unit tests, and both ordinary C and native Forge
backends pass. The two sanitizer builds each reached the declared 1,800-second
limit without producing a diagnostic; those runs are recorded as **TIMEOUT**,
not as passes.

## Claim boundary

This shortfall does not show that the connection matrix is singular, nor that
an additional Bach scattering channel exists or fails to exist. It makes no
endpoint-flux, scattering, pole, stability, CPT, positivity, or unitarity
claim. It establishes that the diagonal long transfer is now certified and
that the first unresolved numerical theorem is shared-parameter correlation
in the structured lower lift.

CLOSE-OUT: SHORTFALL — the affine carrier and kernel chains are uniformly rank-certified on the first required frequency cell, and all 1,792 structured lower Krawczyk solves close, but fixed rational frames decorrelate the common frequency generator and inflate an approximately 3e-11 lower correction to width 3.69e7; a parameter-dependent affine/Taylor frame with correlated rectangular transport is required before the global connection can be certified.

EVIDENCE: black_hole_programme/phase3/axial_global_connection_matrix_v5/certificate.json

MISSING-DEP: sf:forge-request/phase3-ivlinode-parametric-affine-rectangular
