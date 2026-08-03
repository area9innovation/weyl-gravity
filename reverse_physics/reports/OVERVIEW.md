# Reverse physics on the Weyl-gravity substrate — what the probe found

A self-contained account of an experiment: can the certificate substrate built
for the pure-Weyl programme carry **reverse physics** in the Carcassi–Aidala
sense — not deriving laws from axioms, but finding the minimal physical
assumptions a law is equivalent to?

The answer is yes, with texture. Of the nine findings, **five are negative
results** — the more useful outcome. The fifth is the only place a *lattice*
appeared: two laws that constrain each other rather than a list of independent
results. The sixth turned outward, and engages the Carcassi–Aidala programme's
own open conjecture for general relativity. The eighth is the discipline turned
on this document: an interpretation published here in §3.7 was **retracted**,
with proof, after an audit found it backwards.

The ninth (§3.9) is the one a reviewer should read first, because it answers the
objection the other eight invite: **it does reverse physics on Weyl gravity
itself**, not on a carrier. The action turns out to be *equivalent* to five
assumptions rather than implied by six — one of the usual inputs is derivable —
and one assumption is independent and redundant at the same time, depending on
whether you are classifying actions or field equations. The separation of
physics from mathematics that made that visible is written up on its own in
[`PHYSICS-VS-MATH.md`](PHYSICS-VS-MATH.md).

---

## 1. The question

Reverse physics is reverse mathematics applied to physical law. Reverse
mathematics proves `T ⟺ A` over a weak base theory and then shows `A` is
independent. Reverse physics asks the same of a physical law: which assumptions
is it *equivalent* to, not merely implied by?

The first test case is **Hamiltonian privilege**: deterministic and reversible
evolution is standardly said to conserve information, and Hamiltonian structure
standardly said to follow. Which assumption does the work?

A second law — the arrow of disorder — joined later, on a third carrier, and
turned out to consume the same assumption (§3.5). That is what makes this a
lattice rather than a sequence.

Three things are needed. The substrate already supplied one and a half.

| | what it needs | status at the start |
|---|---|---|
| **Necessity** | a system satisfying every assumption but one, in which the law fails | the shape the substrate already had — its no-go certificates are exactly this |
| **Sufficiency** | a derivation | exact rational computation cannot prove; needed a proof assistant |
| **Honest ledger** | what each derivation consumed | `assumption_tags`, `claim_boundary`, `does_not_establish`, `generality_level` — already load-bearing |

---

## 2. The carriers

Three, deliberately unlike each other.

**The linear carrier.** Linear vector fields `ẋ = Ax` on `ℝ^{2n}` with a fixed
degree-of-freedom split and symplectic form. Everything is a rank computation
over ℚ.

**The torus.** Trigonometric-polynomial vector fields on `T⁴`. Everything
block-diagonalises over Fourier modes, so each mode is an exact 8-parameter
rational problem — and, unlike a vector space, the manifold has cohomology.

**The stochastic carrier** (added last). Four states, column-stochastic evolution
on distributions — the ensemble picture. Added because it is the only one of the
three in which determinism and reversibility *can fail*, and it later turned out
to be where the second law lives too.

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

### 3.5 The two laws close a loop

A second law landed on the stochastic carrier: **information conservation entails
that disorder never decreases.** Exactness survived because purity `Σpᵢ²` is the
exact rational content of the Rényi-2 entropy `−log(Σp²)` — and since `−log` is
monotone, *entropy does not decrease* **is** *purity does not increase*, with no
logarithm anywhere. The whole analytic content is one polynomial identity settled
by `ring`.

Then the equality case, both directions:

```
reversible  ⟺  no entropy production
```

So `conserves_information` is load-bearing for **both** laws — it makes
reversibility redundant (§3.4) and it entails the arrow of disorder — and
reversibility *is* the absence of entropy production. **A cycle, not a directed
edge.**

This is the only place in the probe where a lattice appeared. One law is a data
point; two laws that constrain each other is structure, and structure is what
reverse physics is for. Everything in §3.1–3.4 is about a single law; this is
the finding that needed a second.

### 3.6 Counting degrees of freedom is impossible in a conformally invariant theory

