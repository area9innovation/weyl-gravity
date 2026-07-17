# Typed coupled Maxwell q2 and mixed q3

The exact mixed gravity--Maxwell arity-three operation is now exported on all
64 gauge-fixed BV rows.  It contains **59,598** PBW
coefficients in 21 nonzero output rows and has maximum
total jet order 4.

The factor-two arity-two repair is now typed correctly.  With
`S=diag(I54,2 I10)`, the nonlinear presentation uses
`Omega_typed=Omega_legacy S` and `q2_typed=S^-1 q2_legacy`; hence the lowered
cubic tensor is unchanged.  This matters at q3 because output scaling alone
does not commute with coderivation composition.

The mixed operation is derived from the fourth Maxwell action derivative and
the finite BV-canonical ghost shear.  Exact row-bounded replay proves the
mixed part of `q1 q3+q2 q2=0` on every row.  Retained transfer and independent
quantum acceptance are separately versioned downstream gates and are not
promoted by this artifact.
