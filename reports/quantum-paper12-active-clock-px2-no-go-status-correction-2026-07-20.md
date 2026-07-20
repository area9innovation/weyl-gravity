# Paper 12 quadratic active-clock status correction

Date: 2026-07-20

Science Forge work item:
`sf:program/work/quantum-paper12-active-clock-px2-no-go-status-correction`

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`

## Result

Paper 12 now imports the exact quadratic active-clock locus and its
method-distinct freeze audit.  The complete declared shift-symmetric family

```text
C2 + R2 + R + P(X),  P(X)=p0+p1 X+p2 X2
```

with no Henneaux--Teitelboim sector or new fields has a one-dimensional
common stationary locus on the unit-cylinder and frozen Berger fixtures:

```text
t(81/20, 27/3290, -324/1645, 486/1645, 18/25, 1).
```

Its seven-gate good locus is empty.  Two independently reconstructed
separators make the disposition readable:

1. for every nonzero `t`, the coupled gravity--auxiliary velocity form has
   rational congruence diagonal `(-6, 6, -36t/25)` and hence a split
   gravity--auxiliary pair;
2. standard-sign cylinder clock health requires `t<0`, whereas the Berger
   sound-cone and clock gate requires `t>0`.

At `t=0` the action is zero and has no pairing or dynamics.  No
`Candidate C_active` action or action hash is exported, and downstream
selected-action regulator and QAP work remains unauthorized.

This is a scoped quadratic active-clock no-go.  It is not a universal
`k`-essence or compensator no-go and does not cover higher `P(X)`, higher
phase derivatives, nearby backgrounds, fixed-charge sectors, new fields or
enlarged gauge groups.

## Imported evidence

```text
f64be4a57  source commit
9ad148d6b632e215cd75636f5fd5b431fa85cf1698a63f725d8b3c9dfe61de89  locus certificate
9bda4b758616427bdbf401a499ffd2b7cd9dd69a87223f05fcdf636bb31cd533  independent freeze audit
8202001c84b93aec1759ef85a3d53ab96eb9af0d577c197ad58aafe1dad834c5  producer tier receipt
2dd8d5f18100ea73cd5144f22beee7aa6bf4e2b8d39337b4eaf108563f16e733  audit tier receipt
```

Publication hashes:

```text
896d66e405c110964bb3355bf1ccc3540c739cba483291f0487494a299050928  manuscript TeX
10e2277201bba93678d0b938b20262910e08d38d1ff413b912f7230b1f10061c  manuscript PDF
7871dc02f04abd6a8cb7fd0a59a370b7f6ab45a13e43d9927fabafbb18ad41d3  generated claim map
ed42e5ef711becaf96b32843b2e67803c84e0ef6ce6228c7364bf58ac127230a  referee response
b6f901dd6ddf091a1f1eefae50925f6d979ad29bab6f49d74cd93daf1926a156  paper-coverage graph
0b09b9df2aacff9fb491272eef05ad99782d7b710cdc72ea83378c5589bcbe8c  paper-coverage report
```

## Verification

Tier 0, Tier 1 and the affected classical certificate chain passed:

```text
python3 d_quotient_classical/compensator/active_clock_px2_locus.py --check
python3 d_quotient_classical/compensator/verify_active_clock_px2_locus.py
python3 d_quotient_classical/compensator/active_clock_px2_independent_freeze_audit.py --check
python3 d_quotient_classical/compensator/verify_active_clock_px2_independent_freeze_audit.py
python3 -m unittest d_quotient_classical.compensator.tests.test_active_clock_px2_locus -v
python3 -m unittest d_quotient_classical.compensator.tests.test_active_clock_px2_independent_freeze_audit -v
s-f paper-coverage paper/12-pure-weyl-one-loop-bv-anomaly-science-forge-paper-coverage.json --mode advisory -o paper/12-pure-weyl-one-loop-bv-anomaly-paper-coverage-report.json
PYTHONPATH=. python3 paper/generate_12_pure_weyl_one_loop_bv_anomaly_claim_map.py --emit
PYTHONPATH=. python3 paper/verify_12_pure_weyl_one_loop_bv_anomaly_claim_map.py
PYTHONPATH=. python3 paper/generate_12_pure_weyl_one_loop_bv_anomaly_claim_map.py --check
PYTHONPATH=. python3 paper/generate_12_quantum_anomaly_tables.py --check
PYTHONPATH=. python3 paper/verify_12_quantum_anomaly_tables.py
pdflatex -interaction=nonstopmode -halt-on-error 12-pure-weyl-one-loop-bv-anomaly.tex
pdflatex -interaction=nonstopmode -halt-on-error 12-pure-weyl-one-loop-bv-anomaly.tex
```

The producer, independent audit and both independent replays passed in
0.47--0.66 s.  The 9 producer tests and 8 audit tests passed in 0.95 s and
0.77 s.  Those suites reject coefficient, background, rank, sign, omitted
gate, Candidate-promotion and universalization mutations.  The Paper 12
verifier additionally mutates and rejects the two publication-ledger fields
that would activate `Candidate C_active` or broaden the result to a universal
no-go.

Paper coverage has eight results and seven material claims, with zero flags.
The claim-map and table verifiers passed.  The two TeX passes took 0.68 s and
0.62 s; the final 41-page log has no error, warning, undefined-reference,
overfull or underfull diagnostic.

Tier 3 was not run because this is a publication lifecycle correction, not a
freeze, release, tag or shared-core-algebra change.

## Coordination deviation

The work item's stop condition explicitly required the Science Forge coverage
graph, coverage report, referee response, and claim-map generator/verifier,
but its `allowed_paths` list omitted those five existing publication-evidence
files.  They were necessary to meet the stop condition and to keep the
generated claim map reproducible.  The manual explicit-path commit contains
only the ten listed Paper 12, team-brief and receipt files; the shared staged
and dirty work of other teams was not included.

## Nonclaims

This correction changes no strict anomaly or conditional extended-QME
theorem.  It establishes no universal scalar-tensor, `k`-essence or
compensator no-go, no selected action or Hessian, no regulator or QAP, and no
Hadamard, Lorentzian QME, particle, scattering, positivity or unitarity
result.

EVIDENCE: `paper/12-pure-weyl-one-loop-bv-anomaly-claim-map.json`;
`paper/12-pure-weyl-one-loop-bv-anomaly-paper-coverage-report.json`

CLOSE-OUT: DONE — Paper 12 and its generated evidence now carry the
independently frozen scoped quadratic active-clock no-go without selecting an
action-specific quantum consumer.
