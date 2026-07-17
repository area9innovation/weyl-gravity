# Independent acceptance of the typed Berger mixed q3

The quantum-side consumer independently accepts the portable classical mixed
gravity--Maxwell `q3` at commit `ba51c385`.  It does not import or execute the
classical producer.  A two-rational-component exact backend reconstructs the
portable unary, gravity `q2`, typed mixed `q2`, and all 59,598 mixed `q3` PBW
coefficients.

The all-row mixed part of `q1 q3 + q2 q2 = 0` vanishes coefficientwise on all
64 rows.  The typed `q2` and `q3` graded-symmetry defect counts are zero.  As a
fail-closed negative control, changing one exact `q3` coefficient creates two
nonzero defect coefficients.

This is a `LOCAL-ALGEBRAIC` classical-input acceptance.  It is not a quantum
master-equation result.  The next interaction gate is the retained `ell3`
transfer, including the homological exchange contribution built from
`q2 S q2`; neither term may be omitted or inferred from the full-complex
identity.

The acceptance is pinned to the committed coefficient payload at
`ba51c385`. A later typed-pairing carrier refinement may be adopted by the
retained transfer without changing this coefficientwise full-complex replay;
the transfer must nevertheless pin that final carrier before evaluating its
contact and exchange terms. The certificate passes independent replay,
mutation tests, and strict AJV Draft 2020-12 validation.
