# How to Build a Universe—and Find Out Whether Its Ghosts Are Real

*By GPT-5.6-sol and Asger Alstrup Palm*

Einstein's theory of relativity turns gravity into the geometry of spacetime.
Matter and energy curve spacetime; that geometry tells matter, light and
clocks how to move.

This picture explains familiar phenomena. Clocks run at different rates in
different gravitational fields. Light bends and changes color. Gravitational
waves cross the universe. Black holes form. The universe expands.

Our project asks whether a different mathematical theory of spacetime—called
conformal or pure-Weyl gravity—can support a physically coherent universe. Its
equations contain four derivatives instead of Einstein's two. That makes the
theory interesting for quantum gravity, but it also produces extra solutions
whose signs look wrong. These are commonly called gravitational ghosts.

We do not assume in advance that the extra solutions are physical, harmless
or fatal. We build the mathematical universe in layers and make each layer
pass the standard tests physicists use for spacetime, causality, waves,
clocks, interactions and quantum particles.

The basic rule is:

> A pattern in an equation is not yet a physical object. It must survive the
> constraints, carry a measurable physical effect, propagate causally, and
> remain consistent when interactions and quantum physics are included.

## Why this project exists

This is also an experiment in how scientific research can be done with AI. It
is directed by Asger Alstrup Palm, Honorary Professor at DTU Compute, whose
field is computer science rather than physics. The aim is not to use AI merely
to explain established science or polish a manuscript. It is to test whether
AI agents can help formulate sharp questions, construct counterexamples,
derive large symbolic calculations, write verification programs, discover
mistakes, and turn successful results into research that other people can
audit.

Palm chooses the overall direction, decides which questions the teams pursue,
and retains editorial responsibility for the public claims. AI agents propose
and execute much of the detailed mathematical, computational, verification,
literature-mapping, and drafting work. Neither human credentials nor fluent AI
output count as evidence. A result enters the project only with a declared
scope and a reproducible chain connecting the claim to symbolic artifacts and
independent checks.

This is why the repository preserves failed constructions, convention errors,
counterexamples, missing assumptions, exact hashes, and tests designed to
break proposed conclusions. If the candidate theory eventually fails a
physical requirement, locating that failure precisely is still useful physics
and still answers part of the AI-research question.

The intended form of collaboration is open scrutiny. The repository is being
prepared as a public research object so physicists, mathematicians, and AI
researchers can reproduce the calculations, challenge their interpretation,
or continue from a certified boundary without first joining a conventional
collaboration. Palm's DTU affiliation identifies his academic role; it does
not imply that DTU endorses the project or its conclusions.

## The universe in ordinary language

The project has a mathematically complete classical starting universe for
small disturbances before their full interactions are switched on.

Space is finite but has no edge. At each moment it is a three-dimensional
sphere, and that whole sphere evolves through time. This is a model of an
entire universe, not a box cut out of a larger space.

The closest everyday analogy is the two-dimensional surface of the Earth. It
has a finite area, but a traveler can keep moving without reaching an edge. A
three-dimensional sphere is the same closed idea one dimension higher.

Stacking the successive spherical spaces through time produces what
mathematicians call the conformal cylinder. The word *cylinder* describes the
history of a closed universe. It does not mean that space is shaped like a
pipe or that the universe sits inside one.

### The short version of what we have

- **Cause runs from past to future.** If a source is switched on tomorrow,
  the tested classical equations do not let it change a detector today. This
  has been checked for the complete gravitational system and for the version
  containing the matter clock—not merely for one convenient equation.
- **There are physical clocks.** Healthy matter fields provide an internal
  reading that changes steadily. In a particular zero-total-charge version of
  the closed universe, shifting the time label of the entire history can be a
  redundant description even while the internal clock keeps changing. In the
  unrestricted version, the same time shift carries a real charge and is a
  physical symmetry.
- **There are classical light and gravitational-wave directions.** In a
  coupled gravity-and-electromagnetism universe, familiar electromagnetic and
  gravitational wave patterns solve the linear equations and carry a nonzero
  physical comparison rule. This establishes classical waves, not quantum
  photons, quantum gravitons or a detector prediction.
- **A dynamical redshift fixture now works.** A positive-energy, source-free
  Maxwell wave is read by relational observers on the Berger clock
  background. The compact spatially averaged frequency ratio is invariant
  under coordinate, conformal, Maxwell-gauge and total-time relabelings; one
  exact fixture gives \(1+z=2\). Localized emitter and receiver endpoints, a
  retarded pulse, backreaction and phenomenology remain open.
