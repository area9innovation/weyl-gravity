# Axial partial-jet spin-one Levelt horizon v1

This package completes the local three-channel horizon initializer on the
first frequency child.

The spin-one companion state is replaced by

\[
\widehat Z=\operatorname{diag}(\rho,\rho^2)Z.
\]

For the selected spin-one column the spin-two rows are also scaled by
\(\widehat X=\rho X\), \(\widehat Y=\rho Y\).  The resulting four-state base
system is regular singular and the intrinsic tangent is regular.

An order-one resonance is compatible: its base and tangent residuals vanish,
so no logarithm is forced.  Five exact recurrence orders and an all-order
tail majorant initialize the selected mixed column at \(\rho_0=2^{-22}\).
The tail-enclosed column is propagated across the first panel using shared
`IvTaylor4_omega tensor dual_tau`; the direct six-state and partial-jet
routes agree.

Multipanel transport, \(K_H\), \(T_+\), H4, and global scattering remain
fail closed.
