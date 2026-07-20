# Invariant common-action Ward compatibility theorem

## Theorem

Let `(a,b,c)` be the nonzero normalization ratios in

```text
s_Maxwell = a s_tau
s_Maxwell = b s_emitter
s_emitter = c s_tau.
```

For the declared component-preserving pairing family, a nonzero common raising
pairing exists exactly when `a=b*c`.  Equivalently, the cycle holonomy
`H=a/(b*c)` must equal one.  The compatibility matrix has determinant `b*c-a`.

The frozen Berger data are derived from the declared actions and pairings:
the typed Maxwell lowered tensor supplies `a=2`, the switched physical
Maxwell--emitter Hessian supplies `b=1`, and the three variational slots of
`integral <K_plus,L_(tau e0)K>` supply `c=1`.  Thus `H=2`, the determinant is
`-1`, and the matrix has rank three.  No nondegenerate common raising pairing
exists on the present 108-row carrier.

## Invariance

Under nonzero field rescalings `(r_M,r_E,r_T)`, the ratios transform as

```text
a'=(r_M/r_T)a,  b'=(r_M/r_E)b,  c'=(r_E/r_T)c.
```

Therefore `a'/(b'c')=a/(bc)`.  Equivalently the compatibility matrix changes
by invertible diagonal row and column operations, so its rank is invariant.
The imported action-equivalent Maxwell presentation preserves the same lowered
tensor and the independently replayed `tau_star` witness.

## Complete bounded minimal classification

Changing exactly one edge reaches the compatibility locus at:

| changed edge | ratios `(a,b,c)` | null line |
| --- | --- | --- |
| Maxwell--tau | `(1, 1, 1)` | `(1, 1, 1)` |
| Maxwell--emitter | `(2, 2, 1)` | `(2, 1, 1)` |
| emitter--tau | `(2, 1, 2)` | `(2, 2, 1)` |

These are necessary-condition loci, not physical repairs.  None has been
regenerated from a changed action or substituted as a new operator into the
original q1/q2 verifier.

The support-one slack family likewise has exactly three algebraic classes, one
per Ward orbit.  Within the frozen component-preserving family an off-diagonal
block is not admissible.  A one-row carrier enlargement is impossible:
every antisymmetric `109 x 109` pairing over `Q` has zero determinant.  The
first dimension not excluded is 110, obtained by adding a complementary-degree
conjugate pair; its Berger representation and action remain open.

Dropping each orbit is a decisive control:

| dropped orbit | exposed null line |
| --- | --- |
| Maxwell_tau | `(1, 1, 1)` |
| Maxwell_emitter | `(2, 1, 1)` |
| emitter_tau | `(2, 2, 1)` |

The separately recomputed factor-two mutation reaches the first one-edge
normalization locus and restores `(1,1,1)` only as a mutation.  The original
operator still has
`tau_star <- (e0 e1 A_0,K0_01)` with coefficient `+g0 h0`.

## Boundary

The observer-specific Conflux importer is still a typed Forge request, so no
Conflux preflight or candidate exploration was run.  No q3, `K_Berger`,
observer-morphism, detector, second-order-cone, causal, branch, particle, or
quantum claim is promoted.

Machine-readable certificate:
`closed_universe_observers/certificates/BERGER_108_ROW_COMMON_ACTION_COMPATIBILITY_THEOREM.json`.
