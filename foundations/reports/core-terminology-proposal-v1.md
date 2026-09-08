# Proposed core terminology: 150 concepts

**Selection record. The first two batches are now implemented in the [core dictionary](core-dictionary-batch2-v1.md); the seven batch-3 concepts remain proposed.**

Start with the 67 batch-1 concepts, including the seven dictionary entries that existed when this list was proposed. The 76 batch-2 concepts support atlas reading; seven batch-3 concepts cover specialist construction details. These are writing priorities, not reader ability levels: each approved entry should serve all four perspectives.

The proposal replaces frequency as the admission criterion with reader need, relevance to current explanations, and a distinct explanatory purpose. Corpus mentions help locate source material; they do not prove that every occurrence has the proposed meaning. The current introductions take precedence over superseded paper claims.

## How to review and use this list

For each row, choose keep, fold into another entry, defer, or remove. Compound headings group related questions; they do not make their parts synonyms. Source-search phrases are retrieval probes, never automatic annotation aliases. Papers-only or generic mention evidence needs contextual review before drafting.

After selection, write the General explanation around a concrete example, Physics around modeling and measurement, Mathematics around structures and hypotheses, and Specialist around the exact role and limits. Expand every acronym on first use. Link prerequisite explanations rather than repeating them. Publish a term only when its four explanations and crosslinks have passed editorial review.

## Consolidation rules

- Keep ACA₀ and RCA₀ separate; link both to comprehension, base theory and logical strength. Bare ACA and RCA are not automatic aliases.
- Treat finite energy as a subtopic of energy; keep positive energy distinct from positivity of a quantum state.
- Explain ordinary, supplied-rate and fast Cauchy representations together through crosslinks; do not merge their different information requirements.
- Explain observational residuals separately from residual cohomology.
- Keep ghost meanings visibly separated inside the ghost entry; link gauge bookkeeping to BRST and negative-probability issues to state positivity.
- Give dependency tags short scope-specific entries linked to one shared dependency-tag explanation. Do not repeat the scientific introduction in each.
- Project case entries explain what was held fixed and what remains open; link to foundational definitions instead of making each phrase another entry.

## Proposed entries

Batch 1 = introduction essentials; 2 = atlas bridges; 3 = specialist details. “Existing” identifies one of the seven entries present at proposal time. Implementation status is tracked separately.

### Mathematics (50)

