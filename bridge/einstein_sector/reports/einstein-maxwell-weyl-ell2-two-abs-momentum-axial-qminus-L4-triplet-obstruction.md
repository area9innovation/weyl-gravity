# Axial q-minus cross-momentum L=4 obstruction triplet

## Result

The first complete target-primary triplet in the two-absolute-momentum
workload is classified.  In all three rows the input is an axial Einstein
q-minus mode with signed compact momentum (n=+1), crossed with an axial
Einstein q-minus mode with (n=-2), in the positive-frequency sum channel.
The angular output is polar \((L,M)=(4,0)\).  Tuning the compact circumference
separately to candidates 3, 4 and 5 places that output on the q-minus,
p-extra and q-plus target shells, respectively.

Each complete target-shell adjoint pairing is nonzero.  Candidate 4 retains
the previously certified two-dimensional p-primary pairing.  Candidates 3
and 5 each have a one-dimensional q-primary cokernel; both pairings obey the
common exact annihilating polynomial

```text
2401*x^4
+13649577984*x^3
-3277767710343168*x^2
-271550576338082463744*x
+480328793324440503975936.
```

Its nonzero constant term proves that neither pairing vanishes.  Therefore
all three declared tangents are `OBSTRUCTED` in the bounded or finite-
quasiperiodic correction class.

## Scope and interpretation

This is a source-matrix result at three separate algebraic circumferences;
the fibres are not identified.  It shows that changing the resonant target
primary across the complete q-minus/p-extra/q-plus triplet does not remove
the obstruction for this axial q-minus cross-momentum carrier.

The result raises the resolved axisymmetric (L=4) workload from two to four
of 108 scalar adjoint coefficients: the p target has multiplicity two,
whereas each q target has multiplicity one.  The remaining 104 axisymmetric
coefficients and all 56 nonaxisymmetric (L=1,3) coefficients remain open.
It does not classify the complete two-fibre tangent cone.

Smooth secular correction remains `OPEN`.  Causal/retarded correction is
`NO_CERTIFIED_MAP`.  No residual, observational or quantum conclusion is
inferred.

## Independent verification

The verifier does not import the triplet producer.  It independently:

- validates the certificate and every input hash;
- specializes the content-addressed q2 action rows directly;
- reconstructs both q-primary shells and their adjoint kernels;
- verifies both source pairings against the exact common annihilator;
- checks the inherited candidate-4 p-primary nonzero witness; and
- checks the fail-closed workload counts.

## Evidence

- Certificate: `bridge/certificates/einstein_maxwell_weyl_ell2_two_abs_momentum_axial_qminus_L4_triplet_obstruction.json`
- Generator: `bridge/einstein_sector/einstein_maxwell_weyl_two_abs_momentum_axial_qminus_L4_triplet.py`
- PBW slice: `bridge/einstein_sector/generated/einstein_maxwell_weyl_ell2_axial_qminus_pair_L4_q2_slice.json`
- Schema: `bridge/einstein_sector/schema/einstein_maxwell_weyl_ell2_two_abs_momentum_axial_qminus_L4_triplet_obstruction.schema.json`
- Independent verifier: `bridge/einstein_sector/verify_einstein_maxwell_weyl_ell2_two_abs_momentum_axial_qminus_L4_triplet_obstruction.py`
- Scoped tests: `bridge/einstein_sector/tests/test_einstein_maxwell_weyl_ell2_two_abs_momentum_axial_qminus_L4_triplet_obstruction.py`

## Verification commands

```text
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_two_abs_momentum_axial_qminus_L4_triplet --check
python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_ell2_two_abs_momentum_axial_qminus_L4_triplet_obstruction.py
python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_ell2_two_abs_momentum_axial_qminus_L4_triplet_obstruction
```
