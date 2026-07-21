# Paper 12 minimal-compensator ladder synthesis update

Date: 2026-07-21

Science Forge work item:
`sf:program/work/quantum-paper12-minimal-compensator-ladder-synthesis-update`

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`

## Result

Paper 12 now imports
`COMPENSATOR_MINIMAL_LADDER_SYNTHESIS_AFTER_LEVEL3B_V1` as the authoritative
classical action-selection boundary.  The claim-map generator independently
loads and verifies the content hashes, result identifiers and result states of
all fifteen component artifacts consumed by the synthesis.

The manuscript prints the exact tested union of the separately declared:

- passive tau-adic extension;
- minimal polar family with optional small-gauge HT sector;
- quadratic shift-symmetric `P(X)` family;
- first nonexact polynomial braiding family;
- literal linear-`F` curvature family with `+F_X` convention;
- convention-correct linear-`F` Horndeski family with `-2F_X` convention;
- minimal real torsion-free Weyl-connection family.

Every declared component has empty good locus under its own printed
background, charge, derivative and representation assumptions. Candidate
A/B/C, `P(X)`, braiding, both linear-`F` steps and the minimal real-connection
step are terminal components of this exact union rather than live successors
inside it.

The historical complete direct-sum rank-390 causal promotion is marked
superseded by Candidate A's full mixed Hessian. The narrower trace Schur
complement, reduced scalar Green identities and phase scalar-wave block are
preserved as valid subresults.

No selected classical action or Hessian exists for a determinant or QAP
freeze. The separated real scale plus compact internal `U(1)` representation
is recorded as the next preflight only, not as a selected action.

## Scope boundary

This is a theorem about exactly the printed union, not its closure under
hybrids. It does not cover simultaneous braiding and Horndeski couplings,
higher `F/G`, `G5`/DHOST, extra fields, fixed-flux or changed global quotients,
changed backgrounds or fixed-charge reductions, arbitrary hybrids, or
general metric-affine/complex gauge geometry. It changes no strict-theory
anomaly coefficient, tau-adic local-cohomology result, one-loop local-QME
restoration, or conditional formal all-loop theorem. It establishes no
Hadamard, Lorentzian QME, particle, positivity or unitarity claim.

## Imported evidence

```text
2497b1ace8415594bca64d8ba38e25475ca16858  synthesis source commit
a942ff6a15af0c8a79978dc22ff2cc128a238c3abd6feb2685197d48deaeaf37  synthesis certificate
fb52c36f2f23bb19a003cca53ef7ba46085ba17c9d7d261422a2dc047e24f4f8  independent tier receipt
15  independently hash-verified component imports
```

The complete path/result/state/hash/source-commit ledger for those fifteen
imports is embedded under
`minimal_compensator_ladder_synthesis_status.verified_imports` in the Paper
12 claim map.

## Publication artifacts

```text
82c33a046ef891372beac7748fa4ba04bfcb9bc75074c5b0382311c7f34bebdd  manuscript TeX
2a85d2a259d23736b610bd5eb2d21397f340a945fd8df7572cdfa55990e5d040  manuscript PDF
d18cb40ddc1072f0e7e34659491f0fa8c92658580734bda394666ceaf586e862  generated claim map
aaae402f8dbf845def05c7dae642f2792a629b0342e4d8a03b7898e272ab7e66  referee response
5c104633a013ab0ab594420c8d9ebd88e1d4ac8385e4c25d2c7d8b4dee0b68ce  Science Forge coverage fragment
2dbea7a1969dfa9caa7b9c198d861bff7ae43e8cc173fcff2fad1066679be9b6  coverage audit report
```

The coverage graph contains ten classified results and eight material paper
claims, with zero uncovered, stale, lifecycle-disagreement or blocking flags.

## Verification

Tier 0, scoped Tier 1 and the affected certificate chain passed:

```text
python3 -m py_compile \
  paper/generate_12_pure_weyl_one_loop_bv_anomaly_claim_map.py \
  paper/verify_12_pure_weyl_one_loop_bv_anomaly_claim_map.py
python3 -m json.tool \
  paper/12-pure-weyl-one-loop-bv-anomaly-science-forge-paper-coverage.json
python3 d_quotient_classical/compensator/minimal_ladder_synthesis_after_level3b.py --check
python3 d_quotient_classical/compensator/verify_minimal_ladder_synthesis_after_level3b.py
python3 -m unittest \
  d_quotient_classical.compensator.tests.test_minimal_ladder_synthesis_after_level3b -v
pdflatex -interaction=nonstopmode -halt-on-error \
  12-pure-weyl-one-loop-bv-anomaly.tex
# repeated twice
s-f paper-coverage \
  paper/12-pure-weyl-one-loop-bv-anomaly-science-forge-paper-coverage.json \
  --mode advisory --stamp 2026-07-21T00:00:00Z \
  -o paper/12-pure-weyl-one-loop-bv-anomaly-paper-coverage-report.json
PYTHONPATH=. python3 \
  paper/generate_12_pure_weyl_one_loop_bv_anomaly_claim_map.py --emit
PYTHONPATH=. python3 \
  paper/generate_12_pure_weyl_one_loop_bv_anomaly_claim_map.py --check
PYTHONPATH=. python3 \
  paper/verify_12_pure_weyl_one_loop_bv_anomaly_claim_map.py
PYTHONPATH=. python3 paper/verify_12_quantum_anomaly_tables.py
PYTHONPATH=. python3 paper/generate_12_quantum_anomaly_tables.py --check
git diff --check -- <scoped paths>
```

Results: exact synthesis producer PASS in 0.05 s; method-independent replay
PASS in 0.50 s; eight mutation tests PASS in 0.77 s; final PDF passes in 0.85
s and 0.87 s, producing 43 pages with no warning, undefined-reference,
overfull or underfull diagnostic; claim map generator/check and independent
verifier PASS; table verifier PASS; paper coverage reports ten of ten results
classified with zero flags.

Tier 3 was not rerun because this update changes publication integration and
claim edges only; it does not freeze a new theorem, tag a release, or change
shared core algebra. The imported classical synthesis already carries its own
Tier-3 freeze receipt.

## Coordination deviation

The work item listed `notes/quantum-team-brief.md`, which does not exist. The
programme's canonical quantum brief is
`notes/d-quotient-quantum-team-brief.md`; that existing file was updated to
satisfy the common team-brief handoff requirement. No roadmap or another
team's certificates were edited.

CLOSE-OUT: DONE — Paper 12, its generated claim ledger, its independent
verifier, the referee response and the Science Forge paper edge now use the
exact exhausted minimal-ladder union and preserve every noncoverage and
no-selected-action boundary.
