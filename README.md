# Symplectic Reconstruction of the Pais–Uhlenbeck PT Metric

Verification project and paper series on the PT-symmetric Pais–Uhlenbeck
oscillator, the fourth-order scalar field, and quadratic gravity. Started
from the audit spec in `../Symplectic Reconstruction.md`; grew into eight
papers (an expository introduction, five technical papers on the free
theories, and two interaction papers), a Lean formalization, and a
machine-checked verification pipeline.

## Overview

The series does not propose a new free-theory cure for the
higher-derivative ghost. It classifies and canonically reconstructs the
known Bender--Mannheim positive quantization, relates it to the
Bateman--Turok Krein construction through a common **free complex spectral
covariance**, and separates the additional choices of real form,
involution, observable algebra, and completion. The free positive metric
is geometrically canonical, but that kinematic optimality does not imply
interacting stability: Paper 5 finds on-shell conversion obstructions to
its analytic deformation. At the split rational shell the same on-shell
matrix is exactly Krein-pseudo-Hermitian; the stronger one-sided
charge-null mechanism emerges only at the massless perfect-square
boundary. Paper 4 adds gauge reduction and Lorentz covariance and
classifies two free Einstein--Weyl real forms. Paper 6 then tests those
forms against the complete tree-level cubic and quartic vertex content:
cubic order is protected, while the physical `MM -> Mh` channel gives a
nonzero second-order deformation cocycle. The canonical
particle-number-diagonal Krein lift does not make that block null.

## The papers (`paper/`)

| # | File | Title | Status |
|---|------|-------|--------|
| 0 | `ghosts-geometry-reality.tex` / `.pdf` | **Ghosts, Geometry, and Reality in Fourth-Order Quantum Theories** (expository introduction to the series, incl. the interaction results) | draft (28 pp.) |
| 1 | `symplectic-diagonalization.tex` / `.pdf` | **Canonical Positive Symplectic Diagonalization of the Pais–Uhlenbeck Oscillator** | frozen, tag `paper1-v1.2` (17 pp.) |
| 2 | `variational-fock.tex` / `.pdf` | **The Pais–Uhlenbeck Metric as a Minimum-Distortion Principle, and the Representation Problem for the Fourth-Order Field** | frozen, tag `paper2-v1.3` (14 pp.) |
| 3 | `fourth-order-vacuum.tex` / `.pdf` | **The Universal Vacuum of the Fourth-Order Scalar Field: Metric Orbits, Fock Sectors, and the Krein Boundary** | frozen, tag `paper3-v1.3` (13 pp.) |
| 4 | `fourth-order-gravity.tex` / `.pdf` | **Gauge Reduction and the Completion Problem in Fourth-Order Gravity: PU Pairing, Covariant Real Forms, and the Conformal Jordan Boundary** | frozen, tag `paper4-v1.1` (15 pp.) |
| 5 | `interaction-obstructions.tex` / `.pdf` | **Interaction Obstructions, Resonant PT Breaking, and Doubled Jordan Symmetry in Fourth-Order Theories** | frozen, tag `paper5-v1.1` (17 pp.; accepted by team referee, then extended: 5:1 confirmation, Krein separation, literature repositioning, charge-null lemma + regulated-embedding proposition) |
| 6 | `einstein-weyl-interaction-obstructions.tex` / `.pdf` | **Interaction Obstructions in Einstein–Weyl Gravity: Cubic Protection, Second-Order Metric Failure, and Krein Visibility** | draft, major-review revision (30 pp.) |
| 7 | `conformal-residual-cohomology.tex` / `.pdf` | **Residual $SO(4,2)$ Cohomology of Free Weyl Gravity on the Conformal Cylinder** | draft; classical algebraic BV--BFV chain and energy-mode Krein completion certified |

Also: `theorem_statements.tex` — paper-1 theorem list with verification
cross-references.

General-audience article:
[`Before Worrying About a Gravitational Ghost, Ask Whether It Is Really There`](paper/before-worrying-about-a-gravitational-ghost.md)
explains the completed classical pure-Weyl BV–BFV result without assuming
advanced mathematics or physics.

