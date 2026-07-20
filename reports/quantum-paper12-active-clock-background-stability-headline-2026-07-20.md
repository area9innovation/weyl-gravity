# Paper 12 active-clock background-stability headline

Date: 2026-07-20

Science Forge work item:
`sf:program/work/quantum-paper12-active-clock-background-stability-headline`

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`

## Result

Paper 12 now imports the exact background-stability certificate for the
declared quadratic active-clock family.  On the rational open neighbourhood

```text
kappa in (15/16,17/16)
q     in (1/5,1/4)
nu    in (2/3,5/6)
```

the common cylinder/Berger stationary matrix has rank five and its nonzero
solutions form one parameter-dependent action-space ray
`lambda K(kappa,q,nu)`.  The couplings vary with the background, so this is
not a theorem for one fixed action across the neighbourhood.

Two terminal failures are structurally stable throughout the box:

1. the gravity--auxiliary velocity pair retains the exact split eigenvalues
   `(+3,-3)`;
2. the raw-`D` Hamiltonian retains exact field-space witnesses with values
   `+3` and `-3`.

The manuscript also records the first exact boundary bifurcation along
`kappa=1`, `nu=3/4`, `lambda=1`.  Below `q=1/4`, the `q=9/40` witness has

```text
(p1,P_X,P_X+2 X P_XX)
  = (2961/800,-26649/12800,-174699/12800),
```

where only the Berger clock is healthy.  Above the crossing, the `q=21/80`
witness has

```text
(p1,P_X,P_X+2 X P_XX)
  = (-5949/3200,-124929/51200,-184419/51200),
```

where both clocks are standard-sign and hyperbolic.  The crossing repairs
only the clock-sign conflict.  The split inertia and raw-`D` failures remain,
so the upper witness is not a viable phase.

The abstract, theorem discussion, generated claim map, Science Forge
coverage graph and quantum-team status ledger now state that exact scope.
They preserve the boundaries: no fixed-action neighbourhood theorem,
universal `k`-essence no-go, complete causal parent, anomaly/QME consequence,
particle, positivity or unitarity result follows.  This classical
action-selection no-go does not weaken the distinct formal local
Wess--Zumino trivialization in the changed compensator complex.

## Imported evidence

```text
b0ee2bea2  scientific source commit
8a3afc04d72427313fe8770936b03d4f4301277c9783a92e8df6d329e8c0ccba  background-stability certificate
```

Publication hashes:

```text
89384462e424d53ccf573682148c40f601715996f1f1da97d204664b26147c84  manuscript TeX
e4ca4aeffa130db9aadff5ca58052e7654fd678cd80ee827118f1b50c51ee821  manuscript PDF
25d67bda4337c6895ed4505e29103803d4361af31a01061ee1803d14c791afab  generated claim map
100faf90799383cecc9c68f762d213d530f53104c9eaa425a8670ceca3d80d62  paper-coverage graph
0e6aec44a219f60f6c09fc63cfee7f261b72b25b5b898a5812e42bb452befe04  paper-coverage report
```

## Verification

Tier 0 and the scoped publication rail passed:

```text
python3 -m py_compile \
  paper/generate_12_pure_weyl_one_loop_bv_anomaly_claim_map.py \
  paper/verify_12_pure_weyl_one_loop_bv_anomaly_claim_map.py
python3 -m json.tool paper/12-pure-weyl-one-loop-bv-anomaly-claim-map.json
python3 -m json.tool paper/12-pure-weyl-one-loop-bv-anomaly-science-forge-paper-coverage.json
python3 -m json.tool paper/12-pure-weyl-one-loop-bv-anomaly-paper-coverage-report.json
python3 symbolic/verify_programme_introduction.py --filename-policy
s-f paper-coverage \
  paper/12-pure-weyl-one-loop-bv-anomaly-science-forge-paper-coverage.json \
  --mode advisory \
  -o paper/12-pure-weyl-one-loop-bv-anomaly-paper-coverage-report.json
python3 paper/generate_12_pure_weyl_one_loop_bv_anomaly_claim_map.py --emit
python3 paper/generate_12_pure_weyl_one_loop_bv_anomaly_claim_map.py --check
python3 paper/verify_12_pure_weyl_one_loop_bv_anomaly_claim_map.py
pdflatex -interaction=nonstopmode -halt-on-error \
  12-pure-weyl-one-loop-bv-anomaly.tex
pdflatex -interaction=nonstopmode -halt-on-error \
  12-pure-weyl-one-loop-bv-anomaly.tex
```

The filename policy passed for 44 artifacts in 0.04 s.  The coverage audit
passed with nine classified results, seven paper claims and zero flags in
0.02 s.  Claim-map generation and exact regeneration checks each took
0.15 s; the independent claim verifier passed in 0.14 s.  The two TeX passes
took 0.76 s and 0.68 s.  The final 43-page log contains no LaTeX/package
warning, undefined-reference, overfull, underfull or error diagnostic.

Tier 2 was unnecessary because the imported classical certificate and its
content hash were unchanged; this task updated only its paper receiver and
generated evidence map.  Tier 3 was not run because this is not a freeze,
tag, release or shared-core-algebra change.

## Coordination deviation

The work-item stop condition requires a PDF build and reproducible claim-map
and coverage verification.  Its `allowed_paths` omitted the existing PDF,
claim-map generator/verifier, coverage graph/report and the new close-out
report, even though those files are necessary to satisfy that stop condition.
The manual explicit-path commit therefore includes those required
publication artifacts.  It excludes every unrelated staged, modified and
untracked path in the shared tree.

## Nonclaims

This synchronization adds no new quantum calculation.  It does not select a
fixed compensator action, generalize the theorem to arbitrary `P(X)` or
backgrounds, construct a causal parent, alter the strict one-loop anomaly or
formal extended-QME result, or establish a Hadamard, particle, scattering,
positivity or unitarity theorem.

EVIDENCE: `paper/12-pure-weyl-one-loop-bv-anomaly-claim-map.json`;
`paper/12-pure-weyl-one-loop-bv-anomaly-paper-coverage-report.json`;
`d_quotient_classical/certificates/COMPENSATOR_ACTIVE_CLOCK_BACKGROUND_STABILITY_V1.json`

CLOSE-OUT: DONE — Paper 12 now states the exact open-neighbourhood
active-clock no-go and first clock-sign bifurcation with its terminal
obstructions and quantum nonclaims preserved.
