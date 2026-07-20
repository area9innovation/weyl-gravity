# Paper 12 conditional all-loop claim-map refresh

Date: 2026-07-20

## Result

Paper 12 now imports
`TAU_ADIC_ALL_LOOP_LOCAL_QME_STABILITY` as exact `LOCAL-ALGEBRAIC`
evidence.  The generated claim map distinguishes all three theory
dispositions:

1. strict fixed-field-content pure Weyl gravity is obstructed at one loop;
2. the changed tau-adic compensator theory has a restored one-loop local
   Euclidean QME;
3. that changed theory is formally locally QME-restorable at every finite
   order only under the declared quantum action principle.

The import is pinned to source commit
`7fabe987861f1e4facfc2282e7023274df2ddc72` and certificate SHA-256
`3649925e44d99bea0020f3d1c20a16c54a44f6c9714a3c273c20a6e6d8f84dbc`.
The authorized TeX source is pinned to SHA-256
`d2cedfb85a8bf7b1bc5ef2c606c186bdf253767fff30188858cedc0c1982fc1f`.

The former blanket nonclaim `all_loop_extended_QME` was replaced by the
scientifically accurate nonclaims: no unconditional all-loop QME, no
constructed all-loop regulator, no convergence theorem, and no exclusion of
global anomalies.  The existing Lorentzian, Hadamard, residual-transfer,
particle and unitarity nonclaims remain fail-closed.  The referee response was
updated to the same boundary.

## Science Forge paper coverage

The human-directed coverage fragment classifies the conditional theorem as
`TECHNICAL` and links it to a material Paper 12 claim with edge kind
`PRIMARY_THEOREM`.  Its materiality and edge bodies validate against the
landed `materiality-v0` and `result-paper-edge-v0` schemas.  The advisory
bidirectional audit was run after merging this fragment into a fresh
full-corpus shadow import:

```text
24 families
1258 certificates
946 claims
2097 dependency edges
1 Paper 12 result classified
0 unclassified Paper 12 results
0 coverage flags
0 blocking flags
```

The machine-readable audit is
`paper/12-pure-weyl-one-loop-bv-anomaly-paper-coverage-report.json`.
Unrelated imported certificate/claim nodes are not reclassified by this
scoped publication item.

## Verification receipts

Tier 0 and scoped Tier 1/2 publication checks:

```text
pdflatex -interaction=nonstopmode -halt-on-error \
  -output-directory=paper paper/12-pure-weyl-one-loop-bv-anomaly.tex
# repeated twice
! rg -n 'Warning|undefined references|overfull|underfull' \
  paper/12-pure-weyl-one-loop-bv-anomaly.log
python3 paper/generate_12_pure_weyl_one_loop_bv_anomaly_claim_map.py --emit
python3 paper/generate_12_pure_weyl_one_loop_bv_anomaly_claim_map.py --check
python3 paper/verify_12_pure_weyl_one_loop_bv_anomaly_claim_map.py
python3 paper/verify_12_quantum_anomaly_tables.py
```

Result: PASS, two warning-free TeX passes, 40-page PDF, elapsed 4.16 s.

The Science Forge schema check used Python `jsonschema.Draft7Validator`
against the two landed Forge schemas.  Result: PASS, elapsed 0.19 s.

Full-corpus advisory coverage replay:

```text
s-f shadow-import-all <physics-root> <forge-root> \
  /tmp/paper12-full-evidence-final.json \
  /tmp/paper12-import-ledger-final.json
jq -s '{ir:"science-forge-ir-v0",nodes:(.[0].nodes + .[1].nodes)}' \
  /tmp/paper12-full-evidence-final.json \
  paper/12-pure-weyl-one-loop-bv-anomaly-science-forge-paper-coverage.json \
  > /tmp/paper12-live-coverage-graph-final.json
s-f paper-coverage /tmp/paper12-live-coverage-graph-final.json \
  --mode advisory --stamp 2026-07-20T00:00:00Z \
  -o paper/12-pure-weyl-one-loop-bv-anomaly-paper-coverage-report.json
```

Result: PASS in advisory mode with no flags, elapsed 54.99 s.

`git diff --check` passed on the scoped paths.  Tier 3 was not run because
this is a draft publication-integration refresh, not a theorem freeze, tag or
release, and no shared core algebra changed.

## Does not establish

This refresh does not construct the assumed all-order regulator, prove
convergence, repair strict pure Weyl gravity, exclude global anomalies, or
establish Lorentzian products/QME, a Hadamard state, residual transfer,
particles, scattering, positivity or unitarity.

CLOSE-OUT: DONE — The generated claim map, publication hashes, two-pass PDF,
independent verifier and bidirectional Paper 12 coverage edge are current and
preserve every conditional-QAP and open analytic boundary.
