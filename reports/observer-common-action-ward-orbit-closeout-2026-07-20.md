# Observer close-out: temporal common-action Ward orbit

Work item: `sf:program/work/observer-common-action-ward-orbit`

Owner: observer

Input commit: `3d0ed702a78db160ec8f80ab0efa53dd2dbe2d0b`

## Stop-condition audit

The exact common-action branch closes negatively on the present 108-row
carrier.

| Requirement | Evidence | Disposition |
| --- | --- | --- |
| Common-action `q1/q2` export | `BERGER_108_ROW_TEMPORAL_COMMON_ACTION_WARD_ORBIT_PAYLOAD`, SHA-256 `917753ba31ea5cbf3b8ba54634af968ad1bd4ca20249d43fba60936d17cd0b32` | Five exact `q1` and five exact `q2` temporal-orbit fixtures are exported with their source hashes and declared action sectors. |
| One raising pairing | same payload | `OBSTRUCTED`: the scale matrix `[[1,0,-2],[1,-1,0],[0,1,-1]]` has determinant `-1`, rank `3`, and nullity `0`. |
| Independent verifier | `closed_universe_observers/verify_berger_108_row_temporal_common_action_ward_orbit.py` | Recomputes the determinant, mutation, dependency hashes, schemas and source-isolated PBW witness without accepting the producer's conclusion as input. |
| Decisive mutation | payload `factor_two_mutation` | Replacing the imported Maxwell factor two by one makes the matrix singular with null vector `(1,1,1)`. This is explicitly mutation-only, not a fitted repair. |
| Prior residual comparison | certificate `persistent_witness`, SHA-256 `cb92da25ca1b075c6fa5e60c8bb2cf9476fbf1637675bc6f3db506e8aef44cbe` | The first witness remains `tau_star <- (e0 e1 A_0,K0_01)` with coefficient `+g0 h0`, byte-identical on its comparable fields to the prior obstruction. |
| Assembly-only alternative | payload `action_equivalent_presentation_mutation` | Replacing `q2_typed` by the imported action-equivalent presentation `S q2_typed` leaves the witness nonzero. |
| Fail-closed atlas | `observer.berger.interaction.temporal_common_action_carrier_obstruction`, fragment SHA-256 `8b9af0ef114d8becf28d41f7164e00f4325de9212d6a6ccfc5f7dbb570788602` | Interaction and symplectic columns are `OBSTRUCTED`; detector and tangent-cone promotions are `NO_CERTIFIED_MAP`. |

## Scientific disposition

The typed Maxwell temporal Ward orbit requires

```text
s_Maxwell = 2 s_tau,
```

while the switched Maxwell-emitter Hessian and temporal emitter-Diff orbit
require

```text
s_Maxwell = s_emitter = s_tau.
```

No nonzero scale vector satisfies all three equations. This is a genuine
normalization incompatibility within the component-preserving pairing family
of the present frozen carrier. Off-diagonal field mixing, a changed Maxwell
factor, or a different action normalization would define a new carrier or
action and must be separately generated and certified.

The first falsifier fires at `tau_star`, so later memory rows are recorded as
not evaluated rather than passed. The result does not authorize arity three,
`K_Berger` equivariance, observer-morphism stability, detector response on the
second-order cone, nonlinear rank, physical Bridge 3, finite-parameter
causality, or a quantum claim.

## Next recommendation

The smallest honest successor is a typed carrier/action-normalization
diagnosis followed by regeneration of both `q1` and `q2` from one declared
pairing. The deferred observer Conflux ticket may begin only through its own
typed-import reproduction gate; Conflux was not used for this work item.

CLOSE-OUT: OBSTRUCTED — the exact no-go or first obstruction is certified
EVIDENCE: closed_universe_observers/certificates/BERGER_108_ROW_TEMPORAL_COMMON_ACTION_WARD_ORBIT_OBSTRUCTION.json
