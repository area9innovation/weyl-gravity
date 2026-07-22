# Phase-2 quantum BRST–Hadamard stretch

## Result

Exactly one complete causal BV complex was selected: the certified gauge-fixed
54-row Berger complex on the compact positive-clock fixture. Its action-derived
unary differential, nondegenerate odd pairing, componentwise real structure,
and advanced/retarded Green homotopies were imported by content hash. The
retained 26-row carrier is used only to localize the conditional covariance
construction; it is not substituted for the full BV complex.

The full bidistribution contract cannot yet be completed. The first missing
object is the complete 104-by-104 stationary Cauchy carrier
`BERGER_RETAINED_26_STATIONARY_GENERATOR_V1`, comprising `A104`,
`q_Cauchy_104`, `G_Cauchy_104`, and `real_structure_104`. This is an exact
obstruction, not an absence inferred from repository silence: the present
known-entry mask leaves 288 coordinates in the ghost and identity 12-by-12
blocks undetermined, and two exact mask-compatible completions have endpoint
zero-eigenspace dimensions 24 and 0. Therefore the generalized zero/Jordan
space, its smooth covariance correction, and the global BRST-compatible
Hadamard covariance are not determined by current certified data.

The local Hadamard singular structure, graded causal commutator, BRST descent,
and conditional lift from 26 to all 54 rows remain certified
`LORENTZIAN-CAUSAL` inputs. They do not supply the missing global zero-mode
choice. Once the complete exact carrier is imported, a separate analytic
theorem must still decide whether zero is isolated in the declared closed
mixed-Sobolev/Krein realization.

## P2-A adjoint disposition

P2-A certifies positive structured metrics only on finite reduced carriers and
certifies no genuine Mannheim `C` on conformal gravity. It therefore does not
authorize a full-BV adjoint replacement here. This audit retains the imported
action-derived graded adjoint. The `REDUCED-MODE` P2-A conclusion is recorded
as a boundary on the choice of adjoint, not promoted to a
`LORENTZIAN-CAUSAL` state theorem.

## Claim boundary

This establishes a hash-pinned selection audit and the first exact typed
obstruction to the requested bidistribution. It is not a microlocal
nonexistence theorem: supplying the stationary carrier may permit the
construction. No physical positivity, particle space, scattering statement,
renormalized product, QME restoration, or unitarity conclusion follows. The
optional stretch remains outside Phase-2 closure.

## Receipts

- `python3 quantum-weyl/pt_cpt/hadamard_stretch/hadamard_stretch_obstruction.py --check`
- `python3 quantum-weyl/pt_cpt/hadamard_stretch/verify_hadamard_stretch_obstruction.py`
- `python3 -m unittest quantum-weyl/pt_cpt/hadamard_stretch/tests/test_hadamard_stretch_obstruction.py -v`
- `npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s quantum-weyl/pt_cpt/hadamard_stretch/schema/phase2-brst-hadamard-stretch-obstruction-v1.schema.json -d quantum-weyl/pt_cpt/hadamard_stretch/certificates/PHASE2_BRST_HADAMARD_STRETCH_OBSTRUCTION_V1.json`
- `python3 residual_atlas/validate_fragment.py residual_atlas/phase2-quantum-brst-hadamard-fragment-v1.json`

CLOSE-OUT: DONE — exactly one complete causal BV complex was imported and the first exact global Hadamard obstruction was certified without a reduced or Euclidean substitution.

EVIDENCE: quantum-weyl/pt_cpt/hadamard_stretch/certificates/PHASE2_BRST_HADAMARD_STRETCH_OBSTRUCTION_V1.json