Energy-mode analytic completion:
[`analytic_completion/README.md`](analytic_completion/README.md) documents
the infinite-index one-particle and bosonic Krein completions, closed
residual BRST operator, bounded Cartan contraction, and proof that completed
centered cohomology and its $I_2$ Gram matrix are unchanged.  It deliberately
does not claim a covariant metric-field Sobolev or Green-hyperbolic theorem.

Lorentzian cylinder field realization:
[`covariant_completion/README.md`](covariant_completion/README.md) proves the
tensor/vector curl identities, the local Green-hyperbolic factorization of
the reduced physical system, the exact field origin of the `E/A/L` towers,
and the field-induced branch Cauchy--Sobolev topology.  Its harmonic
transform is Krein-unitary onto the energy-mode one-particle completion.
The complete covariant BV Green theorem and distributional/Hadamard theory
are now separated more sharply.  A support-local ordinary-derivative
auxiliary BV realization has a certified four-row symbol witness and an
exact $66$-to-$30$ Fourier-complex deformation retract whose formulas are
support local.  The curved workstreams now additionally certify the exact
covariant action, gauge map and expanded action Hessian, including exhaustive
cancellation of all third- and fourth-order jets and exact formal
adjointness.  The nonlinear BV-canonical auxiliary shift gives the complete
local curved SDR, and the curved presymplectic comparison closes off shell up
to the certified improvement terms.  An exact null-symbol rank obstruction
rules out the original 24-field/9-gauge scalar-symbol witness for every
pointwise nondegenerate fibre pairing and every first-order companion: at a
null covector the Hessian and gauge symbols have ranks 11 and 9.  The
rank-two obstruction is the physical helicity-two module, not missing gauge
freedom.  The linearized Weyl symbol induces the exact isomorphism
`(1/4) I2` from the reduced Hessian quotient to the two-dimensional Weyl
helicity quotient.  The exact curved Bianchi--Bach decomposition now requires
the ten electric/magnetic Weyl components together with a sixteen-component
Cotton slot.  Its 34 covariant rows have temporal rank 26 and eight primary
constraints, and exhaustive comparison on all 150 Weyl two-jets proves the
curved equations and this local first-order closure.  Formal integrability
adds six secondary constraints.  The constraint-adjusted 26-state system is
exactly equivalent as a differential ideal, symmetric hyperbolic with causal
speeds, and has a complete sourced subsidiary identity.  The odd BV mapping
cylinder now gives the complete support-local all-row prolongation and its
nilpotent prolonged differential.  The prolonged Green witness and actual
BV Green homotopy, residual endpoint recovery, `SO(4,2)`-equivariant
transport, and prolonged current comparison are not yet proved.  Hadamard
theory also remains open.  A direct same-bundle
factorization of `B_lin+K T/2` is an optional strengthening, not a hidden
premise.

The generated
[`final_claim_dependencies.md`](covariant_completion/generated/final_claim_dependencies.md)
records the current fail-closed boundary:

```text
curved_operator_identity       = true
curved_deformation_retract     = true
curved_current_comparison      = true
final_covariant_H4             = false
```

The final flag remains false while the complete causal BV Green bridge is
absent.  The negative rank certificate and the positive reduced
Weyl-symbol isomorphism are both exposed independently.

The selected curvature route is split into explicit fail-closed flags:

```text
curved_EB_equations                = true
curved_EB_first_order_closure      = true
curved_EB_symmetric_hyperbolicity = true
curved_sourced_constraint_identity= true
curved_constraint_propagation     = true
EAL_curvature_spectrum_match       = true
support_local_prolongation_retract= true
prolonged_BV_operator_identity     = true
prolonged_green_witness            = false
curvature_causal_green_operators  = false
causal_green_homotopy              = false
causal_quasi_isomorphism           = false
residual_endpoint_recovery         = false
SO42_equivariant_transport         = false
prolonged_current_comparison       = false
```

The exact all-level curvature audit is also complete: symbolic BGG rank and
character identities show that the 26-state covariant equations carry
precisely the parity-complete `E/A/L` towers and that the Cotton graph adds no
second copy.  This is not inferred from a finite harmonic cutoff.

