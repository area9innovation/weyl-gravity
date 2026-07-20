# Einstein--Weyl relative residual-action descent v1

## Result

The frozen compact-product Einstein--Weyl linear triangle is equivariant
under

```text
H_product =
(R_t x U(1)_x x SO(3))_orientation-preserving x U(1)_constant
```

and under the separate large-gauge lattice
`H^1(S1 x S2;Z)=Z`.  The source-to-target map on the six connected
reducibilities and on the winding lattice is the identity, so the relative
endpoint cohomology is zero.

This theorem uses “relative residual cohomology” in one precise sense:
cohomology of the mapping cone retained as an `H_product` representation.
It is not invariant-state cohomology and is not the orbit-space quotient.

## Branch cohomology

| Relative branch | Solution-degree mapping-cone cohomology | Pairing block |
| --- | --- | --- |
| generic axial | `(K_(ell,n)[omega]/(p))^2 tensor V_ell` | nonradical, inertia `(2,0)` |
| generic polar | `(K_(ell,n)[omega]/(p))^2 tensor V_ell` | nonradical, inertia `(2,0)` |
| exceptional `ell=1,k=0` | `(K[x]/(x-4/3))^2 tensor V_1` | nonradical, Gram `diag(16,3)` |
| exceptional `ell=1,k!=0` | `(K_n[s]/(s-4/3))^2 tensor V_1` | nonradical, Gram `4(3k^2+4)` in each parity |
| homogeneous | zero | not applicable |
| twist | zero | not applicable |
| electric/Wilson | zero | not applicable |

On every oscillatory coefficient,

```text
c_(m,k,omega) ->
exp(-i omega tau+i k theta) sum_m' D^ell_(m,m')(R)c_(m',k,omega).
```

The chain maps and primary projections commute with this action because they
are natural and scalar in `m`, and polynomial in the invariant product
operators.  Constant `U(1)` reducibility acts trivially.

For the homogeneous block, time translation acts by

```text
a'   = a+tau*b
b'   = b
c'   = c+tau*d+tau^2*a+(tau^3/3)*b
d'   = d+2*tau*a+tau^2*b
Q_e' = Q_e
W_x' = W_x+tau*Q_e.
```

For twists, `(A,B)` maps to `(R(A+tau B),RB)`.  Independently,
large `U(1)` winding identifies
`W_x ~ W_x+(2*pi/L)r`.  Exact matrix multiplication gives zero invariance
defect for both the source and pulled-back Weyl forms on the homogeneous and
twist blocks.

## Three-form boundary

The following remain distinct:

1. the Einstein--Maxwell source form;
2. the Weyl--Maxwell form pulled back to the Einstein image;
3. the direct Weyl--Maxwell form on the relative solution cofiber.

The generic standard-pairing cyclic map remains obstructed.  Equivariance
does not repair that obstruction.

## Fail-closed boundary

No moment level, orbit-type stratification, or global symplectic quotient is
constructed.  Consequently the global orbit quotient, support-local physical
branch projection, and causal Green descent are all `NO_CERTIFIED_MAP`.
No compact class is promoted to a particle, observable, nonlinear map,
scattering state, unitary sector, or quantum state.

The machine-readable overlay
`residual_atlas/einstein-weyl-relative-residual-action-overlay-v1.json`
adds these cells against the stable branch identifiers in the pinned
manifest without rewriting or regenerating that manifest.

## Coordination incident

The activation commit for this work item also contained pre-existing
observer files that another team had placed in the shared Git index.  The
published commit was not rewritten.  This scientific commit stages explicit
paths only and its exact staged diff is inspected before publication.

CLOSE-OUT: DONE — the complete stop condition is met
EVIDENCE: EINSTEIN_WEYL_RELATIVE_RESIDUAL_ACTION_DESCENT_V1_TIER_RECEIPT
