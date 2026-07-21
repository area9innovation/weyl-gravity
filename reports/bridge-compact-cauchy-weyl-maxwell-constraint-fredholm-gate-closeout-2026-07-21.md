# Compact-Cauchy Weyl--Maxwell constraint/Fredholm gate close-out

Disposition: exact Fredholm obstruction with a certified right-elliptic replacement.

On the fixed magnetic bundle over `Sigma=S1_L x S2`, the action-derived
canonical phase space has the three pairs `(h,pi)`, `(K,P)` and `(a,E)`, for
thirty local components.  The Hamiltonian, three momentum, two conformal and
Maxwell Gauss constraints give seven first-class rows.

For integer `s>=4` the certificate declares the complete weighted Sobolev
domain and target.  It also fixes seven local configuration gauges: spatial
unimodular harmonic gauge, a normal double-divergence gauge, Weyl value and
normal-derivative gauges, and based Maxwell Coulomb gauge.  The gauge symbol
on the seven gauge-orbit directions has normalized determinant `-16`.

The raw constraint symbol is surjective for every nonzero spatial covector:

```text
P^ij  -> (xi_i xi_j P^ij, tr P)       rank 2
pi^ij -> (xi_j pi^ij, tr pi)          rank 4
E^i   -> xi_i E^i                     rank 1
```

Hence the raw constraint map is underdetermined elliptic.  On the compact
slice it has closed range and finite-dimensional cokernel.  The combined
constraint-plus-gauge symbol is also full-row-rank: solve the gauge rows in
configuration variables and then cancel their constraint values with the
independently surjective momentum/electric block.

It is not Fredholm.  The combined symbol maps rank 30 to rank 14 and has
kernel dimension 16, exactly the physical phase-space count.  At the product
covector `xi=(1,0,0)`, both

```text
P_cross: P23=1,
P_plus:  P22=1, P33=-1
```

are explicit nonzero transverse-traceless kernel witnesses.  Appending
`P23=0` raises the rank only by imposing a non-gauge condition on a physical
direction; it is therefore rejected as a gauge repair.

This corrects the analytic target.  Arms--Marsden--Moncrief theory should be
approached through the split right-semi-Fredholm constraint map, not a false
two-sided Fredholm operator.  The adjoint cokernel is finite and contains the
five lifted `H,P_x,J_i` stabilizers, but equality with exactly those five is
still open.  Constant Maxwell gauge is handled as a reducibility by using a
mean-zero Gauss codomain; it is not advertised as a sixth Taub charge.

Delivered:

- complete canonical constraint and weighted Sobolev ledger;
- exact 14-by-30 Douglis--Nirenberg symbol with full-row-rank proofs;
- two physical TT kernel witnesses and a forbidden-gauge mutation;
- method-independent reconstruction, strict schema and eleven tests;
- fail-closed atlas fragment and a scoped Paper 13 correction.

Not delivered:

- the global adjoint-kernel calculation on `S1 x S2`;
- an equality theorem between that kernel and the five stabilizers;
- a nonlinear Sobolev slice or momentum-map normal form;
- evolution, bounded stability, causal, scattering, observable, particle or
  quantum claims.

CLOSE-OUT: OBSTRUCTED — the compact-Cauchy constraint map is right-elliptic with closed range and finite cokernel, but the requested constraint-plus-gauge Fredholm operator is impossible because its exact principal symbol retains a 16-dimensional physical kernel
EVIDENCE: bridge/certificates/EINSTEIN_MAXWELL_WEYL_COMPACT_CAUCHY_CONSTRAINT_FREDHOLM_GATE_V1.json