The BV-canonical Weyl/Cotton graph SDR, autonomous curvature compatibility
complex `26 -> 40 -> 14` with cotangent adjoint, causal curvature-block
solution operators, and analytic block Green witness are exact subtheorems.
The complete graded mapping cylinder is now exact.  The state map
`T=(C1,div C1)` and an order-two equation map satisfy
`E_curv T=A_eq E_aux` on the exhaustive 700-dimensional metric four-jet
fibre.  A sparse order-zero identity map satisfies
`N_curv A_eq=B_id C_aux`, including the differentially generated secondary
rows.  Their odd BV incidence, Koszul adjoints, canonical shears, nilpotent
all-row differential, and support-local SDR are certified, so both
`support_local_prolongation_retract` and `prolonged_BV_operator_identity` are
true.  The canonical direct-sum/conjugated degree-minus-one witness is also
an exact operator identity, and fourteen of its sixteen split diagonal
blocks are Green hyperbolic.  It does not close the theorem: the auxiliary
field block $E_{\rm aux}+KC$ and its cotangent copy are the two remaining
blocks and retain the scalar-wave rank obstruction.  The final witness must
therefore go beyond direct-sum conjugation, using two-way relative
auxiliary--curvature degree-minus-one terms that form a genuinely coupled
saddle operator, unless an independently Green-hyperbolic auxiliary
diagonal witness is found.  Two further fail-closed diagnostics sharpen this
open step.  At an arbitrary covector the auxiliary prenormal principal symbol
satisfies `(P2-q I)^2=0`, with Smith multiplicities `6/12/6` for the
algebraic/wave/biwave factors.  The formal lower factor `2q I-P2` is exact at
principal level, but its naive frozen lower-order completion has nonzero
orders zero through two, so it is not yet a local Green factorization.  The
complete invariant correction spaces have `dim D0=38` and `dim D1=93`.
Exact simultaneous cubic divisibility of both `DP` and `PD` leaves a
45-parameter family, so there is no cubic obstruction.  The
curvature-corrected quadratic and lower equations, including nonlinear
products of the first-order factor matrices, remain open.  Among the nine
allowed odd-adjoint relative pairs, no single pair gives reciprocal
coupling; the smallest two-way saddle uses pairs 4 and 5.  Its exact core is
the coupled `(M_aux,X_U,Y_U_sharp)` block with off-diagonal maps `R,S` and
their odd adjoints.  Its formal Schur complement contains curvature Green
operators and is therefore nonlocal, while the unreduced saddle is order two
and still lacks the required local first-order reduction.  The natural local
instantiation `A_F=pF A_eq`, `S=A_F^sharp`, `R=A_F^sharp J_U` is now ruled out
exactly: its balanced Douglis temporal principal matrix has rank at most
`107/116`, hence defect at least nine, zero temporal leading coefficient and
no positive symmetrizer.  This no-go applies only to that smallest pair-4+5
ansatz, not to larger relative witnesses or an additional local first-order
prolongation.  These are diagnostics, not theorem promotions: the same seven
causal/transport flags remain false.

The residual calculation is already complete: `residual_H4_is_C2` and
`residual_gram_is_I2` are inputs to the terminal transport gate.  The missing
theorem is a pairing-compatible causal BV bridge from compactly supported
metric/auxiliary data through an all-row curvature prolongation to Cauchy
data, the `E/A/L` module, and the residual endpoints.  It must include
compatible inhomogeneous sources and degree-`-1` retarded/advanced maps
`Lambda_±` with `Q Lambda_± + Lambda_± Q = 1`; symmetric hyperbolicity alone
does not establish this identity.

**Paper 1** (the audit paper): the Bender–Mannheim generator Q is
*reconstructed* from the normal-form data (G, J, G₀) + positivity rather than
assumed; unique Hermitian-positive diagonalizer; stabilizer SO(2,ℂ)²
(unitary part generically ℤ₂² in the canonical coordinates, never the
full U(1)²);
corrected claims (canonical rescaling d_xd_y = γω₁ω₂, polar-factor
non-uniqueness); metric classification η′ = ρ†Wρ; distance d(I, M_obs) = 2r;
exact equal-frequency divergence; Lean-formalized Jordan no-go theorem.