- **The larger theory also has two extra classical wave directions in one
  tested family.** They are not disguised Einstein waves, and an exact local
  comparison between them is nonzero and positive at the current reduced
  equation level. This means they do not vanish as mere algebraic
  bookkeeping there. It does **not** yet mean that nature contains two new
  particles: the full spacetime energy rule, causal boundary conditions and
  final physical quotient still have to be checked.
- **The apparent ghost is not automatically a particle.** In the selected
  boundary-free, zero-charge universe, no isolated one-particle conformal
  graviton survives after redundant descriptions are removed. Two collective
  curvature patterns remain with a positive comparison rule. They describe
  possible interactions or changes to the theory, not particles flying
  through space.
- **The first interaction test works in the clock universe.** The quadratic
  interaction satisfies the required gauge and consistency identities. This
  is the first nonlinear rung, not a proof that every higher interaction is
  stable.
- **Every statement has a computational receipt.** Exact symbolic programs
  derive and check the large identities. Separate verifiers, broken-input
  tests, content hashes and clean rebuilds record what was proved and prevent
  a local calculation from being advertised as a quantum or cosmological
  result.

This is a real but incomplete mathematical universe. It has spacetime,
classical causal propagation, clocks, classical electromagnetic and
gravitational wave directions, two classified extra fourth-order directions
in a separate compact gravity-and-electromagnetism setting, and a first
controlled interaction layer. It does not yet have a certified relational
redshift with localized endpoints, a physical mass-generation mechanism,
electrons, non-Abelian gauge fields, quantum particles, a unified
gauge--matter sector, gravitational lensing, black-hole boundaries, a
scattering experiment, or a dark-matter or dark-energy prediction.

The map below shows how these pieces depend on one another. Green boxes are
foundations that have passed their stated mathematical tests, amber boxes are
areas where real results exist but the larger physical claim is not finished,
and gray boxes are still open. The arrows matter: for example, a classical
wave is a prerequisite for a quantum particle, but it is not itself a quantum
particle. Behind every green or amber box is a named computational receipt.

![How the candidate universe is being built](../certificate_graph/universe-building-dag.png)

[Open the scalable construction map](../certificate_graph/universe-building-dag.svg).

## What "gauge" means

Gauge is the physicists' word for redundancy in a description. It means that
two different-looking sets of mathematical variables represent the same
physical situation.

The same place on Earth can be described using latitude and longitude, a
street map or a rotated grid. The numbers change, but the place does not.
Gravity has the same feature: stretching or relabeling the coordinate grid can
change every component of the metric without changing the underlying
spacetime. Conformal gravity has an additional freedom that changes the local
scale—the choice of ruler—while preserving the light cones.

A gauge transformation is not a new force, event or wave. Counting it as
physical would count the same universe more than once. Removing gauge means
identifying all descriptions that differ only by this redundancy.

There is an important difference between a gauge transformation and a
physical symmetry. They can look similar in the equations. A physical
symmetry has a measurable generator or charge, such as energy or angular
momentum. A proper gauge direction has zero generator in the declared
physical setting and changes no observable. The calculation decides which
case applies; the label is not chosen by taste.

Asking whether time translation is gauge does **not** mean that clocks stop,
change is unreal or every moment is identical. It asks whether shifting the
coordinate label of the entire closed universe creates a new physical state,
or only a new description of the same constrained history. Relational
statements—what one field does when a physical clock reads a particular
value—can remain nontrivial even when the total shift is gauge.

This distinction changes the ghost question. A raw extra solution can be a
genuine physical direction, a redundant description, a mode removed by a
constraint, or a boundary excitation. Its sign matters physically only after
that classification is complete.

## What causality means here

A causal theory does not allow an event in the future to change what already
happened in the past. If a source is switched on tomorrow, a detector must not
respond today. A disturbance may influence only events inside its future
light cone.

The physical response used for this test is the **retarded** response: it
starts at the source and propagates toward the future. Physicists also
construct an **advanced** mathematical partner pointing toward the past. That
partner is needed to test the equations and build physical comparison rules;
it does not authorize backward-in-time signalling. The physical
source-response rule is retarded.

The complete free pure-Weyl calculation passes this classical causality test
across all 386 linked parts of its gravitational bookkeeping system. The
clock-coupled Berger universe has a separate causal result across all 54 parts
of its gauge-fixed system. In both cases the retarded response is confined to
the causal future and the constraints propagate with it.

These are classical causality results. A global quantum state with the
required short-distance and causality properties is a separate rung.

