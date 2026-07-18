# Pure-Weyl gravity programme: executive summary for physicists

Last substantive update: 18 July 2026.

This is the short, live front door to the programme. It is written for a
physicist deciding whether the work intersects their own. It summarizes
results; it does not replace the technical manuscripts, certificate ledgers,
or the [universe-building roadmap](../notes/universe-building-roadmap.md).

> **Research context.** This programme is led by Asger Alstrup Palm, Honorary
> Professor at DTU Compute, as an investigation into whether agentic AI can
> make auditable contributions to scientific research. Palm is a computer
> scientist, not a physicist. The physics is therefore offered for expert
> scrutiny through typed claims, exact symbolic artifacts, independent
> verifiers, and explicit limitations—not on the authority of either the
> human director or the AI systems. The DTU affiliation identifies Palm's
> academic role and does not imply institutional endorsement of the project or
> its conclusions.

## The sixty-second version

Fourth-order gravity has more local solutions than Einstein gravity, and its
extra spin-two branch is normally associated with negative energy or norm.
Our starting point is that four logically different questions are often
collapsed into that one statement:

1. What modes solve the local field equations?
2. Which modes survive gauge, charge, and boundary reduction?
3. Which reduced structures survive interactions?
4. Which survive quantization and define asymptotic particles?

We have exact answers to substantial parts of the first two questions,
sharply scoped results on the third, and a first rigorous but indefinite
answer on one reduced free carrier at the fourth. We do not yet have a
full-BV positive state, asymptotic particles, scattering, or unitarity.

### Starting point: choices, not conclusions

The programme began from a deliberately restricted solvable laboratory. The
following are inputs to the first calculation, not claims silently promoted to
all spacetimes or to the completed quantum theory.

\[
S_{\rm W}=\alpha\int d^4x\,\sqrt{-g}\,
C_{\mu\nu\rho\sigma}C^{\mu\nu\rho\sigma},
\qquad M=\mathbb R\times S^3.
\]

| Starting choice | Why it was chosen | What it does **not** imply |
|---|---|---|
| Four-dimensional Lorentzian pure-Weyl action | It is the candidate local, conformally invariant fourth-order gravity theory being stress-tested. | That Weyl gravity is correct, stable, unitary, or ghost-free. |
| Exact conformal cylinder | It is a closed, causal, highly symmetric universe on which the complete gauge complex can be computed exactly. | That the observed universe has this global topology, or that compact results determine boundary charges or scattering. |
| Vacuum, free, linearized starting theory | It isolates the gravitational constraint, propagation, and pairing problem before adding further failure modes. | Nonlinear closure, generic matter compatibility, black holes, cosmology, or quantum particles. |
| Diffeomorphisms and local Weyl transformations treated as gauge | They are the defining local redundancies of pure-Weyl gravity. | That every residual conformal transformation is proper gauge on every phase space. |
| Residual \(D\) tested as a constraint in a selected zero-charge sector | It gives an exact test of whether apparent fourth-order modes survive the proposed reduction. Its legitimacy is decided by the covariant charge. | That \(D\) is universally gauge. It is charged on the unrestricted compact phase space and must be recomputed with matter or boundaries. |
| The full BV--BFV complex, rather than an isolated fourth-order operator, is the classical object | Fields, ghosts, equations, constraints, identities, causal homotopies, and pairings must be reduced together. | That a raw mode is a physical state, that a Hilbert/Fock space already exists, or that a propagator pole is a particle. |

Einstein gravity was not assumed to be a consistent subsector. Constructing
its map into the Weyl complex, the relative cofiber, the induced covariant
forms, and the mixed nonlinear brackets is now one of the programme's
principal tests.

The most complete field-theory result is for free pure-Weyl gravity on the
Lorentzian conformal cylinder, \(\mathbb R\times S^3\), in a selected
closed-universe, zero-charge BV--BFV sector. There the full covariant causal
complex is connected to the residual state complex by retarded and advanced
chain homotopies. After all fifteen residual \(SO(4,2)\) generators are
imposed as constraints, the vacuum and one-particle residual sectors are
acyclic. The first surviving classes are

\[
H^4=\operatorname{span}\{[W_+^2],[W_-^2]\},
\qquad G=I_2.
\]

These are positive-paired deformation or vertex classes, not positive-norm
graviton particles.

The restriction is physical, not cosmetic. On the unrestricted compact
linearized phase space, cylinder time translation \(D\) carries a charge and
is not gauge. It becomes gauge on the full Taub/moment-map zero fibre and its
selected derived quotient. A healthy rotating-scalar Berger-cylinder example
shows that a matter clock can coexist with a vanishing total \(D\) charge at
fixed couplings and linear order, but this is not yet a generic, nonlinear,
quantum, or asymptotic theorem.

The honest present verdict is therefore:

> The free classical cylinder theorem survives in its declared sector and now
> has a covariant causal realization. A universal claim that the fourth-order
> ghost is absent would be false; interactions, quantum anomalies, extra
> fourth-order branches, and asymptotic scattering remain decisive.

The newest compact Einstein--Maxwell calculation makes the extra-branch
qualification concrete. In the generic axial \(\ell\geq2\) block, the
Weyl--Maxwell solution module is strictly larger than the Einstein--Maxwell
image by two exact polarizations. The reduced current now matches a direct
four-dimensional Weyl--Maxwell Lee--Wald current. The extra block is
nonradical with signature \((2,0)\), while the complete generic axial target
has signature \((3,1)\); unexpectedly, its negative direction lies on one
Einstein-image master branch rather than on either extra direction. These are
compact classical current signs, not yet quantum norms or particle claims:
final residual descent, causal boundary admissibility, and a positive-frequency
state space remain open.

The independent polar target operator has now also been reconstructed off
shell. On every declared physical \(\ell\geq2\) compact-momentum fibre,
including zero momentum, its exact polynomial Einstein square and primary
decomposition identify the complete Einstein summand plus two extra polar
summands; its action normalization is derived independently from the
four-dimensional variation and harmonic norms. The direct polar extra
Lee--Wald current, ungauged BV/Noether lift, and final residual descent remain
open.