**Paper 2**: minimum-distortion theorem — F(S) = ‖log S†S‖² ≥ 4r² over the
diagonalizer coset with exact closed form arccosh(cosh r cosh b) ± a
(mixed hyperbolic/flat Pythagoras); recognized as an orthogonal Cartan-norm
projection principle via the canonical compatible hull C_θ(H) = SL(2,ℂ)²
(totally geodesic ℍ³×ℍ³), proved in iff form, with the Sp(2n,ℂ) inter-mode
theorem. Plus the field-theory part: exact PT ground state, fidelity → √3/2,
occupation → 1/3 per UV mode pair, and disjoint auxiliary standard-CCR
product representations under the identity embedding in every d ≥ 1;
the physical Dyson-transported completions are instead pointed-unitarily
equivalent.

**Paper 3**: the three-geometries separation (metric ≠ vacuum ≠ dynamical);
Cartan–parabolic decoupling (beam-splitter identity, analytic no-frame
lemma); orbit constancy ⇒ universal Fock obstruction Θ(VΛ^d) for *all*
admissible positive metrics on the common auxiliary algebra; terminating
ultraviolet sector hierarchy (no UV invariant for d ≤ 3; Σ for
4 ≤ d < 8; the unordered mass pair (Σ,Π) for d ≥ 8). Global
equivalence involving the doubly massless □² vacuum requires a separate
infrared analysis and is not claimed;
**spectral bridge theorem**: the selected vacuum's Wightman function is the
spectral two-point functional of the fourth-order operator for all Δ ≥ 0,
whose confluent limit is the Bateman–Turok Krein vacuum (arXiv:2607.00096) —
same quasifree functional, different completion; fourth-order Hadamard
theorem (WF = 𝒞⁺, log ρ singularity with universal coefficient 1/(8π²),
±KG-Hadamard split structure).

**Paper 4** (the gravity lift): within translation-invariant, quasifree,
mode-local constructions satisfying the spectral condition and Poincaré
covariance, a classification and covariance-obstruction theorem for free
scalar-free Einstein–Weyl gravity (α = −3β).
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

**Paper 5** (the interaction paper): deformation and obstruction theory
for the interacting completions. Three levels of failure of the positive
construction — geometric (the fixed-order deformation generators become
singular toward the Jordan boundary; the general Rₙ ~ ε^{−3n/2} law is
conjectural),
cohomological (exact on-shell conversion classes at ω₁ = 3ω₂, order 2,
and ω₁ = (3/2)ω₂, order 3, gauge-independent, with a transfer-lattice
selection rule), and spectral (a complex-conjugate pair in the E = 27ω₂
multiplet's effective resonant-shell matrix, exact by Sturm certificate;
formally defined PT breaking with 𝒜 = Π∘Θ constructed; persistence
for the full unbounded operator remains open). In the perfect-square field
theory an even-ghost
rule protects the positive metric at first order, but the momentum
continuum makes branch-changing H+L → L+L shells generic and the
analytic deformation of the canonical pointed metric is obstructed on a
nonempty open shell subset (exact value 401√6/(39424g²) at a rational
kinematic point). What survives at
the massless boundary is the exact two-field exchange U↔V of
ℒ = −∂U·∂V + (λ²/2)U²V² (the Bateman–Turok O(1,1) embedding; they
identified the exchange as ghost parity) — a sector-exchanging
involution between two oppositely oriented interaction-generated
Jordan sectors, whose linearization is the bounded confluent limit of
the regulated branch parity on the doubled space. The hierarchy
conjecture's first prediction is confirmed computationally: 5:1 is
unobstructed through order 3 and obstructed at order 4 by exactly
−(203125√5/2341011456)(a₁a₂†⁵−a₁†a₂⁵). And the two completions
*separate* in the verified perturbative setting: at the rational shell
point the complete reachable on-shell T is exactly ghost-parity (Krein)
pseudo-Hermitian and the obstruction lives entirely in its κ-odd block,
while the analytic positive pointed-metric deformation is obstructed. The
result does not exclude a nonanalytic or differently pointed positive
completion. In the cross-paired charge frame the mapped split vacuum has
both charge directions, with the exact ratio
S_UU/S_VV = (δ/2g)² = ε/g. One-sided charge nullity holds exactly on the
ε = 0 confluent line; the Bateman–Turok massless point additionally has
μ² = 0.