The only finding that engages their programme rather than our carriers, and the
one place this being a *Weyl-gravity* repository mattered.

Their unpublished GR conjecture — *GR ⟺ det/rev + DOF independence for
infinitely many dense DOFs* — needs a degree-of-freedom count, proposed as a
spatial volume. They also present a **trilemma** for such counts (every point a
single DOF · finite volume finitely many · additive) with three resolutions:
a density, the counting measure, or a non-additive "quantum measure". They drop
additivity for quantum mechanics and conjecture quantum gravity does the same.

Conformal invariance is **not a fourth item** in that trilemma — it is a *filter*
on which resolutions are admissible. Applying it closes all three:

| branch | status |
|---|---|
| density `∫ρ dvol` | **excluded by parity**: curvature scalars have weight `−(2m+D)`, always even; the volume element has weight `+d`; invariance needs `2m+D = d`, impossible for odd `d`. A Cauchy surface is 3-dimensional. |
| counting measure | invariant but **uninformative** |
| non-additive | **refuted**: on flat space a dilation is conformal, so every ball ties — a unit ball and one of radius 10¹⁰⁰ get the same value. *Additivity is never used*, which is why dropping it buys nothing. |

So *"how many degrees of freedom are in this region"* is not a well-posed
question in a conformally invariant theory.

**But the assumption survives the loss of the count.** A *relative* count
`ν(U,V)` does survive — dilation invariance acts on both arguments, so it sees
only the ratio of scales, which is what conformal invariance always says. With
the chain rule it is multiplicative, hence `f(2ⁿ) = f(2)ⁿ`: **what replaces the
count is a single scaling exponent**. And `#states = ∏ #confDOF`, a product of
counts, transposes to **additivity of that exponent** — proved without
logarithms, since `2^{d_A+d_B} = 2^{d_A}·2^{d_B}` makes the multiplicative
statement the additive one.

Two things fell out that were not planted. In dimension **four** the parity
balance *is* achievable, at `(m,D) = (2,0)` — exactly the weight of
`C_{abcd}C^{abcd}`, the Weyl action. Conformal gravity is the even-dimensional
case where a conformal density exists; a Cauchy surface is the odd case where it
cannot. And the refutation and the replacement are one phenomenon: assuming an
absolute reference region forces the exponent to zero, so **the exponent is
nonzero precisely because no conformally invariant reference exists**.

The full engagement, written to be read by them, is
[`AOP-CONNECTION.md`](AOP-CONNECTION.md).

### 3.7 The method finally earned its keep on a real open problem

Every finding above tests a carrier built to demonstrate the method. A reviewer
would call that bookkeeping. This one does not.

`sf:program/conjecture/coprime-ratio-hierarchy` — a live conjecture in this
programme's own corpus — stood at `VERIFIED_ON_FIXTURES` with the line *"No
ansatz proof exists"*, five fixtures, and a scoping to `p` odd marked *"pending
evidence"*. That `does_not_establish` line was the work queue.

A **preregistered** attack (committed to git before computing) predicted that
the `p`-odd scoping was over-cautious. **Falsified** — and the preregistration
had named that as the better outcome. Six even-`p` loci computed past their
predicted order are not obstructed at a different order; they are **unobstructed
entirely**, 8:1 decisively so at its own predicted order.

Then the order clause, previously observed with no mechanism, **proved**: a word
at order `n` has degree exactly `n+2`, and at degree `p+q` coprimality leaves
only the conversion kernel, so it can appear only at `n = p+q−2` and nowhere
below. And the kernel clause **proved and refined** — the symmetry follows `q`
parity, not order parity, via an involution under which the cubic vertex is odd.

Four new instances (5:2, 7:2, 7:3, 9:1), two of them the loci the conjecture
names as unchecked, at an order deeper than the corpus had reached. Plus a
sub-law nobody had stated, which *predicted* a missing radical at 9:1.

What is now open is sharper than what was open before: not *"does the law hold
at even `p`?"* but *"what makes the even-`p` coefficient vanish?"* — six loci of
evidence and no argument, since neither the degree count nor the involution
mentions `p`'s parity.

