# Ranked low-hanging-fruit completion matrix

**Result:** `FOUNDATIONAL_RANKED_OPPORTUNITY_COMPLETION_MATRIX_V1`

**Lifecycle:** `SEPARATED`

**Dependencies:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`

## Outcome

All nine bounded `first_artifact` tasks ranked in
`FOUNDATIONAL_COVERAGE_MATRIX_V0` now exist, are content-pinned, and pass their
own independent verifiers. This closes the ranked low-hanging-fruit pass. It
does **not** close the broader reverse-foundations programme: every row retains
a deeper research gate, and no continuum quantum or Lorentzian lifecycle claim
is promoted.

The full generated Markdown projection—including the 16-by-6 assumption
matrix, nine completion rows, and all 45 literature points and boundaries—is
[`completion-matrix.md`](completion-matrix.md).

| Rank | Opportunity | First artifact | Scientific status | Main open gate |
|---:|---|---|---|---|
| 1 | `OP-EXACT-BV-WEAK-BASELINE` | complete | `SUFFICIENCY_PROVED` | weakest base/reversal and other energies |
| 2 | `OP-KREIN-EXPLICIT-J-AUDIT` | complete | `SUFFICIENCY_PROVED` | arbitrary Krein, domains, traces, probability |
| 3 | `OP-SEPARATION-WITNESS-CROSSWALK` | complete | displayed-certificate avoidance proved | continuum arguments |
| 4 | `OP-SEPARABLE-CSTAR-STATE-CHAIN` | complete | `SEPARATED` | physical state, local normality, dynamics |
| 5 | `OP-SPECTRAL-FRAGMENT-AUDIT` | complete | `SUFFICIENCY_PROVED` | spectral measures, determinants, traces |
| 6 | `OP-OPERATIONAL-RECONSTRUCTION-STRENGTH` | complete | `SEPARATED` | full reconstruction and reversals |
| 7 | `OP-GREEN-OPERATOR-FOUNDATIONS` | complete | dependency cut complete | analytic weak/choice strength and full BV propagator |
| 8 | `OP-FINITE-FIELD-WEYL-BRIDGE` | complete | `SEPARATED` | comparison maps and convergence theorem |
| 9 | `OP-TOPOS-WEYL-BV` | complete | `LITERATURE_SCOPED` | select a topos and internalize finite BV |

Ranks 1 and 3 deliberately share one certificate: its finite integer SDR both
establishes the weak-base sufficiency upper bound and retains the explicit
witnesses that avoid general Hahn–Banach separation for that displayed
derivation. All other rows have distinct artifacts.

## What the pass found

The sharpest positive results occur where repository objects are explicitly
enumerated: the finite BV contraction, the energy-labelled Krein symmetry, and
the diagonal energy operator. In each case an existential functional-analytic
theorem can be replaced by retained finite or countable data.

The middle rows expose non-implications. A separable algebra plus explicit GNS
does not choose a physical state. Operational continuity does not by itself
physically imply `RCA_0` or `WKL_0`. Finite-field phase space, finite mode
cutoff, finite-dimensional complex Hilbert space, and finitism are different
types of assumption.

The continuum and topos rows are maps of work, not completed theories. The
Green audit identifies where PDE existence and causal support enter. The topos
ledger identifies the prior need to select an ambient topos and rebuild smooth,
distributional, causal, completion, state, and renormalization layers.

## Claim boundary

`ALL_RANKED_FIRST_ARTIFACTS_COMPLETE` means exactly nine bounded deliverables
from the source ranking have verified receipts. It establishes neither survey
completeness nor a weakest foundation for Weyl gravity. There remains no full
Lorentzian off-shell BV propagator, BRST-compatible Hadamard state, renormalized
Lorentzian time-ordered product, causal perturbative AQFT construction, or
Lorentzian QME theorem.

## Verification

```bash
python3 foundations/check_ranked_opportunity_completion.py
python3 foundations/verify_ranked_opportunity_completion.py
python3 foundations/render_completion_matrix_md.py --check
python3 -m unittest foundations.tests.test_ranked_opportunity_completion
python3 -m unittest foundations.tests.test_render_completion_matrix_md
```