| Batch | Proposed concept | Why include it | Source evidence |
| --- | --- | --- | --- |
| 1 | Reverse mathematics (existing) | Explains how a theorem can measure which existence axioms are necessary. | `foundations/editorial/reading-content.json` · `/audiences/mathematics/background` |
| 1 | Axiom and axiom system | Distinguishes an assumed starting rule from a proved result. | `foundations/editorial/reading-content.json` · `/claims/wave/boundary` |
| 1 | Base theory | Explains the common starting assumptions used in a strength comparison. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/4/paragraphs/0` |
| 1 | RCA₀ (existing) | Decodes Recursive Comprehension Axiom and explains the role of the subscript-zero base system. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/mathematics/4/paragraphs/0` |
| 1 | ACA₀ (existing) | Decodes Arithmetical Comprehension Axiom and explains the stronger existence principle in the wave result. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/mathematics/4/paragraphs/0` |
| 2 | PRA | Decodes Primitive Recursive Arithmetic and explains why fixed finite fixtures can use it. | `foundations/site/data.json` · `/ladder/0/display/base/3` |
| 2 | WKL₀ | Decodes Weak König’s Lemma and locates an intermediate logical benchmark without making it a physical accuracy scale. | `foundations/site/data.json` · `/axes/0/keys/1/includes/2` |
| 2 | ZF and choice principles | Explains Zermelo–Fraenkel set theory and separates it from added choices of infinite families. | `foundations/site/data.json` · `/ladder/5/display/excluded/9` |
| 1 | Comprehension | Explains the permission to form sets that distinguishes the named axiom systems. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/mathematics/4/paragraphs/0` |
| 1 | Logical strength | Explains what stronger assumptions mean and why strength is not empirical success. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/mathematics/0/paragraphs/1` |
| 1 | Reverse implication | Explains the necessity direction that turns an upper bound into a reverse-mathematical equivalence. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/mathematics/4/paragraphs/1` |
| 2 | Computability | Separates existence of an object from a procedure that constructs its requested representation. | `foundations/site/data.json` · `/axes/0/keys/3/label` |
| 1 | Representation of data | Explains why two encodings of the same intended wave can give different reconstruction tasks. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/7/paragraphs/1` |
| 1 | Cauchy sequence | Explains the convergence promise at the center of the wave example. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/specialist/4/paragraphs/0` |
| 1 | Modulus of convergence (existing) | Explains the extra information telling a reader when an approximation is accurate enough. | `foundations/editorial/reading-content.json` · `/claims/wave/summary` |
| 1 | Fast Cauchy name | Explains the output representation demanded by the wave reconstruction theorem. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/mathematics/4/paragraphs/1` |
| 1 | Completion | Explains what must be added when finite approximations are used to describe limiting objects. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/1/paragraphs/0` |
| 2 | Uniformity | Explains the difference between a construction at every finite stage and one construction working across all stages. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/mathematics/3/paragraphs/0` |
| 1 | Continuity | Explains controlled dependence on data and why a continuity statement need not supply a rate. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/mathematics/0/paragraphs/0` |
| 1 | Topology | Explains how a chosen notion of closeness changes convergence and continuity. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/mathematics/1/paragraphs/0` |
| 1 | Vector space | Supplies the basic structure used to combine waves and field perturbations. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/mathematics/1/paragraphs/0` |
| 1 | Function space | Explains why specifying which functions are allowed is part of a theorem. | `foundations/editorial/reading-content.json` · `/topics/wave/versions/specialist/1/paragraphs/1` |
| 1 | Norm | Explains how the size of an error or a field is measured. | `foundations/site/data.json` · `/axes/1/keys/1/plain_meaning` |
| 1 | Inner product and pairing | Explains the structures used to compare states, while distinguishing a general pairing from a positive inner product. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/5/paragraphs/0` |
| 1 | Hilbert space | Explains the completed setting familiar in quantum theory and the assumptions it adds. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/1/paragraphs/0` |
| 2 | Operator and domain | Explains why a formula for an operator is incomplete without the inputs on which it acts. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/1/paragraphs/0` |
| 2 | Self-adjointness | Explains a condition behind spectral interpretation without confusing it with positive energy. | `foundations/site/data.json` · `/evidence/FOUNDATIONAL_EXPLICIT_ENERGY_SPECTRAL_FRAGMENT_ZF_V1/does_not_establish/2` |
| 2 | Spectrum | Explains what spectral calculations describe and why a real spectrum is only one acceptance condition. | `foundations/site/data.json` · `/axes/2/keys/5/label` |
| 2 | Distribution | Explains generalized fields that act on test functions rather than having ordinary point values. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/specialist/1/paragraphs/0` |
| 1 | Test function and smearing | Explains how a finite-resolution detector extracts a number from a field or distribution. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/4/paragraphs/0` |
| 1 | Support and compact support | Explains where an object can be nonzero before introducing locality and causal restrictions. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/specialist/1/paragraphs/0` |
| 2 | Weak solution | Explains how a differential equation can hold after testing rather than by pointwise differentiation. | `foundations/site/data.json` · `/ladder/2/display/excluded/13` |
| 2 | Regularity | Explains the smoothness requirements that distinguish finite corrections from an acceptable full construction. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/4/paragraphs/1` |
| 2 | Existence, uniqueness and well-posedness | Gives readers the three separate questions behind a claim that an evolution problem is solved. | `foundations/editorial/reading-content.json` · `/claims/wave/summary` |
| 2 | Algebra | Explains a space with multiplication, including why finite algebraic checks need not settle analytic limits. | `foundations/site/data.json` · `/ladder/4/display/excluded/7` |
| 2 | Quotient | Explains identifying descriptions judged equivalent and the need to preserve relevant structure. | `foundations/site/data.json` · `/evidence/FOUNDATIONAL_SUPPORT_INDEXED_TEST_SPACE_COMPARISON_V1/does_not_establish/1` |
| 2 | Kernel and image | Supplies the ingredients of cohomology without presupposing specialist homological algebra. | `foundations/site/data.json` · `/evidence/FOUNDATIONAL_CODED_WEAK_WAVE_H2_TEST_COMPLETION_V1/does_not_establish/3` |
| 1 | Differential complex | Explains a sequence of maps whose consecutive composition vanishes, rather than merely a complicated construction. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/5/paragraphs/0` |
| 1 | Nilpotency | Explains the consistency prerequisite currently blocking the advertised full export. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/5/paragraphs/0` |
| 1 | Cohomology | Explains which closed objects remain after exact redundancies are removed, without assigning them a particle interpretation. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/mathematics/3/paragraphs/0` |
| 2 | Cocycle and coboundary | Unpacks the two tests hidden inside a cohomology claim. | `foundations/editorial/dictionary.json` · `cohomology/explanations/specialist/0` |
| 2 | Chain map | Explains preservation of differentials and why it does not automatically preserve pairings or causality. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/specialist/1/paragraphs/0` |
| 2 | Homotopy contraction | Explains how a large complex can be related to a reduced one and which identities must hold. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/5/paragraphs/0` |
| 2 | Projection | Explains the reduction map and distinguishes a valid map from an assumed component selection. | `foundations/site/data.json` · `/evidence/FOUNDATIONAL_BT_CORNER_BORN_INTERFACE_V1/does_not_establish/2` |
| 2 | Cyclicity | Explains compatibility with a pairing that is additional to the chain-map condition. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/specialist/1/paragraphs/0` |
| 2 | Exact arithmetic | Explains why rational identities can be checked without numerical tolerance. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/mathematics/6/paragraphs/0` |
| 2 | Finite field | Prevents confusion between a finite algebraic number system and finitely many physical field modes. | `foundations/site/data.json` · `/theory_passports/passports/4/stages/0/boundary` |
| 2 | Fourier mode | Explains the building blocks used in the finite wave fixtures. | `foundations/site/data.json` · `/ladder/3/display/object/2` |
| 2 | Galerkin approximation | Explains approximation by nested finite spaces and why nesting alone does not prove convergence. | `foundations/site/data.json` · `/ladder/0/display/establishes/8` |
| 2 | Bound and estimate | Explains what a claimed bound controls and why logical bounds and analytic estimates require different readings. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/3/paragraphs/1` |

### Physics (55)

| Batch | Proposed concept | Why include it | Source evidence |
| --- | --- | --- | --- |
| 1 | Physical state (existing) | Explains what specifies a system and separates an algebraic state from a wavefunction or cohomology class. | `foundations/editorial/reading-content.json` · `/claims/cutoff/summary` |
| 1 | Observable (existing) | Explains which mathematical quantity is tied to a proposed measurement. | `foundations/editorial/reading-content.json` · `/audiences/physics/purpose` |
| 1 | Measurement and detector | Explains the operational step between a mathematical field and a reported outcome. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/general/1/paragraphs/0` |
| 1 | Field | Supplies the basic idea of quantities assigned across space and time. | `foundations/editorial/reading-content.json` · `/audiences/mathematics/background` |
| 1 | Spacetime and metric | Explains the geometrical structure on which gravity and propagation statements depend. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/specialist/5/paragraphs/0` |
| 1 | Wave equation | Gives the central worked example its physical meaning before its logical encoding. | `foundations/editorial/reading-content.json` · `/topics/wave/versions/general/3/paragraphs/1` |
| 1 | Mode and amplitude | Distinguishes a wave pattern from the coefficient specifying how much of it is present. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/4/paragraphs/0` |
| 2 | Chirality | Explains the selected wave sector used in the benchmark without assuming particle-physics terminology. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/4/paragraphs/0` |
| 1 | Energy | Explains what finite energy asserts and why it is separate from a full probabilistic state construction. | `foundations/editorial/reading-content.json` · `/topics/wave/versions/physics/1/paragraphs/0` |
| 1 | Positive energy | Separates an energy bound from positivity of a quantum state or inner product. | `foundations/site/data.json` · `/ladder/0/display/establishes/9` |
| 1 | Causality and causal support | Explains the propagation restriction that algebraic and Euclidean calculations do not supply. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/0/paragraphs/0` |
| 2 | Finite propagation speed | Explains the stronger localization statement beyond solving a wave equation. | `foundations/site/data.json` · `/ladder/5/display/object/2` |
| 1 | Locality and spatial localization | Distinguishes local dependence of laws from localization of particular data or states. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/1/paragraphs/0` |
| 1 | Initial-value problem | Explains what data must determine an evolution before discussing its mathematical acceptance conditions. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/4/paragraphs/0` |
| 2 | Boundary condition | Explains restrictions at boundaries and why they change admissible solutions. | `foundations/editorial/dictionary.json` · `function-space/definitions/physics` |
| 1 | Lorentzian and Euclidean signature | Explains the two geometrical settings and why a result in one does not establish causal physics in the other. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/1/paragraphs/1` |
| 2 | Green operator and propagator | Explains how source-response solutions are built and separates that role from a quantum state. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/specialist/5/paragraphs/1` |
| 2 | Retarded and advanced solutions | Explains which temporal support direction is chosen by a causal response. | `foundations/site/data.json` · `/ladder/5/display/object/2` |
| 2 | Hyperbolicity | Explains the equation structures targeted by the scoped propagation no-go results. | `foundations/site/data.json` · `/evidence/FOUNDATIONAL_CODED_WAVE_FRONTIER_V2/does_not_establish/3` |
| 1 | Symmetry | Explains transformations that preserve a law and introduces the distinction from descriptive redundancy. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/1/paragraphs/0` |
| 1 | Gauge symmetry | Explains why distinct field descriptions can represent the same physical situation. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/1/paragraphs/1` |
| 2 | Gauge fixing and constraints | Explains restrictions used to handle redundant descriptions without silently removing physical solutions. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/3/paragraphs/0` |
| 1 | Action and Lagrangian | Explains the variational starting point of the gravity programme. | `foundations/site/data.json` · `/theory_passports/passports/4/stages/2/summary` |
| 2 | Equation of motion | Distinguishes the dynamical condition from gauge identities and quantum consistency conditions. | `foundations/editorial/dictionary.json` · `action-and-lagrangian/definitions/general` |
| 1 | Weyl gravity | Introduces the originating proposal and explains what the pure-Weyl specialization selects. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/general/0/paragraphs/1` |
| 2 | Conformal symmetry | Explains the scale transformation at the center of Weyl gravity. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/general/3/paragraphs/1` |
| 2 | Curvature and Weyl tensor | Explains the geometrical quantity from which the theory’s action is built. | `foundations/editorial/dictionary.json` · `weyl-gravity/definitions/general` |
| 2 | Higher-derivative theory | Explains why extra solution directions and stability questions arise. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/general/3/paragraphs/1` |
| 1 | Perturbation and linearization | Explains the use and limits of studying small deviations from a background. | `foundations/site/data.json` · `/evidence/FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1/does_not_establish/4` |
| 1 | Free and interacting theory | Explains why success for uncoupled modes does not settle an interacting construction. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/3/paragraphs/0` |
| 2 | Nonlinear continuation | Explains the additional test of extending a linear solution direction beyond first order. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/3/paragraphs/0` |
| 1 | Quantum field theory | Explains the wider target beyond a classical wave or finite algebraic model. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/specialist/5/paragraphs/1` |
| 1 | Quantization | Explains the transition being attempted and why it needs more than a formal replacement rule. | `foundations/site/data.json` · `/axes/2/keys/11/plain_meaning` |
| 1 | Particle and one-particle state | Explains the interpretation that must not be inferred merely from a residual cohomology class. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/3/paragraphs/0` |
| 1 | Ghost | Separates gauge bookkeeping fields from extra modes and negative-probability concerns. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/general/3/paragraphs/0` |
| 1 | Positivity of a state | Explains the requirement tested by the reduced cutoff obstruction. | `foundations/editorial/reading-content.json` · `/claims/cutoff/boundary` |
| 2 | Indefinite inner product | Explains why an unreduced gauge description may lack a direct probability interpretation. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/1/paragraphs/1` |
| 1 | Born rule | Explains the rule connecting the chosen quantum state to probabilities. | `foundations/site/data.json` · `/axes/2/keys/3/label` |
| 1 | Unitarity | Explains a physical consistency requirement distinct from real frequencies and finite positivity. | `foundations/site/data.json` · `/evidence/FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1/does_not_establish/7` |
| 2 | Vacuum | Explains a particular state choice rather than absence of all mathematical structure. | `foundations/site/data.json` · `/axes/2/keys/4/meaning` |
| 2 | Two-point function | Explains the correlation object used in the state and Hadamard discussions. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/general/5/paragraphs/1` |
| 2 | Hadamard state | Explains the regularity condition and why BRST compatibility and positivity require separate checks. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/specialist/5/paragraphs/1` |
| 2 | Commutator and CCR | Decodes Canonical Commutation Relations and explains what the positivity correction must preserve. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/4/paragraphs/1` |
| 1 | Cutoff and truncation | Explains the finite-stage approximation whose success does not guarantee a full-limit result. | `foundations/editorial/reading-content.json` · `/claims/cutoff/summary` |
| 1 | Continuum limit | Explains the physical transition that requires control beyond a sequence of finite models. | `foundations/site/data.json` · `/evidence/FOUNDATIONAL_FINITE_FIELD_FINITE_MODE_NON_EQUIVALENCE_V1/does_not_establish/1` |
| 2 | Regularization and renormalization | Explains two related but distinct steps in making quantum calculations meaningful. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/5/paragraphs/1` |
| 2 | Counterterm | Explains what is classified before coefficients are calculated. | `foundations/site/data.json` · `/axes/2/keys/10/label` |
| 2 | Anomaly | Explains a possible quantum failure of a symmetry or identity without conflating distinct anomaly kinds. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/specialist/1/paragraphs/0` |
| 2 | Loop expansion | Explains the perturbative order of the quantum calculations. | `foundations/site/data.json` · `/evidence/FOUNDATIONAL_FINITE_BRST_TWENTY_CELL_CLOSURE_V1/does_not_establish/4` |
| 2 | Time-ordered product | Explains an essential Lorentzian quantum construction that remains an independent obligation. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/specialist/5/paragraphs/1` |
| 2 | Algebraic quantum field theory | Decodes AQFT and its perturbative form and explains the causal construction being sought. | `foundations/site/data.json` · `/evidence/FOUNDATIONAL_SCALAR_BIWAVE_TO_WEYL_BV_DEPENDENCY_DELTA_V1/does_not_establish/3` |
| 2 | Scattering | Explains a route from an interacting theory to observable predictions. | `foundations/site/data.json` · `/evidence/FOUNDATIONAL_BT_EUCLIDEAN_LATTICE_IMPORT_V1/does_not_establish/5` |
| 2 | Empirical prediction and fit | Explains why a mathematical result must still connect to a specified observational comparison. | `foundations/editorial/reading-content.json` · `/claims/wave/summary` |
| 2 | Residual and uncertainty weighting | Separates observational discrepancies and error weighting from residual objects in homological algebra. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/1/paragraphs/0` |
| 2 | Galaxy rotation curve | Explains the observational case study used to test a concrete gravity prediction. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/general/3/paragraphs/1` |

