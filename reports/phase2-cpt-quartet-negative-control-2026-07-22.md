# Phase-2 structured-metric contract and quartet negative control

Result: `STRUCTURED_METRIC_CONTRACT_FIXED_AND_COUNTERFLOW_POSITIVE_ETA_INFEASIBLE`.

## What is established

The structured pseudo-Hermitian preflight now has a fail-closed contract.  A
positive metric `eta` must be exact Hermitian and strictly positive, satisfy
`H^dagger eta = eta H`, lie in the declared invariant commutant, respect the
real-field and opposite momentum/frequency involutions, and remain nonsingular
on its full parameter locus.  A field-theoretic promotion must separately
preserve the CCR under the new adjoint and retain the required causal and
microlocal properties.

A positive `eta` is not called a Mannheim `C` operator.  Such a claim also
requires an independently declared `P` and anti-linear `T`, `C^2=1`,
`[C,H]=0`, `[C,PT]=0`, the convention relating `eta`, `P`, and `C`, and an
explicit BRST chain map including any ghost action.

## Corrected BRST gate

The initially proposed condition

```text
Q^dagger eta = eta Q,  eta > 0
```

cannot be imposed on a nontrivial nilpotent BRST complex.  If `Q^2=0`, then

```text
||Qv||_eta^2 = <Qv,Qv>_eta = <v,Q^2 v>_eta = 0.
```

Strict positivity implies `Qv=0` for every `v`, hence `Q=0`.  The corrected
gate is chain-map/cohomology compatibility: `C` must preserve `ker Q` and
`im Q`, preferably through `C_(n+1) Q_n = Q_n C_n`, and positivity must be
proved on an explicit representative of `H^0(Q)`.  The certificate requests
maps `pi,i` satisfying `pi i=1`, `Q i=0`, and `pi Q=0`, or an equivalent
proved Hodge representative.  Exact states are removed cohomologically; they
are not nonzero null vectors of a strictly positive metric.

## Exact counterflow negative control

The hash-pinned repaired `j=1/2` physical payload contains two copies of

```text
40 D^4 + 773 D^2 + 3748.
```

For one copy the exact real companion evolution generator is

```text
A = [[0,       1,       0,       0],
     [0,       0,       1,       0],
     [0,       0,       0,       1],
     [-937/10, 0,      -773/40,  0]],
H = i A.
```

Writing `y=z^2`, the discriminant is

```text
773^2 - 4*40*3748 = -2151 = -9*239,
```

and the two exact roots are

```text
y = (-773 +/- 3 i sqrt(239))/80.
```

Thus every characteristic root `z` has nonzero real and imaginary parts.
The eigenvalues `i z` of `H` are nonreal.  If a strictly positive Hermitian
`eta` satisfied `H^dagger eta=eta H`, every eigenvalue of `H` would be real;
equivalently, `H` would be similar to a Hermitian operator.  Therefore the
positive-`eta` feasibility set is exactly empty on this block.  This is a
spectral Hamiltonian--Hopf obstruction, not a wrong-norm diagnosis.

The same conclusion holds throughout the imported trace-healthy stationary
family because

```text
disc_w F2 = 256 q^5 (9q-8) < 0,  0 < q < 1/4.
```

The stronger lower endpoint of the trace-healthy component is retained in the
certificate; only the displayed inequalities are needed for this sign proof.

## Evidence and boundary

The machine-readable result is
`quantum-weyl/pt_cpt/negative_control/certificates/STRUCTURED_METRIC_QUARTET_NO_GO_V1.json`.
Its independent verifier reconstructs the companion matrix directly from the
frozen classical payload, repeats the characteristic/discriminant calculation,
and independently solves a general Hermitian two-by-two fixture to confirm
that positive-metric self-adjointness trivializes a nonzero nilpotent operator.
It rejects real-spectrum, positive-eta, norm-only rescue, invalid BRST,
eta-as-C, and unitarity mutations.

This is a `LOCAL-ALGEBRAIC` / `REDUCED-MODE` classification.  It constructs no
Mannheim `C` operator, full-BV state, Hadamard covariance, particle space,
scattering theory, anomaly result, QME result, or unitarity theorem.  It is not
a no-go for PT/CPT quantization of pure conformal gravity; the counterflow
model is a changed theory used as an exact broken-PT negative control.

## Test tiers

- Tier 0: Python compilation, strict JSON/schema parsing, scoped whitespace
  audit, and exact changed-path inspection.
- Tier 1: deterministic producer replay, independent verifier, mutation
  controls, and scoped tests.
- Tier 2: not required because all imported mathematical inputs are unchanged
  and hash-pinned; this package adds a downstream classification only.
- Tier 3: not required because no freeze, shared core algebra change, or
  Lorentzian/quantum lifecycle promotion occurs.

CLOSE-OUT: DONE — the structured eta/C and corrected BRST contract is exact, and the counterflow quartet is certified as a familywide positive-pseudo-Hermitian negative control.
EVIDENCE: quantum-weyl/pt_cpt/negative_control/receipts/STRUCTURED_METRIC_QUARTET_NO_GO_V1_TIER_RECEIPT.json
