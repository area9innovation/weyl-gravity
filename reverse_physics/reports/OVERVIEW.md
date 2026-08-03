# Reverse physics on the Weyl-gravity substrate — what the probe found

A self-contained account of an experiment: can the certificate substrate built
for the pure-Weyl programme carry **reverse physics** in the Carcassi–Aidala
sense — not deriving laws from axioms, but finding the minimal physical
assumptions a law is equivalent to?

The answer is yes, with texture. Three of the four findings are **negative
results about the programme's own shape**, which is the more useful outcome.

---

## 1. The question

Reverse physics is reverse mathematics applied to physical law. Reverse
mathematics proves `T ⟺ A` over a weak base theory and then shows `A` is
independent. Reverse physics asks the same of a physical law: which assumptions
is it *equivalent* to, not merely implied by?

The test case throughout is **Hamiltonian privilege**: deterministic and
reversible evolution is standardly said to conserve information, and Hamiltonian
structure standardly said to follow. Which assumption does the work?

Three things are needed. The substrate already supplied one and a half.

| | what it needs | status at the start |
|---|---|---|
| **Necessity** | a system satisfying every assumption but one, in which the law fails | the shape the substrate already had — its no-go certificates are exactly this |
| **Sufficiency** | a derivation | exact rational computation cannot prove; needed a proof assistant |
| **Honest ledger** | what each derivation consumed | `assumption_tags`, `claim_boundary`, `does_not_establish`, `generality_level` — already load-bearing |

---

## 2. The carriers

Two, deliberately unlike each other.

**The linear carrier.** Linear vector fields `ẋ = Ax` on `ℝ^{2n}` with a fixed
degree-of-freedom split and symplectic form. Everything is a rank computation
over ℚ.

**The torus.** Trigonometric-polynomial vector fields on `T⁴`. Everything
block-diagonalises over Fourier modes, so each mode is an exact 8-parameter
rational problem — and, unlike a vector space, the manifold has cohomology.

**The stochastic carrier** (added last). Four states, column-stochastic evolution
on distributions — the ensemble picture. Added because it is the only one of the
three in which determinism and reversibility *can fail*.

---

## 3. What was found

### 3.1 The assumption gap splits into a local part and a topological part

On the torus the chain has **four** levels, not three:

```
Hamiltonian ⊆ symplectic ⊆ marginal ⊆ volume-preserving
```

The linear carrier only has three, because `H¹(ℝ⁴) = 0` collapses *preserves ω*
and *is Hamiltonian* into one condition. Computed in Forge with exact rational
rank:

| N | vol | marg | symp | ham | **symp−ham** | marg−symp | vol−marg |
|---|---|---|---|---|---|---|---|
| 0 | 4 | 4 | 4 | 0 | **4** | 0 | 0 |
| 1 | 244 | 180 | 84 | 80 | **4** | 96 | 64 |
| 2 | 1876 | 1300 | 628 | 624 | **4** | 672 | 576 |
| 3 | 7204 | 4900 | 2404 | 2400 | **4** | 2496 | 2304 |

The two local gaps **grow** with resolution. The symplectic→Hamiltonian gap is
**4 at every truncation** and every nonzero Fourier mode contributes exactly zero
to it — the whole obstruction sits in the zero mode and equals `b₁(T⁴)`. Nothing
in the computation mentions cohomology; the Betti number is reproduced, not
assumed.

Later proved for *all* modes in Rocq, which needed no induction: at a mode with
some nonzero frequency the potential is *constructed explicitly* from a direction
whose frequency doesn't vanish, and that construction is indifferent to how large
the mode is.

**So part of what is missing between "conserves information" and "is Hamiltonian"
is not a physical postulate at all.** It is a property of the state space,
invisible to any assumption formulated pointwise, per degree of freedom, or
differentially, at any resolution.

### 3.2 Two very different carriers localise the gap in the same place

On the linear carrier the residual obstruction sits in the inter-DOF block
`J A₁₂ = −(A₂₁)ᵀ J`. On the torus, `symplectic ⟹ marginal` consumes only **two of
the six** closedness equations — the *intra*-degree-of-freedom pairs — and the
other four are proved not recoverable.

A vector space measured by rank and a compact manifold measured by cohomology put
the gap in the same place: **what a per-degree-of-freedom condition cannot express
is inter-degree-of-freedom coupling.**

### 3.3 The physical/geometric decomposition of the law is not canonical

The reversal (§4) decomposes the law into three independent assumptions, of which
only two can be stated in physical vocabulary. The third, `inter_dof_closed`, is
a geometric consistency condition with no physical reading.

That looked like a defect until the split analysis explained it:

> For **every** pairing `P` of the four coordinates, `intra_P ∧ inter_P` is the
> same proposition — closedness — which mentions no split at all.

So the third assumption is the **remainder of a bookkeeping choice**. Having
elected to call two of the six equations "each degree of freedom conserves its own
information", the third is whatever is left over. Choose a different split and the
same content divides differently; the law admits three such decompositions.

And the first assumption is itself **not split-independent**: the same field is
marginal for the standard degree-of-freedom split and not for a rotated one, with
*both* splits genuinely symplectic.

**A reverse-physics assumption ought not to depend on a coordinate choice.
"Each degree of freedom independently conserves information" does.** Only its
conjunction with the remainder is split-independent — and that conjunction is just
*preserves ω*, the law's own geometric content, not a physical postulate.

This bears directly on Carcassi–Aidala's *infinitesimal reducibility*, which
presupposes a decomposition into independent degrees of freedom. Here that
decomposition is provably a choice, and any assumption built on it inherits the
arbitrariness.

### 3.4 The assumption vocabulary was redundant

