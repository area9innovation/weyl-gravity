# Classical minimal-BV q3 export v1

**Result:** `CLASSICAL_MINIMAL_BV_Q3_EXPORT_V1`

**State:** `MINIMAL_BV_Q3_EXPORTED_ARITY_THREE_REPLAY_AND_NONMINIMAL_STABILIZATION_OPEN`
**Dependency:** `LOCAL-ALGEBRAIC`

## Result

The authoritative pure-Weyl minimal master action determines the entire
arity-three Taylor component on its six-generator carrier.  Exactly one row
is nonzero:

```text
q3(h1,h2,h3) = D^3[-2 sqrt(abs(g)) B(g)^sharp](h1,h2,h3)
```

All antifield-dependent master-action summands are cubic, so their BV
Hamiltonian derivatives are at most quadratic.  They generate q1 and q2 but
no q3.  This is an export from the existing certified classical complex. It
is not a reconstruction of a second BV complex.

| Output row | q3 status | Accepted inputs |
|---|---|---|
| `g` | `IDENTICALLY_ZERO_BY_MASTER_ACTION_DEGREE` | none |
| `xi` | `IDENTICALLY_ZERO_BY_MASTER_ACTION_DEGREE` | none |
| `omega` | `IDENTICALLY_ZERO_BY_MASTER_ACTION_DEGREE` | none |
| `g_star` | `NONZERO_NATURAL_OPERATOR` | g, g, g |
| `xi_star` | `IDENTICALLY_ZERO_BY_MASTER_ACTION_DEGREE` | none |
| `omega_star` | `IDENTICALLY_ZERO_BY_MASTER_ACTION_DEGREE` | none |

The natural-operator root is symmetric, fourth order and support-local.  On
diagonal input the convention is `D3E(h,h,h)=6*[t^3]E(g+t h)`.

## Boundary

This producer classifies and exports the complete minimal q3, but does not
count its own construction as an independent component replay.  The
coefficientwise arity-three identity, quartic cyclicity, and the 386-row
nonminimal stabilization remain open and fail closed.

## Reproduction

```text
python3 d_quotient_classical/minimal_bv_antifield/classical_minimal_bv_q3_export_v1.py --check
python3 d_quotient_classical/minimal_bv_antifield/check_classical_minimal_bv_q3_export_v1.py
```

## Does not establish

- an independent exact component execution of the natural-operator AST.
- the coefficientwise arity-three identity q1 q3 plus q2 q2 plus q3 q1 equals zero.
- quartic BV cyclicity in the quantum receiver convention.
- a cyclic stabilization or L-infinity equivalence on the 386-row nonminimal carrier.
- causal compatibility of q3 with a Green homotopy.
- a Hadamard state, renormalized time-ordered products, QME restoration, or a Lorentzian quantum theory.
