# Symplectic Reconstruction of the Pais–Uhlenbeck PT Metric — Verification

Audit implementation of the spec in `../Symplectic Reconstruction.md`
(Verifications A–L). **Main result: the Bender–Mannheim construction verifies,
with three corrected claims** — see `reports/verification.md` for the full
report, including answers to the spec's 12 research questions.

## Headline findings

- All candidate formulas (G, char. poly, α/β/r, M, K, exponential S, G₀,
  congruence `SᵀGS = G₀`, distance `2r`, equal-frequency limit) **confirmed**.
- Convention derived, not assumed: `[Q,V] = −iKV`, `e^{−Q/2}Ve^{Q/2} = SV`.
- **Corrected:** S is Hermitian-positive only after a canonical symplectic
  rescaling `d_x·d_y = γω₁ω₂` (not in the original variables).
- **Corrected:** `Stab(J,G₀) = SO(2,ℂ)²`, not `U(1)²` (that is its unitary
  subgroup).
- **Disproved:** "the positive polar factor of every admissible diagonalizer
  is the same" — replaced by the correct uniqueness theorem (unique
  Hermitian-positive diagonalizer `S′₊`; polar factor constant exactly on its
  `U(1)²` coset).
- Reconstruction-without-assuming-Q succeeds: `log S′₊` rebuilds `Q = αpq+βxy`.

## Layout

```
symbolic/verify_sympy.py     51 machine-checked claims (SymPy). ~4 min.
symbolic/verify_wolfram.wl   independent Wolfram audit (needs Mathematica; not run here)
numeric/regression.py        4 parameter triples, 50–80 digits (mpmath). ~4 min.
reports/verification.md      THE REPORT (4 sections + 12 answers)
reports/verification.json    machine-readable claim table
reports/regression.json      all numerical residuals
lean/                        Lean 4 + Mathlib v4.29.0 formalization
  PaisUhlenbeck/Definitions.lean       J, G, G₀, M, K, N, S;  K = J·M
  PaisUhlenbeck/Symplectic.lean        K² = −(αβ)I; N² = 1; SᵀJS = J; det S = 1
  PaisUhlenbeck/NormalForm.lean        SᵀGS = G₀ (division-free, certificates)
  PaisUhlenbeck/JordanObstruction.lean Jordan no-go: structure thm, no PD form,
                                       PSD ⇒ degenerate, nondeg ⇒ indefinite
paper/theorem_statements.tex paper-ready theorem statements
```

All Lean files compile with **zero `sorry`** (`cd lean && lake build`).

## Reproduce

```bash
cd symbolic && python3 verify_sympy.py     # writes ../reports/verification.json
cd numeric  && python3 regression.py       # writes ../reports/regression.json
cd lean     && lake exe cache get && lake build
```
