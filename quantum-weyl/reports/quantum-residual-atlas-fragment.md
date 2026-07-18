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
modewise fields remain `NO_CERTIFIED_MAP` or `OPEN`. Their strict interacting
quantum lifecycle is separately `OBSTRUCTED` by the local Euclidean QME
result; this does not alter the accepted classical causal carrier.

The classes `W_+^2` and `W_-^2` remain explicitly identified as classical
deformation/vertex classes. Their Gram matrix and free-BV cohomology status
are certified. Their strict fixed-field-content quantum survival cannot be
transferred because the local Euclidean QME is obstructed. They are never
emitted as particles.

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

The explicit regulated insertion is now certified as

```text
(199/30) [omega C2] - (87/20) [omega E4],
```

and gives `OBSTRUCTED_STRICT_FIELD_CONTENT`. This closes the general strict
QME disposition but not the carrier-specific crosswalk from a classical Taub
or resonance obstruction to that insertion. The latter therefore remains
`NO_CERTIFIED_MAP`.

An exact separating witness also rules out cancellation by nonnegative
collections of standard-sign free conformal scalars, Weyl/Dirac fermions and
gauge vectors. This strengthens the declared strict/ordinary-matter lifecycle
without changing any mode-to-particle crosswalk. Compensator and nonstandard
matter extensions remain separate open theories.

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