[Full report](coprime-hierarchy-rocq.md).

### 3.8 …and then the ledger caught this stream's own overreach

§3.7 came with a physics reading, flagged as interpretation: that the
obstruction is the `q ↔ p` conversion through which a ghost mode talks to the
healthy one — the mechanism of the instability — so that even-`p` vanishing
**closes the ghost channel**. Auditing it, exactly, refuted it twice over.

**There is no ghost.** `moyal.model` returns a free Hamiltonian that is four
pure squares with four positive coefficients whenever `w1 > w2 > 0`, which the
model already requires. In mode variables it is exactly `w1·a1a1b + w2·a2a2b`:
both frequencies positive, bounded below.

**And the obstruction bounds rather than destabilises.** With
`J = p·n̂₁ + q·n̂₂`, the bracket `{J, M} = i[(n₁−m₁)p + (n₂−m₂)q]·M` — its
eigenvalue *is* the resonance frequency. So `J`'s commutant is exactly the
resonant sector, every possible obstruction at the critical degree conserves `J`
automatically, and `J` positive with nonnegative occupations gives `n₁ ≤ J/p`,
`n₂ ≤ J/q` for all time at any coupling. The derivation never sees the sign of
either frequency, so **a real ghost would not break it**. The structure that
does run away is pair creation `a1^q·a2^p`, which provably breaks `J` and
conserves only the indefinite `p·n₁ − q·n₂`, whose level sets are unbounded.

Nothing mathematical changes: the order law, the selection rule, the kernel
clause and the even-`p` refutation all stand. Only the gloss does. The first
attempt at this audit was a numerical integration that ran ten minutes without
finishing and produced two integrator artefacts; as an exact polynomial identity
in Forge it runs in two seconds and proves something stronger.

That the honest-ledger discipline caught a claim *this stream published* is the
strongest evidence in this document that it is load-bearing rather than
decorative.

[Full report](coprime-charge-bound.md).

### 3.9 And then the method was pointed at Weyl gravity itself

Every finding above tests a carrier, a toy, or another programme's conjecture.
This one is about the theory this repository is named for.

The law is `S[g] = α ∫ √−g C_abcd C^abcd`, and modulo topological terms it is
the **unique** action satisfying `RP-LOCAL`, `RP-METRIC`, `RP-DIFF`, `RP-WEYL`,
`RP-DIM4` — an equivalence, with an independence witness for each.

The computation is small enough to state here. In coordinates
`X = a·Riem² + b·Ric² + c·R²`, the Gauss–Bonnet density is `(1,−4,1)` and the
Weyl square is `(1,−2,⅓)`. The whole conformal anomaly of the sector is carried
by the `R²` coordinate, so Weyl invariance is the single linear equation

```
a + b + 3c = 0
```

whose solution space is exactly `span{C², E₄}` — two-dimensional, and
one-dimensional after the topological quotient. Rational linear algebra in `ℚ³`,
proved in Rocq and independently re-derived by exact Gaussian elimination in
Forge.

**Both sides are done, and the ledgers differ.** A physicist writes the field
equation, not the action. `RP-WEYL` on the action is `RP-TRACELESS` on the
equations — proved equivalent in both directions via Noether. But `RP-TOPO-INERT`
is an assumption *with an independence witness* on the action side and
**invisible** on the field-equation side, since the variation of a topological
term vanishes identically; and divergence-freedom, always quoted as a property of
the Bach tensor, is **free** from `RP-DIFF` and has no independence witness at
all. So an assumption *count* is vocabulary-dependent: six on one side, five on
the other, for the same theory.

**Three more things came out that were not put in.**

*The derivative order is not an assumption.* "Quadratic in curvature" is
normally listed as an input. A density `√−g X` of curvature degree `k` has
constant-Weyl weight `D − 2k`, so invariance forces `k = D/2`; at `D = 4` only
`k = 2` survives, and the same line excludes the cosmological term and
Einstein–Hilbert. The standard motivation uses one more physical input than it
needs.

