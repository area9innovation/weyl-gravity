# Symplectic Reconstruction of the Pais–Uhlenbeck PT Metric

Verification project and paper series on the PT-symmetric Pais–Uhlenbeck
oscillator, the fourth-order scalar field, and quadratic gravity. Started
from the audit spec in `../Symplectic Reconstruction.md`; grew into four
papers, a Lean formalization, and a machine-checked verification pipeline.

## The four papers (`paper/`)

| # | File | Title | Status |
|---|------|-------|--------|
| 1 | `main.tex` / `main.pdf` | **Canonical Positive Symplectic Diagonalization of the Pais–Uhlenbeck Oscillator** | frozen, tag `paper1-v1.0` (13 pp.) |
| 2 | `variational-fock.tex` / `.pdf` | **The Pais–Uhlenbeck Metric as a Minimum-Distortion Principle, and the Representation Problem for the Fourth-Order Field** | frozen, tag `paper2-v1.1` (12 pp.) |
| 3 | `fourth-order-vacuum.tex` / `.pdf` | **The Universal Vacuum of the Fourth-Order Scalar Field: Metric Orbits, Fock Sectors, and the Krein Boundary** | frozen, tag `paper3-v1.1` (10 pp.) |
| 4 | `fourth-order-gravity.tex` / `.pdf` | **Gauge Reduction and the Completion Problem in Fourth-Order Gravity: PU Pairing, Covariant Real Forms, and the Conformal Jordan Boundary** | draft (8 pp.) |

Also: `theorem_statements.tex` — paper-1 theorem list with verification
cross-references.

**Paper 1** (the audit paper): the Bender–Mannheim generator Q is
*reconstructed* from the normal-form data (G, J, G₀) + positivity rather than
assumed; unique Hermitian-positive diagonalizer; stabilizer SO(2,ℂ)²;
corrected claims (canonical rescaling d_xd_y = γω₁ω₂, polar-factor
non-uniqueness); metric classification η′ = ρ†Wρ; distance d(I, M_obs) = 2r;
exact equal-frequency divergence; Lean-formalized Jordan no-go theorem.

**Paper 2**: minimum-distortion theorem — F(S) = ‖log S†S‖² ≥ 4r² over the
diagonalizer coset with exact closed form arccosh(cosh r cosh b) ± a
(mixed hyperbolic/flat Pythagoras); recognized as an orthogonal Cartan-norm
projection principle via the canonical compatible hull C_θ(H) = SL(2,ℂ)²
(totally geodesic ℍ³×ℍ³), proved in iff form, with the Sp(2n,ℂ) inter-mode
theorem. Plus the field-theory part: exact PT ground state, fidelity → √3/2,
occupation → 1/3 per UV mode pair, disjoint representations in every d ≥ 1.

**Paper 3**: the three-geometries separation (metric ≠ vacuum ≠ dynamical);
Cartan–parabolic decoupling (beam-splitter identity, analytic no-frame
lemma); orbit constancy ⇒ universal Fock obstruction Θ(VΛ^d) for *all*
positive metrics; one universal UV-dressed sector for d ≤ 3 anchored by the
□² vacuum, terminating sector hierarchy (∅ | Σ | (Σ,Π) at d<4 | 4≤d<8 | d≥8);
**spectral bridge theorem**: the selected vacuum's Wightman function is the
spectral two-point functional of the fourth-order operator for all Δ ≥ 0,
whose confluent limit is the Bateman–Turok Krein vacuum (arXiv:2607.00096) —
same quasifree functional, different completion; fourth-order Hadamard
theorem (WF = 𝒞⁺, log ρ singularity with universal coefficient 1/(8π²),
±KG-Hadamard split structure).

**Paper 4** (the gravity lift): classification and covariance-obstruction
theorem for free scalar-free Einstein–Weyl gravity (α = −3β).
Diffeomorphism reduction stratifies the phase space — PU pairing survives
exactly at helicity ±2 (γ = α/2, masses (M,0), M² = c₁/α); helicities
±1, 0 are *unpaired* massive ghosts subject to a completion trilemma
(positive norm / positive energy / standard reality: any two). Schur ⇒ no
covariant helicity-hybrid completion; exactly two covariant real forms
(positive pseudo-Hermitian with uniformly rotated massive reality, Krein
with standard gravitational reality) sharing one complex spectral quasifree
functional (covariant projector reassembly ½ : M²/2 : 1/6, 𝒩 = 4/c₁);
M-regular gauge-invariant Weyl correlator (DΠ^{(2,M)}D = DΠ₀D); conformal
boundary c₁ → 0 sectorwise (TT → □² Jordan, vectors → massless ghosts,
scalar → Weyl-null; count 4+2+0 = 6) at which the positive form terminates
(cond(N) → ∞) and only the Krein form continues.

