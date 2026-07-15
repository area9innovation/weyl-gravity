# Anomalies

`ghost_number_1/ANOMALY_CANDIDATES.json` contains the Weyl-ghost lifts of the
generated dimension-four curvature densities.  `omega Box R` has an explicit
primitive and local current in `../local_bv/certificates/TRIVIALITY_CERTIFICATE.json`.
The file does not claim
complete `H^{1,4}(s|d)`, anomaly coefficients, cancellation, or QME status.

All candidates reference their generated four-step universal Diff tower in
`../local_bv/descent/DESCENT_DATABASE_DIMENSION_FOUR.json`.  A separate
`intrinsic_weyl_descent_status` records type-B triviality, the explicit
type-D primitive, or the type-A continuation.  For `omega E4`, the
variational current, nonzero first residual, ordinary-bidegree connecting
equations, terminal closure, and Lorentzian epsilon-contracted head are now
independently certified.  Its intrinsic status is `NONTRIVIAL_COMPLETE`.
Its relative BV class remains `UNDECIDED`: descent completion is not a
nontriviality proof in `H^{1,4}(s|d)`.
