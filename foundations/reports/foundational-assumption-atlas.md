# Reverse foundations: physics × mathematics × logic

**Result:** `FOUNDATIONAL_ASSUMPTION_ATLAS_V0`

**Lifecycle:** `LITERATURE_SCOPED`

**Dependency tag:** `LOCAL-ALGEBRAIC`

The proposed programme is coherent, and the repository is unusually well
prepared for it.  The pieces have been studied separately: reverse mathematics
asks which axioms prove a mathematical theorem; reverse physics asks which
physical postulates recover a law; operational quantum reconstructions ask
which physical principles recover Hilbert-space quantum mechanics; weak-choice
and constructive analysis ask which analytic structures survive under a change
of foundations.  What is not yet present here, or apparently standard in the
literature surveyed so far, is one auditable product that varies all of them at
once.

The right object is not literally a Cartesian product of theories.  It is a
parameterized derivability relation:

```text
L + S + M + Enc(P) |- O
```

`L` is logic, `S` the set/type/existence theory, `M` the mathematical carrier
and analytic machinery, `P` physical postulates after an explicit encoding,
and `O` one level-specific physical or mathematical conclusion.  The reverse
question is: over a fixed weak base, which parts can be removed, which can be
derived back from `O`, and which can be avoided by choosing another
representation?

This extends the repository's existing
[`PHYSICS-VS-MATH`](../../reverse_physics/reports/PHYSICS-VS-MATH.md) ledger and
[`weakenable-base`](../../reverse_physics/reports/weakenable-base.md) result.
Those correctly separate physical assumptions, imported geometry, and proved
mathematics, and recognize carrier constraints as a weakenable structural base.
They also say exactly what is missing: no proof system and no logical
independence result.  This stream supplies that missing coordinate rather than
replacing the existing work.

## 1. Six axes, not one switch

“Drop the axiom of Choice” is not a sufficiently specified theory change.
At least six axes must remain separate.

| axis | examples | question |
|---|---|---|
| logic | classical; intuitionistic; topos-internal Heyting | Which inference rules are allowed? |
| existence/set theory | ZFC; ZF+DC; ZF; IZF/CZF; type theory; `RCA_0`, `WKL_0`, … | Which sets, functions, sequences, and witnesses exist? |
| infinity | finite; potential; countable/separable; arbitrary set-sized; continuum | Which limiting and totality claims are admitted? |
| carrier geometry | Hilbert; Krein/Pontryagin; rigged Hilbert; C\*-algebra; locally convex; locale/topos; finite GPT | What represents states, observables, and dynamics? |
| physics | causality; locality; composition; positivity; spectral condition; continuity; purification | What is asserted about the world? |
| conclusion level | finite prediction; solution existence; representation; Born probability; scattering; QME | What exactly has been established? |

These axes are not linearly ordered.  ZF without Choice can retain classical
logic and actual infinity.  Constructive mathematics changes logic and the
meaning of existence.  Finitism challenges actual infinity.  Topos quantum
theory uses intuitionistic internal logic and point-free spectra.  A finite
cutoff inside ordinary ZFC changes none of those foundations by itself.

This is why the programme needs an atlas rather than a slogan.

## 2. The first answer about Choice

There are three different questions that are often collapsed.

1. **Did a familiar proof use Choice?** This gives an upper bound on what was
   sufficient for that proof.
2. **Does the theorem require a choice principle over a named base?** This
   needs a reversal or a separating model.
3. **Does the physical postulate require that theorem in its full generality?**
   This needs an encoding and an avoidance audit across alternative
   formulations.

Only the second is reverse mathematics.  Only the third connects it to reverse
physics.

