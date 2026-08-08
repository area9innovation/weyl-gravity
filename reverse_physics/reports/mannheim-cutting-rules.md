# The loop-unitarity theorem, and the point pure Weyl gravity sits at

**Certificate** `REVERSE_PHYSICS_MANNHEIM_CUTTING_RULES_V1`
**Verifier** `reverse_physics/mannheim_cutting_rules.py --check` — 14 checks, all PASS
**Dependency tag** `LOCAL-ALGEBRAIC`
**Lifecycle** `CLASSIFIED`
**Source read** P. D. Mannheim, *Unitarity of loop diagrams for the ghost-like
`1/(k²−M₁²) − 1/(k²−M₂²)` propagator*, Phys. Rev. D **98**, 045014 (2018),
[arXiv:1801.03220](https://arxiv.org/abs/1801.03220)

> Nothing in this repository cited this paper. It is the only one in the
> fourth-order-gravity literature about **loop diagrams** rather than free-field
> norms, and its closing paragraph applies itself to conformal gravity by name.
> So it had to be read before any loop calculation in pure Weyl gravity could be
> scoped. The answer is in the paper, and it is not in the closing paragraph.

---

## 1. Why this was worth reading at all

The paper's last substantive sentence is:

> *"Conformal gravity is thus offered as a fully consistent and renormalizable
> quantum theory of gravity."*

If that stands as written, then a loop calculation in pure Weyl gravity has an
imported prescription, and this programme's ghost stream has a settled boundary
condition. The question is therefore not whether Mannheim is right about the
theory he proves a theorem about. It is **whether pure Weyl gravity is that
theory.**

## 2. The answer is Section VI, in the author's own words

Section VI studies the equal-frequency limit — coincident poles — and ends:

> *"However, since non-stationary states are involved in the ε = 0 Jordan-block
> case, the standard cutting rules would not apply."*

Pure Weyl gravity is a coincident-pole theory. Its propagator is `1/k⁴`, a double
pole at the origin, and the same paper calls it *"a pure fourth-order derivative
Jordan-block theory"*.

Section VI also records, independently, that at coincidence the partial-fraction
decomposition *"becomes undefined, with the limit being singular"*, that the
commutation relations *"become singular"*, and that the Hamiltonian *"cannot be
brought to a Hermitian form at all, as it instead becomes of non-diagonalizable
Jordan-block form."*

So the paper contains both a concession and a claim. Section VII is what
reconciles them. This gate computes the bridge in order to name the step that
carries the weight.

## 3. Eq. (84) contains Eq. (76) — the object of §VII is the object of §VI

Mannheim's Eq. (84) partial-fractions the massless propagator. Verified here as
an identity in `ℚ[E, ω]` — cleared by `4ω³(E−ω)²(E+ω)²`, both sides reduce to the
same polynomial, so this is a coefficient comparison and not a sampled family:

```
LHS = -4*w^3
RHS = -4*w^3
```

Its positive-energy bracket is, coefficient for coefficient, Eq. (76) — the
equal-frequency Jordan-block Green's function of Section VI:

| ω | simple-pole coeff | double-pole coeff | Eq. (76) = Eq. (84) half |
|---|---|---|---|
| 1 | 1/4 | −1/4 | ✓ |
| 2 | 1/32 | −1/16 | ✓ |
| 3 | 1/108 | −1/36 | ✓ |
| 5 | 1/500 | −1/100 | ✓ |

Mannheim states this in a single clause — *"With (84) recovering (76) at the
E = +ω pole"* — and it is the hinge of the entire disposition, so it is checked
rather than taken. **The object Section VII declares viable is the object
Section VI excludes from the standard cutting rules.**

## 4. What the reconciling step assumes

Section VII's route is Eq. (85)–(86): build the massless propagator as

```
1/k⁴  =  lim_{M²→0}  d/dM² [ 1/(k² − M² + iε) ]
```

and then, since *"the M_i² → 0 limit is continuous, we can determine the cutting
rules for the massless theory before we take the M_i² → 0 limit."*

That is the named assumption, and the reason it is an assumption is arithmetic.
Write the fourth-order line by partial fractions with `m_i = M_i²`. The
functional a cut integrates a test function against is

```
W[f]  =  Σ_i R_i f(m_i)  =  ( f(m₁) − f(m₂) ) / (m₁ − m₂)
```

On the monomial ladder `f = sⁿ` this is exact and rational — verified over 12
rational pairs (integers, fractions, negatives, both orderings) for `n ≤ 8`:

```
W_n(m₁,m₂) = h_{n−1}(m₁,m₂)        W_0 = 0        W_1 = 1
at m₁ = m₂ = m:   W_n → n·m^(n−1)  =  d/ds sⁿ |_{s=m}
```

So the coincidence limit of the cut weight is the **derivative-evaluation
functional** `f ↦ f′(m)`, i.e. `−δ′(s−m)`: **total mass zero, first moment one.**

A derivative of a delta is not a positive measure, and not a measure of any
definite sign. A cutting rule is a resolution of the identity over intermediate
states with positive weight, and this functional admits none.

And that is precisely what `d/dM²` does: it is the operation carrying
`δ(s−M²)` to `−δ′(s−M²)`. **The step that makes the propagator's limit
non-singular is the step that destroys the positivity of the cut weight.** The
propagator's limit was never in doubt — `1/(k²+iε)²` is perfectly finite. The
state-space decomposition is what fails to have a limit.

## 5. The theorem's own states go null

Independent of the above, from the same paper's Appendix A, Eq. (A2) — the
one-particle normalisation whose positivity **is** the theorem:

```
[a_i, a_i†]  =  [ 2 (M₁² − M₂²) (k̄² + M_i²)^{1/2} ]^{-1} δ³(k̄ − k̄′)
```

Its rational core is `1/(m₁ − m₂)`. Exactly, and for every separation:

| separation | `R₁` | rescaled norm scales as |
|---|---|---|
| 2 | 1/2 | 2 |
| 1 | 1 | 1 |
| 1/2 | 2 | 1/2 |
| 1/4 | 4 | 1/4 |

`(m₁ − m₂) · R₁ = 1` identically — a simple pole in the separation. The
positive-norm states the theorem is about are not merely hard to track at
coincidence. **They are null there.** Negative norm has been traded for *zero*
norm, which is the repeated finding of this programme's ghost stream from the
other side: the signature is an **order**, not a sign.

## 6. Controls, and they are live

Every control was mutation-tested; a gate that cannot fail establishes nothing.

- **Known answer.** A genuine second-order propagator has cut weight of total
  mass **1**, a positive measure. It separates from the fourth-order `W_0 = 0`.
- **The obstruction is not "taking a limit".** A *sum* of two simple poles,
  `1/(s−m₁) + 1/(s−m₂)`, has residues `(1, 1)`: no pole in the separation and a
  healthy coincidence limit `2/(s−m)`. So the obstruction is the fourth-order
  **product** structure, not the act of coalescing poles.
- **Non-vacuity.** The ladder is not identically zero for `n ≥ 2`, so `W_0 = 0`
  carries information rather than being a bookkeeping artefact.
- **Fail closed.** The residue routine refuses `m₁ = m₂` rather than silently
  returning a value.
- **The pencil control tracks the right thing.** `M(ε) = [[ω,1],[ε²,ω]]` is
  diagonalizable for every `ε ≠ 0` and not at `ε = 0` (alg 2, geo 1). Critically,
  a scalar matrix `ω·I` is *also* eigenvalue-degenerate and **is** reported
  diagonalizable — so the control detects non-diagonalizability, not mere
  degeneracy. `ghost_harmless` already established that the Bender–Mannheim
  quasi-Hermiticity route requires **diagonalizable and real spectrum**; that
  criterion is imported as a statement here, not re-derived, and this control
  shows which conjunct fails and exactly where.
- **The Eq. (84) check detects its own corruption.** Flipping one term's sign
  makes the polynomial comparison fail.

## 7. What this does not establish

- **Not** that pure Weyl gravity is non-unitary. Only that PRD 98, 045014 does
  not cover it — by its own Section VI — and that the reconciling step is an
  assumption rather than a corollary.
- **Not** that no cutting rule exists on the Jordan-block state space. One may.
  Constructing it **directly**, rather than as a limit of the non-degenerate
  construction, is the open problem this names. Nobody has done it.
- **Nothing about `g−2`.** No value, bound, or sign for a muon anomalous
  magnetic moment in Weyl gravity is claimed or approached here.
- **Nothing `LORENTZIAN-CAUSAL`.** No Lorentzian propagator, Hadamard state,
  renormalized time-ordered product, or QME theorem is claimed or used.

## 8. Consequence for the calculation this was scoped for

A one-loop lepton vertex in pure Weyl gravity can be **written**: the amplitude
is finite and the Berends–Gastmans diagram template applies with
`κ²/k² → 1/(α k⁴)`. What cannot currently be done is **certify that its
imaginary part is a sum over positive-norm intermediate states**, because the
only published prescription for that is proved off the coincident-pole point and
its states go null on it.

So the honest ordering is: the degenerate cutting rule is upstream of the number,
not downstream. That is a question this repository is equipped for — Papers 00,
05, 06, 07 and 15 own the Jordan-block and Krein machinery — and it is the
cheaper of the two problems.

## 9. Provenance

Read from `arXiv:1801.03220v3` (18 pp.), retrieved 2026-08-08 from
`export.arxiv.org`. Quotations are from §VI, §VII, Eqs. (73)–(86), and
Appendix A(2). All arithmetic is exact over `ℚ` via `fractions.Fraction` and a
dependency-free bivariate polynomial routine; no floating point appears
anywhere. The module imports nothing from the repository.
