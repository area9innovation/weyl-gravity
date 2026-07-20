# Science Forge observer-stream cutover

Date: 2026-07-20

## Disposition

The `observer` stream is accepted as the second authoritative Science Forge
stream in this programme. The black-hole stream remains authoritative. The
bridge, classical, nonlinear, and quantum-qme streams remain in shadow mode
until a programme-wide acceptance run is recorded.

This cutover adopts the `s-f` coordination surface only. It does not adopt
Conflux for observer work and does not certify a scientific claim.

## Clean-snapshot acceptance

The acceptance run copied the committed `planning/` tree to
`/tmp/sf-observer-cutover.yicA6z` and operated only on that copy. It used the
production `/home/alstrup/.local/bin/s-f` launcher and a sixth configured
`observer` stream.

The following checks passed:

1. `s-f work new` created the new observer successor as a stable immutable
   item.
2. `s-f work ready --stream observer` returned exactly that item.
3. The first exclusive `work pull` succeeded and emitted a complete brief.
4. A second exclusive pull by a different agent was refused with exit code 7.
5. `work report` accepted the complete checkpoint field set.
6. A six-stream coordinator view displayed the observer item, its live lease,
   and its last report.
7. `import-program` accepted the copied programme with 66 nodes, zero invalid
   items, and zero malformed events.

The live programme then created
`sf:program/work/observer-common-action-ward-orbit`. At creation time it was
`READY`, had no unresolved dependency, and was not leased.

## Scientific successor

The previous nonlinear-clock work item closed through its exact-obstruction
branch. It is not reopened. The new item asks the observer team to re-export
the temporal gravity-clock-Maxwell-emitter `q1/q2` Ward orbit from one declared
action and decide whether the certified arity-two residual is:

- an assembly mismatch that disappears in the common-action export; or
- a genuine incompatibility of the present carrier, witnessed independently.

The item explicitly forbids Conflux, fitted cancellation, and promotion to
`q3`, detector physics, causal physics, branch physics, or quantum claims.

## Boundary

This receipt establishes stream-level task coordination. It does not establish
the Ward identity, resolve the observer obstruction, validate Conflux on
observer inputs, or authorize programme-wide Science Forge cutover.

