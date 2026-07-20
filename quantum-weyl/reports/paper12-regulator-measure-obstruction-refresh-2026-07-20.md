# Paper 12 regulator/measure obstruction refresh

Date: 2026-07-20

Science Forge work item:
`sf:program/work/quantum-paper12-regulator-measure-obstruction-refresh`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

## Result

Paper 12 now imports the four post-QAP regulator and measure preflights by
exact hash and keeps their claim boundaries separate:

- ordinary DR/MS is obstructed on the declared strict four-dimensional
  module by the nonzero Euler pole and evanescent continuation ambiguity;
- the dressed canonical BV transformation has a nonunit finite-carrier
  Berezinian, while no action-independent continuum-local Jacobian
  counterterm is established;
- the common even AFN0 \(d\)-dimensional premodule is exact, while full BV
  completion requires selected-action Koszul--Tate rows and a parity-odd
  continuation prescription;
- a strictly four-dimensional covariant regulator receiver is proved only
  conditionally on selected-Hessian symbol, domain, projector and
  intertwining hypotheses; it is not an instantiated QAP regulator.

The manuscript records Candidate A as classically obstructed and Candidate B
as under test. Neither action is imported into the quantum theorem. The
formal all-loop restoration theorem remains conditional on its declared QAP.

## Imported hashes

```text
20915ec21d0c96534a7091b57ee2c3baf5728526a32d00de83dd75b4b94e7e5f  TAU_ADIC_DR_MS_QAP_EVANESCENT_CLOSURE_OBSTRUCTION.json
28d6821e0774767f991ce79d507dd0059eae2f274c7114c4bec8a07ccc915371  DRESSED_CANONICAL_BEREZINIAN_LOCALITY_PREFLIGHT.json
8685f36ddfbc6a77cdab8048965fb54b575e160a96962651c05a66c167390724  DRESSED_EVANESCENT_GEOMETRIC_BV_MODULE_PREFLIGHT.json
62f53393712a58c25ca26f2318e9feba4fea8efedd2659e4eeb76b7634de2f13  DRESSED_FOUR_DIMENSIONAL_COVARIANT_REGULATOR_PREFLIGHT.json
889c3c2870bb2b28dfe2e4e510526f8644c0b7358884d07fcad351199ae747c6  COMPENSATOR_CANDIDATE_A_R2_AUXILIARY_SCALAR_OBSTRUCTION_V1.json
```

## Publication hashes

```text
05e3e844f765f797caa27c239abbe80fe4d5a393e1932822f57b3d6bf210dae3  manuscript TeX
3b7640c4c81963f98e5cbb5912eef1ef309b78bb228e277dda533572dcfcb67f  manuscript PDF
5b541a7a32af2cad9e559fb94b80452a4fd8fa18746ac152f7d52008a817870e  generated claim map
0e04defaaa3569a451839b0a089b3f3f3a0d897a56d1b4994e348af46b9c7e83  referee response
e7fd180eaa3b668a924a60362e577482b3f0dd1a00ea0bfb4066100e927df063  paper-coverage graph
8b6db5ce928c111f455c0fdc7afe2e0b54093f5d3089356e933e7011d80383d6  paper-coverage report
```

## Verification

Tier 0 and Tier 1 passed:

```text
python3 -m json.tool <each changed JSON>
python3 -m py_compile paper/generate_12_pure_weyl_one_loop_bv_anomaly_claim_map.py paper/verify_12_pure_weyl_one_loop_bv_anomaly_claim_map.py paper/generate_12_quantum_anomaly_tables.py paper/verify_12_quantum_anomaly_tables.py
PYTHONPATH=. python3 paper/generate_12_pure_weyl_one_loop_bv_anomaly_claim_map.py --emit
PYTHONPATH=. python3 paper/verify_12_pure_weyl_one_loop_bv_anomaly_claim_map.py
PYTHONPATH=. python3 paper/generate_12_quantum_anomaly_tables.py --check
PYTHONPATH=. python3 paper/verify_12_quantum_anomaly_tables.py
s-f paper-coverage paper/12-pure-weyl-one-loop-bv-anomaly-science-forge-paper-coverage.json --mode advisory -o paper/12-pure-weyl-one-loop-bv-anomaly-paper-coverage-report.json
pdflatex -interaction=nonstopmode -halt-on-error 12-pure-weyl-one-loop-bv-anomaly.tex
pdflatex -interaction=nonstopmode -halt-on-error 12-pure-weyl-one-loop-bv-anomaly.tex
```

The two TeX passes took 0.81 s and 0.80 s. The final PDF has 41 pages and
the final log has no errors, warnings, undefined references, overfull boxes
or underfull boxes. The claim-map and generated-table independent verifiers
passed. The advisory paper-coverage audit found five results, five classified
material claims and zero flags.

The coverage audit is scoped to the Paper 12 graph containing the conditional
all-loop result and these four preflights. It is not the project-wide
certificate corpus baseline.

Tier 2 was unnecessary because no mathematical input, shared operator or
schema was changed. Tier 3 was not run because this refresh does not freeze,
tag or release the theorem.

## Open gates

This refresh does not establish a selected-action determinant or regulator,
scheme equivalence, anomaly coefficients beyond their existing certificates,
global-anomaly exclusion, Lorentzian QME, Hadamard state, positivity, particle
interpretation, scattering, unitarity or residual quantum transfer.

EVIDENCE: `paper/12-pure-weyl-one-loop-bv-anomaly-claim-map.json`;
`paper/12-pure-weyl-one-loop-bv-anomaly-paper-coverage-report.json`

CLOSE-OUT: DONE — Paper 12 and its generated publication evidence now state
the exact regulator/measure obstruction sequence without promoting the
conditional QAP hypothesis.
