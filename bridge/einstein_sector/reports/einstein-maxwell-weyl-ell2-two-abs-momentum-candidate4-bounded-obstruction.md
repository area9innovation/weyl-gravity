# Candidate-4 two-momentum bounded obstruction

## Result

The first source calculation from the parity-reduced two-absolute-momentum
ledger is complete.  Candidate 4 consists of two axial Einstein q-minus
modes with signed compact momenta

\[
k_1=\sqrt\rho,\qquad k_2=-2\sqrt\rho,
\qquad
\rho=\frac{29(-361+783\sqrt3)}{26772},
\]

in the positive-frequency sum channel.  Their product has output
\((L,M)=(4,0)\), momentum \(K=-\sqrt\rho\), and lies exactly on the polar
extra shell,

\[
\Omega^2-K^2=\frac{58}{3}.
\]

The projected quadratic source has a nonzero component in the complete
two-dimensional adjoint cokernel of the polar p-primary action block.  In
the certified cokernel basis its pairings are

\[
\left(
0,
-\frac{1152}{203}(-265+149\sqrt3)
\right).
\]

The second component is nonzero because

\[
265^2-3\,149^2=3622\ne0.
\]

Therefore no bounded or finite-quasiperiodic second-order correction exists
for this declared tangent.  The smooth-secular class remains open, and the
causal/retarded class is `NO_CERTIFIED_MAP`.

## Exact PBW replay and calibration

The source evaluator uses a 5.8 KiB content-addressed symbolic slice extracted
from the exact Weyl-Maxwell product \(q_2\) payload.  The slice retains the
parent q2, action and row-layout hashes.  Only 842 sparse terms can contribute
from physical input rows
\(9,12,16,17\) to Euler rows \(20,21,24,33\).  Coefficient jets through
theta order four reconstruct the \(L=4\) scalar and axial output.

The action crosswalk is load-bearing:

- the metric Taylor rows are variational densities and require the factor
  two that restores the action-row convention;
- scalar density rows are expanded in \(P_L(\cos\theta)\), without an extra
  background volume factor;
- the Maxwell Euler row is contravariant and is expanded in
  \(-\partial_\theta P_L/\sin\theta\).

Before evaluating candidate 4, this crosswalk reproduces all four frozen
action rows of the independent opposite-momentum \(L=4\) source exactly.
No fitted normalization or floating-point comparison is used.

## Cokernel completeness

On the \(L=4\) polar p shell the action block has rank two.  With output
momentum \(K\) and frequency \(\Omega\), a complete adjoint basis is

\[
z_1=\left(1,-\frac{3K^2+29}{3K\Omega},1,0\right)^T,
\qquad
z_2=\left(\frac43,-\frac{2(K^2+20)}{3K\Omega},0,1\right)^T.
\]

The generator checks \(H_P^Tz_i=0\), rank \(H_P=2\), rank
\((z_1,z_2)=2\), and the two exact source pairings.  The independent verifier
reconstructs the shell, target block, adjoints, pairings and quadratic-field
nonvanishing witness without importing the producer.

## Workload disposition

This resolves the two polar p-primary coefficients in the axial-axial parity
channel of candidate 4.  It is two of the 108 axisymmetric \(L=4\) reduced
adjoint coefficients.  The remaining 106 axisymmetric coefficients and all
56 nonaxisymmetric \(L=1,3\) coefficients remain open.

This is not a classification of the complete two-fibre tangent cone, and it
does not establish smooth-secular, causal, residual, observable or quantum
claims.

## Evidence

- Certificate: `bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_candidate4_bounded_obstruction.json`
- Generator: `bridge/einstein_sector/einstein_maxwell_weyl_two_abs_momentum_candidate4_pbw_probe.py`
- PBW slice: `bridge/einstein_sector/generated/einstein_maxwell_weyl_ell2_axial_qminus_pair_L4_q2_slice.json`
- Independent verifier: `bridge/einstein_sector/verify_einstein_maxwell_weyl_ell2_two_abs_momentum_candidate4_bounded_obstruction.py`
- Scoped tests: `bridge/einstein_sector/tests/test_einstein_maxwell_weyl_ell2_two_abs_momentum_candidate4_bounded_obstruction.py`

## Verification commands

```text
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_candidate4_pbw_probe --check
python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_ell2_two_abs_momentum_candidate4_bounded_obstruction.py
python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_ell2_two_abs_momentum_candidate4_bounded_obstruction
```

An attempted direct four-dimensional replay spent 1,863 CPU seconds inside
the legacy truncation engine's symbolic GCD simplification before reaching
source projection.  It was terminated and is **not** counted as a pass.  A
future direct audit must first replace that simplification bottleneck; the
certified evidence here is the exact content-addressed q2 slice, its frozen
opposite-momentum calibration, and the separate algebraic verifier.
