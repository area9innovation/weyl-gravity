# Two-interface foundations cube v6

**Result:** `FOUNDATIONAL_INTERSECTION_CUBE_V6`

**Lifecycle:** `CROSS_CELL_INTERFACES_CERTIFIED`

## Outcome

Cube v6 preserves all 452 v5 coordinates, all migration fields, and the
finite-corner state-to-probability bridge. It adds a second certified
`CONDITIONAL_BRIDGE`, from physical state selection to generator/spectral
dynamics on the identical free Krein--Fock carrier.

Both endpoint cells were already local results, so no coverage grade changes.
The surface remains at **89 local-result**,
**93 literature-result**,
**159 pieces-only**, **30 gaps**,
and **81 not-mapped** emitted cells. What changes is
object-level composition: the free energy uniquely selects the normal
zero-energy vacuum state and the generated dynamics fixes it.

## Reproduction

```text
python3 foundations/refine_intersection_cube_v6.py --check
python3 foundations/check_refined_intersection_cube_v6.py
python3 foundations/verify_refined_intersection_cube_v6.py
```

## Boundaries

- This does not establish state-to-dynamics composition outside the certified free reduced-mode Fock system.
- This does not establish that stationarity alone uniquely selects a state.
- This does not establish an interacting, thermal, Hadamard, BRST-compatible, or thermodynamic state.
- This does not establish cross-cell composition for the other five assembly interfaces.
- This does not establish causal response, a prediction chain, or empirical agreement.
- This does not establish a complete physical theory or Lorentzian completion.
- This does not establish literature completeness or coherence of unassessed coordinates.
