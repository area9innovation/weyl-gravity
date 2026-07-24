# Correlated affine/Taylor export audit

Dependency tag: `REDUCED-MODE`

Status: `RERUN_FROM_SYMBOLIC_SEED_REQUIRED`

The last accepted checkpoint and the terminal pre-normalization enclosure do
not retain a correlated affine or omega-Taylor state. The transport is issued
at the single exact frequency `4097/8192`. Each seed coordinate is inflated
into an independent complex ball, each radial Taylor step keeps its
coefficients only as local temporaries, and each accepted step serializes only
the resulting Cartesian balls. Equal printed radii are not shared remainder
symbols.

Consequently no rigorous affine pivot or successor step can be reconstructed
from panel 30, panel 31, or the nine later shared-reciprocal checkpoints
without inventing correlations that the artifacts do not certify.

The earliest required restart is the symbolic mixed Levelt seed at
`rho=1/4194304`, before `seed_vector`, initial projective normalization, and
the substitution of the fixed frequency in `RationalFunction`. The new export
must retain:

- a declared omega Taylor coordinate, radius, and order for the reduced
  moving-phase amplitude;
- base and intrinsic tau-tangent polynomials sharing the same affine noise
  symbols;
- a coupled vector residual in a declared norm;
- radial Taylor coefficients or a content-addressed exact replay sufficient
  to reconstruct them;
- chart, reciprocal, and normalization operations acting on the complete
  correlated representation;
- a content hash covering the parent, generator, polynomial, affine
  generators, noise domain, residual, and chart.

Only after that regeneration may a fixed row be certified nonzero over the
correlated set and one transformed successor substep attempted.

This result does not say that the true transported line contains zero, and it
does not establish an obstruction for a stronger correlated enclosure. It
does not certify a successor step, transport to `r=4`, H4, `T_+`, a Gram or
Stokes identity, or any `LORENTZIAN-CAUSAL` theorem.
