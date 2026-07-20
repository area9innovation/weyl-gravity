# Paper 12 Candidate A/B terminal-status correction

Date: 2026-07-20

Science Forge work item:
`sf:program/work/quantum-paper12-candidate-b-terminal-status-correction`

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`

## Correction

Paper 12 and its focused referee response no longer describe Candidate B as
under test. They now state:

- Candidate A is a scoped classical obstruction for its declared
  auxiliary-scalaron action and frozen carrier;
- Candidate B is a scoped classical obstruction for its declared
  unimodular three-form action, background and small gauge group;
- neither declared minimal repair selects an action;
- neither candidate Hessian is imported into the conditional quantum theorem;
- the two scoped failures do not prove a universal compensator no-go.

The generated claim map imports both exact certificates and records the
result and planning-close commits:

```text
Candidate A result commit  5c642e2ad14d45f6074b1327c69707b7b9b08f5d
Candidate A close commit   218cd5ad9
Candidate A certificate    889c3c2870bb2b28dfe2e4e510526f8644c0b7358884d07fcad351199ae747c6

Candidate B result commit  cc0e0036c6acce2bc3d8ba81057031d90a71333a
Candidate B close commit   c7af7b707
Candidate B certificate    e8a8aeb97398c3b8812b20118daa56850e32a516bf4e9db15c00b99cec7a8faa
```

Publication hashes:

```text
d1a5fccfb25a6656bff1b9dea489e52cd23db2a36ed4301c5db087b3e95bf817  manuscript TeX
93a2ba00eedf337b8a3c4d837bf7717b45ad58ff517ffad8d1e011ff5567e1b4  manuscript PDF
6148b31e69e1ab78be101bcd731b03caaf006dfded3f02ebd57c0f7c639b043e  generated claim map
521cdfe6f77808505f97acc9d1161b7160ebf6f559c75babbe99ad2f7e1e60ae  referee response
```

## Verification

Tier 0 and Tier 1 passed:

```text
rg -n -i 'candidate.?b.*under test|under test.*candidate.?b|UNDER_TEST_NOT_IMPORTED' <Paper 12 bundle>
python3 -m json.tool <changed JSON>
python3 -m py_compile paper/generate_12_pure_weyl_one_loop_bv_anomaly_claim_map.py paper/verify_12_pure_weyl_one_loop_bv_anomaly_claim_map.py
PYTHONPATH=. python3 paper/generate_12_pure_weyl_one_loop_bv_anomaly_claim_map.py --emit
PYTHONPATH=. python3 paper/verify_12_pure_weyl_one_loop_bv_anomaly_claim_map.py
PYTHONPATH=. python3 paper/generate_12_quantum_anomaly_tables.py --check
PYTHONPATH=. python3 paper/verify_12_quantum_anomaly_tables.py
s-f paper-coverage paper/12-pure-weyl-one-loop-bv-anomaly-science-forge-paper-coverage.json --mode advisory -o paper/12-pure-weyl-one-loop-bv-anomaly-paper-coverage-report.json
pdflatex -interaction=nonstopmode -halt-on-error 12-pure-weyl-one-loop-bv-anomaly.tex
pdflatex -interaction=nonstopmode -halt-on-error 12-pure-weyl-one-loop-bv-anomaly.tex
```

The stale-wording search returned no matches after regeneration. The
claim-map and generated-table independent verifiers passed. The two TeX
passes took 0.65 s and 0.60 s; the final log contains no warning, error,
undefined-reference, overfull or underfull diagnostic. The advisory
paper-coverage audit has zero flags.

Tier 2 was unnecessary because no mathematical input, shared operator or
schema changed. Tier 3 was not run because this factual publication
correction is not a theorem freeze, tag or release.

## Nonclaims

This correction changes no regulator theorem and establishes no universal
compensator no-go, selected action, selected Hessian, QAP, Lorentzian QME,
Hadamard state, particle, scattering or unitarity result.

EVIDENCE: `paper/12-pure-weyl-one-loop-bv-anomaly-claim-map.json`;
`paper/12-pure-weyl-one-loop-bv-anomaly.pdf`

CLOSE-OUT: DONE — Paper 12 now agrees with the terminal classical
Candidate A/B evidence and preserves its conditional quantum boundary.
