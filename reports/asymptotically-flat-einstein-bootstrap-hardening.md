# Asymptotically flat Einstein bootstrap hardening receipt

Date: 2026-07-15

## Exact operator premise

The new flat TT certificate derives rather than assumes the reduced
linearized Bach equation.  For an off-shell two-polarization perturbation on
four-dimensional Minkowski space with signature `(-,+,+,+)`, exact tensor
algebra verifies

```text
tr(h)=0,
div(h)=0,
R_1=0,
Ric_1=-Box h_TT/2,
tr(C_1)=0,
B_1(h_TT)=-(1/4) Box^2 h_TT.
```

The resulting polarization operator commutes exactly with the helicity
generator.  The certificate distinguishes the geometric Bach normalization
from any nonzero action-level rescaling, which does not change the equation
kernel.

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

## Interpretive repairs

The asymptotic bootstrap now distinguishes:

1. algebraic substitution `q=0` in the homogeneous Fourier oscillator;
2. the zero-frequency soft/memory limit of radiative data; and
3. Coulombic mass and angular-momentum aspects at null infinity.

The matrix intertwining identity is polynomial and remains exact at `q=0`,
but the homogeneous plane wave is normally inadmissible under asymptotically
flat spatial falloff.  No soft or Coulombic theorem is inferred from it.

The earlier single candidate topology is split into a finite-flux `L2` rail,
a strong `L1 intersect L2` scattering core with endpoint shear, and an open
soft/memory completion.  No density or completion theorem is promoted.

Physical Weyl transformations of `g` are now distinct from rescalings of the
unphysical compactification pair `(g_tilde,Omega)`.  Their boundary
intersection remains open pending a zero-charge boundary map.

## Machine contract

The bootstrap certificate now binds the flat TT operator certificate by
SHA-256 and declares a versioned JSON schema.  Every `AF-E1` through `AF-E8`
row carries its partial-receipt tag and requires `LORENTZIAN-CAUSAL` for full
closure.  The manual contract validator fails on unknown tags, missing or
reordered obligations, and any unsupported full-claim promotion.

All full asymptotic flags remain false.

## Provenance

Classical input commit:
`439a8e6bcc42a2458a7e1adf96ff0a5bb0dcac78`.

New or changed scoped artifacts:

- `bridge/einstein_sector/flat_tt_bach.py`;
- `bridge/certificates/flat_tt_bach_operator.json`;
- `bridge/einstein_sector/asymptotic_bootstrap.py`;
- `bridge/einstein_sector/schema/asymptotic_bootstrap.schema.json`;
- `bridge/certificates/asymptotically_flat_einstein_bootstrap.json`;
- associated tests and the asymptotic bootstrap note.

## Verification

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0 | `python3 -m py_compile bridge/einstein_sector/flat_tt_bach.py bridge/einstein_sector/asymptotic_bootstrap.py bridge/einstein_sector/tests/test_flat_tt_bach.py bridge/einstein_sector/tests/test_asymptotic_bootstrap.py` | 0.03 s | PASS |
| 0 | `python3 -m json.tool` on the schema and both generated certificates | 0.08 s | PASS |
| 1 | `python3 -m bridge.einstein_sector.flat_tt_bach --verify bridge/certificates/flat_tt_bach_operator.json` | 0.44 s | PASS |
| 1 | `python3 -m bridge.einstein_sector.asymptotic_bootstrap --verify bridge/certificates/asymptotically_flat_einstein_bootstrap.json` | 0.33 s | PASS |
| 1 | `python3 -m unittest discover -s bridge/einstein_sector/tests -p 'test_*.py'` | 0.80 s | PASS (12 tests) |

Tier 2 was limited to the affected new certificate chain: flat TT operator to
asymptotic bootstrap.  Existing cylinder, residual, and quantum inputs were
unchanged and checked by their recorded content hashes and scope fields.
Tier 3 was not run because no paper theorem, quantum lifecycle state, shared
core algebra, freeze, tag, or release was promoted.

## Concurrent work

The shared tree contained unrelated paper-split, quantum local-BV/transfer,
medical, workflow, and backgammon changes.  None is included in this receipt
or its intended commit.