The construction graph below makes the dependency structure explicit. Green
nodes are demonstrated in a declared setting, gold nodes are working examples,
red nodes record exact limits, and gray nodes are the next frontiers. Every
non-open node points back to named machine-verifiable certificates; an arrow
means that the lower claim depends on the upper one.

![Certificate-backed construction map for the candidate universe](../certificate_graph/universe-building-dag.png)

[Open the scalable public graph](../certificate_graph/universe-building-dag.svg)
or the [complete technical certificate DAG](../certificate_graph/certificate-dag.svg).

## How claims are typed

> **Comparison protocol.** Every conclusion is indexed by
>
> ```text
> (theory, background, generator, phase space, boundary conditions, lifecycle)
> ```
>
> Two conclusions are compared as competing physical claims only after these
> six entries have been matched or an explicit map between them has been
> proved. The same protocol is used in papers, talks, and external bridge
> notes.

This prevents a local mode, a compact reduced class, a boundary charge, and an
asymptotic particle from being treated as four descriptions of the same
object without proof. In particular, `LOCAL-ALGEBRAIC` and `REDUCED-MODE`
results are not reported as `LORENTZIAN-CAUSAL` or quantum theorems.

We use four plain-language states in this document:


- **Certified**: an exact artifact and an independent verifier establish the
  scoped claim.
- **Partial**: a real theorem or obstruction is established, but a named
  dependency needed for the larger conclusion is still open.
- **Fail-closed**: a proposed promotion was tested and is not accepted; this
  may be a no-go for one ansatz rather than for the theory.
- **Open**: the calculation required for the claim has not been completed.

## The result spine

This is the authoritative public claims table. Papers, talks, and bridge notes
should link to or quote its scoped rows rather than independently broadening
their status.