Functional analysis gives immediate test cases.  General Banach--Alaoglu
compactness has Boolean-prime-ideal/ultrafilter strength rather than requiring
full Choice in the undifferentiated way often claimed; Rossi gives the direct
equivalence with Tychonoff compactness for compact Hausdorff spaces
([paper](https://arxiv.org/abs/0911.0332)).  But that does not show that a
particular separable PDE argument or a concrete Green operator requires that
full statement.  The target theorem must be narrowed before its strength is
classified.

Recent work makes the point especially sharp.  Blackadar, Farah, and Karagila
study Hilbert spaces in ZF without countable Choice
([paper](https://arxiv.org/abs/2304.09602)); Blackadar and Farah show that a
substantial theory of **separable** C\*-algebras, including representation and
functional-calculus results, can be developed in ZF, while also constructing
non-choice pathologies outside that protected region
([paper](https://arxiv.org/abs/2602.15812)).  So “quantum theory uses Hilbert
space, therefore quantum theory uses Choice” is not a valid inference.  The
choice cost is theorem-by-theorem and often representation-by-representation.

Solovay's model supplies another guardrail: relative to the stated large-cardinal
consistency assumption, ZF+DC can coexist with every set of reals being
Lebesgue measurable
([paper](https://doi.org/10.2307/1970696)).  Merely deleting Choice from ZFC
does **not** imply that regularity conclusion.  A replacement theory must be
named, not imagined.

## 3. Hilbert versus Krein: what is actually thrown out

Krein space is an excellent first example because it reveals two different
layers.

A Krein space throws out **positive definiteness of the distinguished
indefinite pairing**.  With a fundamental symmetry `J`, however, the associated
positive product supplies a Hilbert-space norm and topology.  This is part of
the standard structure, not an optional rhetorical gloss
([one explicit formulation](https://doi.org/10.15352/bjma/09-1-1)).

So the move is:

```text
positive physical/state pairing
        -> indefinite pairing + fundamental decomposition
        -> associated positive Hilbert topology
```

It is not:

```text
Hilbert mathematics -> no Hilbert mathematics
```

Nor does it by itself remove completeness, bases, infinite sums, spectral
arguments, or Choice.  Those are separate audits.  In the Bateman--Turok
proposal ([paper](https://arxiv.org/abs/2607.00096)), the geometry changes the
adjoint, trace, null directions, and positivity mechanism.  The repository's
own audit then exposes further assumptions about implementability, trace class,
vacuum topology, and the operator map.  This makes it an ideal first case:
separate the indefinite physical pairing from the positive auxiliary topology,
then ask the set-theoretic strength of each analytic theorem actually used.

## 4. Hilbert space may be a conclusion, not a postulate

Operational reconstruction programmes already perform one half of the desired
reversal.  Hardy derives finite-dimensional quantum structure from operational
axioms and makes continuity explicitly load-bearing
([paper](https://arxiv.org/abs/quant-ph/0101012)).  Chiribella, D'Ariano, and
Perinotti formulate a wider operational-probabilistic class and use purification
to select quantum theory
([paper](https://doi.org/10.1103/PhysRevA.84.012311)).

This changes the ledger entry for Hilbert space:

```text
textbook formulation:       Hilbert space is a mathematical postulate
operational reconstruction: Hilbert structure is a derived representation
```

The physical content has not vanished; it has migrated into continuity,
composition, tomography, purification, or faithful-state assumptions.  The
repository already has the machinery to ask whether each is independent and
at which level.  The new task is to audit the **proof-theoretic** resources of
the reconstruction as well.  Finite-dimensional reconstruction cannot be
silently promoted to infinite-dimensional interacting QFT.

## 5. Changing logic without losing all quantum structure

Constructive Gelfand duality shows that important commutative C\*-algebraic
structure survives constructively when spectra are treated point-free
([Coquand--Spitters](https://doi.org/10.1017/S0305004109002515)).  Heunen,
Landsman, and Spitters use this inside a topos: a noncommutative algebra is read
through its commutative contexts, the internal spectrum is a locale, and the
propositional structure is intuitionistic
([paper](https://arxiv.org/abs/0709.4364)).

That is a real alternative architecture, but two warnings matter.

- Internal intuitionistic logic is not the same claim as classical ZF with
  Choice deleted.
- Birkhoff--von Neumann “quantum logic” concerns the algebra of propositions;
  it does not automatically replace the metalogic used to prove theorems about
  the theory.

The programme must therefore record both **object logic** and **metalogic**.
Otherwise it will call two distinct changes by the same name.

## 6. The implication protocol

Every proposed edge receives one of seven statuses:

| status | what has actually been shown |
|---|---|
| `USED_BY_DISPLAYED_PROOF` | one proof invokes the principle |
| `SUFFICIENT_OVER_BASE` | a formal derivation exists over the declared base |
| `NECESSARY_OVER_BASE` | a separating model/witness rules out its omission |
| `EQUIVALENT_OVER_BASE` | both directions are proved over that base |
| `AVOIDED_BY_REFORMULATION` | a different carrier proves the same target without it |
| `INDEPENDENT_OVER_BASE` | models on both sides exist |
| `UNKNOWN` | no promotion is permitted |

The central anti-overclaim rule is:

> An empirically motivated postulate cannot be said to imply a set-theoretic
> axiom until the postulate is encoded over a shared weak base and a reversal is
> proved there.

Even then, the conclusion concerns that formal encoding.  An experiment does
not quantify over every family of nonempty sets in the mathematical universe.
It can motivate a physical totality or selection principle; identifying that
principle with a fragment of Choice is a theorem still to be proved.

## 7. First repository audits

The highest-value sequence is not “remove all of Choice from Weyl gravity.”
That target is too coarse.  Start with four bounded cases.

### A. Krein/Hilbertization audit

For the Bateman--Turok carrier, list separately:

- indefinite pairing;
- existence and choice of fundamental symmetry;
- induced positive norm and completion;
- orthogonal or Schauder/Hilbert bases actually used;
- positive versus Krein adjoints;
- trace-class and Hilbert--Schmidt assertions.

Then mark each as finite algebra, explicit construction, separable theorem, or
arbitrary-space existence theorem.  This will answer exactly how much Hilbert
mathematics remains after positivity is changed.

### B. Separable observable-algebra audit

For one quantum result, separate:

```text
algebra definition -> state existence -> GNS representation
                   -> state selection -> dynamics -> physical conclusion
```

The 2026 separable C\*-algebra results suggest that the first and some middle
arrows may survive in ZF.  State selection, pure states, nonseparable limits,
and QFT locality require their own checks.

### C. Weyl BV proof-dependency cut

Take one certified local Weyl result and follow it until the first genuinely
analytic input:

```text
finite exact local algebra
 -> formal deformation/BV identities
 -> distributions and Green operators
 -> state/Hadamard selection
 -> renormalized time ordering and QME
```

The repository's dependency tags already prevent a local or reduced result
from becoming Lorentzian evidence.  Add a foundational tag at each arrow:
finite, constructive, predicative, countable-choice, BPI, stronger-choice, or
unknown.  The first `UNKNOWN` is the gate, not an invitation to guess.

### D. Operational reconstruction cross-audit

Choose one finite-dimensional reconstruction and classify both sides:

- which operational postulates produce Hilbert/Jordan structure;
- which logical and compactness principles the proof consumes;
- whether a constructive or finite proof gives the same conclusion;
- which step fails on passage to fields or infinitely many degrees of freedom.

This is where reverse physics and reverse mathematics genuinely meet.

## 8. What has and has not been done before

Much of the square has mature literatures:

- reverse mathematics and foundational analysis
  ([Simpson](https://doi.org/10.1017/CBO9780511581007),
  [Eastaugh](https://arxiv.org/abs/1807.10022));
- reverse physics
  ([Carcassi--Aidala](https://doi.org/10.1007/s10701-022-00555-z));
- operational reconstruction of quantum theory;
- constructive functional analysis and topos quantum theory;
- weak-choice Hilbert and operator-algebra theory;
- finite and alternative state-space geometries.

The preliminary novelty claim is deliberately narrower: this survey found no
single source that builds a claim-by-claim evidence graph whose nodes vary
physical postulates, representation geometry, infinity commitments, choice or
comprehension strength, and logic simultaneously, with reversals and avoidance
proofs kept distinct.  That is a literature-search result, not a priority or
uniqueness theorem.  A broader review may find precedents.

## 9. Boundaries

This atlas establishes a vocabulary, a pinned seed corpus, and executable
internal-consistency checks.  It does **not** establish that Choice is physically
true or dispensable, that a physical postulate entails Choice, that all quantum
mechanics survives in ZF, that Krein space abandons Hilbert topology, or that a
finite/constructive/topos reformulation supplies a Lorentzian Weyl QFT.

In particular it computes no coefficient, restores no QME, transfers no
residual class, constructs no Hadamard state, and proves no scattering theorem.
The exact open is now sharper: find the first nontrivial repository claim whose
minimal **physical and foundational** assumptions can both be reversed over one
declared base.
