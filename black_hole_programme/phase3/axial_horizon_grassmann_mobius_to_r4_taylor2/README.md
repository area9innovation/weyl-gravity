# Axial horizon Grassmann/Möbius Taylor2 q0 consumer

This sibling package imports the frozen affine q0 horizon consumer by exact
path, commit, and SHA-256.  It lifts the affine initializer and every local
transition with `ivtm_from_affine`, then performs the Grassmann chart,
right-action solve, rebase, amplitude, covariance, overlap, and rank work with
the degree-two shared-parameter Taylor matrix kernel pinned at Tango commit
`972aa4337b73cc0f632d9599fb345098bc8ccce8`.

The first sentinel is intentionally limited to q0 =
`[1/2,2049/4096]`.  It preserves the 20 charts, 23 exact dyadic shells, 256
panels per shell, separate amplitude rail, real rank-six certification on a
64-cell frequency cover, and chart norm bound two.

Dependency tag: `LOCAL-ALGEBRAIC`.

This package does not establish a horizon-to-infinity connection, scattering,
flux sign, stability, ghost, positivity, CPT, unitarity, or any
`LORENTZIAN-CAUSAL` quantum result.

Render and compile against a library snapshot extracted from the pinned Tango
commit:

```bash
PYTHONPATH=. python3 -m \
  black_hole_programme.phase3.axial_horizon_grassmann_mobius_to_r4_taylor2.produce
FORGE_LIB=/tmp/forge-972aa4337/forge/lib forge \
  -o /tmp/axial-horizon-taylor2-q0 \
  black_hole_programme/phase3/axial_horizon_grassmann_mobius_to_r4_taylor2/transport_c00_taylor2.forge
```
