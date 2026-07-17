# Berger rank-46 STF2 branch-projector solver contract

The landed cyclic graph carrier is now a complete input to a scoped binary
projector calculation.  The independent ansatz is a constant `15 x 15`
Einstein block in graph coordinates: 225 coefficients over `Q(sqrt(10))`.
The exported projector is obtained with the exact cyclic graph shear and has
PBW order at most two.  Degree-one, ghost and ghost-dual entries are forced by
the typed cyclic-adjoint and `q1`-intertwining equations rather than fitted as
independent `46 x 46` operator blocks.

The two-helicity anchor is no longer a declaration of this contract.  It is
imported from the exact transverse-traceless projective-module certificate,
which keeps the full six-dimensional null-symbol cohomology visible and
distinguishes the rank-two polarization module from the rank-four generalized
repeated-wave module.

The solve is ordered: principal symbol/idempotence, lower-order chain and
cyclic completion, then real and `K_Berger` equivariance.  The result must be
either exact complementary Einstein-like/extra-Weyl projectors or a normalized
dual obstruction at the first failed stage.  A success still does not
authorize an `ell3` mixing table until the nonlinear lift is materialized.
