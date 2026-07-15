# Anomalies

`ghost_number_1/ANOMALY_CANDIDATES.json` contains the Weyl-ghost lifts of the
generated dimension-four curvature densities.  `omega Box R` has an explicit
primitive and local current in `../local_bv/certificates/TRIVIALITY_CERTIFICATE.json`.
The file does not claim
complete `H^{1,4}(s|d)`, anomaly coefficients, cancellation, or QME status.

All candidates reference their generated four-step universal Diff tower in
`../local_bv/descent/DESCENT_DATABASE_DIMENSION_FOUR.json`.  A separate
`intrinsic_weyl_descent_status` records type-B triviality, the explicit
type-D primitive, or the pending type-A continuation.  The Euler
variational current and the nonzero first `omega E4` residual are certified;
the two ordinary-bidegree connecting equations are now exact in the frozen
Euler carrier algebra.  The status remains `IN_PROGRESS` until the
epsilon-contracted carrier head is independently identified with the frozen
`omega E4` tensor representative.
