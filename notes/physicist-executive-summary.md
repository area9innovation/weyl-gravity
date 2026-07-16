# Pure-Weyl gravity programme: executive summary for physicists

Last substantive update: 16 July 2026.

This is the short, live front door to the programme. It is written for a
physicist deciding whether the work intersects their own. It summarizes
results; it does not replace the technical manuscripts, certificate ledgers,
or the [universe-building roadmap](universe-building-roadmap.md).

## The sixty-second version

Fourth-order gravity has more local solutions than Einstein gravity, and its
extra spin-two branch is normally associated with negative energy or norm.
Our starting point is that four logically different questions are often
collapsed into that one statement:

1. What modes solve the local field equations?
2. Which modes survive gauge, charge, and boundary reduction?
3. Which reduced structures survive interactions?
4. Which survive quantization and define asymptotic particles?

We have exact answers to substantial parts of the first two questions and
sharply scoped results on the third. We do not yet have the fourth.

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

## How claims are typed

Every physical conclusion is indexed by

```text
(theory, background, generator, phase space, boundary conditions, lifecycle)
```

We use four plain-language states in this document:

- **Certified**: an exact artifact and an independent verifier establish the
  scoped claim.
- **Partial**: a real theorem or obstruction is established, but a named
  dependency needed for the larger conclusion is still open.
- **Fail-closed**: a proposed promotion was tested and is not accepted; this
  may be a no-go for one ansatz rather than for the theory.
- **Open**: the calculation required for the claim has not been completed.

In particular, `LOCAL-ALGEBRAIC` and `REDUCED-MODE` results are not reported as
`LORENTZIAN-CAUSAL` or quantum theorems.

## The result spine

| Question | Current result | Status | Main limitation |
|---|---|---:|---|
| Can the free Pais--Uhlenbeck system admit a positive representation? | The positive symplectic metric is reconstructed canonically and its relation to Krein and real-form choices is classified. | **Certified** | Free representation theory is not interacting stability. |
| Does that positive structure survive interactions? | Explicit resonant conversion channels obstruct analytic continuation of the free positive metric; Einstein--Weyl cubic order is protected but a physical second-order channel is nonzero. | **Certified / Paper 6 under review** | These are specified interactions and sectors, not a universal no-go for every completion. |
| What is the selected residual cohomology of free pure-Weyl gravity on \(\mathbb R\times S^3\)? | Vacuum and one-particle sectors are acyclic; \(H^4\cong\mathbb C^2\), represented by \([W_+^2]\) and \([W_-^2]\), with normalized Gram matrix \(I_2\). | **Certified; Paper 7 artifact-ready** | All fifteen residual generators, including \(D\), are constrained in a zero-charge closed sector. The classes are deformations, not particles. |
| Is that residual calculation connected to the covariant field theory? | The complete free metric BV--BFV complex has causal retarded/advanced chain homotopies, compact-to-spacelike-compact transport, residual endpoint recovery, and matching Green/current/residual pairings. | **Certified; Paper 8 artifact-ready** | Conformal cylinder, free classical theory, selected polarization; no Hadamard or quantum construction. |
| Must \(D\) be gauge? | No. It is charged on the unrestricted compact phase space and gauge on the Taub-zero derived sector. | **Certified** | The answer is sector- and boundary-dependent. |
| Can a healthy clock coexist with total \(D\)-gauge? | On one positive Berger-cylinder background, fixed-coupling linearized constraints force \(\delta Q_D=0\) although the matter clock has nonzero internal momentum. | **Certified in the stated linear sector** | Relational observables, nearby backgrounds, nonlinear closure, and quantum stability are not all complete. |
| Does the Berger nonlinear Cartan mechanism survive first contact with interactions? | The complete retained \(q_2\) is exact and cyclic; a causal cyclic \(D\)-Cartan contraction has been constructed through arity two on all 54 rows. | **Certified algebraically and at the stated classical causal level** | Arity three, Hadamard data, QME restoration, and quantum claims are open. A downstream Volterra import remains fail-closed until its analytic estimates and source/solution maps are certified. |
| Is ordinary Einstein--Maxwell radiation present inside the Weyl--Maxwell system? | The complete standard fixed-bundle harmonic Einstein--Maxwell tangent injects on shell before the final residual quotient, and its Weyl--Maxwell pullback is nondegenerate. | **Certified, reduced-mode/local-algebraic** | The pullback is not generally the Einstein symplectic form; radiative blocks are relatively indefinite, and the complementary fourth-order branch is not yet solved. |
| Is the Einstein sector nonlinearly closed? | Explicit compact fixed-charge photon and gravitational tangents have second-order Taub obstructions; a nonzero null tangent on the universal cover extends in the tested channel. | **Certified examples / classification in progress** | No universal nonlinear Einstein-sector closure theorem. |
| Is the quantum theory anomaly-free and unitary? | The even antifield-zero, local dimension-four anomaly candidates reduce to \([\omega C^2]\) and \([\omega E_4]\), with \(\omega\Box R\) exact. | **Partial, local-algebraic** | Coefficients, antifield-dependent sectors, QME restoration, Lorentzian time-ordered products, Hadamard state, and asymptotic unitarity are open. |

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

