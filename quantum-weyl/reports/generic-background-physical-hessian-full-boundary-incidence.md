# Generic physical-Hessian full boundary incidence

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

The six ordered `H1^3` triangle corner rows and all six endpoints of the three
`H1-H2` contacts are now assembled as exact generic rational functions of
`(x1,x2,x3)`.  Their sum is nonzero.  Consequently algebraic `H2`
cancellation is refuted generically, and the `M14` corner is disposed as a
nonzero scale row renormalized by the already-certified common Mellin
extension—not as a cancellation.

The exact equal-box TT replay remains

```text
-1975/72 + 2704/27 = 15707/216.
```

The `I28` relation vanishes separately in the triangle, contact and combined
generic rows.  Finite local terms and the complete physical form factors are
still open, so this result does not alter the anomaly/QME or Lorentzian claim
boundary.

Replay:

```text
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.generic_background_physical_hessian_full_boundary_incidence --check
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_generic_background_physical_hessian_full_boundary_incidence
PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_generic_background_physical_hessian_full_boundary_incidence
```

The exact regeneration check took `1.53 s` and the independent consumer
`0.37 s` on the producing workstation. Tier 3 was not run under the same
criterion: finite local rows, QME, residual transfer and Lorentzian states all
remain fail-closed.
