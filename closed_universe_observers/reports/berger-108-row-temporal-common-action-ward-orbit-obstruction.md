# Temporal common-action Ward-orbit obstruction

## Result

The temporal gravity-clock-Maxwell-emitter orbit cannot be raised from one
declared action in the component-preserving pairing family of the present
canonical 108-row carrier.  The exact pairing scale constraints, in the order
`(s_Maxwell,s_emitter,s_tau)`, are

```text
[1, 0, -2]
[1, -1, 0]
[0, 1, -1]
```

Their determinant is `-1` and their rank is `3`.  Thus their only common
solution is the degenerate zero scale vector.  The typed Maxwell block requires
`s_Maxwell=2 s_tau`; the switched emitter Hessian requires
`s_Maxwell=s_emitter`; and the temporal emitter Diff--BV vertex requires
`s_emitter=s_tau`.

This is a carrier-normalization incompatibility, not a missing PBW source.
The canonical 108-row carrier has unit-magnitude Maxwell, emitter and temporal
pairing entries with no hidden rescaling, while the imported typed Maxwell
presentation places a factor two in the Maxwell fibre pairing.

## Persistent coefficient

An independent source-pair replay reproduces

```text
tau_star <- (e0 e1 A_0,
K0_01)    coefficient +g0 h0.
```

It is identical to the first witness in
`BERGER_108_ROW_ARITY_TWO_OBSTRUCTION`.  Replacing the typed Maxwell binary
operation by the action-equivalent legacy presentation `S q2_typed` leaves
this coefficient unchanged.

## Mutation and boundary

Changing the imported Maxwell factor two to one makes the constraint matrix
singular with null vector `(1,1,1)`.  That is a mutation-sensitive diagnostic,
not an authorized repair.  Off-diagonal field mixing would likewise change
the declared row carrier rather than repair its fixed pairing.  A repair must
change and re-certify the carrier or regenerate the coupled unary and binary
operations from one pairing.

The first persistent falsifier stops the calculation before later memory
rows; they are not marked as passed.  Arity three, `K_Berger`, observer
morphisms, detector response on the second-order cone, nonlinear rank,
physical Bridge 3 and every quantum promotion remain fail-closed.

Machine-readable certificate:
`closed_universe_observers/certificates/BERGER_108_ROW_TEMPORAL_COMMON_ACTION_WARD_ORBIT_OBSTRUCTION.json`.
