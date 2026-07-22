# Phase-2 cylinder CPT/BRST feasibility

Result: `REDUCED_C0_POSITIVE_BUT_RESIDUAL_CHAIN_DESCENT_OBSTRUCTED`.

## Reduced stationary construction

On the normalized cylinder one-particle carrier the canonical Krein form is

```text
G = +1_E direct-sum -1_A direct-sum -1_L.
```

The obvious stationary candidate is the same fundamental symmetry,

```text
C0 = +1_E direct-sum -1_A direct-sum -1_L,
eta0 = G C0 = 1.
```

Thus `C0^2=1`, `[C0,D]=0`, and `eta0` is exactly positive on every reduced
energy block.  This reproduces the attractive finite-block CPT answer.  It is
not yet a residual or BRST-compatible `C` operator.

## Exact energy-five regression

The all-level oscillator implementation was assembled through energy five for
both chiralities.  Each chirality has dimension 134, canonical Krein inertia
`(70,64,0)`, and `eta0` inertia `(134,0,0)`.  Direct computation gives:

| Generator rows | Number | `rank [C0,rho(T)]` per row and chirality |
| --- | ---: | ---: |
| `D` | 1 | 0 |
| compact `SO(4)` | 6 | 0 |
| proper-conformal `K^-` | 4 | 32 |
| proper-conformal `K^+` | 4 | 32 |

The rank 32 is computed from the exact sparse matrices; it is a regression,
not an encoded expected value.  Stacking all eight proper-conformal defects
has rank 102 per chirality and 204 on their direct sum.

For the residual CE/BRST differential at degree zero,

```text
Q(v) = sum_a rho(T_a)v tensor c^a,
[C0 tensor 1,Q](v) = sum_a [C0,rho(T_a)]v tensor c^a.
```

The ghost directions `c^a` are linearly independent.  Hence any nonzero
proper-conformal coefficient proves that `C0 tensor 1` is not a chain map.
The reduced sign flip therefore does not descend through the declared
identity-ghost residual complex.

The energy-five object is only a buffer: its top shell lacks the outgoing
raising blocks.  Its ranks and finite link graph are not promoted to an
all-energy representation theorem.

## Full invariant-commutant search

The all-energy obstruction uses the analytic tower structure instead of the
cutoff.  At fixed chirality, the `E_n`, `A_n`, and `L_n` summands are
multiplicity-one, pairwise inequivalent `SO(4)` irreducibles once energy is
included.  Schur reduction therefore makes every operator commuting with
`D` and both compact `SO(4)` factors a scalar on each tower-energy summand.

Commutation with a nonzero proper-conformal link equates the source and target
scalars.  The exact coefficient squares show, throughout their full tails,

```text
EE_n != 0  for n >= 3,
AE_n != 0  for n >= 3,
LE_n != 0  for n >= 4.
```

The `EE` links connect every `E_n` to `E_2`; `AE` connects every `A_n` to
that chain; and `LE` connects every `L_n`.  Thus the full connected conformal
commutant on the common finite-energy-support core is

```text
C = c_- I on chirality -1 direct-sum c_+ I on chirality +1.
```

Hermitian involutions have `c_+,c_-` in `{+1,-1}`; parity identifies them.
For either choice, `eta=G C` still has both `E` and `A/L` signs in each
chirality.  No positive structured metric arises from a residual-invariant
Hermitian involution.  The remaining `AA`, `LA`, and `LL` links provide
redundant exact checks of the same connected graph.

This is the first representation-theoretic obstruction requested by the work
item.  It stops the calculation before a positive metric can be induced on
BRST cohomology.

## Boundary and evidence

The machine certificate is
`quantum-weyl/pt_cpt/cylinder_brst/certificates/CYLINDER_BRST_STRUCTURED_CPT_FEASIBILITY_V1.json`.
Its independent rail reconstructs every generator matrix, recomputes the
rank-32 and stacked-rank defects, rebuilds the tower graph, and separately
checks strict positivity of all six analytic coefficient-square tails.  It
also rejects chain-map, rank, cutoff-promotion, positive-commutant,
ghost-scope, and full-unitarity mutations.

The result is tagged `LOCAL-ALGEBRAIC` and `REDUCED-MODE`.  It does not exclude
a more general construction that acts nontrivially on ghosts and normalizes,
rather than commutes with, the residual action.  It constructs no complete
Lorentzian off-shell BV propagator, BRST-compatible Hadamard state, full-BV
`C` operator, scattering positivity, anomaly cancellation, or unitarity.

## Test tiers

- Tier 0: Python compilation, JSON/schema parsing, scoped whitespace audit,
  and exact changed-path diff inspection.
- Tier 1: deterministic producer replay, independent exact verification,
  six decisive mutation controls, and scoped tests.
- Tier 2: not required because imported mathematical operators are unchanged
  and hash-pinned; this is a downstream feasibility classification.
- Tier 3: not required because no freeze, shared core algebra change, release,
  or Lorentzian/quantum lifecycle promotion occurs.

CLOSE-OUT: DONE — `eta0=G*C0` is exactly positive on the stationary reduced E/A/L carrier, but `C0` fails the proper-conformal BRST chain test and the full declared all-energy invariant commutant contains no corrected positive `G*C` involution.
EVIDENCE: quantum-weyl/pt_cpt/cylinder_brst/receipts/CYLINDER_BRST_STRUCTURED_CPT_FEASIBILITY_V1_TIER_RECEIPT.json
