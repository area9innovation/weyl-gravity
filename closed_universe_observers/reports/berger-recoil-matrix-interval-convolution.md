# Berger recoil matrix interval convolution

`BERGER_RECOIL_MATRIX_INTERVAL_CONVOLUTION` lifts the scalar finite-slab
Volterra engine to complex interval vectors and square interval-matrix kernel
polynomials.  Every stage checks dimensions, applies the exact beta-integral
coefficient, and propagates source-vector and kernel-operator remainders in
the induced infinity norm.  A sparse-to-dense adapter consumes the certified
finite sine-kernel enclosure directly.  A companion callable encloses pointwise
multiplication by a real switch-cell interval.

The exact fixture sends the constant vector `(1,2)` through `diag(1,2)` and
then the identity kernel, producing the `x^2` coefficient `(1/2,2)`.
Dimension mismatches and acausal orientations fail closed.

This is the execution layer required to combine finite Berger kernel matrices
with form-valued profiles.  The detector polynomials, exact spacetime
`d/delta` matrices and emitter Cauchy coefficients are not yet bound, so no
physical `I_abc` or recoil record is claimed.