*Parity is independent on actions and redundant on field equations.* Adjoining
the parity-odd Pontryagin density gives a genuine two-parameter family of
actions `α W₊² + β W₋²` — but a **one**-parameter family of field equations,
since the difference from `((α+β)/2)C²` is `((α−β)/2)P`, which is topological.
The fibre is a gravitational θ-angle: real, but visible only in the quantum
theory, which this programme's claim boundary does not reach.

*And `[W₊²]`, `[W₋²]` — the programme's own certified residual classes — are
exactly the parity eigenbasis of this sector*, since `C² = W₊² + W₋²` and
`P = W₊² − W₋²`. `RP-PARITY` is precisely the assumption that ties them
together, and classically it is free of charge.

**And a prediction, cheap to check.** The conformally invariant curvature degree
in `D` dimensions is `k = D/2`, so **no conformally invariant local curvature
action exists in any odd-dimensional spacetime**, at any derivative order, and
each even dimension admits exactly one degree. Weyl gravity is a
four-dimensional accident in a precise sense, and `D = 6` selects the *cubic*
sector — which is what makes the successor gate well-posed.

**This closes a loop with §3.6.** That section found, without looking for it,
that the parity balance excluded in odd dimension *is* achievable in dimension
four at exactly the weight of `C_abcd C^abcd`. The counting argument predicted
that a conformal density exists there. This section proves it is, modulo
topology, the only one. Two independent lines meet on the same object and
neither was set up to find the other — and the odd-dimension results meet too:
no conformal DOF *density* on an odd-dimensional slice, no conformal curvature
*action* in an odd-dimensional spacetime. Different parity obstructions,
different objects, the same shape.

[Full report](weyl-action-reverse-physics.md) ·
[separation ledger](PHYSICS-VS-MATH.md).

---

## 4. The reversal

The positive structural result on the Hamiltonian side (§3.5 is the other one).
Over the declared carrier:

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
of the findings in §3.1–3.4. And §3.6 exists only because a `does_not_establish`
line — "no physical reading of A2" — was left standing as a problem instead of
being smoothed away.

Three other pieces of discipline paid.

**Negative controls** caught a wrong witness during development — a candidate
control that was itself non-symplectic — and later showed that a *uniform* test
distribution would prove nothing, which is why the entropy converse uses one with
distinct entries.

**Fail-closed hash pinning** caught its own misuse twice: a harness script pinned
alongside the mathematics, recorded and then removed rather than re-bumped.

**Recording why a proof attempt failed** made the retry cheap. The entropy
converse was cut once on cost — a case analysis expanded the test distribution's
values and `coqc` was killed after 2m40s. The certificate recorded the cause *and
the cheaper route*; taking that route compiled in 2.2 seconds. Had the failure
been recorded only as "not done", the second attempt would have been guesswork.

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
- **The conformal results are for CONSTANT rescalings**, and the parity argument
  only for densities built from the metric alone. There *are* conformal
  invariants on a 3-manifold — the gravitational Chern–Simons invariant is one
  (Chern–Simons, *Ann. Math.* 1974) — but it is global rather than a local
  density, real-valued modulo a framing ambiguity, and neither monotone nor
  region-additive, so it is not a count. It bounds the claims rather than
  contradicting them.
- **§3.6 formalises a reading of an unpublished talk.** Their DOF count appears
  on a slide with a question mark. We have attacked one interpretation of it,
  and they may mean something else.
- **No physical reading of A2** — §3.3 explains why it resists one; it does not
  supply one.
- **Nothing transfers between carriers.** The stochastic equivalence is four
  states and one step; the torus results are flat `T⁴` and polynomial fields.
- **Not a reproduction, confirmation, or refutation of Carcassi–Aidala's own
  derivation.** This tests candidate assumptions on declared carriers; it does not
  reconstruct their argument.
- **No Shannon entropy.** The second law is Rényi-2 purity only; the logarithmic
  quantity is never formalised, and nothing here is about equilibration or the
  approach to uniformity.
