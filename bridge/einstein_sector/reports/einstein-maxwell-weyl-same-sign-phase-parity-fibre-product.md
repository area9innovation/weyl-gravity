# Same-sign phase/parity fibre products

The six candidate bounded cones now have exact necessary-and-sufficient
equational descriptions.  For candidate (i=16,\ldots,21), let

- `pi_i` be the six-node absolute-current occupation map;
- `C_i` be its certified four-ray `H/Px/Rc` zero cone;
- `mu_J` be the three lifted rotation moment maps; and
- `B_i` be the complete cross-fibre resonant phase/parity map.

Then

```text
Z_i^bounded = pi_i^{-1}(C_i) intersect mu_J^{-1}(0) intersect V(B_i).
```

The equality is necessary and sufficient because the finite-harmonic
adjoint-cokernel theorem exhausts bounded obstructions, while the exact
same-fibre census makes every other nonzero-frequency block removable.  The
complex varieties `V(B_i)` are already decomposed for all six candidates:
candidate 16 has one dimension-12 component, 17 and 20 one dimension-14
component each, 18 one dimension-22 component, 19 six components, and 21
four components.

This closes the equational-formula gate but not the real Hermitian geometry.
The remaining task is to intersect those complex resonance components with
the nonnegative norm cone and the three rotational zero levels, then classify
the resulting real components and singular strata.

## Verification receipt

- Tier 0: Python/JSON parsing and scoped `git diff --check`.
- Tier 1: deterministic producer, independent verifier, and two unit tests.
- Tier 2: content-addressed composition of the finite-harmonic cokernel
  theorem, six scalar cones, six cross-fibre zero-variety decompositions,
  the 864-defect same-fibre census, and the bounded section theorem.
- Tier 3 is not run because no lifecycle state is promoted and the real
  component decomposition, all-orders integration, causal correction and
  higher interpretations remain open.