| Question | Current result | Status | Main limitation |
|---|---|---:|---|
| Can the free Pais--Uhlenbeck system admit a positive representation? | The positive symplectic metric is reconstructed canonically and its relation to Krein and real-form choices is classified. | **Certified** | Free representation theory is not interacting stability. |
| Does that positive structure survive interactions? | Explicit resonant conversion channels obstruct analytic continuation of the free positive metric; Einstein--Weyl cubic order is protected but a physical second-order channel is nonzero. | **Certified / Paper 6 under review** | These are specified interactions and sectors, not a universal no-go for every completion. |
| What is the selected residual cohomology of free pure-Weyl gravity on \(\mathbb R\times S^3\)? | Vacuum and one-particle sectors are acyclic; \(H^4\cong\mathbb C^2\), represented by \([W_+^2]\) and \([W_-^2]\), with normalized Gram matrix \(I_2\). | **Certified; Paper 7 artifact-ready** | All fifteen residual generators, including \(D\), are constrained in a zero-charge closed sector. The classes are deformations, not particles. |
| Is that residual calculation connected to the covariant field theory? | The complete free metric BV--BFV complex has causal retarded/advanced chain homotopies, compact-to-spacelike-compact transport, residual endpoint recovery, and matching Green/current/residual pairings. | **Certified; Paper 8 artifact-ready** | Conformal cylinder, free classical theory, selected polarization. The separately certified reduced Hadamard/Krein carrier is not a consequence of this theorem and is not full BV. |
| Does causal transfer survive beyond the cylinder? | The abstract cyclic transfer theorem has complete Berger and flat-Minkowski consumers and a curved Nariai consumer. The repaired 310-component Nariai cone retracts to the 26-component metric Bach endpoint with exact advanced/retarded homotopies. The full retract and causal homotopies now also possess a global support-local cyclic formal first variation along one transverse Einstein tangent. | **Certified on three scoped consumers; first background-tangent variation certified** | The variation is a theorem at deformation parameter zero, not a smooth finite neighborhood, uniform stability on an open background family, or a Hadamard theorem. |
| Must \(D\) be gauge? | No. It is charged on the unrestricted compact phase space and gauge on the Taub-zero derived sector. | **Certified** | The answer is sector- and boundary-dependent. |
| Can a healthy clock coexist with total \(D\)-gauge? | On one positive Berger-cylinder background, fixed-coupling linearized constraints force \(\delta Q_D=0\) although the matter clock has nonzero internal momentum. An exact clock-slice Maxwell observable now evolves nontrivially on that same scoped background. | **Certified in the stated linear/probe sector** | Nearby backgrounds, localized backreacting apparatus, all-orders closure, and quantum stability remain open. |
| Is there a clock-defined redshift observable? | An actual retarded Maxwell signal with compact spacetime source support gives a Diff-, Weyl-, Maxwell-gauge-, and raw-\(D\)-invariant clock-slice field-strength observable; its exact spatially global fixture has \(1+z=2\). Two localized emitters produce a leading rank-two detector matrix. Exact selected charge-block temporal images and a Green-weighted tail reduction are also certified. | **Global relational observable, localized leading response, and selected temporal propagation certified** | A correlated refinement lowers the clock-uniform high-mode Sobolev bound below \(1.95\times10^3\), but it is still not small. A full spatial detector image, common emitter comparison, recoil, backreaction, phenomenology, and quantum interpretation remain open. |
| Does the Berger nonlinear Cartan mechanism survive first contact with interactions? | The complete support-local gravitational \(q_2,q_3\), the 64-row gravity--clock--Maxwell \(q_2\), the typed 59,598-term mixed \(q_3\), and the 25,950-term retained \(\ell_3\) representative are exact and cyclic. The background-preserving \(K_{\rm Berger}=D-\omega R\) Cartan identities close through arity three on the declared classical carrier. | **Certified algebraically and at the stated classical causal level** | This is not an affine raw-\(D\), all-orders, cohomological-nontriviality, or physical branch-mixing theorem. Localized apparatus, QME restoration, and quantum claims remain open. |
| Does the retained interaction yet distinguish Einstein-like and extra-Weyl branches? | A support-local rank-46 STF2 graph prolongation is an exact cyclic carrier over the retained 36-row complex, with exact SDR and contractible complement. It supplies the enlarged architecture needed to attempt branch resolution. | **Carrier certified; physical split open** | No support-local branch projector or invariant branch manifest has passed. Therefore no Einstein/extra-Weyl/Maxwell \(\ell_3\) mixing table or physical closure claim is authorized. |
| Is ordinary Einstein--Maxwell radiation present inside the Weyl--Maxwell system? | The complete standard tangent injects, and a natural finite-order support-local chain morphism now closes every local BV row. Together with the residual and large-gauge endpoints it defines a complete linear mapping-cofiber triangle and exports the Einstein, pulled-back Weyl, and relative forms separately. | **Certified off-shell noncyclic linear triangle** | The standard pairings cannot make the triangle cyclic. The 38-row Einstein--Maxwell package through \(q_3\) is certified; the matching Weyl package, relative nonlinear morphism, causal map, observables, particles, and quantum interpretation remain open. |
| Is the complementary fourth-order branch real at the classical level? | For generic compact axial \(\ell\geq2\), the quotient by the Einstein--Maxwell image consists of two exact extra polarizations. Direct four-dimensional Lee--Wald matching makes their block nonradical with signature \((2,0)\); the full generic axial target has signature \((3,1)\), with the negative direction on an Einstein-image branch. On every declared physical polar fibre, the independently reconstructed module contains the complete Einstein primary summand plus two extra summands, with action normalization derived from the four-dimensional variation. | **Axial current certified; polar physical module certified** | The polar extra current, ungauged BV/Noether lift, final residual quotient, causal boundaries, positive-frequency state, and particle interpretation remain open. |
| Is the Einstein sector nonlinearly closed? | Every nonzero pure-extra generic Weyl--Maxwell tangent is Taub-obstructed on the tested fixed compact bundle. In the declared homogeneous/twist--\(\ell=2\) extra carrier, the complete common-zero cone is exactly one aligned \(SO(3)\) orbit. Every nonzero point is obstructed in the bounded finite-quasiperiodic correction class by an unavoidable quadratic-in-time source, yet admits a constructive real smooth exponential-polynomial second-order correction. | **Necessary cone classified; bounded continuation obstructed; smooth-secular continuation certified** | The smooth correction is generally secular, not stable bounded motion. Causal/retarded corrections, generalized/infinite targets, a structural all-background theorem, and all-orders closure remain open. |
| Is there a free Lorentzian quantum-observable algebra? | Gauge-invariant curvature test observables carry an exact causal presymplectic form, and the corresponding curvature-image CCR algebra is defined with the expected causal commutator and quotient relations. | **Certified, LORENTZIAN-CAUSAL free observable algebra** | No compatible positive/Hadamard state, Hilbert representation, interacting product, particle interpretation, or QME theorem follows from the algebra alone. |
| Does a reduced free Lorentzian mode carrier admit Hadamard two-point functions? | On the unit vacuum cylinder, the normalized E/A/L modes, causal Green blocks, and transported current determine a compatible complex structure and microlocal Hadamard distributions. E is positive; A and L have negative Krein sign. | **Reduced Bridge 4 certified, REDUCED-MODE + LORENTZIAN-CAUSAL** | This is not the full off-shell BV distributional complex, a BRST-positive graviton Hilbert space, a Berger result, an interacting state, or an asymptotic particle theorem. |
| Can the Berger system support the short-distance structure needed for quantum fields? | The base tensor and ghost wave factors have a certified local Hadamard parametrix, and exact typed Møller intertwiners give the unique formal companion-kernel candidate. | **Partial; microlocal promotion fail-closed** | The order-two transport has no certified Hörmander composition or uniform wavefront control. No companion Hadamard parametrix, global state, QME, or quantum theory is claimed. |
| Is the quantum theory anomaly-free and unitary? | The strict one-loop insertion has coefficients \((199/30,-87/20)\), so strict field content is obstructed. The tau-adic compensator restores the local Euclidean QME at one loop. The anomaly-induced representative, universal \(-199/60\) \(C^2\log\) coefficient, and exact \(\Box R\) scheme conversion are certified. The generic longitudinal ghost tower is one normalized scalar Schur factor with exact residues and scale row; both reference finite rows, the canonical \(\det_3\) tail and the selected weighted modified determinant are complete on round \(S^4\), with a smoothing proof that generic values require global spectral data. | **Strict theory obstructed; extended local Euclidean QME restored; generic ghost determinant architecture sharply reduced** | A generic primed Green/spectral carrier, possible multiplicative anomaly, the generic physical fourth-order Hessian, complete \(\Gamma_1,Q_1\), Lorentzian QME, residual transfer, positive state, particles, and unitarity remain open. |
| Are black-hole solutions, thermodynamics, and linear gravitational branches present? | The static spherical family has exact energy, Wald entropy, and \(dH=T\,dS\). On Schwarzschild, the axial \(\ell=2\) Bach system splits into the Regge--Wheeler and extra Lichnerowicz branches. The extra branch reaches the horizon in a two-parameter ingoing-regular family, while the action-derived pure Einstein/Regge--Wheeler flux block is symplectically null for conjugate wave pairs. | **Static theorem and BH-2A stages 1--3 certified** | Radiation is now decided by the open Einstein--extra and extra--extra flux blocks, their horizon/outer domains, and causal exterior evolution. Polar modes, ringdown, stability, and Hawking states remain open. |

## Highlights by audience

### Higher-derivative quantization and unitarity

The programme separates the free positive metric, Krein completion, real
form, gauge reduction, and interacting deformation problem. The mechanical
and flat-field papers show why a free positive representation can be both
mathematically canonical and physically insufficient. The gravity papers
then ask whether gauge reduction changes the carrier space before positivity
is judged.

The potentially useful contribution is a common diagnostic framework for
claims that a ghost is removed, rendered null, or made positive. Those claims
can disagree because they use different observable algebras, phase spaces,
boundary conditions, quotients, or inner products. Our cylinder result does
not settle the Mannheim versus Fock--BRST debate; it supplies a third,
cohomological reduction whose state type must not be confused with an
asymptotic Fock particle.

The key open comparison is one common flat or asymptotic fixture evaluated in
all three descriptions.

**Possible novelty, pending literature audit:** a claim-typed comparison
protocol that separates Fock states, BV classes, deformation classes,
boundary charges, and asymptotic particles before competing ghost or unitarity
claims are compared.

### BV, BRST, and perturbative quantum field theory