**Paper 6** (the interacting-gravity paper): applies Paper 5's
deformation complex to the two covariant free real forms classified in
Paper 4. The exact Einstein consistent truncation kills all tree
amplitudes with one massive and otherwise massless external legs, while
equal-mass kinematics closes the remaining odd-massive cubic channel, so
the first-order obstruction vanishes. At second order the open process
`MM -> Mh` has a nonzero complete tree amplitude: an independent
Einstein-frame rail gives pole residue `sqrt(3)/8`, and the original
fourth-order perturbiner gives the exact interior-shell reduced
certificate `7881241032/5584765625`. A Born--deformation identity now
proves that the anti-Hermitian part of this stationary Born block is the
full metric-deformation cocycle, including both quartic contact and
two-cubic exchange terms. Within the explicitly stated natural,
particle-number-diagonal, cluster-multiplicative class, the induced Krein
grading is `(-1)^N_M`; the obstruction is non-null, survives physical
BRST cohomology, and admits no uniform abelian charge-null analogue.

**Paper 7** (the residual conformal branch): starts from pure-Weyl metric
fields on the conformal cylinder, derives the minimal and gauge-fixed
BV--BFV state complex, and gauges all fifteen residual conformal generators
for the selected closed-universe boundary problem.  The centered
one-particle cohomology vanishes; exactly the two ghost-dressed chiral
curvature-square vertex classes `[W_+^2]` and `[W_-^2]` survive, with
field-induced Gram matrix `I2`.  The normalized `E/A/L` module now has an
infinite-index energy-mode Krein completion, its symmetric bosonic Fock
space has fundamental symmetry `Gamma_s(J)`, and the residual differential
has a closed maximal block realization.  A bounded Cartan contraction
proves closed range and reduces completed cohomology to the unchanged finite
centered block.  This is not a positive graviton Hilbert-space theorem, a
quantum anomaly result, or a full covariant BV Green-complex theorem.  At the
reduced one-particle level, the Lorentzian tensor/vector fields now have an
exact Cauchy--Sobolev realization: the TT branches use
`H^1 + L^2`, the vector branch uses `H^(3/2) + H^(1/2)`, and the resulting
harmonic transform is Krein-unitary onto the completed `E/A/L` module.

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
- `gravity_perturbiner.py` — shared exact multi-wave Einstein–Weyl
  perturbiner used by the cubic and four-point checks.
- `gravity_four_point.py` — import-safe exact four-point assembler exposing
  the quartic contact and all three gauge-fixed exchange channels.
- `verify_gravity_cubic.py` — gravity G13–G14 in the original
  fourth-order variables: exact multi-wave perturbiner, one-massive-leg
  cubic rule, Ward identities, nonzero `MMM`/`MMh` amplitudes and
  massive-pole factorization.
- `verify_gravity_factorization.py` — independent Einstein-frame G14
  rail: cubic-potential cancellation, exact amplitudes
  `A3(MMM)=-sqrt(6)/8` and `A3(MMh)=-sqrt(2)/8`, symbolic Ward identity,
  complete five-polarization residue numerator `sqrt(3)/32`, and explicit
  massive inverse-kernel normalization.
- `verify_gravity_g15.py` — exact real-shell `MM -> Mh` certificate with
  quartic contact plus all exchanges, Ward/Bose/internal-gauge checks, and
  pole-factorization regression.
- `verify_gravity_obstruction.py` — gravity G17: termwise uniform
  quarter-turn of the full connected second-order Born operator,
  reversed-process physical adjoint, shell projection, the exact nonzero
  obstruction `-2i A_K`, first-order metric-ambiguity independence, and
  the exact Born--deformation-source identity.
