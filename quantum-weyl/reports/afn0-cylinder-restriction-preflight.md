# AFN0 cylinder restriction preflight

Date: 2026-07-16

Dependency tag: `LOCAL-ALGEBRAIC`

Result state: `STRUCTURAL_RESTRICTION_VERIFIED_PROJECTION_BLOCKED`

## Outcome

The stabilized AFN0 ghost-zero basis now has an exact structural restriction
preflight on the Einstein cylinder. The background calculation independently
verifies

\[
\bar g=-dt^2+d\Omega_3^2,
\qquad
\bar C=0,
\qquad
\bar E_4=0.
\]

The component audit gives

\[
\bar R_{ijkl}=\bar g_{ik}\bar g_{jl}-\bar g_{il}\bar g_{jk},
\qquad
\bar R_{ij}=2\bar g_{ij},
\]

with all time-curvature components zero and

\[
\bar R_{\mu\nu\rho\sigma}^2=12,
\qquad
\bar R_{\mu\nu}^2=12,
\qquad
\bar R=6.
\]

Consequently the Weyl-square and Pontryagin carriers have no zeroth- or
first-order term:

\[
(C^2)^{(0)}=(C^2)^{(1)}=0,
\qquad
(C\widetilde C)^{(0)}=(C\widetilde C)^{(1)}=0.
\]

Their polarized quadratic heads are recorded as

\[
C_1(h)\cdot C_1(k),
\qquad
C_1(h)\cdot *C_1(k).
\]

## Curvature and parity bridge

The preflight hash-binds the all-energy cylinder metric-preimage certificate,
including

```text
C1 R_n = id
```

on the `E/A/L` curvature image blocks. The orientation-reversing isometry
`alpha <-> gamma` exchanges the chiral families and carries orientation
`-1`; the stored Lorentzian Hodge eigenvalues are `-i` and `+i`.

This proves the support pattern

| Local source | even residual evidence | odd residual evidence |
|---|---|---|
| `C2` | allowed nonzero | zero by parity |
| `C dual C` | zero by parity | allowed nonzero |

where

\[
e=(W_+^2+W_-^2)/\sqrt2,
\qquad
o=(W_+^2-W_-^2)/\sqrt2.
\]

The entries say only which blocks parity permits. They are not normalized
projection coefficients.

## Fail-closed boundary

No `LOCAL_TO_CYLINDER_MAP` is emitted. The normalization matrix remains
`null`, and the result explicitly records these blockers:

- the frozen quantum import still lacks the portable project-wide `pi_cl`;
- normalized coefficient vectors for `W_+^2` and `W_-^2` are absent;
- centered bases in degrees 3 and 5 are absent;
- the parity Ward identity is not computed;
- the Euler temporal/boundary policy is not frozen.

Thus `E4` is withheld pending the boundary policy, while `Box R` is already
zero in the relative quotient by its explicit covariant current.

## Machine receipt

- `quantum-weyl/cylinder/certificates/AFN0_CYLINDER_RESTRICTION_PREFLIGHT.json`
- `quantum-weyl/cylinder/afn0_restriction_preflight.py`
- `quantum-weyl/cylinder/schema/afn0_cylinder_restriction_preflight.schema.json`

## Verification receipt

| Command | Elapsed | Status | Tier |
|---|---:|---|---:|
| focused cylinder preflight suite | 0.55 s | 5 pass | 1 |
| deterministic preflight emitter/checker | under 2 s | pass | 1 |
| Python compile and `git diff --check` | under 1 s | pass | 0 |

Higher tiers were not run because this certificate consumes existing
hash-bound classical cylinder evidence without changing it and deliberately
does not promote Gate C to a projected cohomology map.