Papers 7--8 give an explicit large gauge complex rather than a mode-only
quotient. The residual BFV complex is obtained from the metric BV complex,
the quadratic moment map is identified with the Taub obstruction, and the
derived zero fibre explains why the zero-charge condition cannot be omitted.

For quantum field theorists the programme now has a coefficient-bearing local
one-loop QME disposition. The strict fixed-field-content theory is obstructed,
whereas the formal tau-adic compensator theory has a restored local Euclidean
QME at one loop. The generic longitudinal ghost determinant is no longer three
unrelated towers: it is one normalized scalar Schur factor with a canonical
modified-Fredholm tail and exact critical local residue. Its first two finite
weighted traces, canonical \(\det_3\) tail, and selected weighted modified
determinant are complete on round \(S^4\); a finite-rank smoothing theorem
shows that their generic versions require the full primed Green kernel or
spectral measure. That carrier, the possible multiplicative anomaly, and the
same-gauge physical fourth-order Hessian remain coefficient gates. The subsequent target is a
compensator-inclusive classical contraction and the renormalized Slavnov
operator \(Q_1\), followed by the \(D\)-Cartan transfer test. Lorentzian
time-ordered products and a compatible state remain independent gates.

**Possible novelty, pending literature audit:** a coefficient-bearing map from
the standard type-A/type-B Weyl-anomaly classes to the obstruction of a
specific residual Cartan contraction, after the full antifield and QME gates
are closed.

### Matter content, scale generation, and unification

The programme does not yet contain a Grand Unified Theory. A GUT would unify
the strong, weak, and electromagnetic gauge sectors; it would not by itself
quantize or unify gravity. The relevant long-range target here is an
anomaly-free unified gauge--matter sector consistently coupled to pure-Weyl
gravity.

The first credible bridge result would be smaller: construct a non-Abelian
Yang--Mills/chiral-fermion BV complex, classify gauge, mixed gauge--gravity,
and Weyl anomalies, and determine whether their cancellation selects matter
representations. A GUT candidate additionally requires a conformal
mass-generation and symmetry-breaking mechanism, a physical particle
spectrum, running couplings, and low-energy recovery. Likewise, \(E=mc^2\)
is not an independent construction target; it follows at rest from a
Lorentz-invariant mass shell once a stable physical mass scale and massive
excitation exist.

### Lorentzian PDE and Green-hyperbolic complexes

The free pure-Weyl metric Hessian does not become a scalar normally
hyperbolic operator on a simple same-bundle auxiliary enlargement; exact
symbol-rank no-go results explain that failure. The successful object is the
whole complex. Curvature prolongation, a symmetric-hyperbolic Weyl--Cotton
system, adjoint-tractor transfer, and support-local retracts produce
retarded/advanced degree-minus-one homotopies on all 386 prolonged rows.

This construction has now been extracted into a conditional cyclic
causal-transfer theorem.  A finite-order support-local cyclic strong
deformation retract transfers same-sided advanced/retarded chain homotopies
by \(\Lambda_C=h+i\Lambda_Ep\), preserves their causal support and cyclic
adjoint relation, and is stable under finite direct sums and finite-order
cyclic shears.  The complete Berger 54- and 64-row complexes replay as exact
consumers.  Endpoint Green hyperbolicity remains a hypothesis rather than a
conclusion of the theorem.

**Possible novelty, pending literature audit:** constructive cyclic transfer
of retarded/advanced Green homotopies and current pairings from a hyperbolic
parent to a fourth-order gauge/detour complex through support-local
differential contractions.

On the Berger quantum route, the normally hyperbolic tensor and ghost factors
now carry the standard local Hadamard singularity, and the typed source and
solution Møller maps satisfy their exact formal intertwining and adjoint
identities. The attempted promotion usefully found the remaining analytic
obstruction: convergence in finite-slab Sobolev energy norms does not imply
that the kernel compositions are defined in the Hörmander sense or that their
wavefront cones are uniformly controlled. Thus the formal transported kernel
is fixed, while the companion Hadamard claim remains fail-closed.

The newest contraction theorem sharpens the remaining work: a valid
covariance on the retained 26-row complex would lift canonically to all 54
rows without new wavefront directions or an independent state on the 28
contractible rows. The stationary-pencil preflight has now converted the
retained equations into an exact rank-52 second-order hybrid companion and a
rank-104 first-order Cauchy target. The next gate is a closed realization of
that generator with an isolated zero spectral sector; no Riesz projector,
covariance, or Hadamard state has yet been constructed.

### Conformal geometry, tractors, BGG, and detour complexes

The geometric bridge uses the adjoint-tractor Yang--Mills detour complex and
curved BGG/homological transfer to reach the metric Bach complex. This gives
Lorentzian causal content to structures usually presented through formal
self-adjointness, ellipticity, or representation theory.

The result of interest here is not merely another realization of the Bach
operator. It is that the reduced fourth-order operator can inherit causal
meaning from a larger tractor complex even when a preferred scalar-principal
factorization of the isolated metric operator does not exist. A nearby
conformal higher-spin or detour example is the natural portability test.

**Possible novelty, pending literature audit:** a Lorentzian causal
interpretation of a Bach detour complex inherited from its tractor parent,
including explicit differential splitting, homotopy, support, and pairing
transport rather than formal self-adjointness alone.

### General relativity and mathematical relativity

The compact Einstein--Maxwell work separates three statements that are often
conflated:

1. Einstein solutions solve the Weyl equations on a common background.
2. Einstein linear tangents inject into the Weyl solution space.
3. The Einstein sector is preserved by nonlinear evolution and has the same
   symplectic form.

The first two now hold in the complete certified standard harmonic tangent
before the final quotient. They have also been globalized from harmonic
tables to a natural finite-order support-local morphism on every local BV
row. With the residual and large-gauge endpoints, this gives the complete
linear mapping-cofiber triangle. The third statement does not follow: the
Einstein--Maxwell form is positive on the generic image, whereas the
pulled-back Weyl form has inertia \((1,1)\). Inertia is invariant under
congruence, so no real product-equivariant standard-pairing cyclic correction,
chain homotopy, or exact current improvement can identify the two. The honest
linear theorem therefore carries the Einstein, pulled-back Weyl, and relative
forms separately.

