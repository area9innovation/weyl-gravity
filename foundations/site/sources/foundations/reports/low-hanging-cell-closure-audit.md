# Low-hanging cell closure audit

Result: `FOUNDATIONAL_LOW_HANGING_CELL_CLOSURE_AUDIT_V1`
Dependency boundary: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Outcome

### Three corrections, not three new theories

Three of the 25 assessed open cube cells were stale relative to evidence that
the repository already certifies:

| Mathematical regime | Carrier | Physical obligation | Old | New | Why |
|---|---|---|---|---|---|
| Classical standard | Smooth/PDE/distributional | Gauge/BV/cohomology | Pieces only | Local result | Exact gauge-fixed local BV cohomology is complete in the declared bounded sector on the regular Bach locus. |
| Classical standard | Smooth/PDE/distributional | Interactions/renormalization/QME | Priority gap | Local result | The exact `H^{0,4}(s\|d)` and `H^{1,4}(s\|d)` results already classify bounded local counterterm and anomaly classes. |
| Finite/discrete restriction | Finite exact algebra | Dynamics/propagation | Priority gap | Local result | The certified energy group restricts to every displayed finite cutoff, and its finite matrix-unit dynamics is checked exactly. |

The word “local” is doing real work. A local result means a bounded theorem
occupies the intersection; it does not say the entire cell is solved.

## Why the two local-BV cells now qualify

The authoritative local-BV chain records both gauge-fixed results as
`GAUGE_FIXED_BV_LOCAL_COHOMOLOGY_COMPLETE` on the regular Bach locus:

- `H^{0,4}(s|d)` has two even classes and one odd class, represented by
  `CT_C2`, `CT_E4`, and `CT_C_DUAL_C`; `CT_BOX_R` is exact.
- `H^{1,4}(s|d)` has two even classes and one odd class, represented by
  `ANOM_OMEGA_C2`, `ANOM_OMEGA_E4`, and `ANOM_OMEGA_C_DUAL_C`;
  `ANOM_OMEGA_BOX_R` is exact.
- The general nonminimal/gauge-fixed contraction certifies the transfer from
  the minimal calculation and explicitly leaves analytic QME work open.

This imports a completed `LOCAL-ALGEBRAIC` result. It does not claim a global
smooth/distributional off-shell complex, coefficients, renormalized products,
QME restoration, residual transfer, or a Lorentzian construction. In
particular, the broader classical freeze gate remains failed: the import
certificate still says `FAIL_CLOSED` and forbids publishable quantum promotion.

## Why finite dynamics now qualifies

The free mode certificate constructs the actual diagonal unitary group and
checks a finite representative cutoff using 18 modes, 324 matrix units, 5,832
product-degree identities, 5,832 derivation identities, and 15,876 formal
two-time identities. Those checks use exact integer Laurent exponents, not
floating-point samples.

The previous priority-gap wording required the finite dynamics to arrive with
a controlled continuum comparison. That mixed two obligations. Evolution on
the finite cutoff belongs to dynamics; **continuum comparison belongs to reconstruction**.
The cell can therefore contain a bounded local result while
the continuum comparison, causal propagation, and regulator-independence
questions remain open.

## Exhaustion boundary

After these corrections, 22 assessed open cells remain: five are “pieces
only” and 17 are priority gaps. Each now has a typed missing gate in the
machine-readable audit. They need a new bridge or construction—such as a
weak-base continuum theorem, constructive proof object, internal topos
construction, physical state selector, finite interaction, or controlled
continuum limit—rather than another relabeling of an existing certificate.

This is a bounded exhaustion result for the previously assessed openings. The
157 not-mapped cells are outside the audit; they have not been searched and
must not be called empty, impossible, or even gaps. The pair-frontier analyzer
remains the tool for ranking the 22 typed gates and for deciding which
not-mapped products deserve an evidence pass next.

## What is not established

No coefficient, regulated Slavnov breaking, renormalized product, restored
QME, residual transfer, continuum-limit theorem, causal propagator, or
`LORENTZIAN-CAUSAL` result is established. The residual classes remain centered
deformation/vertex classes, not one-particle graviton states.

## Verify

```bash
python3 foundations/check_low_hanging_cell_closure.py
python3 foundations/verify_low_hanging_cell_closure.py
python3 -m unittest foundations.tests.test_low_hanging_cell_closure
```
