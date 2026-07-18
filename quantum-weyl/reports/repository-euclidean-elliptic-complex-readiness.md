# Repository Euclidean elliptic-complex readiness

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

The missing full Euclidean elliptic-complex gate now has an executable
symbol-level receiver. For every nonzero cotangent vector, reduced to one
`SO(4)` representative, it requires exact sparse incoming and outgoing
principal-symbol matrices. The receiver independently recomputes:

- zero adjacent-symbol composition;
- exact rational ranks;
- equality of incoming image and outgoing kernel;
- nonzero principal scalars for every gauge-fixed kinetic block;
- complete minimal, nonminimal, auxiliary, and symbol-sector coverage;
- formal-adjoint, gauge-fixing, multiplicity, normalization, and snapshot
  proof roles.

The current round-`S4` full-BV multiplicity ledger is a reduced determinant
ledger, not this full covariant symbol sequence. The local gauge-fixed BV
contraction contains the algebraic cohomology data but not an analytic
ellipticity proof. Nariai is a Lorentzian classical complex, and the standard
TT auxiliary identity covers only one physical block. None is silently
promoted.

The synthetic exact sequence tests receiver mechanics and rejects nonzero
composition, false rank, zero-principal-scalar, out-of-bounds sparse
coordinates, and digest mutations. It is not evidence that the physical
Weyl-gravity complex is elliptic.

## Verification

```bash
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.elliptic_complex_readiness --check
PYTHONPATH=quantum-weyl python3 -m spectral.euclidean.verify_elliptic_complex_readiness
PYTHONPATH=quantum-weyl python3 -m unittest spectral.euclidean.tests.test_elliptic_complex_readiness
```
