# Nariai parent-detour mapping-cone repair

## Result

The obstructed 288-component multiplier saddle is replaced by an economical
310-component cyclic parent-detour cone.  It adds only the eleven-dimensional
complement of the metric ghost splitting and its dual.  In split variables,
the complex is the direct sum of the metric Bach complex, the pointwise pair
`epsilon_perp -> s`, and the parent saddle

```text
[[ -(1/2) M^D, 1 ],
 [       1,     0 ]].
```

Its exact inverse is `[[0,1],[1,(1/2)M^D]]`; it is a finite-order local
operator, not an inverse of `M^D`.

## Coefficient checks

- rank `p0`: `4`;
- dimension `ker p0`: `11`;
- `p0 J0`: rank `0`;
- `g J0-1`: `0` entries;
- `J0 g-(1-L0 p0)`: `0` entries;
- reconstructed gauge arrow `d J0 g+L1 k-d`: `0` entries;
- `M L1-Phi`: `0` entries;
- effective Hessian minus `B_action`: `0` entries.

## Cyclic SDR

The serialized ten-block matrices verify `Q^2=0`, odd cyclicity, `PI=1`, both
chain-map identities, the exact retract identity

```text
1-IP = QH+HQ,
```

and odd cyclicity of `H`.  The triangular field transform and its forced
cotangent transform are mutually inverse and BV canonical.  Therefore the
same identities hold in the original parent/metric graph coordinates.

## Boundary

This is a local cyclic deformation retract on the unit Nariai background.
It is not a retarded/advanced Green construction.  The next gate is
`C_G2_NARIAI_REPAIRED_PARENT_GREEN_TRANSFER`.