### BV, BRST, and perturbative quantum field theory

Papers 7--8 give an explicit large gauge complex rather than a mode-only
quotient. The residual BFV complex is obtained from the metric BV complex,
the quadratic moment map is identified with the Taub obstruction, and the
derived zero fibre explains why the zero-charge condition cannot be omitted.

For quantum field theorists the present result is a classical input, not a
QME theorem. The immediate target is to finish local anomaly cohomology,
compute the actual type-A and type-B coefficients by two independent methods,
restore or obstruct the QME, and only then ask whether the \(D\)-Cartan
identity transfers quantum mechanically.

### Lorentzian PDE and Green-hyperbolic complexes

The free pure-Weyl metric Hessian does not become a scalar normally
hyperbolic operator on a simple same-bundle auxiliary enlargement; exact
symbol-rank no-go results explain that failure. The successful object is the
whole complex. Curvature prolongation, a symmetric-hyperbolic Weyl--Cotton
system, adjoint-tractor transfer, and support-local retracts produce
retarded/advanced degree-minus-one homotopies on all 386 prolonged rows.

The externally reusable question is whether this construction can be
abstracted into a cyclic transfer theorem for Green-hyperbolic complexes:
when a hyperbolic parent complex contracts onto a detour complex, under what
hypotheses do causal homotopies and current pairings descend?

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

### General relativity and mathematical relativity

The compact Einstein--Maxwell work separates three statements that are often
conflated:

1. Einstein solutions solve the Weyl equations on a common background.
2. Einstein linear tangents inject into the Weyl solution space.
3. The Einstein sector is preserved by nonlinear evolution and has the same
   symplectic form.

The first two now hold in the complete certified standard harmonic tangent
before the final quotient. The third does not follow: the Weyl--Maxwell
pullback is nondegenerate but differs blockwise from the Einstein--Maxwell
form, and fixed-charge second-order Taub obstructions occur for explicit
photon and gravitational modes.

This connects most directly to linearization stability, charge-fibre
obstructions, and the Lorentzian complement to boundary-selected
"Einstein from conformal gravity." The decisive next step is the full extra
fourth-order quotient and then an asymptotically flat Bach phase space with
Bondi/ADM charges and flux.

### Relational clocks and the problem of time

The charge calculation replaces the slogan "time is gauge" with a test:

\[
\delta H_D=\Omega(\delta\phi,\mathcal L_D\phi).
\]

For unrestricted compact data this is nonzero. On the Taub-zero sector it
vanishes. The Berger construction adds a healthy rotating scalar reference
system and shows, at fixed couplings and linear order, that nontrivial matter
clock momentum need not make the total \(D\) transformation physical.

To connect this to the relational-observable literature, the remaining task
is to construct explicit observables \(\mathcal O_A(\tau)\), prove their
gauge invariance and causal dependence, and calculate an actual clock-defined
redshift or response.

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

This programme is not yet a dark-matter, dark-energy, or black-hole model.
Those applications require a physical Lorentzian phase space, stable
backgrounds, observables, and boundary charges before fitting rotation
curves or expansion histories is meaningful.

