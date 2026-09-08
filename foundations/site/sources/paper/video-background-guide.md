# Video guide: conformal ghosts, fourth-order gravity, and quantum completion

**Audience:** physicists or mathematically mature readers who want enough background to assess the *Conformal Ghosts* research programme.

**Purpose:** This is not meant to teach all of quantum gravity. It is a guided route through the specific question:

> Can a fourth-order theory of gravity be made into a consistent physical theory once the state space, inner product, gauge reduction, interactions, and quantum anomalies are treated carefully?

The central tension is simple:

- adding curvature-squared terms improves the short-distance behaviour of gravity and makes perturbative renormalizability plausible;
- the same fourth-order equations introduce extra modes that look like negative-energy or negative-norm “ghosts” in the standard formulation.

Different programmes solve different parts of this problem. The useful question is therefore not merely *“Does the theory have a ghost?”*, but:

1. What is the state space?
2. What is the adjoint or reality condition?
3. Which modes are physical after gauge reduction?
4. How are probabilities defined?
5. Does the construction survive interactions?
6. Does it survive loops, anomalies, and renormalization?

---

## The shortest useful route

For a first pass, watch these four strands in this order:

1. **Bender/Mannheim:** the positive-metric, PT-symmetric route.
2. **Bateman/Turok:** the Krein-space and hidden ghost-parity route.
3. **Hamada:** conformal-cylinder BRST reduction.
4. **One contrasting interacting prescription:** Donoghue–Menezes or Anselmi.

That is enough to understand why the present programme tries to classify several apparently incompatible “ghost cures” inside one framework.

---

# 1. Orientation: what is the higher-derivative ghost problem?

### Video search