Work toward that quantum rung has identified the standard local
short-distance wave pattern for the basic clock-universe fields and derived
an exact formal recipe for transporting it through the coupled equations.
The recipe is not yet a quantum state. The current mathematical estimates do
not prove that all singular directions of the transported distributions fit
together safely. The certification therefore stops at that precise boundary.

## What each rung has to prove

Words such as *light*, *particle* and *black hole* carry a great deal of
physics. We do not count a phenomenon merely because something in an equation
has a familiar shape. Each rung has a recognized acceptance test.

### Spacetime and curvature

The geometry must solve the gravitational field equations. Small disturbances
must obey compatible equations and constraints. This is what gives defined
meaning to distances, durations, curvature and light cones.

### Causality

Sources must produce responses only where the light cones permit them. In
particular, a future source must not alter the past. For gravity this must hold
for the entire constrained gauge system, not just one selected component.

### Light

Classical light requires electromagnetic equations, nontrivial wave solutions
and propagation along the spacetime light cones. Observable light also
requires sources, detectors and energy flux. A photon requires the additional
quantum-particle tests below.

### Electrons and charged matter

An electron-like field must have the correct spin, electric charge and
fermionic behavior. It needs causal propagation, stable coupling to
electromagnetism and gravity, and a physical mechanism that supplies a mass
scale in a conformal theory. A classical spinor field is still not a quantum
electron until the particle tests pass.

### Physical mass and rest energy

Pure conformal gravity has no built-in mass scale. The open task is therefore
not to invent \(E=mc^2\), which already follows from relativistic symmetry.
It is to construct a physical mass-generation mechanism and stable massive
excitations. Once such an excitation has a Lorentz-invariant relation

\[
E^2=p^2c^2+m^2c^4,
\]

the rest-energy formula \(E=mc^2\) follows at \(p=0\). In the present closed
universe this must eventually be stated through local inertial observables or
an asymptotically flat sector with physical energy and momentum.

### A unified gauge--matter sector

A Grand Unified Theory, or GUT, normally combines the strong, weak and
electromagnetic interactions in one gauge structure. It does not by itself
include gravity. For this project the honest long-range target is therefore
pure-Weyl gravity coupled to a unified gauge--matter candidate.

That requires non-Abelian Yang--Mills fields, chiral fermions with the right
charges, cancellation of gauge and mixed anomalies, a symmetry-breaking and
mass-generation mechanism, quantum particle states, and recovery of the
known low-energy interactions. Choosing a large gauge group alone would be a
candidate ansatz, not a completed GUT.

### Gravitational waves

A gravitational wave must solve the linearized gravitational equations,
survive all redundant coordinate and scale descriptions, carry a nonzero
physical comparison rule, and propagate causally. An observable waveform also
needs energy flux, boundary conditions and a response in a detector.

### Clocks, time dilation and redshift

A clock must change steadily, have healthy energy and couple consistently to
gravity. Time dilation requires comparing two such physical clocks.
Gravitational redshift requires an emitter, a light signal and a receiver; the
observable is the ratio of the frequencies measured by the two clocks, stated
without relying on arbitrary coordinate labels. The present Berger fixture
passes this test for a dynamical Maxwell wave and compact spatially averaged
relational observers, with an exact ratio \(1+z=2\). Turning that global
fixture into localized endpoints and a retarded signal is the next rung.

### Gravitational lensing

Lensing requires a physical source of curvature, causal light paths around
that source and observable comparisons of angles, brightness or arrival
times. Drawing a bent line in a coordinate system is not enough—the result
must be independent of how the spacetime map was drawn.

### Interactions

The nonlinear equations must say how waves and matter exchange energy. The
interactions must preserve all constraints and must not regenerate a forbidden
or unstable physical mode. Passing quadratic order does not automatically
grant cubic order, higher orders or global evolution.

### Quantum particles

A particle requires a global quantum state, a positive probability rule and a
controlled separation into physical and redundant states. Scattering
particles additionally require meaningful incoming and outgoing regions. A
classical wave is therefore evidence for a field mode, not yet for a photon,
electron or graviton.

### Black holes

A black-hole candidate must possess a genuine horizon rather than a coordinate
artifact. Its boundary conditions, conserved charges, causal perturbations,
thermodynamic quantities and stability must all be controlled. A metric with a
zero in one coefficient is not by itself a physical black hole.

### Quantum gravity

The quantum gauge identities must remain consistent after regularization and
renormalization. Quantum anomalies must either cancel or have an allowed
repair. The theory also needs suitable short-distance states, causal quantum
products and a physical state space. Classical causal propagation is an
essential input, not the completed quantum theory.