- **The stochastic results are four states and one step.** The case analyses are
  sized to that; a general finite state space is not covered.
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
| `..._SECOND_LAW_ROCQ_V1` | 4 states | a second law: information conservation entails that disorder never decreases |
| `..._ENTROPY_EQUALITY_ROCQ_V1` | 4 states | reversible evolution is exactly entropy-neutral |
| `..._ENTROPY_CONVERSE_ROCQ_V1` | 4 states | the biconditional: reversible iff no entropy production |
| `..._CONFORMAL_COUNT_ROCQ_V1` | all dimensions | no conformally invariant DOF density in odd dimension, by parity |
| `..._NO_CONFORMAL_COUNT_ROCQ_V1` | flat space | and none non-additive either: every ball ties |
| `..._RELATIONAL_COUNT_ROCQ_V1` | flat space | what replaces it: a single scaling exponent |
| `..._EXPONENT_ADDITIVITY_ROCQ_V1` | products | and DOF-independence becomes additivity of that exponent |
| `..._COPRIME_HIERARCHY_ROCQ_V1` | all coprime p:q | the programme's own conjecture: order law proved, even `p` unobstructed, four new instances |
| `..._COPRIME_CHARGE_BOUND_ROCQ_V1` | all p,q > 0 | and the physics reading of it **retracted**: the obstruction conserves a positive charge, so it bounds rather than destabilises |
| `..._WEYL_ACTION_V1` | all quadratic curvature actions, all dimensions | **the subject itself**: the Weyl action is *equivalent* to five assumptions on the action side and five on the field-equation side; the derivative order is derived, not assumed; parity is independent on actions and redundant on field equations; and odd dimensions admit no conformal curvature action at all |

Nineteen zero-axiom Rocq modules, `coqchk` axiom section `<none>`, twenty-three
fail-closed negative controls, three Forge gates on both backends under ASan, two
independent Python rails. `rocq/ReversePhysicsAOPBridge.v` additionally proves
that the ω used throughout **is** their `J ⊗ Iₙ`, so the engagement in §3.6 is
bridged rather than asserted.

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

The second law and its equality case have since landed, closing the loop
described in §3.5. Everything declared open after that — `SP4_ORBIT`,
`STOCHASTIC_GENERAL_N`, `PARAMETERISED_BASE` — is a **refinement that would add
certificates without adding findings**, and should be skipped unless something
else needs them.

The directions that would still yield something:

- **A third law.** The lattice has one cycle. Two cycles, or a law that
  *conflicts* with the assumption set, is where the method starts discriminating
  between accounts rather than describing one.
- **Non-constant conformal factors.** Everything in §3.6 uses constant `Ω`. The
  no-go should strengthen under the full local group, but that is not shown.
- **A weakenable base** (§4). Everything here is an equivalence over a *declared
  carrier*. Reverse mathematics compares against a base one can weaken; this
  probe never built one, and `marginal_depends_on_the_dof_split` is the only
  result that gestures at it.
- **The corpus's own `does_not_establish` lines.** That is where the seventh
  finding came from — `sf:program/conjecture/coprime-ratio-hierarchy` carried
  the line *"No ansatz proof exists"*, and it turned out to be a degree count
  plus an involution. There are 9,000+ certificates here; that queue is long,
  and it is the answer to the objection that this stream tests carriers built
  to demonstrate the method.
- **This stream's own `does_not_establish` lines.** §3.8 came from auditing an
  interpretation published here, and it was backwards. Every remaining
  interpretation flagged as such is a candidate for the same treatment — and
  `GHOST_MODEL_OBSTRUCTION`, redoing the deformation with a genuinely indefinite
  `h0 = w1·n̂₁ − w2·n̂₂`, is the one that follows directly.
- **Six derivatives in six dimensions.** The weight argument in §3.9 says the
  conformally invariant curvature degree is `k = D/2`, so odd dimensions have no
  such sector at all and `D = 6` selects the *cubic* one. Running the same exact
  linear algebra there tests whether the method scales and whether the parity
  result has an analogue. Declared as `WEYL_ACTION_SIX_DERIVATIVE_D6`.
- **Someone reading this and disagreeing.** Three of the five findings are
  negative claims about a live research programme. They should be argued with —
  [`AOP-CONNECTION.md`](AOP-CONNECTION.md) puts two of them in front of that
  programme directly, in its own notation, and adds an observation about
  conformal invariance that its open conjecture for GR has to face.