The complementary axial block is now explicit rather than inferred from a
determinant. For every physical \(\ell\geq2\) in the generic compact domain,
the quotient contains two extra solution polarizations. Their reduced current
has now been matched to the direct four-dimensional Lee--Wald current. The
extra block is nonradical with signature \((2,0)\), but the complete axial
target has signature \((3,1)\): the negative direction occurs on one
Einstein-image master branch. This rules out both the claim that the extra
root is merely a radical multiplicity and the naive identification of the
extra root with the negative direction on this fixture. Final residual,
positive-frequency, and causal-boundary selection still decide the physical
interpretation.

The polar block has now crossed the physical coefficient-module gate.
Independent four-dimensional linearizations reconstruct its formally
self-adjoint four-by-four Hessian. For every declared physical
\(\ell\geq2\) and compact momentum, including zero, the exact polynomial
square identifies the complete Einstein primary image and two additional
polar primary summands. The action row weights are derived from the
four-dimensional variational convention and harmonic norms. This is not yet
the polar analogue of the preceding physical-current theorem: its direct
Lee--Wald form and final gauge/residual descent remain to be computed.

At second order, the latest real axial--polar \(\ell=2\) fixed-bundle tangent
has a positive-definite Taub form and is obstructed in every nonzero real
direction. A separately computed sum-frequency source is removable; the
obstruction instead comes from conjugate self-products in the zero-frequency
constraint channel. This distinction is why individual vertex blocks cannot
substitute for the full linearization-stability test.

This connects most directly to linearization stability, charge-fibre
obstructions, and the Lorentzian complement to boundary-selected
"Einstein from conformal gravity." The decisive next step is the full extra
fourth-order quotient and then an asymptotically flat Bach phase space with
Bondi/ADM charges and flux.

**Possible novelty, pending literature audit:** explicit dependence of
second-order integrability on the global charge fibre, together with a
harmonic obstruction bilinear that separates removable dynamical sources from
Taub/cokernel obstructions.

### Relational clocks and the problem of time

The charge calculation replaces the slogan "time is gauge" with a test:

\[
\delta H_D=\Omega(\delta\phi,\mathcal L_D\phi).
\]

For unrestricted compact data this is nonzero. On the Taub-zero sector it
vanishes. The Berger construction adds a healthy rotating scalar reference
system and shows, at fixed couplings and linear order, that nontrivial matter
clock momentum need not make the total \(D\) transformation physical.

The first explicit observable now uses an actual retarded Maxwell response to
a source compact in spacetime.  The clock-slice field-strength observable is
Diff-, Weyl-, Maxwell-gauge-, and raw-\(D\)-invariant, has a nonzero reduced
probe-mode Poisson bracket and evolves nontrivially; its exact spatially global
fixture has \(1+z=2\).  The clock-dressed source schedule is correctly an
equivariant family, not an invariant source at fixed schedule.  This is a G0
retarded relational-observable theorem; it is spatially global.  A separate
observer theorem now constructs two receiver-adjacent localized conserved
emitters, exact causal preparations, and a leading rank-two detector matrix.
It does not yet identify those preparations with one common emission event or
the complete clock-frequency observable.  The full apparatus Dirac bracket,
evaluated recoil, all-orders backreaction, and phenomenology remain open.

The first gravity-coupled stress projection now sharpens that gate. The
diagonal energy-pressure source is exact, but a single travelling Hopf mode
has nontrivial stationary momentum flux with an exact dual obstruction
witness. A coherent counter-propagating mode in the same Maxwell field forms
a standing wave, cancels that flux including interference stress, and admits
an explicit second-order homogeneous gravity correction. Its phase plane has
positive energy and no new negative direction. The next physical test is to
join the localized preparations into one emitter--receiver comparison and
evaluate apparatus recoil or a support-local response to the lone travelling
beam—not another homogeneous balance calculation.

The detector-profile calculation has also separated time propagation from
spatial resolution. Exact selected Maxwell charge blocks and their temporal
functional calculus are certified, and the Green multiplier does not amplify
the omitted high-mode tail. The correlated clock-uniform Sobolev bound above
the retained rail is now below approximately \(1.95\times10^3\), so it is a
rigorous finite bound rather than a small-error theorem. Full detector
response, recoil, massive continuation, and restriction to the nonlinear
tangent cone therefore remain fail-closed.

**Possible novelty, pending literature audit:** an explicit healthy clock with
nontrivial relational evolution while total \(D\) remains presymplectically
degenerate, extended to a gauge-invariant light observable and its first
interaction obstruction.

### Amplitudes, twistors, and Einstein from conformal gravity

Our current Einstein result is complementary to boundary selection and
twistor embeddings: it asks whether the selected Einstein tangent is a
causally and symplectically closed sector, and whether it extends beyond
linear order. It does not yet compute an S-matrix.

A useful bridge would identify the certified Einstein projection in helicity
or twistor variables and evaluate one cubic or MHV fixture. A later result
should determine whether the compact charge-sector obstruction has an
amplitude or soft-charge interpretation.

### Phenomenology, black holes, and cosmology

This programme is not yet a dark-matter, dark-energy, or dynamical black-hole
model.  It now has a classified static spherical pure-Weyl family, a regular
non-Einstein horizon fixture, and an exact normalized static first law.  In
the axial Schwarzschild fixture the extra branch reaches the horizon, while
the pure Einstein/Regge--Wheeler flux block is symplectically null.  The
Einstein--extra and extra--extra flux blocks now decide whether radiative
pure-Weyl black-hole dynamics is nontrivial.  Their horizon and outer domains,
causal evolution, ringdown and stability remain open.  Galaxy and cosmology
applications likewise require stable backgrounds, observables, and boundary
charges before fitting rotation curves or expansion histories is meaningful.

The infrastructure is relevant because it can test whether the extra Weyl
branch that drives such phenomenology is physical, gauge, constrained,
unstable, or boundary-selected. The sequence is: asymptotic and horizon
phase spaces; extra-branch classification; nonlinear stability; redshift,
lensing, and waveform observables; only then galaxy and cosmology fits.

## What we can offer collaborators now

