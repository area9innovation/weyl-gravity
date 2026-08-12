# Exact finite-graph wave causality

**Result:** `FOUNDATIONAL_FINITE_GRAPH_WAVE_CAUSALITY_V1`

## Result

A rational nearest-neighbour wave recurrence has exact retarded and advanced kernels on three finite graph fixtures. The retarded kernel at step `n` vanishes beyond graph distance `n-1`; the advanced kernel is the time-reversed transpose.

The checker covers **3 fixtures**, **16 vertices**, **23 kernel steps**, **491 recurrence entries**, and **663 adjoint entries**, with **0 support violations**.

## Why this is causal only in the finite-discrete sense

The result supplies an exact graph-step domain of dependence. It does not identify graph distance with a Lorentzian metric, prove convergence as a mesh is refined, or turn a Lieb–Robinson tail into strict continuum support.

## Reproduction

```text
python3 foundations/build_finite_graph_wave_causality.py --check
python3 foundations/check_finite_graph_wave_causality.py
python3 foundations/verify_finite_graph_wave_causality.py
```

## Boundaries

- This does not establish continuum finite propagation.
- This does not establish a Lorentzian advanced or retarded Green operator.
- This does not establish CFL stability or convergence under refinement.
- This does not establish a regulator-independent continuum limit.
- This does not establish a Weyl metric BV propagator.
- This does not establish a reverse-mathematical classification of continuum PDE.