### Cosmology, dark matter and dark energy

The theory must supply stable evolving universes and galaxy-scale solutions,
derive observables such as expansion, lensing and rotation curves, and compare
them with data. Fitting a curve is meaningful only after the underlying modes,
clocks, causality and stability have passed their own tests.

## The universe-building map

The table below is both a status summary and a public TODO list. A scoped pass
means that the stated phenomenon exists in a precisely declared mathematical
setting. It does not automatically extend to every background, interaction or
quantum theory.

| Familiar feature | Where the project stands | Decisive next test |
|---|---|---|
| **Spacetime and curvature** | **Scoped pass.** Exact boundary-free spherical and Berger backgrounds solve their declared classical equations. | Extend causal control to broader globally hyperbolic backgrounds. |
| **Causality** | **Scoped pass.** Retarded responses in the complete 386-part gravity system and 54-part clock system do not let future sources alter the past. | Construct the corresponding global quantum state and quantum causality theorem. |
| **Clocks and time dilation** | **Partial.** A healthy matter clock changes internally while total time shift can remain gauge in the fixed-coupling, linear, zero-charge sector. | Compare two physical clocks and calculate an observable time-dilation law. |
| **Gravitational redshift** | **Scoped partial pass.** A positive-energy dynamical Maxwell mode and invariant compact spatially averaged relational frequency ratio are certified; one exact fixture gives \(1+z=2\). | Localize emitter and receiver, construct a compact retarded pulse, include gravity--Maxwell interaction dressing and backreaction, then test phenomenology. |
| **Classical light** | **Partial.** Standard electromagnetic wave directions occur in the compact Einstein--Maxwell inclusion. | Build physical sources, detectors, energy flux and boundary conditions. |
| **Physical mass scale and massive matter** | **Open.** The conformal theory has no certified mass-generation mechanism or stable massive excitation. \(E=mc^2\) is a later relativistic consistency check, not the missing mechanism. | Generate a physical scale, construct a stable massive mode, and verify its causal dynamics and relativistic mass shell. |
| **Electrons and charged matter** | **Open.** No certified charged spin-one-half matter sector exists in the current universe. | Add a Dirac field, a physical mass/scale mechanism, causal propagation and stable interactions. |
| **Non-Abelian gauge fields and chiral matter** | **Open.** The certified matter content does not yet contain a Yang--Mills gauge group or chiral fermion spectrum resembling the strong and weak interactions. | Build the causal BV complex, physical pairing and stable interactions for a non-Abelian gauge group and chiral representations. |
| **Unified gauge--matter sector (GUT candidate)** | **Open, long-range target.** No unified group, anomaly-free matter representation, breaking mechanism or low-energy recovery theorem has been selected. This would initially be a GUT coupled to Weyl gravity, not a theory unifying gravity itself. | Find a viable group and chiral matter sector, cancel all relevant anomalies, generate and break the physical scale, and recover Standard Model particles and interactions. |
| **Gravitational waves** | **Partial.** Standard linear gravitational wave directions occur with a nonzero physical pairing, and the pure-gravity complex propagates causally. In a separate compact axial family, two extra fourth-order directions survive the reduced equation and local-pairing tests. | Match the extra directions to the direct four-dimensional physical current, impose causal boundary conditions, and produce measurable waveforms, flux and detector response. |
| **Gravitational lensing** | **Open, with geometric ingredients present.** Curved spacetime and light cones exist, but no certified lensing observable does. | Add a localized lens, propagate light around it and compare observable angles and arrival times. |
| **Quantum particles** | **Open.** Classical waves are not yet photons, gravitons or electrons; the surviving curvature classes are not particles. | Construct a global quantum state, physical positive pairing and incoming/outgoing particle interpretation. |
| **Interactions** | **Partial.** The complete quadratic clock-coupled interaction passes its declared cyclic and gauge tests. | Pass cubic and higher identities, resonant channels and global nonlinear evolution. |
| **Black holes** | **Open in this certified pipeline.** No horizon phase space, boundary charge or stability theorem has been imported into the universe. | Select a black-hole background and certify its horizons, causal perturbations, charges, entropy and stability. |
| **Quantum gravity** | **Early groundwork only.** Candidate anomaly types and the basic local short-distance wave structure are partly classified. Exact formal transport through the clock system is known, but its distributional wavefront safety is not; there is no coupled Hadamard state or restored quantum master equation. | Prove or obstruct the microlocal transport, then compute anomaly coefficients, restore the quantum gauge identity and construct the global quantum theory. |
| **Cosmology, dark matter and dark energy** | **Open.** The current work establishes consistency machinery, not a fitted cosmological model. | Build stable cosmological and galaxy backgrounds, derive observables, then compare them with data. |