The programme is not only a collection of conclusions. A collaborator can
currently use:

- exact coefficient-level operators, pairings, contractions, currents, and
  obstruction witnesses with declared conventions and provenance;
- small independent verifiers and machine-readable certificates rather than
  requiring trust in the main symbolic producer;
- compact cylinder, Berger-clock, Einstein--Maxwell product, Nariai, and
  static spherical black-hole backgrounds as reproducible test laboratories;
- explicit missing-object and failed-promotion ledgers, including normalized
  defects that can be attacked without adopting the programme's
  interpretation;
- tractor/BGG, BV, Green-homotopy, Lee--Wald, Taub, and harmonic adapters that
  can receive an outsider's preferred formulation or benchmark.

The practical offer is: provide an operator, background, boundary condition,
mode, charge convention, or proposed reduction, and we can attempt to place it
in the comparison protocol and run it through the relevant certificate chain.

## Bridge-project status

Readiness is reported by lifecycle and missing gate.

| Bridge project | Current readiness | Exact next gate |
|---|---|---|
| [Cyclic causal Green transfer](90-cyclic-green-transfer-bridge.md) | **Abstract conditional theorem certified** with Berger, flat-Minkowski, and curved Nariai consumers; the Nariai rank-310 retract and causal homotopies also have a global formal transverse first variation | Extend the tangent theorem to a smooth finite background family or add a different detour/higher-spin theory. |
| [Pure-extra obstruction and balanced extension](91-charge-fibre-taub-bridge.md) | **Theorem frozen** on the generic fixed-bundle domain; finite-harmonic, opposite-momentum, and exceptional all-\(m\) successors certified | Dispose the phase-sensitive quadratic source on the remaining mixed strata and extract the structural definite/indefinite Taub theorem. |
| [Extra axial branch and physical current](92-extra-axial-lee-wald-bridge.md) | **Axial direct current and polar physical module certified** | Compute the polar extra Lee--Wald current and ungauged lift, perform final residual descent, and test causal boundary admissibility. |
| Relational clock and light | **Spatially global retarded redshift, localized causal emitters, exact selected temporal Maxwell images, and leading rank-two response certified; the first rigorous high-mode tail bound is finite but not small** | Obtain a genuinely small full-profile tail, unite the preparations into one clock-frequency comparison, and complete recoil, backreaction, and the apparatus Dirac bracket. |
| Black holes and axial radiation | **Static first law and BH-2A stages 1--3 certified: branch split, horizon reach of the extra family, and symplectic nullity of the pure Einstein flux block** | Compute the Einstein--extra and extra--extra horizon/outer flux blocks and causal domains before ringdown or stability claims. |
| Einstein--Weyl relative triangle | **Natural support-local all-row noncyclic linear triangle certified, including global endpoints and three action-derived forms; the 38-row Einstein--Maxwell Taylor package through \(q_3\) is also certified** | Import the matching Weyl--Maxwell \(q_2,q_3\) payload and determine the relative \(L_\infty\) extension. |
| Residual branch mixing | **Rank-46 cyclic carrier and retained \(\ell_3\) theorem frozen; the requested canonical support-local projector is obstructed** | Find a noncontractible filtered or mixed-bundle split, or retain the unsplit physical statement; only then compute a branch-resolved mixing table. |
| Quantum anomaly and state bridge | **Strict one-loop obstruction, tau-adic local Euclidean restoration, anomaly-fixed terms, reduced Hadamard/Krein carrier, normalized longitudinal Schur/modified-Fredholm reduction, and complete round-\(S^4\) weighted modified-determinant benchmark certified** | Supply a generic primed Green/spectral carrier, evaluate the possible multiplicative anomaly together with the physical fourth-order Hessian, then complete \(Q_1\) and test the Lorentzian/full-BV state and quantum \(D\) defect. |
| Asymptotic Bach/BMS | **Programme stage** | Construct a closed Lorentzian boundary phase space with differentiable charges, flux, and extra-branch signs. |

The charge-fibre project has been promoted from a bridge note to a standalone
scoped manuscript: it proves the complete pure-extra generic obstruction and
one explicit balanced Einstein--extra second-order extension.  The cyclic and
extra-current bridge notes retain their shorter adapter format.

## Where the strongest criticism currently lands

The criticism is correct in four important senses:

- \(D\) is not universally gauge. It is charged on the unrestricted compact
  phase space and is expected to be physical in ordinary asymptotic settings.
- A zero one-particle residual cohomology on the selected closed cylinder is
  not a proof of particle unitarity or of the absence of radiative degrees of
  freedom in an asymptotically flat universe.
- The Einstein image is not automatically a nonlinear, symplectic, or
  exclusive sector of the fourth-order theory.
- In the generic compact axial block, the extra fourth-order module survives
  both the reduced Green-pairing radical test and the direct four-dimensional
  Lee--Wald comparison. It can no longer be dismissed there as determinant
  multiplicity, although its residual, boundary, and quantum admissibility
  remain undecided.
- In the Berger interaction theorem, the exact nonlinear Cartan generator is
  \(K_{\rm Berger}=D-\omega R\), not affine raw cylinder translation \(D\).
  Raw-\(D\) nonlinear closure therefore remains open.

The selected construction nevertheless survives the criticism where it
actually claims to apply:

- the zero-charge condition is now derived and audited rather than assumed
  silently;
- the residual calculation is connected to the complete covariant causal
  free complex;
- a healthy clock counterexample shows that matter does not automatically
  turn total \(D\) into a charge;
- the nonlinear Berger \(K_{\rm Berger}\)-Cartan recurrence closes through
  arity three; mixed gravity--clock--Maxwell \(q_2,q_3\) and the retained
  \(\ell_3\) representative are certified; and an actual retarded relational
  signal exists.  Localized emitter preparations and a leading rank-two
  response now exist as a separate observer theorem.  The branch projector,
  invariant interaction meaning, unified clock-frequency comparison, recoil,
  and complete backreacted apparatus remain open.

Thus the sector is neither an arbitrary patch nor a model of the whole
universe. It is a mathematically consistent physical choice whose range of
stability is now the subject of the programme.

## What would materially change the verdict

A strong positive change would be any of:

- a single localized Berger emission-and-reception experiment whose complete
  clock-frequency comparison, recoil, backreaction, and apparatus Dirac
  bracket preserve the certified leading rank-two response;
- a support-local rank-46 branch projector followed by a nonremovable
  Einstein-like/extra-Weyl/Maxwell interaction coefficient;
- localized apparatus recoil or a support-local single-beam response
  compatible with the arity-three Cartan contraction;
- a polar extra Lee--Wald current, ungauged lift, and final residual descent
  that either preserve or sharply obstruct the axial classification under
  causal physical boundary conditions;
- vanishing or removable quantum \(D\)-anomaly after QME restoration;
- an asymptotically flat, positive reduced Einstein scattering sector with
  the extra Weyl branch excluded or controlled.

A strong negative change would be any of:

- failure of the Berger contraction in the next physical interaction
  channel;
- survival of the compact negative Lee--Wald direction as an unavoidable
  physical state after residual descent and admissible causal boundaries;
- an unavoidable nontrivial quantum Cartan anomaly;
- a negative physical extra branch in the asymptotic Bach phase space;
- failure of causal nonlinear closure for every physically admissible
  Einstein-sector boundary condition.

Either outcome is publishable: the programme is designed to locate the first
precise obstruction, not to protect a preferred interpretation.

## Reading and verification map

- [Series overview and papers](../README.md)
- [Paper 7: residual cohomology](07-conformal-residual-cohomology-krein.pdf)
- [Paper 8: covariant causal transport](08-conformal-covariant-causal-transport.pdf)
- [Papers 7--8 computational supplement](07-08-conformal-residual-cohomology-computational-supplement.pdf)
- [Paper 9: Berger relational clocks and Cartan contraction](09-relational-clocks-berger-d-cartan.pdf)
- [Paper 10: compact Einstein--Maxwell/Weyl--Maxwell phase space](10-compact-einstein-maxwell-weyl-phase-space.pdf)
- [Clean publication-release audit](../conformal-publication-release-audit.json)
- [Live \(D\)-quotient status ledger](../d_quotient_programme/reports/consolidated-status.md)
- [Generic axial extra-branch and pairing report](../notes/einstein-maxwell-weyl-axial-operator-report.md)
- [Generic polar off-shell operator certificate](../bridge/certificates/einstein_maxwell_weyl_polar_full_tensor.json)
- [Physical polar module and action-normalization certificate](../bridge/certificates/einstein_maxwell_weyl_polar_physical_completion.json)
- [Complete Berger gravity--clock--Maxwell \(q_2\) report](../d_quotient_classical/reports/berger-support-local-coupled-maxwell-q2.md)
- [Real axial--polar Taub obstruction receipt](../bridge/reports/einstein-maxwell-weyl-hermitian-axial-polar-ell2-taub-receipt.md)
- [Berger arity-three Cartan report](../d_quotient_classical/reports/berger-causal-D-Cartan-arity-three.md)
- [Berger Maxwell interaction-obstruction report](../d_quotient_classical/reports/berger-maxwell-stress-residual-projection.md)
- [Berger momentum-balanced second-order fixture](../d_quotient_classical/reports/berger-maxwell-momentum-balanced-fixture.md)
- [Retarded Berger relational Maxwell observable](../d_quotient_classical/reports/berger-retarded-relational-maxwell-observable.md)
- [Localized dynamical-emitter rank-two response](../closed_universe_observers/reports/berger-dynamical-emitter-cauchy-rank-two.md)
- [Curved Nariai 310-row causal transfer](../d_quotient_classical/reports/nariai-repaired-310-all-row-green-transfer.md)
- [Free curvature-observable causal propagator](../quantum-weyl/reports/curvature-observable-causal-propagator.md)
- [Free curvature-image CCR algebra](../quantum-weyl/reports/curvature-image-presymplectic-ccr.md)
- [Static pure-Weyl black-hole background](../black_hole_programme/reports/bh0-static-spherical-background.md)
- [Normalized black-hole generator and first law](../black_hole_programme/reports/bh1a-normalized-generator.md)
- [Black-hole axial Regge--Wheeler/extra branch split](../black_hole_programme/reports/bh2a-axial-operator.md)
- [Rank-46 cyclic Berger branch carrier](../d_quotient_classical/reports/berger-retained-46-stf2-prolongation-branch-carrier.md)
- [Paper 11: retained mixed gravity--Maxwell bracket](11-gravity-light-cyclic-causal-ell3.pdf)
- [Homogeneous/twist--extra common-zero cone](../d_quotient_classical/reports/ph-homogeneous-twist-ell2-extra-bounded-tangent-cone.md)
- [Bounded-correction obstruction on the aligned orbit](../bridge/einstein_sector/reports/einstein-maxwell-weyl-global-extra-bounded-correction-obstruction.md)
- [Smooth-secular extension on the aligned orbit](../bridge/einstein_sector/reports/einstein-maxwell-weyl-global-extra-smooth-secular-second-order.md)
- [Complete noncyclic Einstein--Weyl linear triangle](../bridge/einstein_sector/reports/einstein-weyl-relative-linear-triangle-v1.md)
- [Einstein--Maxwell Taylor package through q3](../bridge/einstein_sector/reports/einstein-maxwell-product-linfinity-through-arity-three.md)
- [Standard-pairing cyclic inertia obstruction](../d_quotient_classical/reports/einstein-weyl-generic-cyclic-map-inertia-obstruction.md)
- [Formal transverse Nariai causal variation](../d_quotient_classical/reports/nariai-transverse-global-hpl-rank310-causal-variation.md)
- [BH-2A action-derived flux matrix](../black_hole_programme/reports/bh2a-flux-matrix.md)
- [Correlated observer high-mode Sobolev bound](../closed_universe_observers/reports/berger-correlated-profile-sobolev-n1.md)
- [Generic ghost Schur Schatten split](../quantum-weyl/reports/generic-background-ghost-schur-schatten-split.md)
- [Paper 12: one-loop BV anomaly and formal compensator resolution](12-pure-weyl-one-loop-bv-anomaly.pdf)
- [Exact Weyl-graviton \(\Box R\) scheme conversion](../quantum-weyl/reports/weyl-graviton-box-r-scheme-conversion.md)
- [Reduced vacuum-cylinder Hadamard/Krein carrier](../quantum-weyl/reports/vacuum-cylinder-reduced-bridge4-hadamard.md)
- [Berger typed Møller and microlocal-gate report](../quantum-weyl/reports/berger-typed-companion-moller-preflight.md)
- [Bridge note: cyclic causal Green transfer](90-cyclic-green-transfer-bridge.pdf)
- [Paper 91: pure-extra obstruction and balanced extension](91-charge-fibre-taub-bridge.pdf)
- [Exceptional all-\(m\) \(\ell=1\) obstruction](../bridge/reports/einstein-maxwell-weyl-exceptional-ell1-all-m-resonance.md)
- [Bridge note: axial current and polar module audits](92-extra-axial-lee-wald-bridge.pdf)
- [Long-term programme and publication gates](../notes/universe-building-roadmap.md)
- [General-audience introduction](99-how-to-build-a-universe.md)

