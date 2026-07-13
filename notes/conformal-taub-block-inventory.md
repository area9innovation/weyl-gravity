# C2c-I staging: exact proper-conformal Taub-block inventory

## Purpose

`symbolic/verify_conformal_taub_block_inventory.py` determines the complete
representation-allowed workload for the proper-conformal part of the Taub
constraint map on the local gauge-reduced `E/A/L` oscillator towers.

It does not compute an unseeded coefficient.  Its purpose is to prevent two
opposite errors:

1. treating the two C2b reduced coefficients as the complete low-energy
   constraint map; or
2. launching unrelated curvature calculations without first using compact
   energy and `SU(2)_L x SU(2)_R` representation theory.

## All-energy families

Let `n=2J`.  The three branches have

```text
E_n: D=n,   2j=(n+2 chi,n-2 chi),
A_n: D=n+1, 2j=(n+chi,n-chi),
L_n: D=n+2, 2j=(n+2 chi,n-2 chi).
```

A lowering proper-conformal kernel has compact energy `-1` and doubled
spatial representation `(1,1)`.  Both `SU(2)` tensor products are
multiplicity-free.  The complete stable list of source-to-target branch
families is

```text
E -> E,
A -> E,  A -> A,
L -> E,  L -> A,  L -> L,
```

with chirality preserved.  Parity supplies the conjugate chirality, leaving
one reduced coefficient per listed family and energy level.

At the lower boundary:

- source energy 3 permits `E -> E` and `A -> E`;
- source energy 4 permits all stable families except `L -> L`;
- every source energy at least 5 permits all six families.

Consequently the exact number of chiral blocks through cutoff `D_max>=4` is

\[
N_{\rm block}(D_{\max})=14+12(D_{\max}-4)=12D_{\max}-34,
\]

and the parity-reduced coefficient count is

\[
N_{\rm red}(D_{\max})=6D_{\max}-17.
\]

Through energy four there are seven reduced coefficients.  The direct C2a
curvature seeds and C2b Wigner--Eckart reconstruction fix only two:

```text
A_1 -> E_1,
L_1 -> A_1.
```

Five reduced coefficients already remain at that minimal cutoff.  Through
energy six there are 19 parity-reduced coefficients, of which 17 remain
unseeded.  This is the finite representation-theoretic target for the first
complete truncated Taub map.

## What representation theory does and does not supply

Multiplicity one means that one directly normalized magnetic entry fixes an
entire `(1/2,1/2)` block.  It does not fix the reduced coefficient itself.
Those values must come from one of:

- a direct action/symplectic calculation;
- a rigorously normalized conformal-generator representation;
- conformal-algebra recursion after the relation between the Taub bilinear
  kernel and the oscillator generator has been established; or
- selected curvature seeds used as independent normalization checks.

At present, the action-normalized kernels contain factors not yet matched to
the full oscillator symplectic normalization.  Therefore one must not impose
the `[K^+,K^-]` algebra directly on the C2b coefficient kernels as if they
were already oscillator-generator matrices.

## Acceptance boundary

The inventory proves:

- exact energy and representation allowance;
- multiplicity one;
- parity orbit counts;
- the six stable all-energy branch families; and
- the precise number of missing reduced coefficients at every cutoff.

It does not prove:

- any value for an unseeded coefficient;
- full coadjoint equivariance;
- the seven Killing-charge kernels;
- the fifteen quadratic charge polynomials;
- the full constraint zero locus, its symplectic moment-map identity, or its
  quotient; or
- global BRST cohomology.

Both scope guards fail closed:

```bash
python3 symbolic/verify_conformal_taub_block_inventory.py \
  --require-all-coefficients
python3 symbolic/verify_conformal_taub_block_inventory.py \
  --require-full-moment-map
```
