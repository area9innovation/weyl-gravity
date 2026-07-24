# Bplus4 bounded chunk 03 refusal

This package records one bounded attempt to resume the content-addressed
chunk-02 checkpoint. The source probed a `7/32`, order-168 primary panel
before a `5/32`, order-120 pre-tail fallback.

Compilation succeeded, but the executable reached its 42-second runtime
limit before emitting any boundary diagnostic. The attempt therefore stops
at the first genuine gate. No selected branch is inferred, no successor
checkpoint is serialized, and no direct sixteen-state validation is claimed.

The generated Forge source and raw stdout are not retained. Their
content-addressed descriptor and the empty-output boundary are recorded in
the compact run manifest.

Full `r=4`, `Bplus4`, `T_plus`, and Stokes claims remain false.
