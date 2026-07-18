# Quantum residual-atlas fragment

This generated fragment owns the quantum-status column and the
classical-to-quantum import boundary. Its status vocabulary is strictly:

```text
CERTIFIED
OBSTRUCTED
OPEN
NOT_APPLICABLE
NO_CERTIFIED_MAP
```

The generator emits a strict common-envelope fragment with thirteen entries:
six all-energy vacuum-cylinder E/A/L mode-family rows, two residual
deformation-class rows, one Berger carrier-gap row, one classical-to-quantum
tangent-cone crosswalk, and three non-mode particle guards. Every row carries
the full declared mode scope and separately records classical
import, BRST closure and exactness, pairing, compatible complex structure,
Hadamard two-point function, state-space signature, anomaly/QME dependency,
and lifecycle state.

The E/A/L rows import the exact selected positive-frequency and infinite-index
Krein ledgers as `REDUCED-MODE` evidence. They do not promote that evidence to
a covariant distributional complex structure, a Hadamard state, physical
positivity, or a Lorentzian particle interpretation. The Berger causal
26-row carrier is imported, but no stationary mode basis exists; its per-mode
quantum fields therefore remain `NO_CERTIFIED_MAP` or `OPEN`.

The classes `W_+^2` and `W_-^2` remain explicitly identified as classical
deformation/vertex classes. Their Gram matrix and free-BV cohomology status
are certified, while their quantum survival is open. They are never emitted
as particles.

The guards are first-class atlas crosswalk entries and assign
`NO_CERTIFIED_MAP` to particle
interpretations of local anomaly classes, Euclidean determinant factors, and
curvature-observable generators. These carriers remain available in their
own local, spectral, or observable-algebra roles without being inserted into
the physical mode atlas.

## Tangent-cone boundary

For

```text
Z2^C = {u: mu_X(u)=0 and R_j^C(u)=0},
```

the tangent-cone crosswalk entry imports the general
correction-class-sensitive theorem directly and keeps its abstract criterion
separate from background fixtures and the quantum bridge. All three abstract
classical criteria are certified. The
finite `k=0` bounded/quasiperiodic cone is certified, but opposite-momentum
resonances obstruct inference from moment maps alone. The fixed-`(ell,|k|)`
smooth-secular cone is certified in its declared scope. The causal/retarded
criterion has no background-specific Green theorem in this import. Every
correction class still has `NO_CERTIFIED_MAP` to a quantum insertion.

None of these classical statements implies disappearance from interacting
BRST cohomology, a nonzero loop interaction, a quantum constraint, or a
BRST-exact Taub insertion. Those conclusions require an explicit
classical-to-quantum insertion, an exactness or nonmembership certificate,
and a restored QME—or a normalized QME obstruction.

## Verification

```bash
PYTHONPATH=quantum-weyl python3 -m atlas.generate_quantum_atlas_fragment --check
PYTHONPATH=quantum-weyl python3 -m atlas.verify_quantum_atlas_fragment
PYTHONPATH=quantum-weyl python3 -m unittest atlas.tests.test_quantum_atlas_fragment
python3 residual_atlas/validate_fragment.py quantum-weyl/atlas/quantum-atlas-fragment.json
```
