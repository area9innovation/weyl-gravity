# Strict cylinder metric-antifield basepoint row v1

**Result:** `STRICT_CYLINDER_HSTAR_BASEPOINT_ROW_V1`

**State:** `HSTAR_BASEPOINT_ROW_AND_DIFF_IDENTITY_ASSEMBLED_PORTABLE_GLOBALIZATION_AND_POLARIZATION_OPEN`

**Dependency:** `LOCAL-ALGEBRAIC`

## Outcome

The sixth strict minimal-BV diagonal Taylor row is now assembled at the
declared homogeneous cylinder frame:

```text
q2_diagonal(h_star)^{mu nu}=(1/2)K^{mu nu}[h,h]+Lie_c(h_star)^{mu nu}-2 omega h_star^{mu nu}
```

The exact classical export fixes `Q(g_star)=E_g+Lie_c(g_star)-2 omega g_star`.
The universal table stores the coefficient of `a*b`, hence the diagonal
`epsilon^2` coefficient is **one half** of `K[h,h]`. Both cotangent signs are
also recovered independently as minus the metric Euler derivative of the two
metric gauge master terms, including the density-divergence contribution.

This is real progress past a missing-row placeholder, but it is deliberately a
**basepoint assembly**, not a portable six-row `q2`: the large `K` table still
needs tensor-natural globalization and suspended graded polarization. The
separate universal fifth-jet calculation now certifies all four differentiated
Diff Noether rows exactly.

## Three components

| Component | Inputs | Coefficient | Portability | Formula |
|---|---|---:|---|---|
| `q2_hstar_hh_basepoint` | `h, h` | `1/2` | `HOMOGENEOUS_BASEPOINT_ONLY` | (1/2) K^{mu nu}[h,h] |
| `q2_hstar_chstar` | `c, h_star` | `1` | `TENSOR_NATURAL` | c^rho partial_rho h_star^{mu nu} - h_star^{rho nu} partial_rho c^mu - h_star^{mu rho} partial_rho c^nu + (partial_rho c^rho) h_star^{mu nu} |
| `q2_hstar_omegahstar` | `omega, h_star` | `-2` | `TENSOR_NATURAL` | -2 omega h_star^{mu nu} |

## Gate ledger

| Gate | Status | Evidence or missing proof |
|---|---|---|
| `HSTAR_BASEPOINT_DIAGONAL_ASSEMBLY` | `PASS` | all three source-fixed terms are serialized; the exact Hessian factor 1/2 and cotangent signs are replayed |
| `TENSOR_NATURAL_GLOBALIZATION` | `OPEN` | the K term remains a one-frame component table without an SO(4)-isotropy/coordinate-change certificate |
| `DIFFERENTIATED_DIFF_NOETHER` | `PASS` | all four background, unary and quadratic fifth-jet coordinate rows cancel in the universal engine and three independent point probes |
| `SUSPENDED_GRADED_POLARIZATION` | `OPEN` | this artifact fixes the diagonal Taylor row, not the repository suspended bilinear sign convention |
| `SIX_ROW_INTERACTION_IDENTITIES` | `OPEN` | q1q2=0, Koszul symmetry, D derivation and BV cyclicity await a portable six-row payload |

## Missing-object ledger

| Object | Status | Blocks |
|---|---|---|
| SO(4)-isotropy-covariant globalization of K | `MISSING` | portable h-star row |
| suspended graded bilinear polarization of all six rows | `MISSING` | Koszul symmetry and complete q2 receiver |
| full local D action and common BV pairing replay | `MISSING` | D derivation, cyclicity and Gate A |

## Independent replay

The fast receiver checks the authoritative source row and the independent
classical-import hashes, re-derives the complete contravariant-density Lie
formula from the negative variational adjoint, replays the Weyl sign, evaluates
three exact diagonal Hessian fixtures with the factor `1/2`, pins the universal
table hash, and rejects every stronger lifecycle flag.

```text
python3 quantum-weyl/classical_import/build_strict_cylinder_hstar_basepoint_row.py --check
python3 quantum-weyl/classical_import/check_strict_cylinder_hstar_basepoint_row.py
python3 quantum-weyl/classical_import/verify_strict_cylinder_hstar_basepoint_row.py
python3 -m unittest quantum-weyl/classical_import/tests/test_strict_cylinder_hstar_basepoint_row.py -v
```

## Does not establish

- a coordinate-independent or SO(4)-isotropy-covariant globalization of the metric Hessian table.
- the complete arity-two master identity beyond the now-certified differentiated Diff Noether row.
- the repository suspended graded bilinear q2 or its Koszul symmetry.
- a portable complete six-row support-local q2 or complete local D action.
- BV cyclicity on a common support-local pairing or a passed classical import Gate A.
- a Lorentzian causal Green homotopy, Hadamard state, restored QME, or Lorentzian quantum theory.