The infrastructure is relevant because it can test whether the extra Weyl
branch that drives such phenomenology is physical, gauge, constrained,
unstable, or boundary-selected. The sequence is: asymptotic and horizon
phase spaces; extra-branch classification; nonlinear stability; redshift,
lensing, and waveform observables; only then galaxy and cosmology fits.

## Where the strongest criticism currently lands

The criticism is correct in three important senses:

- \(D\) is not universally gauge. It is charged on the unrestricted compact
  phase space and is expected to be physical in ordinary asymptotic settings.
- A zero one-particle residual cohomology on the selected closed cylinder is
  not a proof of particle unitarity or of the absence of radiative degrees of
  freedom in an asymptotically flat universe.
- The Einstein image is not automatically a nonlinear, symplectic, or
  exclusive sector of the fourth-order theory.

The selected construction nevertheless survives the criticism where it
actually claims to apply:

- the zero-charge condition is now derived and audited rather than assumed
  silently;
- the residual calculation is connected to the complete covariant causal
  free complex;
- a healthy clock counterexample shows that matter does not automatically
  turn total \(D\) into a charge;
- the first nonlinear Berger Cartan test closes through arity two, while the
  still-missing analytic and quantum gates remain explicit.

Thus the sector is neither an arbitrary patch nor a model of the whole
universe. It is a mathematically consistent physical choice whose range of
stability is now the subject of the programme.

## What would materially change the verdict

A strong positive change would be any of:

- a certified Berger relational observable with nontrivial redshift while
  total \(D\) remains gauge;
- arity-three and first resonant-channel survival of the interacting Cartan
  contraction;
- vanishing or removable quantum \(D\)-anomaly after QME restoration;
- an asymptotically flat, positive reduced Einstein scattering sector with
  the extra Weyl branch excluded or controlled.

A strong negative change would be any of:

- failure of the Berger contraction in the next physical interaction
  channel;
- an unavoidable nontrivial quantum Cartan anomaly;
- a negative physical extra branch in the asymptotic Bach phase space;
- failure of causal nonlinear closure for every physically admissible
  Einstein-sector boundary condition.

Either outcome is publishable: the programme is designed to locate the first
precise obstruction, not to protect a preferred interpretation.

## Reading and verification map

- [Series overview and papers](../README.md)
- [Paper 7: residual cohomology](../paper/07-conformal-residual-cohomology-krein.pdf)
- [Paper 8: covariant causal transport](../paper/08-conformal-covariant-causal-transport.pdf)
- [Papers 7--8 computational supplement](../paper/07-08-conformal-residual-cohomology-computational-supplement.pdf)
- [Clean publication-release audit](../conformal-publication-release-audit.json)
- [Live \(D\)-quotient status ledger](../d_quotient_programme/reports/consolidated-status.md)
- [Long-term programme and publication gates](universe-building-roadmap.md)
- [General-audience introduction](../paper/how-to-build-a-universe.md)

Papers 7--8 are `ARTIFACT_READY`: the manuscripts, supplements, hashes, and
clean reproduction audit pass. They are not `SUBMISSION_READY` until human
authorship, literature, venue, and prose review and a public archival release
are complete.

## Update policy

This document should remain short enough to read in roughly ten minutes. A
new calculation changes it only when at least one of the following happens:

1. a lifecycle state advances or retreats;
2. a theorem gains or loses a dependency needed for its physical reading;
3. a new background or boundary condition changes a verdict;
4. an open decisive test becomes a certified pass, obstruction, or no-go;
5. a manuscript becomes artifact- or submission-ready.

Raw term counts, implementation milestones, and unverified candidate results
belong in team reports, not in this front door. Every update should preserve
the strongest limitation immediately beside the headline result.

## Changelog

- **16 July 2026:** created the physicist-facing summary; recorded Papers
  7--8 as artifact-ready, the completed cylinder causal bridge, the
  sector-dependent \(D\) verdict, Berger arity-two status with the separate
  fail-closed analytic import, and the complete standard Einstein--Maxwell
  harmonic inclusion before the final quotient.