Papers 7--8 are `ARTIFACT_READY`: the manuscripts, supplements, hashes, and
clean reproduction audit pass.  Their next lifecycle gate is a public
repository release audit, including link integrity, provenance, readable
scope boundaries, and a clean tagged replay.

Papers 9--10 have frozen scoped theorems. Paper 11 is theorem-frozen for its
retained cyclic-causal \(\ell_3\) representative and declared filtered-cyclic
nonremovability result; branch-resolved physical meaning remains a later
paper. Paper 12 has a compiled theorem-spine manuscript and computational
supplement and is `DRAFT_ALLOWED` pending specialist prose, citation, and
clean release review.

## Update policy

This document should remain short enough to read in roughly ten minutes. A
new calculation changes it only when at least one of the following happens:

1. a lifecycle state advances or retreats;
2. a theorem gains or loses a dependency needed for its physical reading;
3. a new background or boundary condition changes a verdict;
4. an open decisive test becomes a certified pass, obstruction, or no-go;
5. a manuscript becomes artifact-ready or repository-released.

Raw term counts, implementation milestones, and unverified candidate results
belong in team reports, not in this front door. Every update should preserve
the strongest limitation immediately beside the headline result.

## Changelog

- **18 July 2026, round-\(S^4\) modified-determinant closure:** upgraded the
  special-background Schur benchmark from two finite weighted traces to the
  complete selected weighted modified determinant. Exact rational
  alternating-series and Euler--Maclaurin bounds enclose the canonical
  \(\det_3\) tail to width below \(5.8\times10^{-48}\); generic finite rows
  still require global spectral data.
- **18 July 2026, relative-triangle, causal-stability, horizon-flux,
  observer-tail, and Schur update:** added the complete noncyclic
  Einstein--Weyl linear mapping-cofiber triangle, its inertia obstruction,
  and the complete Einstein--Maxwell Taylor package through \(q_3\);
  the global formal transverse variation of the Nariai rank-310 causal
  contraction; BH-2A's ingoing-regular extra family and symplectically null
  pure Einstein flux block; the finite-but-coarse observer Sobolev tail bound;
  and the generic ghost modified-Fredholm Schur reduction with exact critical
  residue. The nonlinear relative morphism, cross/extra black-hole flux,
  small observer tail, regulated determinant, Lorentzian QME, and particles
  remain open.
- **18 July 2026, nonlinear-cone, reduced-state, and black-hole-wave update:**
  added the complete aligned homogeneous/twist--extra common-zero cone and its
  bounded-continuation obstruction and complementary smooth-secular extension;
  the reduced vacuum-cylinder E/A/L
  Hadamard/Krein carrier with signs \(+,-,-\); the anomaly-induced and
  curvature-squared logarithmic one-loop terms and exact \(\Box R\) scheme
  conversion; the Schwarzschild axial
  Regge--Wheeler/extra-Lichnerowicz split; and the Paper 11/Paper 12 lifecycle
  advances. Full-BV positivity, causal nonlinear continuation, horizon flux,
  and release review remain open.
- **18 July 2026, curved-causal, observer, black-hole, and quantum-observable
  update:** added the complete 310-row Nariai causal consumer, localized
  dynamical-emitter rank-two response, exceptional all-\(m\) \(\ell=1\)
  obstruction, the free curvature-observable CCR algebra, and the static
  pure-Weyl black-hole family with its normalized exact first law; retained
  the open-background, full-apparatus, quantum-state, and dynamical-horizon
  boundaries.
- **17 July 2026, observable and branch-carrier update:** promoted the Berger
  redshift fixture to an actual retarded spatially global relational
  observable; recorded the landed mixed \(q_3\), retained \(\ell_3\), and exact
  rank-46 cyclic carrier; kept localization, branch projection, invariant
  interaction meaning, and apparatus backreaction explicitly open.
- **17 July 2026, relative-spine update:** corrected the Berger nonlinear
  generator from affine raw \(D\) to \(K_{\rm Berger}=D-\omega R\); added the
  complete 64-row gravity--clock--Maxwell \(q_2\), the all-physical-fibre polar
  module and action normalization, and the sectoral Einstein--Weyl
  relative-complex status.
- **17 July 2026:** promoted the Berger Cartan result through arity three;
  recorded the one-way Maxwell momentum-flux obstruction and its exact
  counter-propagating second-order resolution; replaced the pending
  axial Lee--Wald gate with the completed direct-current match, signatures,
  and real axial--polar Taub obstruction; added the comparison protocol,
  collaborator offer, possible-novelty statements, and exact bridge gates.
- **16 July 2026:** added the generic axial strict-inclusion theorem and its
  nonradical reduced Green signature \((2,0)\); recorded the exact typed
  Møller transport algebra and the fail-closed Hörmander/wavefront gate that
  prevents promotion to a companion Hadamard parametrix or quantum state.
- **16 July 2026:** created the physicist-facing summary; recorded Papers
  7--8 as artifact-ready, the completed cylinder causal bridge, the
  sector-dependent \(D\) verdict, Berger arity-two status with the separate
  fail-closed analytic import, and the complete standard Einstein--Maxwell
  harmonic inclusion before the final quotient.