- `verify_gravity_krein.py` — gravity G18: covariant one-particle grading
  commutant, cluster-factorizing Fock lift, exact non-null Krein quadratic
  block, continuous-charge no-go, and BRST-cohomology survival.
- `verify_gravity_paper6.py` — one-command Paper-6 reproduction driver;
  use `--quick` to omit only the slower G15 pole regression.
- `verify_paper1_referee.py`, `verify_paper2_referee.py`,
  `verify_paper3_referee.py` — referee-round claim verification
  (spectrum of Q, normalization proposition; pointed-unitary identity;
  bridge signs, Hadamard remainder, IR anchor, Cartan convention).
- `verify_interaction_deformation.py` (ID1–ID10),
  `verify_interaction_order3.py` (SR/O3), `verify_pt_breaking.py`
  (PT/PS), `verify_perfect_square.py` (PS-A–H), `verify_two_field.py`
  (TF1–TF7), `verify_sector_obstruction.py` (SO1–SO7),
  `verify_hardening.py` (HX1–HX3) — paper-5 interaction-deformation
  program: cubic PU deformation through third order, 3:1/3:2
  obstructions, spectral PT-breaking, selection rules, perfect-square
  field theory, exact two-field rewriting and sector-exchange κ₀,
  sectorwise second-order obstruction (exact value 401√6/39424),
  confluent parity theorem.
- `verify_doubled_theory.py` (DQ1–DQ9) — doubled/Krein structure:
  O(1,1) hyperbolic-polar form and Noether current, mirror-adjoint
  relation H_B = WH_A†W† exact with W = ι∘(−1)^{N_ghost} (= Krein
  pseudo-Hermiticity), graph theorem (positive invariant half ⇔
  pointed positive metric), finite-time paired pseudo-unitarity,
  κ-odd localization of the on-shell obstruction, classical Ward
  identity with exact regulator breaking.
- `verify_obstruction_null.py` (ON1–ON4) — obstruction-to-null program:
  finite-particle charge-null lemma (graded Krein trace), canonical
  Bogoliubov map of the regulated split theory onto the cross-paired
  Bateman–Turok charge basis, exact law S_UU/S_VV = ε/g for the mapped
  vacuum's charged squeezing (one-sided iff ε = 0; the BT massless point
  also has μ² = 0), confluent coefficient −g/(4w²) (−1/(4w²) at g = 1),
  exact reference-dispersion no-go, and residual-frame runaway evidence.
- `verify_51_order4.py` (FO1–FO9) — order-4 machinery (programmatic
  adjoint-series word generation, re-derives orders 2–3 exactly):
  5:1 obstruction confirmed at order 4, ω₂⁻⁹ scaling, gauge
  independence, R₄ = O(ε⁻⁶).

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
cd symbolic && python3 verify_gravity_paper6.py       # paper 6, full suite
cd symbolic && python3 verify_conformal_paper_free.py --guards  # paper 7, full suite
cd numeric  && python3 regression.py && python3 distortion_scan.py && python3 cartan_checks.py
cd lean     && lake exe cache get && lake build    # zero sorry
cd symbolic && for f in verify_interaction_deformation verify_interaction_order3 verify_pt_breaking verify_perfect_square verify_two_field verify_sector_obstruction verify_hardening verify_doubled_theory verify_51_order4 verify_obstruction_null; do python3 $f.py; done   # paper 5
cd paper    && for f in symplectic-diagonalization variational-fock fourth-order-vacuum fourth-order-gravity ghosts-geometry-reality interaction-obstructions einstein-weyl-interaction-obstructions conformal-residual-cohomology; do pdflatex $f.tex; done
```

Release tags: `paper1-v1.2`, `paper2-v1.3`, `paper3-v1.3`,
`paper4-v1.1`, `paper5-v1.1` (current freezes; earlier tags remain for
history). Before submission: replace
"companion paper" citations with arXiv IDs, check the "to appear"
references, match IR-extension conventions noted in paper 3's bridge
theorem, mint a DOI for the archived commit.