## If the universe differs from standard physics

Agreement with Einstein gravity and ordinary quantum field theory is one
possible result. It would show that the new mathematical framework can recover
known physics while organizing its gauge and causal structure differently.

A controlled difference could be new physics. An extra wave, charge,
interaction or cosmological effect would be interesting only if it passes the
same causality, stability, gauge and quantum tests as the familiar phenomena.

The two newly isolated extra wave directions are now at exactly this fork.
They have survived enough exact tests that they cannot be dismissed as a
repeated factor in an equation, but not enough to call them observable new
physics. The next physical comparison may show that they are healthy, ghostly,
removed by admissible boundaries, or confined to this compact sector.

A difference can also be a no-go result. The calculation may show that a
clock cannot remain healthy, a mode has an unavoidable negative physical
direction, an interaction cannot preserve the constraints, a black-hole
boundary condition is inconsistent, or a quantum anomaly cannot be removed.

Sector dependence is another possible outcome. The theory may work on a
closed zero-charge universe but fail when time translation carries energy at
an outer boundary. That is not a contradiction; it is a statement that the
physical theory requires a selection rule and does not describe every
possible universe in the same way.

The project can therefore stop at any rung. If it stops because an exact
obstruction is found, that obstruction is still valuable physics. It tells us
which attractive idea cannot describe nature, under which assumptions, and
what a successful theory would have to change. If it continues, every passed
rung narrows the space of viable alternatives and makes a possible new
prediction more credible.

Success and failure are both scientific outcomes:

- **recovery** shows that known physics is contained;
- **new physics** is a difference that survives all required tests;
- **sector selection** identifies the conditions under which the theory
  works;
- **a scoped no-go** rules out a complete family of proposed constructions;
- **a decisive obstruction** marks the rung where this candidate universe
  ends.

## The code is a symbolic physics laboratory

The calculations are too large and too sensitive to signs and conventions to
manage reliably as hand algebra alone. We use code to perform exact symbolic
derivations while keeping the physical assumptions visible.

This is not a numerical simulation of a universe. The programs derive and
check algebraic consequences of the equations. They generate differential
operators from the action, expand large interactions coefficient by
coefficient, and compute ranks, constraints, pairings, signs and obstructions
using exact rational or algebraic arithmetic.

The scale is substantial. The free causal gravity model links 386 rows of
fields, equations and gauge data. The clock-coupled interaction uses a
54-part system and contains 54,236 canonical nonzero coefficients after exact
simplification.

Every material claim carries an accountability trail:

1. The theory, background, charge sector, boundary conditions and claim level
   are declared.
2. A machine-readable certificate records inputs, assumptions, hashes,
   outputs and unresolved fields.
3. An independent verifier replays the decisive identity instead of trusting
   the program that generated it.
4. Deliberately broken inputs must fail, preventing a verifier from passing
   without actually checking the mathematics.
5. Local algebra, causal physics and quantum claims receive different labels
   and cannot be silently exchanged.
6. Publication files are rebuilt from a clean archived commit and compared
   with recorded hashes.
7. Failed approaches and no-go results remain in the ledger instead of
   disappearing when another route succeeds.

The repository therefore functions like a symbolic experimental laboratory.
A result can be inspected at three levels: the physical statement, the
mathematical identity and the exact computational receipt.

The code cannot prove assumptions that were never encoded. Analytic
existence, global boundary conditions and quantum interpretation must each
pass their own tests. The system is designed to fail closed when a required
layer is missing.

## Where the technical continuation lives

This article is the general-audience front door. The specialist continuation
is maintained separately so that this explanation does not gradually turn
into a technical paper.

The [physicist executive summary](98-physicist-executive-summary.md)
gives the claim-by-claim result spine, audience-specific connections,
lifecycle labels and direct links to the papers and certificates. A
[PDF version](98-physicist-executive-summary.pdf) is available as a
short technical briefing.

The central research question is:

> Is the apparent extra gravitational branch a physical instability, a gauge
> direction, a constrained sector, a boundary excitation or a quantum
> anomaly—and which answer applies in each mathematically complete universe?

The project builds enough of each universe to make that question testable.
Passing a rung expands the universe. Failing a rung produces an exact,
reproducible boundary on what the theory can describe.