### Project (45)

| Batch | Proposed concept | Why include it | Source evidence |
| --- | --- | --- | --- |
| 1 | Reverse foundations of physics | Names the wider programme and distinguishes it from reverse mathematics alone. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/general/0/paragraphs/1` |
| 1 | Physical postulate | Explains the physical assumptions supplied before mathematical inference begins. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/0/paragraphs/1` |
| 1 | Carrier (existing) | Explains the chosen realization and why its topology, pairing and domains belong to the claim. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/1/paragraphs/0` |
| 1 | Foundational regime | Explains the atlas axis describing allowed mathematical assumptions. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/2/paragraphs/0` |
| 1 | Physical obligation | Explains the concrete task a theory must discharge instead of treating a theory name as an answer. | `foundations/editorial/reading-content.json` · `/audiences/specialist/purpose` |
| 1 | Atlas cell and evidence grade | Explains what a cell’s recorded evidence covers and why a populated grid is not a completed theory. | `foundations/editorial/reading-content.json` · `/audiences/specialist/purpose` |
| 1 | Theory journey and interface | Explains why composing results requires a verified connection between their constructions. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/general/7/paragraphs/1` |
| 1 | Claim scope and assumptions | Explains how to read exactly what a result quantifies over and what it leaves conditional. | `foundations/editorial/reading-content.json` · `/audiences/mathematics/purpose` |
| 1 | Certificate and provenance | Explains what was encoded and checked and how to trace the inputs behind an assertion. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/3/paragraphs/1` |
| 1 | Independent verification | Explains why replaying a producer and checking by another route provide different evidence. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/6/paragraphs/0` |
| 2 | Formal proof and computational check | Separates finite tests, written arguments and completed formal derivations. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/6/paragraphs/0` |
| 1 | Fail-closed claim boundary | Explains why missing, skipped or failed checks cannot authorize a stronger published status. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/6/paragraphs/0` |
| 1 | No-go theorem and obstruction | Explains how a failure can exclude a specified route without refuting an entire programme. | `foundations/editorial/reading-content.json` · `/claims/cutoff/boundary` |
| 1 | Finite-stage versus uniform construction | Explains the quantifier distinction linking the wave and positivity case studies. | `foundations/editorial/reading-content.json` · `/claims/cutoff/summary` |
| 1 | Supplied-rate and rate-free wave reconstruction | Names the two benchmark tasks and identifies the representation change carrying their logical difference. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/mathematics/4/paragraphs/0` |
| 2 | Fixed wave-detector benchmark | Explains which physical ingredients are held fixed while the reconstruction assumptions change. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/general/4/paragraphs/0` |
| 2 | Finite chiral fixture | Explains the ladder’s finite exact starting object and its limited claim boundary. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/4/paragraphs/0` |
| 2 | Completion ladder | Explains the sequence of additional requirements from finite modes toward distributional and energy carriers. | `foundations/editorial/reading-content.json` · `/topics/wave/versions/specialist/3/paragraphs/1` |
| 2 | Representation invariance | Explains the question of whether a result survives changing the encoding while preserving its observable. | `foundations/editorial/reading-content.json` · `/topics/wave/versions/mathematics/3/paragraphs/1` |
| 2 | BRST formalism | Expands Becchi–Rouet–Stora–Tyutin and explains the symmetry differential used to organize gauge redundancy. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/5/paragraphs/0` |
| 2 | BV formalism | Expands Batalin–Vilkovisky and explains the field–antifield structure beyond the BRST acronym. | `foundations/site/data.json` · `/axes/2/keys/8/label` |
| 3 | BFV boundary formalism | Expands Batalin–Fradkin–Vilkovisky and explains the boundary partner of the classical construction. | `foundations/site/data.json` · `/cells/310/summary` |
| 2 | Field, ghost and antifield complex | Explains the full collection of variables whose identities must be checked together. | `foundations/site/data.json` · `/evidence/FOUNDATIONAL_SCALAR_MINKOWSKI_GREEN_CHOICE_AUDIT_V1/does_not_establish/3` |
| 3 | Classical master equation | Explains the classical consistency identity separately from its quantum counterpart. | `foundations/site/data.json` · `/axes/2/keys/13/meaning` |
| 2 | Quantum master equation | Expands QME and explains why restoring it is a specific obligation rather than a completed quantum theory. | `foundations/site/data.json` · `/axes/2/keys/13/label` |
| 3 | Local BRST cohomology | Explains the classification problem for local counterterms and anomalies before coefficient computation. | `foundations/site/data.json` · `/evidence/barnich-brandt-henneaux-2000/boundary` |
| 2 | Residual complex and cohomology | Explains the reduced mathematical object while distinguishing it from an observational residual. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/specialist/1/paragraphs/1` |
| 2 | Centered deformation and vertex class | Explains the certified residual classes’ role without presenting them as one-particle gravitons. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/specialist/5/paragraphs/1` |
| 2 | Residual transfer | Explains what must be transported to the reduced complex after earlier consistency gates. | `foundations/site/data.json` · `/axes/2/keys/14/label` |
| 2 | Classical import gate | Explains why an imported classical object needs all required identity checks before dependent quantum claims. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/0/paragraphs/0` |
| 2 | Dependency tag | Explains that a tag records a kind of dependency, not a confidence score or audience level. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/specialist/1/paragraphs/1` |
| 2 | LOCAL-ALGEBRAIC | Defines the boundary of algebraic quantum results that do not by themselves construct causal observables. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/specialist/1/paragraphs/1` |
| 2 | EUCLIDEAN-SPECTRAL | Defines the boundary of Euclidean spectral calculations relative to Lorentzian physics. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/specialist/1/paragraphs/1` |
| 2 | REDUCED-MODE | Defines what restricting to a mode sector establishes and what it leaves out. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/5/paragraphs/1` |
| 2 | LORENTZIAN-CAUSAL | Defines the dependency class relevant to actual causal constructions without implying certification. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/specialist/1/paragraphs/1` |
| 2 | Lifecycle state | Explains classification, coefficient calculation, QME restoration, residual transfer and Lorentzian certification as separate statuses. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/specialist/1/paragraphs/1` |
| 2 | TT sector | Expands transverse–traceless and explains the restricted sector used in the positivity example. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/specialist/4/paragraphs/1` |
| 2 | Reduced positivity obstruction | Explains the finite-repair versus smooth-full-repair distinction and its reduced-model scope. | `foundations/editorial/reading-content.json` · `/claims/cutoff/boundary` |
| 2 | Full-export consistency failure | Explains the current correction to older introductions and why partial repair does not reopen the full-transfer claim. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/5/paragraphs/0` |
| 3 | Off-shell BV propagator | Explains the full propagator obligation beyond an on-shell solution or reduced-sector construction. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/specialist/4/paragraphs/1` |
| 3 | BRST-compatible Hadamard construction | Explains the simultaneous compatibility requirements hidden by a short transfer label. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/5/paragraphs/0` |
| 3 | Lorentzian renormalization gate | Explains why local or Euclidean calculations do not supply renormalized causal time-ordered products. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/specialist/5/paragraphs/1` |
| 3 | Scoped hyperbolicity witnesses | Explains exactly which tested propagation architectures are ruled out rather than claiming no possible causal theory. | `foundations/site/data.json` · `/evidence/FOUNDATIONAL_CYLINDER_WAVE_STRENGTH_LADDER_V1/does_not_establish/6` |
| 2 | Empirical acceptance protocol | Explains the specified data, error model and acceptance conditions behind a comparison of theories. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/physics/0/paragraphs/0` |
| 2 | AI editorial review | Explains authorship and the difference between assisted drafting, mechanical checks and independent scientific approval. | `foundations/editorial/reading-content.json` · `/topics/introduction/versions/general/6/heading` |

## Evidence and limitations

145 proposals have mentions in the reading accounts, ladder or atlas. Five are explicit background exceptions supported by matrix/paper mentions: Cocycle and coboundary; Boundary condition; Equation of motion; Curvature and Weyl tensor; BFV boundary formalism. Their reasons are prerequisite value, not frequency. Review these exceptions before commissioning explanations.

The [machine-readable proposal](../editorial/core-terminology-proposal.json) owns the selection. The [evidence inventory](../results/CORE_TERMINOLOGY_PROPOSAL_V1.json) pins the corpus and current reading sources and records scope counts and original source spans. Search can find generic or overloaded mentions; those are navigation aids, not definition validation. This is AI editorial work, not independent human approval.

Run `python3 foundations/build_core_terminology_proposal.py --check` for deterministic reproduction and `python3 foundations/verify_core_terminology_proposal.py` for independent structural and source-span checks. The [receipt](../receipts/core-terminology-proposal-v1.json) records commands, timings and test-tier boundaries. The proposal generator does not publish definitions; the separate dictionary implementation has its own website checks.
