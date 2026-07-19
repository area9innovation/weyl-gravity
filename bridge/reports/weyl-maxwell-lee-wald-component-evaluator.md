# Component-complete Lee--Wald evaluator

The action-derived Einstein--Maxwell and Weyl--Maxwell Lee--Wald evaluator now
exposes every vector-density component.  The existing `*_current_time`
functions remain exact wrappers for component zero, so all existing fixtures
retain their public interface and normalization.

The new entry points are:

```text
weyl_maxwell_current_component(..., component, alpha_b=3)
einstein_maxwell_current_component(..., component, kappa=1)
```

All four components use the same curvature-momentum variation, including the
variation of the covariant divergence of the Weyl momentum.  Component bounds
are fail-closed.  This is an executable local-current prerequisite; it does
not by itself certify the relative Noether divergence cone or a causal
homotopy.
