# Anomalies

`ghost_number_1/ANOMALY_CANDIDATES.json` contains the Weyl-ghost lifts of the
generated dimension-four curvature densities.  `omega Box R` has an explicit
primitive and local current in `../local_bv/certificates/TRIVIALITY_CERTIFICATE.json`.
The historical candidate file does not itself claim a quotient theorem. The
successor gauge-fixed result now completes `H^{1,4}(s|d)` on the regular Bach
locus with even/odd dimensions `2/1`. The assembly preflight at
`certificates/REGULATED_SLAVNOV_BREAKING_ASSEMBLY_PREFLIGHT.json` binds that
quotient to the known standard background even coefficient vector while
keeping repository coefficient matching, cancellation, and QME status open.

All candidates reference their generated four-step universal Diff tower in
`../local_bv/descent/DESCENT_DATABASE_DIMENSION_FOUR.json`.  A separate
`intrinsic_weyl_descent_status` records type-B triviality, the explicit
type-D primitive, or the type-A continuation.  For `omega E4`, the
variational current, nonzero first residual, ordinary-bidegree connecting
equations, terminal closure, and Lorentzian epsilon-contracted head are now
independently certified.  Its intrinsic status is `NONTRIVIAL_COMPLETE`.
Its relative BV class is nontrivial in the completed gauge-fixed quotient;
descent completion alone was not the proof, and the historical candidate
record remains an immutable earlier receipt.
