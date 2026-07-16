# Einstein–Maxwell standard-harmonic inclusion in Weyl–Maxwell theory

Dependency boundary: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`. Lifecycle: `CLASSIFIED`.

The certificate
`bridge/certificates/einstein_maxwell_weyl_standard_harmonic_symplectic_inclusion.json`
assembles four independently verified pullback calculations. On the complete
certified fixed-bundle standard Einstein–Maxwell harmonic tangent of
`R_t x S1_L x S2`, before the final residual `SO(4,2)` quotient, the
Weyl–Maxwell pullback is nondegenerate.

The blocks are:

- standard axial and polar `ell>=2` radiation: nondegenerate, with relative
  coefficient signature `(2,2)` per real spatial harmonic;
- physical axial and polar `ell=1`: exactly `4 Omega_EM` in normalized quotient
  coordinates;
- homogeneous `(a,b,c,d,Q_e,W_x)`: an invertible unipotent shear
  `R=I+N`, `rank N=2`, `N^2=0`, with an explicit `S=I+N/2` satisfying
  `S^T Omega_EM S=Omega_WM`;
- the three axial `ell=1` generalized twist pairs: exactly `-2 Omega_EM`.

Consequently no certified standard Einstein–Maxwell tangent direction becomes
a presymplectic null direction in the target at this stage. This does not make
the identity solution inclusion symplectic, nor does it prove equality of the
theories. Extra fourth-order Weyl–Maxwell branches, nonlinear closure, extension
of observables off the Einstein subspace, the final residual quotient, and
asymptotically flat scattering remain separate gates.

The graviton interpretation is correspondingly precise: the conventional
radiative oscillator blocks are present and nondegenerately paired before the
final global quotient. A vanishing one-particle residual cohomology after that
quotient is not a statement that asymptotically flat gravitational radiation
does not exist.

Verification:

```text
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_standard_harmonic_symplectic_inclusion --verify bridge/certificates/einstein_maxwell_weyl_standard_harmonic_symplectic_inclusion.json
python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_standard_harmonic_symplectic_inclusion.py
python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_standard_harmonic_symplectic_inclusion
```

Receipt (2026-07-16): Tier 0 Python compilation, JSON parsing, and scoped
`git diff --check` passed. Tier 1/affected-chain replay passed: the homogeneous
direct current took 12.34 s, the twist direct current took 9.62 s, and the
26-test restriction suite took 1.50 s. The three independent verifiers passed.
Tier 3 was not run because no shared core algebra, freeze, release, or theorem
lifecycle promotion changed; the unchanged current engine is imported by hash.