## Reports (`reports/`)

- `verification.md` — paper-1 audit report: confirmed / corrected /
  unproved / failed, plus answers to the spec's 12 research questions.
- `variational-and-field-theory.md` — running log for papers 2–3: theorem
  statements, refuted claims (with what replaced them), freeze passes.
- `verification.json`, `regression.json` — machine-readable claim tables.

## Verification pipeline (`symbolic/`, `numeric/`, `lean/`)

Symbolic (SymPy):
- `verify_sympy.py` — paper-1 audit, 51 claims (Verifications A–L of the spec).
- `verify_variational_fock.py` — paper-2 claims (20 checks): distortion
  closed form, PT ground state, fidelity/occupation, r(k) identity.
- `verify_paper3_audit.py` — paper-3 claims (P1–P10): beam splitter, orbit
  constancy, sector expansions (coefficients 1/12 and 29/576), bridge
  Wightman functions, no-frame lemma.
- `verify_hadamard.py` — Hadamard audit (H1–H6): bisolution, commutator
  normalization, log-coefficient 1/(8π²), IR smoothness, ±Hadamard split.
- `verify_wolfram.wl` — independent Wolfram rail (not run: no Mathematica).
- `gravity_engine.py` — O(ε²) second variation of √−g(c₁R + αR²_μν + βR²)
  around flat space, per helicity sector (shared engine for G-checks).
- `verify_gravity_reduction.py` — paper-4 G1–G7: TT PU blocks, vector/scalar
  unpaired ghosts, scalaron decoupling, mode count, stabilizer 4→16.
- `verify_gravity_completion.py` — paper-4 G8–G9: quarter-turn trilemma,
  T₀·SO(2,ℂ) real-form coset, Schur no-hybrid, covariant D_tot, TT assembly.
- `verify_gravity_spectral.py` — paper-4 G10–G12: helicity kernels with
  symplectic residues, covariant projector reassembly, Weyl-correlator
  M-regularity, sectorwise conformal limits + cond(N) divergence.

Numeric (mpmath/numpy):
- `regression.py` — paper-1 regression, 4 parameter triples at 50–80 digits.
- `distortion_scan.py` — global optimization test of the minimum-distortion
  conjecture + invariant cross-checks.
- `cartan_checks.py` — hull Lie-closure dims, inter-mode normal space,
  first-variation identity, normalization dictionary.

Lean 4 + Mathlib v4.29.0 (`lean/`, builds with **zero `sorry`**):
- `PaisUhlenbeck/Definitions.lean` — J, G, G₀, M, K, N, S; K = J·M.
- `PaisUhlenbeck/Symplectic.lean` — K² = −(αβ)I; N² = 1; SᵀJS = J; det S = 1.
- `PaisUhlenbeck/NormalForm.lean` — SᵀGS = G₀ (division-free certificates).
- `PaisUhlenbeck/JordanObstruction.lean` — full 2×2 Jordan no-go theorem.

## Reproduce

```bash
cd symbolic && python3 verify_sympy.py             # paper 1 (~4 min)
cd symbolic && python3 verify_variational_fock.py  # paper 2
cd symbolic && python3 verify_paper3_audit.py      # paper 3
cd symbolic && python3 verify_hadamard.py          # paper 3, Hadamard
cd symbolic && python3 verify_gravity_reduction.py   # paper 4, G1–G7
cd symbolic && python3 verify_gravity_completion.py  # paper 4, G8–G9
cd symbolic && python3 verify_gravity_spectral.py    # paper 4, G10–G12
cd numeric  && python3 regression.py && python3 distortion_scan.py && python3 cartan_checks.py
cd lean     && lake exe cache get && lake build    # zero sorry
cd paper    && pdflatex main.tex; pdflatex variational-fock.tex; pdflatex fourth-order-vacuum.tex; pdflatex fourth-order-gravity.tex
```

Release tags: `paper1-v1.0`, `paper2-v1.1`, `paper3-v1.1`. Before submission: fill author
metadata (title pages are blank), check the "to appear" references, match
IR-extension conventions noted in paper 3's bridge theorem.