- [Ghost particles / higher-derivative gravity — accessible overview](https://www.youtube.com/results?search_query=ghost+particles+higher+derivative+gravity+explained)
- [Ostrogradsky instability — introductory lectures](https://www.youtube.com/results?search_query=Ostrogradsky+instability+higher+derivative+theories+lecture)
- [Quadratic gravity overview](https://www.youtube.com/results?search_query=quadratic+gravity+ghost+renormalizable+lecture)

### What to learn

Einstein gravity has second-order field equations. Adding terms quadratic in curvature gives fourth-order equations and improves ultraviolet power counting, but creates additional solutions. In the usual decomposition of quadratic gravity, these include a massive spin-2 sector with the wrong-sign residue.

The phrase **ghost problem** can refer to several different failures:

- energy unbounded below;
- negative norm;
- negative transition probability;
- violation of the optical theorem;
- runaway classical solutions;
- an unphysical gauge mode being mistaken for a particle.

Keep these separate. A proposal may solve one without solving the others.

---

# 2. Bender and Mannheim: PT symmetry and a positive metric

## TOE videos

YouTube did not expose stable direct watch URLs through the public search interface used to build this guide, so these links search within the **Theories of Everything** channel:

- [TOE channel search: Philip Mannheim](https://www.youtube.com/@TheoriesofEverything/search?query=Philip%20Mannheim)
- [TOE channel search: Carl Bender](https://www.youtube.com/@TheoriesofEverything/search?query=Carl%20Bender)

One of these should be replaced by the exact TOE watch URL already held by the project maintainer.

## Additional video searches

- [Philip Mannheim — conformal gravity and the ghost problem](https://www.youtube.com/results?search_query=Philip+Mannheim+conformal+gravity+ghost+problem)
- [Carl Bender — PT-symmetric quantum mechanics](https://www.youtube.com/results?search_query=Carl+Bender+PT+symmetric+quantum+mechanics+lecture)

## Companion papers

- [Mannheim: *Solution to the ghost problem in higher-derivative gravity*](https://arxiv.org/abs/2109.12743)
- [Bender and Mannheim: search for the Pais–Uhlenbeck no-ghost papers](https://arxiv.org/search/?query=Bender+Mannheim+Pais-Uhlenbeck&searchtype=all)

## Core idea

A Hamiltonian need not be Hermitian with respect to the naïve Dirac inner product in order to have real energies and unitary evolution. If it has the appropriate antilinear or PT symmetry, one may construct a different positive inner product.

For the Pais–Uhlenbeck oscillator, this changes the question from:

> “Why is one oscillator negative?”

to:

> “Which complex real form, adjoint, and metric define the physical theory?”

## Relation to the present programme

This is closest to the programme’s positive branch:

- reconstruct the positive transformation rather than assuming it;
- classify the metric ambiguity;
- prove why the preferred transformation is geometrically optimal;
- determine whether the free metric deforms consistently under interactions.

## Listen for

- Is the metric bounded and defined on the completed field space?
- Is the transformed theory local?
- What happens in the equal-frequency Jordan limit?
- Is the interacting metric constructed or only the free metric?
- Is unitarity proved for gravity itself or inferred from an oscillator model?

---

# 3. Bateman and Turok: Krein space and hidden ghost parity

## TOE video

- [TOE channel search: Neil Turok](https://www.youtube.com/@TheoriesofEverything/search?query=Neil%20Turok)
- [TOE channel search: Sam Bateman](https://www.youtube.com/@TheoriesofEverything/search?query=Sam%20Bateman)

Use the exact TOE watch URL already held by the project maintainer when this file is committed.

## Additional video searches

- [Neil Turok and Sam Bateman — hidden ghost parity](https://www.youtube.com/results?search_query=Neil+Turok+Sam+Bateman+hidden+ghost+parity)
- [Krein space, ghosts, and the Born rule](https://www.youtube.com/results?search_query=Krein+space+ghosts+Born+rule+quantum+field+theory)

## Companion paper

- [Bateman and Turok: *Escape from Ostrogradsky via Hidden Ghost Parity*](https://arxiv.org/abs/2607.00096)

## Core idea

Instead of rotating to an ordinary positive Hilbert space, retain an **indefinite Krein space** and construct a probability rule compatible with it. In the Bateman–Turok model, a hidden ghost-parity symmetry becomes manifest after embedding the fourth-order theory into a two-field \(O(1,1)\)-symmetric system.

Their 2026 preprint claims, for its model:

- a consistent perturbative expansion;
- an all-orders optical theorem;
- positive tree-level transition probabilities;
- a generalized Born rule on the Krein space.

## Relation to the present programme

This is the closest external programme to the natural energy-mode Krein–Fock completion.

The important comparison is not “Hilbert good, Krein bad.” It is:

- what extra symmetry makes the indefinite theory probabilistically meaningful?
- does gravity possess an analogue of the Bateman–Turok ghost parity?
- if not, can one prove that no local, covariant, factorizing analogue exists?

The present programme’s interaction calculations are designed to make that comparison precise.

## Listen for

- What exactly is the physical probability formula?
- Which states can appear externally?
- Which symmetry protects positivity?
- Does the proof rely on the special \(O(1,1)\) embedding?
- Can the construction survive gauge constraints and a spin-2 multiplet?

---

# 4. Hamada and Horata: BRST conformal gravity on the cylinder

## Video searches

- [Ken-ji Hamada — BRST conformal gravity](https://www.youtube.com/results?search_query=Ken-ji+Hamada+BRST+conformal+gravity)
- [Ken-ji Hamada — quantum gravity on R x S3](https://www.youtube.com/results?search_query=Ken-ji+Hamada+quantum+gravity+R+x+S3)
- [BRST cohomology and conformal gravity lectures](https://www.youtube.com/results?search_query=BRST+cohomology+conformal+gravity+lecture)

There appears to be less polished long-form public material here than for Mannheim, Turok, or Donoghue; seminar-level talks are the likely result.

## Companion paper

- [Hamada: *BRST Conformal Symmetry as A Background-Free Nature of Quantum Gravity*](https://arxiv.org/abs/1707.06351)

## Core idea

Place the theory on the conformal cylinder

\[
\mathbb{R}\times S^3
\]

and identify physical states by BRST cohomology under the residual conformal algebra. Hamada’s programme argues that negative-metric modes become unphysical after the complete conformal constraint structure is imposed, and that physical fields are scalar composites of the appropriate conformal weight.

## Relation to the present programme

This is the nearest predecessor to the pure-Weyl cylinder paper.

The present programme aims to make the full chain explicit:

\[
\text{covariant causal fields}
\rightarrow
\text{Cauchy–Sobolev completion}
\rightarrow
\text{Krein–Fock space}
\rightarrow
\text{BV}
\rightarrow
\text{BFV}
\rightarrow
\text{residual cohomology}.
\]

In the selected fully gauged sector, the centered one-particle classes vanish and two weight-four curvature classes survive:

\[
[W_+^2],\qquad [W_-^2].
\]

## Listen for

- Which conformal generators are treated as gauge?
- Is cylinder time translation included among the constraints?
- Is the result classical BRST, quantum BRST, or both?
- What topology or completion is used for the state space?
- What happens to the conformal anomaly and the quantum master equation?

---

# 5. Jeffrey Kuntz: PT-symmetric quadratic gravity

## Video searches

- [Jeffrey Kuntz — PT-symmetric quantum quadratic gravity](https://www.youtube.com/results?search_query=Jeffrey+Kuntz+PT+symmetric+quantum+quadratic+gravity)
- [Jeffrey Kuntz — unitarity through PT symmetry](https://www.youtube.com/results?search_query=Jeffrey+Kuntz+unitarity+through+PT+symmetry)

## Companion papers

- [Kuntz: *Unitarity through PT symmetry in Quantum Quadratic Gravity*](https://arxiv.org/abs/2410.08278)
- [Kubo and Kuntz: *Analysis of Unitarity in Conformal Quantum Gravity*](https://arxiv.org/abs/2202.08298)

## Core idea

Complex-deform quadratic gravity into a PT-symmetric theory whose free part is ghostless in the chosen representation, while the interactions become non-Hermitian. The programme seeks a positive physical inner product compatible with the gravitational gauge structure.

## Relation to the present programme

Kuntz is an especially useful comparison because he treats both:

- the gauge structure of gravity;
- the non-Hermitian/PT-symmetric route.

The interaction-obstruction papers in the present programme ask whether the canonical free positive metric can actually be continued through resonant gravitational channels.

## Listen for

- Is the interacting metric explicitly constructed?
- Is the result evidence, a perturbative construction, or a theorem?
- How is BRST compatibility enforced?
- Is the inner product local or momentum dependent?
- What happens to Lorentz covariance across the full massive spin-2 multiplet?

---

# 6. Alberto Salvio: Dirac–Pauli quantization

## Video searches

- [Alberto Salvio — quadratic gravity](https://www.youtube.com/results?search_query=Alberto+Salvio+quadratic+gravity)
- [Alberto Salvio — non-perturbative quadratic gravity](https://www.youtube.com/results?search_query=Alberto+Salvio+non-perturbative+background-independent+quadratic+gravity)
- [Alberto Salvio — Dirac–Pauli quantization](https://www.youtube.com/results?search_query=Alberto+Salvio+Dirac+Pauli+quantization)

## Companion papers

- [Salvio: *Quadratic Gravity*](https://arxiv.org/abs/1804.09944)
- [Salvio: *A non-Perturbative and Background-Independent Formulation of Quadratic Gravity*](https://arxiv.org/abs/2404.08034)

## Core idea

Use Dirac–Pauli quantization for the higher-derivative sector. Salvio argues that this gives a well-defined Euclidean path integral, nonnegative probabilities, and a nonperturbative, background-independent formulation of quadratic gravity.

## Relation to the present programme

This is a broad competing completion claim. It should be compared against the present programme’s classification of:

- reality conditions;
- positive versus Krein completions;
- field-theoretic domains;
- interaction stability;
- gauge reduction.

## Listen for

- What is the physical adjoint?
- Which variables have imaginary eigenvalues?
- How is reflection positivity or its replacement established?
- How are interactions and gauge constraints incorporated?
- Is locality preserved in the physical variables?

---

# 7. Donoghue and Menezes: the ghost as an unstable resonance

## Video searches

- [John Donoghue — quadratic gravity and unstable ghosts](https://www.youtube.com/results?search_query=John+Donoghue+quadratic+gravity+unstable+ghosts)
- [Gabriel Menezes — quadratic gravity ghosts](https://www.youtube.com/results?search_query=Gabriel+Menezes+quadratic+gravity+ghosts)
- [Donoghue and Menezes — unitarity, stability, and loops](https://www.youtube.com/results?search_query=Donoghue+Menezes+unitarity+stability+loops+unstable+ghosts)

For a gentler entry, Donoghue’s lectures on gravity as an effective field theory are excellent:

- [John Donoghue — quantum gravity as effective field theory](https://www.youtube.com/results?search_query=John+Donoghue+quantum+gravity+effective+field+theory+lecture)

## Companion paper

- [Donoghue and Menezes: *Unitarity, stability and loops of unstable ghosts*](https://arxiv.org/abs/1908.02416)

## Core idea

The problematic massive mode is treated as an unstable resonance rather than a stable asymptotic particle. If it never appears as an external state, the unitarity sum may involve only stable states, while the ghostlike pole is handled through its dressed propagator.

## Relation to the present programme

This is a different answer from both positive-metric and Krein completion:

- do not reinterpret every free ghost state as a physical particle;
- let interactions move the pole and make the mode unstable;
- formulate unitarity in terms of the stable asymptotic spectrum.

The present interaction papers are relevant because they identify the channels through which the massive sector converts into ordinary gravitons.

## Listen for

- Is the ghost excluded from the asymptotic Hilbert space?
- How is the pole prescription fixed?
- Does the optical theorem hold beyond a selected loop order?
- Is microscopic causality modified?
- What is the free-theory limit as the width goes to zero?

---

# 8. Damiano Anselmi: fakeons

## Video searches

- [Damiano Anselmi — fakeons and quantum gravity](https://www.youtube.com/results?search_query=Damiano+Anselmi+fakeons+quantum+gravity)
- [Fakeons, microcausality, and the classical limit](https://www.youtube.com/results?search_query=fakeons+microcausality+classical+limit+quantum+gravity)

## Companion paper

- [Anselmi: *Fakeons, quantum gravity and the correspondence principle*](https://arxiv.org/abs/1911.10343)

## Core idea

Keep the extra higher-derivative mode inside internal quantum calculations, but quantize it with a special prescription so that it is not a physical asymptotic particle. The resulting theory aims to retain renormalizability and unitarity, at the price of a nonstandard classical limit and microscopic violations of causality.

## Relation to the present programme

Fakeons alter the propagator prescription and the physical spectrum rather than constructing the positive or Krein completion studied in the current papers.

This is a useful benchmark for asking whether the programme’s obstruction results are:

- obstructions to *all* fourth-order theories;
- or only to analytic deformations of a particular positive completion.

## Listen for

- Which poles correspond to particles and which to fakeons?
- What replaces the usual causal prescription?
- Where does nonlocality enter?
- How is the classical limit obtained?
- Can the construction be expressed in BV–BFV language?

---

# 9. Juan Maldacena: boundary projection to the Einstein sector

## Video searches

- [Juan Maldacena — Einstein gravity from conformal gravity](https://www.youtube.com/results?search_query=Juan+Maldacena+Einstein+gravity+from+conformal+gravity)
- [Maldacena — conformal gravity boundary conditions](https://www.youtube.com/results?search_query=Maldacena+conformal+gravity+boundary+conditions)

## Companion paper

- [Maldacena: *Einstein Gravity from Conformal Gravity*](https://arxiv.org/abs/1105.5632)

## Core idea

In asymptotically de Sitter or Euclidean anti-de Sitter settings, impose a Neumann boundary condition that selects the Einstein solutions from the larger conformal-gravity solution space. The unwanted modes are then absent from the relevant semiclassical computation.

## Relation to the present programme

This is not primarily a new inner product or a Krein probability rule. It is a **boundary-condition projection**.

It is therefore a valuable control case:

- Mannheim changes the adjoint and metric.
- Bateman–Turok change the probability structure on a Krein space.
- Hamada uses BRST/conformal reduction.
- Maldacena restricts the allowed solution space by boundary conditions.

## Listen for

- Which spacetime asymptotics are required?
- Is the equivalence tree-level or nonperturbative?
- Does the projection retain the full conformal theory or only its Einstein subsector?
- What happens away from the chosen boundary conditions?
- Does it address interacting conformal gravity as an independent theory?

---

# How the approaches compare

| Programme | Main move | What happens to the extra mode? | Main unresolved comparison |
|---|---|---|---|
| Bender–Mannheim | PT/pseudo-Hermitian positive metric | Reinterpreted using a different adjoint and real form | Does the positive metric survive local interactions and field completion? |
| Bateman–Turok | Krein space plus hidden ghost parity | Retained in an indefinite space with a generalized Born rule | Does gravity possess the required protecting symmetry? |
| Hamada–Horata | BRST conformal reduction on the cylinder | Negative-metric one-particle modes are removed from physical cohomology | What survives the anomaly and full quantum BV analysis? |
| Kuntz | Complex PT deformation of quadratic gravity | Free ghost is removed in the deformed representation | Can the interacting positive metric be constructed rigorously? |
| Salvio | Dirac–Pauli quantization | Quantized with nonstandard reality/eigenvalue structure | How does this map onto the real-form and gauge classification? |
| Donoghue–Menezes | Unstable-resonance interpretation | Not a stable asymptotic particle | What is the exact nonperturbative causal and unitary framework? |
| Anselmi | Fakeon prescription | Internal only; excluded from the physical spectrum | Cost in locality, causality, and classical interpretation |
| Maldacena | Boundary-condition projection | Removed by selecting the Einstein subsector | Limited to selected asymptotics and semiclassical settings |

---

# How this maps onto the Conformal Ghosts papers

A useful reading map is:

### Free positive geometry

Compare primarily with:

- Bender–Mannheim;
- Kuntz;
- Salvio.

Questions: uniqueness of the positive metric, optimality, real forms, domains, and the Jordan boundary.

### Krein–Fock completion

Compare primarily with:

- Bateman–Turok;
- Salvio;
- standard indefinite-metric field theory.

Questions: the generalized Born rule, physical observables, factorization, covariance, and optical-theorem positivity.

### Gauge reduction on the conformal cylinder

Compare primarily with:

- Hamada–Horata;
- Maldacena.

Questions: which symmetries are gauge, whether time translation is constrained, and whether one-particle ghost classes survive residual cohomology.

### Interaction obstructions

Compare primarily with:

- Bateman–Turok;
- Kuntz;
- Donoghue–Menezes;
- Anselmi.

Questions: whether the free completion deforms, whether resonant channels create cohomological obstructions, and whether a different asymptotic-state or pole prescription evades them.

### Quantum BV, anomalies, and renormalization

Compare with all of the above, but especially:

- Hamada;
- Salvio;
- Anselmi;
- Kuntz.

The key tests are the quantum master equation, anomaly cohomology, counterterms, and preservation of the physical pairing.

---

# Five questions to use when assessing any talk

A physicist watching these videos should keep asking:

1. **What is the exact state space?**  
   Formal modes, a Hilbert space, a Krein space, a Fock completion, or BRST cohomology?

2. **What is the physical adjoint?**  
   Ordinary Hermitian conjugation, PT/CPT conjugation, a metric-dependent adjoint, or a Dirac–Pauli reality condition?

3. **What counts as physical?**  
   Every free pole, only BRST classes, only stable asymptotic states, or only an Einstein boundary subsector?

4. **Where are interactions treated?**  
   Merely proposed, checked at tree level, proved perturbatively, or controlled nonperturbatively?

5. **What is the precise scope?**  
   An oscillator, a scalar QFT, linearized gravity, Einstein–Weyl gravity, pure Weyl gravity, or a renormalized quantum theory?

These questions prevent different uses of the word *unitary* or *ghost-free* from being treated as equivalent.

---

# Suggested viewing schedules

## Two-hour triage

1. One Mannheim/Bender TOE interview.
2. The Bateman/Turok TOE interview.
3. The first half of a Hamada seminar or BRST conformal-gravity talk.
4. Ten minutes each from Donoghue–Menezes and Anselmi.

Goal: understand the taxonomy of proposed resolutions.

## One-day technical orientation

1. Mannheim/Bender — PT symmetry and Pais–Uhlenbeck.
2. Bateman/Turok — Krein Born rule and ghost parity.
3. Hamada — \( \mathbb{R}\times S^3 \), residual conformal algebra, physical states.
4. Kuntz — PT-symmetric quadratic gravity with gauge structure.
5. Donoghue–Menezes — unstable resonance.
6. Anselmi — fakeons.
7. Maldacena — boundary projection.

Goal: be able to state which problem each programme solves and which it leaves open.

## Deeper reading week

Watch the videos above, then read the companion papers in this order:

1. Mannheim, arXiv:2109.12743.
2. Bateman–Turok, arXiv:2607.00096.
3. Hamada, arXiv:1707.06351.
4. Kuntz, arXiv:2410.08278.
5. Salvio, arXiv:2404.08034.
6. Donoghue–Menezes, arXiv:1908.02416.
7. Anselmi, arXiv:1911.10343.
8. Maldacena, arXiv:1105.5632.

Goal: assess the *Conformal Ghosts* programme as a proposed classification and synthesis, rather than as one more isolated ghost prescription.

---

# Final orientation

The programme should not initially be judged by the sentence:

> “The ghost has been removed.”

The stronger and more falsifiable ambition is:

> Build the free theory on completed state spaces; classify its positive and Krein real forms; perform the full selected gauge reduction; test whether those structures survive interactions; and then determine whether quantum anomalies and renormalization preserve the result.

Even a negative answer at one of the later stages would be scientifically valuable if it produces a precise obstruction theorem and identifies which competing ghost resolutions remain possible.
