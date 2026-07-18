# Coefficient-bearing one-loop BV obstruction

Status: `OBSTRUCTED_STRICT_FIELD_CONTENT`
Dependencies: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

The repository Euclidean principal-symbol complex is exact and elliptic. At a
nonzero covector its physical sequence has dimensions `5 -> 10 -> 5`, ranks
`5,5`, zero composition, an exact formal-adjoint sequence, and exact Diff and
Weyl nonminimal doublets. The accepted local determinant blocks have ranks
`(5,1,5,3)`.

A compactly supported local Ricci-flat carrier away from the Euclidean
Schwarzschild bolt and infinity has

\[
R=0,\quad R_{\mu\nu}R^{\mu\nu}=0,\quad
C^2=E_4={3\over256},\quad C\widetilde C=0.
\]

The factorwise local heat-kernel calculation, combined with the independent
round-`S4` Euler calculation, gives

\[
(c,-a,p,b)=\left({199\over30},-{87\over20},0,0\right)
\]

in the convention `(4 pi)^(-2) [c C2-a E4+p CdualC+b BoxR]`. The parity-odd
zero follows from the recorded Ward identity. `BoxR` is zero in the declared
scheme and remains removable through the explicit `R2` primitive.

Reduction against the complete gauge-fixed `H^{1,4}(s|d)` basis yields

\[
\mathcal A^{(1)}={199\over30}[\omega C^2]-{87\over20}[\omega E_4].
\]

Wess--Zumino consistency, the empty positive-antifield completion, gauge and
regularization decomposition, measure/contour ledger, and parity Ward
identity replay independently. Both displayed coordinates are nonzero in the
complete quotient. Strict pure-Weyl gravity with fixed field content therefore
has an obstructed local Euclidean BV quantum master equation at one loop.

This is an obstruction theorem, not a Lorentzian quantization theorem. It does
not construct a global BRST Hadamard state, renormalized Lorentzian products,
particles, or residual quantum transfer. It also does not rule out coefficient
cancellation by added matter or restoration in a certified Wess--Zumino
compensator extension.

The first extension test is also complete: a dual-cone witness proves that no
nonnegative collection of standard-sign free conformal scalars, Weyl/Dirac
fermions, or gauge vectors cancels the two even coordinates. The strict QME
obstruction therefore persists throughout that declared ordinary unitary
matter class. Interacting, nonunitary, higher-spin, and compensator extensions
are outside this no-go.

Primary receipts:

- `spectral/euclidean/certificates/REPOSITORY_EUCLIDEAN_ELLIPTIC_COMPLEX.json`
- `spectral/euclidean/certificates/REPOSITORY_NONCONFORMALLY_FLAT_OR_RICCI_FLAT_FULL_BV_OPERATOR_MEASURE_COEFFICIENT_MATCH.json`
- `anomalies/certificates/REGULATED_REPOSITORY_BV_SLAVNOV_BREAKING.json`

Independent replay:

```text
PYTHONPATH=quantum-weyl python3 quantum-weyl/spectral/euclidean/verify_repository_euclidean_elliptic_complex.py
PYTHONPATH=quantum-weyl python3 quantum-weyl/spectral/euclidean/verify_repository_ricci_flat_coefficient_match.py
PYTHONPATH=quantum-weyl python3 quantum-weyl/anomalies/verify_repository_regulated_slavnov_breaking.py
```
