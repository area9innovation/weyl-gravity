# Compensator Candidates A/B: exact common disposition

## Verdict

On the declared unit-cylinder, coupling, raw-\(D\), frozen-Berger-clock and
small-gauge conventions, neither minimal repair passes the common seven-gate
receiver:

\[
\boxed{\text{Candidate A: OBSTRUCTED},\qquad
       \text{Candidate B: OBSTRUCTED},\qquad
       \text{selection: NEITHER}.}
\]

This is an exact `LOCAL-ALGEBRAIC`/`LORENTZIAN-CAUSAL` comparison of two
scoped action-derived theories. It is not a universal compensator no-go.

## Frozen inputs

The comparison imports, without reconstruction:

| Candidate | Scientific commit | Lifecycle commit | Action hash |
| --- | --- | --- | --- |
| A: \(R(\widehat g)^2\) auxiliary scalar | `5c642e2ad14d45f6074b1327c69707b7b9b08f5d` | `218cd5ad90cb9df537eb368a9312cb745a21044f` | `2fa3f7ff15b95fcebed9c8bfbdf33a33942ef79a66d23d33f00a3f63d0213e11` |
| B: Henneaux--Teitelboim three-form | `cc0e0036c6acce2bc3d8ba81057031d90a71333a` | `c7af7b707831a848e3e110f45bb746478473dbc6` | `8c1466831f8b6aecdc771cd0aed7de07a5c7a5777a88ede90e638ba7ea6d6f51` |

The certificate independently re-hashes each imported certificate, report and
tier receipt. It also checks that both candidates import the identical
action-preflight, positive-Berger-clock and strict-\(\tau\) obstruction
artifacts. The shared fixture has

\[
\bar g=-dt^2+d\Omega_3^2,\qquad R=6,\qquad
M_P^2=\frac16,\qquad V_0=\frac14,\qquad D=\partial_t,
\]

closed \(S^3\) Cauchy surfaces, the original contracted Weyl quartet and the
same rational Berger clock. Candidate B retains the declared small reducible
three-form gauge group; it does not silently quotient the global \(H^3\)
shift.

## Common seven-gate matrix

| Gate | Question | Candidate A | Candidate B |
| ---: | --- | --- | --- |
| 1 | action-derived BV/CME | PASS | PASS |
| 2 | compact-support dressed trace | PASS with physical replacement | FAIL |
| 3 | complete support-local causal parent | NOT REACHED after gate 5 | FAIL |
| 4 | cyclic current and reduced pairing | reduced block only; complete parent not reached | PASS, exposing global pair |
| 5 | physical sign or topological control | FAIL | FAIL |
| 6 | raw-\(D\) charge sector | FAIL | FAIL |
| 7 | frozen Berger-clock compatibility | FAIL | FAIL |

The decision rule is conjunctive: a candidate is selectable only if all seven
gates pass without an uncontrolled, conditional or not-reached remainder.
Partial scores have no role, and the comparison is not authorized to combine
the two actions into a hybrid.

## Independent obstruction replay

For Candidate A, the independent rail retains the complete mixed
auxiliary-scalar Hessian and verifies

\[
\operatorname{inertia}H_{\rm vel}=(1,1),\qquad
\mu_D(\lambda)=(\lambda^2-2)^2,
\]

with real roots \(\pm\sqrt2\), size-two Jordan blocks, a both-sign raw-\(D\)
Hamiltonian and four nonzero changed-action Berger Euler residuals.

For Candidate B, it retains the off-shell trace-free cylinder Euler row

\[
\operatorname{diag}\left(\frac18,\frac1{24},\frac1{24},\frac1{24}\right),
\]

the exact polynomial HT kernel

\[
H_B(D)(D/2,1,0)^T=0,
\]

the nonzero \(H^3(S^3)\) and \(H_c^4(\mathbb R\times S^3)\) classes, the
raw-\(D\) Hamiltonian \(V_{S^3}\lambda_{\rm HT}\), and the nonexact Berger
flux shift \(\mathcal L_D\bar A_3=\operatorname{vol}_{\rm Berger}\).

## Downstream disposition

No selected action, action hash or carrier is exported. Selected-repair
nonlinear, Einstein-bridge, observer-clock and dressed-regulator consumers
must remain retired or inactive.

The smallest open theory classes are instead:

1. a differently tuned or backgrounded \(R(\widehat g)^2\) theory with a
   separately certified healthy full mixed scalar sector;
2. an active-clock HT theory with explicit fixed flux/\(\lambda\)
   superselection and a declared global quotient;
3. a theory with an independent conformal gauge generator and complete BV
   cotangent lift;
4. the bounded minimal-action classification activated by this result.

None is promoted here. In particular, the comparison establishes no
Hadamard state, anomaly/QME result, particle interpretation, scattering
theory, positivity theorem or unitarity theorem.

## Reproduction

```bash
python3 d_quotient_classical/compensator/candidate_ab_neither_comparison.py --check
python3 d_quotient_classical/compensator/verify_candidate_ab_neither_comparison.py
python3 -m unittest d_quotient_classical.compensator.tests.test_candidate_ab_neither_comparison -v
npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true \
  -s d_quotient_classical/schema/compensator-candidate-ab-neither-comparison-v1.schema.json \
  -d d_quotient_classical/certificates/COMPENSATOR_CANDIDATE_AB_NEITHER_COMPARISON_V1.json
python3 -m d_quotient_classical.atlas.generate_classical_atlas_fragment --check
python3 residual_atlas/validate_fragment.py \
  d_quotient_classical/atlas/classical-causal-atlas-fragment.json
python3 d_quotient_classical/atlas/verify_classical_atlas_fragment.py
python3 -m unittest d_quotient_classical.atlas.tests.test_classical_atlas_fragment -v
```

CLOSE-OUT: DONE — both scoped terminal inputs are independently replayed
under one exact seven-gate rule; the declared minimal-action selection is
`NEITHER`, no hybrid or selected-action consumer is authorized, and the
smallest open theory classes remain explicit.
