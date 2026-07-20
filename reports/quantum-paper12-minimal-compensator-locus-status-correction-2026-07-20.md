# Paper 12 minimal-compensator locus status correction

Date: 2026-07-20

Science Forge work item:
`sf:program/work/quantum-paper12-minimal-compensator-locus-status-correction`

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`

## Result

Paper 12 now imports the complete declared minimal compensator-family
classification rather than stopping at the Candidate A/B `NEITHER`
comparison. The exact seven-gate good locus is empty for the formal
\(\rho\ne0\) polar family with:

- constant real couplings and global \(U(1)\);
- four metric derivatives and at most two compensator derivatives;
- one invertible algebraic auxiliary presentation of \(R^2\);
- an optional minimal Henneaux--Teitelboim sector under the small reducible
  three-form gauge group.

The manuscript prints the excluded enlarged classes: higher-derivative phase
operators, nonconstant phase couplings, multiplier kinetic/nonlinear
potentials, fixed-flux or fixed-multiplier superselection, large/global
three-form quotients, active-clock retunings, an independent conformal gauge
connection, and the parity-odd Pontryagin direction.

Accordingly, this is a scoped minimal-family no-go, not a universal
compensator no-go. No Candidate C action or action hash is selected, no
candidate Hessian is imported, and regulator, Jacobian, mixing and QAP
implementation remain action dependent.

## Imported evidence

```text
a5924e707352bab92db2caa4c19cf4223c60f0e3  source commit
41ce6db6ab8fc58f4cc1ecedb205f732fd3dcee645f9408506d3535545f7026a  classification certificate
229828007c736b99b3aee2bd0f817fe2d32035da1e4349752f1855cb93628106  independent tier receipt
```

Publication hashes:

```text
372e7bbc73534e7a39593f07b032f7ffbf74acad80895342643c20e3fa706a9b  manuscript TeX
5988b3038070912366e6127d584c276c8940ee35ce632f3ff61eeab7ba529c63  manuscript PDF
b43155a69c6fcfc7ab2145d6b7c7bfa6f3f73b1cbccb21069e0774571e84f104  generated claim map
3db81f306ff5f429198f0be5749d5310e9b536781871378f7a5e40bc2cb3d019  referee response
2619c8a5c5836889c7fc6fa56952c72d99e6d8595995bef2dfad47a29acddab5  paper-coverage graph
92cc84586e0f03e32d323a18fad8582c7cb78b7824601b74189f0351ba960792  paper-coverage report
```

## Verification

Tier 0, Tier 1 and the affected certificate chain passed:

```text
python3 d_quotient_classical/compensator/minimal_action_classification_after_neither.py --check
python3 d_quotient_classical/compensator/verify_minimal_action_classification_after_neither.py
python3 -m unittest d_quotient_classical.compensator.tests.test_minimal_action_classification_after_neither -v
s-f paper-coverage paper/12-pure-weyl-one-loop-bv-anomaly-science-forge-paper-coverage.json --mode advisory -o paper/12-pure-weyl-one-loop-bv-anomaly-paper-coverage-report.json
PYTHONPATH=. python3 paper/generate_12_pure_weyl_one_loop_bv_anomaly_claim_map.py --emit
PYTHONPATH=. python3 paper/verify_12_pure_weyl_one_loop_bv_anomaly_claim_map.py
PYTHONPATH=. python3 paper/generate_12_quantum_anomaly_tables.py --check
PYTHONPATH=. python3 paper/verify_12_quantum_anomaly_tables.py
pdflatex -interaction=nonstopmode -halt-on-error 12-pure-weyl-one-loop-bv-anomaly.tex
pdflatex -interaction=nonstopmode -halt-on-error 12-pure-weyl-one-loop-bv-anomaly.tex
```

The exact producer check, independent reconstruction and all 11 mutation
tests passed. Paper coverage now has six results and six classified claims
with zero flags. The independent claim-map and table verifiers passed. The
two TeX passes took 0.66 s and 0.62 s; the final 41-page log has no error,
warning, undefined-reference, overfull or underfull diagnostic.

Tier 3 was not run because this is a publication lifecycle correction, not a
freeze, release, tag or shared-core-algebra change.

## Nonclaims

This correction changes no strict anomaly or conditional extended-QME
theorem. It establishes no universal compensator no-go, repaired strict
theory, selected action, selected Hessian, regulator, QAP, Hadamard state,
QME, positivity, particle, scattering or unitarity result.

EVIDENCE: `paper/12-pure-weyl-one-loop-bv-anomaly-claim-map.json`;
`paper/12-pure-weyl-one-loop-bv-anomaly-paper-coverage-report.json`

CLOSE-OUT: DONE — Paper 12 now carries the exact scoped empty locus and its
excluded enlarged classes without activating an action-specific quantum
consumer.
