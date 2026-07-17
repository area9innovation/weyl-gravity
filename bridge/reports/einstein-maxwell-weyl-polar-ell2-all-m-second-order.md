# All-m polar ell=2 second-order cone

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

The complete polar `ell=2,k=0` block contains the Einstein `q` primary and
both extra `p` primaries.  For arbitrary `m`, its quadratic product has polar
outputs at even `L=0,2,4` and axial outputs at odd `L=1,3`.

The only physical zero-frequency adjoint pairings are the constant-lapse
Hamiltonian charge at `L=0` and the rotation triplet at `L=1`.  They vanish on
the common-zero cone `H=J_i=0`.  The remaining zero blocks and every nonzero
sum/difference-frequency block are invertible.  Five direct Hermitian
fixtures give a rank-one source matrix.  In the
`(plus,minus,extra-e1,extra-e2)` basis its scalar columns are

```text
-864(11+7 sqrt(3))/5,
 864(-11+7 sqrt(3))/5,
-12/5,
-29952/5,
```

all multiplying `(1,0,1/2,0)`.  The two extra polarizations have zero
off-diagonal source.  These coefficients agree with the declared
Lee--Wald basis normalization.

Therefore every finite real pure-polar `ell=2,k=0` common-zero tangent admits
a complete second-order correction.  This does not yet combine axial and
polar inputs: their cross terms have the opposite output-parity pattern and
remain the next gate.

## Verification receipt

Date: 2026-07-17.

* Tier 0: scoped `py_compile`, `0.04 s`, passed.
* Tier 1: four certificate replays, `2.69 s`, passed.
* Tier 1: five independent verifiers plus 13 unit tests, `3.11 s`, passed.
* Tier 2: full four-dimensional Einstein-minus polar source replay,
  `840.06 s`, passed.  The other four Hermitian entries were produced by the
  same direct generator in the preceding batch and are checked by the
  independent rank/conjugacy verifier.
* Tier 3 was not run: no shared core operator or programme-wide freeze was
  changed; the affected certificate chain and its direct source audit were
  run instead.