`RP-DETERMINISTIC` and `RP-REVERSIBLE` appeared under `consumed` in every
certificate and under `under_test` in none — structurally, because on the
Hamiltonian carriers every evolution is `exp(tA)` and neither can fail.

On the stochastic carrier, where both *can* fail:

```
reversible  ⟺  deterministic ∧ conserves_information
```

**Reversibility was never an independent postulate.** Both conjuncts are
necessary (collapse is deterministic and destroys information; uniform mixing
conserves it and is not deterministic), but together they force it.

The existing `consumed` listings were left intact rather than merged, because the
equivalence is proved for four states and one step, not for the continuous
carriers those certificates use. But they should not be read as a count of
independent postulates.

---

## 4. The reversal

The one positive structural result. Over the declared carrier:

```
hamiltonian  ⟺  A1 ∧ A2 ∧ A3
```

| | assumption | vocabulary |
|---|---|---|
| **A1** | each DOF independently conserves its own phase-space area | physical |
| **A2** | the cross-DOF closedness equations | geometric (see §3.3) |
| **A3** | no uniform drift — at the zero mode the field vanishes | topological |

The forward direction is the reversal proper: from the law alone, each assumption
is derived. Each is independent, witnessed explicitly.

**What this is not.** The base theory — fixed `ω`, fixed split,
trigonometric-polynomial fields — is *definitional context, not an axiom schema*.
Reverse mathematics needs a base one can weaken and compare against. This is an
equivalence over a declared carrier with independence: real, and the half that was
missing, but not a reversal over a weakenable base.

---

## 5. What the substrate actually contributed

The finding least visible in any certificate: **the bookkeeping fields generated
the results.**

- A2's non-physicality surfaced only because the schema forced a `vocabulary`
  label on every assumption.
- The isotropic-pairing correction happened only because the record claimed
  something about *degree-of-freedom splits*, so the word had to mean something —
  and it turned out that of the three ways to pair four coordinates, exactly one
  is symplectic.
- The redundancy came from auditing `consumed` against `under_test`.
- The local/topological split came from `generality_level` forcing a statement of
  which truncations were covered, which turned "constant in N" into a question.

A looser process would have produced four positive-sounding certificates and none
of the four findings.

Two other pieces of discipline paid: **negative controls** caught a wrong witness
during development (a candidate control that was itself non-symplectic), and
**fail-closed hash pinning** caught its own misuse twice — a harness script pinned
alongside the mathematics, recorded and then removed rather than re-bumped.

---

## 6. What was not established

Stated plainly, because the certificates each carry their own version:

- **The physics is modest.** `symplectic/Hamiltonian ≅ H¹` is classical symplectic
  geometry; the stochastic result is a classical Markov fact. What is new is the
  assumption analysis and the mechanization, not the underlying mathematics.
- **No reversal over a weakenable base** — see §4.
- **No `Sp(4)`-orbit statement.** Split-dependence is witnessed between two
  admissible splits and cancellation proved for three coordinate pairings; the
  continuum is not quantified over.
- **No physical reading of A2** — §3.3 explains why it resists one; it does not
  supply one.
- **Nothing transfers between carriers.** The stochastic equivalence is four
  states and one step; the torus results are flat `T⁴` and polynomial fields.
- **Not a reproduction, confirmation, or refutation of Carcassi–Aidala's own
  derivation.** This tests candidate assumptions on declared carriers; it does not
  reconstruct their argument.
- No quantum, causal, or field-theoretic claim anywhere.

---

## 7. The certificates

| certificate | carrier | says |
|---|---|---|
| `..._LINEAR_G0_V1` | linear, n=1,2 | marginal conservation necessary, not sufficient; obstruction in the inter-DOF block; survives to finite time |
| `..._GENERAL_N_V1` | linear, all n | separation threshold exactly n=2; gap `2n(n−1)` grows quadratically |
| `..._TORUS_G1_V1` | `T⁴`, N ≤ 3 | four-level chain; gap `= b₁ = 4`, entirely zero-mode; local gaps grow |
| `..._TORUS_ALL_MODES_ROCQ_V1` | `T⁴`, all modes | the topological step proved, no induction needed |
| `..._TORUS_FULL_CHAIN_ROCQ_V1` | `T⁴`, all modes | full chain, both inclusions strict; marginal = intra-DOF content exactly |
| `..._TORUS_REVERSAL_ROCQ_V1` | `T⁴`, all modes | the reversal: law ⟺ A1 ∧ A2 ∧ A3, each independent |
| `..._TORUS_SPLIT_ROCQ_V1` | `T⁴`, all modes | the decomposition is not canonical; corrects the split-dependence claim |
| `..._STOCHASTIC_ROCQ_V1` | 4 states | reversibility is not an independent assumption |

Five zero-axiom Rocq modules, `coqchk` axiom section `<none>`, five fail-closed
negative controls, one Forge gate on both backends under ASan, two independent
Python rails.

```bash
cd rocq && ./run.sh                                          # the proofs
PYTHONPATH=. python3 -m unittest discover -s reverse_physics/tests -t .
```

---

## 8. Where it stands

The question that opened the probe is answered: the substrate carries reverse
physics, and the discipline is what makes it worth doing rather than an
elaborate way to restate known geometry.

The Hamiltonian-privilege line is well mined. The remaining declared gates —
`SP4_ORBIT`, `STOCHASTIC_GENERAL_N`, `PARAMETERISED_BASE` — are refinements of
things already known and would add certificates without adding findings.

The direction with genuine yield is a **second law**. Reverse physics pays off as
a *lattice* of law/assumption pairs, and this probe has one law plus a
side-result. The stochastic carrier is the natural home for a second, and
majorization gives an exactly-rational route to it that avoids the logarithms
which would otherwise break exact arithmetic.
