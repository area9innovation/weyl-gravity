# Axial Weyl--Maxwell extra-module import

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

Lifecycle state: `CLASSIFIED`

## Result

The quantum nonlinear programme now imports the classical team's complete
generic axial `ell>=2` Weyl--Maxwell operator, its reduced and ungauged local
Green currents, and the pairing on the two extra algebraic solution summands.
The import is pinned to classical snapshot `e2b7e20b` and independently
replays the formal adjoint, Hessian determinant, Smith factors, both extra
kernel representatives, both off-shell Green identities, and the normalized
pairing determinant. It also replays the direct four-dimensional Lee--Wald
samples at `ell=2,3,4`, their generic spectral interpolation, and the complete
Einstein/extra pairing decomposition.

On the shell

```text
omega^2=k^2+lambda-2/3
```

the extra module is `(F[omega]/(p))^2`. Its normalized reduced-Hessian Green
pairing has

```text
det N_extra=lambda^4*(lambda-2)*(9lambda-2)/3
signature=(2,0), lambda=ell(ell+1)>=6.
```

Thus the extra branch is not a radical of this reduced current. In ordinary
language, the repository now has a certified linearized sector in which
metric and Maxwell perturbations are coupled and the Weyl--Maxwell equations
contain two additional axial algebraic polarizations beyond the
Einstein--Maxwell image.

The direct compact Lee--Wald match is now certified. The Einstein and extra
blocks are symplectically orthogonal; the extra block has signature `(2,0)`,
the Einstein image has `(1,1)`, and the complete generic axial block has
signature `(3,1)`. In this convention the negative direction belongs to an
Einstein-image master branch, not to either new extra direction.

This is still not interacting light. No mixed gravity--photon `q2` or `q3` has
been transferred, and no final residual or causal boundary selection exists.
Consequently the direct classical signature is not promoted to a
positive-frequency particle norm, ghost verdict, causal scattering state, or
quantum-unitarity statement.

## Next gates

1. Import a support-local mixed gravity--Maxwell `q2/q3` block and transfer it
   through the certified contraction.
2. Perform final residual descent and test causal boundary admissibility of
   the extra primary factor.
3. Only after causal/Hadamard and QME gates close, ask for photon scattering or
   a quantum particle interpretation.

## Verification

| Tier | Command scope | Elapsed | Result |
|---:|---|---:|---|
| 0 | Python compilation, JSON parsing, and scoped `git diff --check` | <1 s | PASS |
| 0 | Strict Draft 2020-12 AJV validation of the import schema | 1.31 s | PASS |
| 2 | Import, Møller, decomposability, aggregate, independent verifiers, and 25 focused tests | 28.33 s | PASS |

Tier 3 was not run: the pinned classical inputs and shared algebra are
unchanged, and this import does not promote a freeze, release, causal theorem,
QME lifecycle, particle classification, or quantum result.

```text
PYTHONPATH=quantum-weyl python3 -m transfer.einstein_maxwell_weyl_axial_import_certificate --check
PYTHONPATH=quantum-weyl python3 -m transfer.verify_einstein_maxwell_weyl_axial_import
python3 -m unittest quantum-weyl/transfer/tests/test_einstein_maxwell_weyl_axial_import.py -v
npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true \
  -s quantum-weyl/transfer/schema/einstein-maxwell-weyl-axial-import-v1.schema.json \
  -d quantum-weyl/transfer/certificates/EINSTEIN_MAXWELL_WEYL_AXIAL_EXTRA_MODULE_IMPORT.json
```
