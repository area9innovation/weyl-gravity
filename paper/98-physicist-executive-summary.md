# Pure-Weyl gravity programme: executive summary for physicists

**Public pre-release — 27 July 2026**

*By GPT-5.6.sol and Asger Alstrup Palm*

> **Research context.** Asger Alstrup Palm, a computer scientist and Honorary
> Professor at DTU Compute, orchestrates the programme and is the accountable
> human contact. AI systems perform substantial derivation, programming,
> verification, literature work, adversarial review, and drafting. The work
> must be judged from its arguments and reproducible evidence, not its unusual
> authorship.

## Sixty-second summary

Pure Weyl gravity is a fourth-order conformal metric theory. It contains more
local gravitational solutions than general relativity, and familiar
decompositions give some of them indefinite signs. This programme separates
four questions that are often compressed into the word “ghost”:

1. Which local solutions exist?
2. Which classical directions survive gauge, constraints, charges,
   boundaries, and the symplectic radical?
3. Which directions continue through nonlinear interactions?
4. Which directions become states or particles in a positive quantum theory?

The programme has not rescued pure Weyl gravity, nor proved a universal
no-go theorem. Its Phase-1 result is a scoped classification: additional
classical directions survive some reductions, while nonlinear, boundary,
stability, and quantum tests exclude or obstruct others. No tested candidate
has reached a positive full-BV state, scattering theory, or unitarity theorem.

The strongest current black-hole result is sharper. In axial
Schwarzschild $\ell=2$, standard Lorentzian conditions—future-horizon
regularity and ordinary incoming/outgoing trace conditions—do **not** select
the Einstein subsector. The two repeated spin-two Regge–Wheeler layers form a
non-split self-extension. At one validated damped Schwarzschild frequency,
the connection has Smith type $(0,0,2)$: algebraic multiplicity two,
geometric multiplicity one, and a length-two root chain. Its generalized
member has nonzero traceless-Ricci carrier. The compactly cut-off exterior
radial Green operator has a nonzero rank-one second-order pole.

The isolated local resonance contour consequently contains a
$t e^{i\omega_n t}$ Einstein-profile term. This is **not** yet a theorem
about the complete retarded Schwarzschild waveform.

The stable Phase-1 synthesis is
[Paper 15](15-four-level-ghost-classification-phase1-synthesis.pdf). The
current black-hole statements are in [Paper 16](16-lorentzian-endpoint-nonselection-pure-weyl.pdf)
and [Paper 17](17-pure-weyl-schwarzschild-extension-structure.pdf).

## Current verdict

**Established in a declared setting**

- exact free fourth-order completions, Krein/Jordan limits, and selected
  interaction obstructions;
- complete causal free gauge complexes on several controlled backgrounds;
- additional compact axial and polar classical directions with nonzero
  action-derived pairings;
- a nonzero strict local Euclidean one-loop BV anomaly;
- axial Schwarzschild endpoint non-selection and a populated indefinite
  incoming trace space;
- one validated defective axial $\ell=2$ Schwarzschild QNM, a cut-off
  exterior double Green pole, and a fixed-domain global complex-scaled
  radial Fredholm realization.

**Partial or local**

- positive metrics on selected reduced blocks;
- relational clocks and detector preparations on compact laboratories;
- finite-harmonic nonlinear continuation;
- compensator restoration in an enlarged theory;
- outgoing Schwarzschild population on a certified band and generically away
  from isolated reflection zeros;
- Bondi observation and complexified, radially compact frequency-domain
  source overlap for the leading QNM pole.

**Open**

- a positive full-BV Hilbert space and unitarity;
- realistic local apparatus and cosmology;
- the complete bounded nonlinear cone and stability;
- the Lorentzian QME and interacting observables;
- the complete Schwarzschild scattering operator and polar analogue;
- global causal contour deformation and real astrophysical excitation.

## The claim architecture

The repository distinguishes these dependency classes:

```text
LOCAL-ALGEBRAIC
EUCLIDEAN-SPECTRAL
REDUCED-MODE
LORENTZIAN-CAUSAL
```

A result does not move between them silently. In particular, the repository
does not currently contain:

- a complete Lorentzian off-shell BV propagator;
- a BRST-compatible Hadamard state for the full metric BV complex;
- renormalized Lorentzian time-ordered products;
- a causal perturbative AQFT construction;
- a Lorentzian quantum-master-equation theorem;
- a global proof that a QNM residue controls the full late-time waveform.

## Four principal result groups

### 1. Free completion and interaction

Papers 01–04 classify the Pais–Uhlenbeck and fourth-order field completion
problem. They distinguish:

- a finite-dimensional positive metric;
- a Krein real form;
- a vacuum covariance;
- a field representation and Fock sector;
- the equal-frequency Jordan limit;
- gauge and Lorentz-covariant gravitational reduction.

These structures are related but not interchangeable. Papers 05–06 then show
that the canonical analytic positive completion need not survive
branch-changing interactions. The obstruction is scoped: it does not exclude
every indefinite, nonlocal, singular, or nonperturbative prescription.

### 2. Causal reduction and compact laboratories

Papers 07–08 construct the selected free pure-Weyl residual and causal
BV–BFV problems on the conformal cylinder. In the declared zero-charge
derived sector,

$$
H^4_{\mathrm{res}}
=\operatorname{span}\{[W_+^2],[W_-^2]\},
\qquad G_{\mathrm{res}}=I_2.
$$

These are centered deformation or vertex classes, not one-particle
gravitons.

On compact Weyl–Maxwell laboratories, Papers 09–13 and their certificate
chains identify ordinary Einstein-image and additional fourth-order
directions. Selected additional axial and polar blocks are nonradical under
the action-derived Lee–Wald form. Their signs do not obey the shortcut
“Einstein positive, additional negative.”

At second order, finite-harmonic exponential-polynomial continuation is
controlled by five stabilizer moment maps. Bounded continuation obeys
additional secular-growth and shell-resonance conditions. A causal changed
gravity–clock parent was constructed, but its physical
$j=\tfrac12$ block has a Hamiltonian–Hopf quartet throughout the connected
trace-healthy same-field stationary family. Phase 1 therefore selected no
robust Phase-2 theory.

### 3. Schwarzschild endpoint and resonance structure

Paper 16 proves that the complete axial $\ell=2$ Schwarzschild system has
the filtered differential module

$$
M_{\rm RW}^{(2)},\qquad
M_{\rm RW}^{(2)},\qquad
M_{\rm RW}^{(1)}.
$$

The repeated spin-two factors form a non-split self-extension. The incoming
trace form is nondegenerate with inertia $(1,2)$; in factor coordinates it
is congruent to

$$
\pi\alpha_{\rm W}
\begin{pmatrix}
0&576\omega/5&0\\
576\omega/5&0&0\\
0&0&-32/(15\omega)
\end{pmatrix}.
$$

Scalar Wronskian arguments show that every incoming direction is populated
by a future-horizon-regular solution for all real $\omega>0$. Thus
horizon regularity and one-sided radiative traces select propagation
direction, not position in the extension. The same filtration excludes
exponentially growing separated axial modes. Indefinite populated flux and
separated-mode stability therefore coexist.

At a validated simple Regge–Wheeler QNM, a nonzero extension selector gives
Smith valuations $(0,0,2)$. Paper 17 reduces the projective class to

$$
[\mathcal I_{\rm Bach}]
=\frac{i\omega}{2}\left[1-\frac2r\right].
$$

Writing $m=\mu^2$ for the signed squared-mass parameter, the exact
first-jet reduction of the complete coupled massive axial system gives

$$
[\mathcal I_{\rm phys}]
=\frac13\left[1-\frac2r\right],
\qquad
[\mathcal I_{\rm Bach}]
=\frac{3i\omega}{2}[\mathcal I_{\rm phys}].
$$

This closes the local coupled-system crosswalk, and the result is no longer
only a leading-phase comparison: matrix Frobenius and sectorial Volterra
constructions identify the complete endpoint-normalized Jost planes and
exclude an opposite-Jost component. Consequently,

$$
\omega_n'(0)=\frac{2i}{3\omega_n}\kappa_n\ne0
$$

for the signed squared-mass parameter.

For the doubled radial problem,

$$
R(\omega)
=\frac{R_{-2}}{(\omega-\omega_n)^2}
 +\frac{R_{-1}}{\omega-\omega_n}
 +R_{\rm hol}(\omega),
\qquad R_{-2}\ne0.
$$

The result holds for a finite-interval problem with exact transparent
conditions, for the compactly cut-off exterior radial Green operator, and
for a fixed-domain two-ended $\pi/4$ complex-scaled
$H^1\to L^2$ Fredholm pencil of index zero. The differentiated Jost tangent
belongs to that same fixed Sobolev domain. This still does not construct a
causal uncut real-axis inverse or justify a retarded contour deformation.
The geometric root is Einstein; the generalized root has nonzero
traceless-Ricci carrier. Exact reconstruction gives nonzero Bondi shear for
the Einstein range of $R_{-2}$, and a complexified conserved, traceless,
radially compact odd source can have nonzero adjoint overlap.

The isolated local contour contribution is therefore

$$
e^{i\omega_n t}\left(V_1+i t\,V_0\right).
$$

This is the asymptotically flat Schwarzschild analogue of the
critical-gravity logarithmic-partner mechanism, but its endpoint tangent is
polynomial rather than a literal independent radial logarithm.

### 4. Quantum obstruction

Paper 12 reconstructs the nonzero local Euclidean one-loop Weyl anomaly in
the declared strict pure-Weyl BV complex. A formal compensator makes the
tested cocycle exact and restores the tested Euclidean QME at one loop, but
changes the theory and counterterm space.

A separate reduced E/A/L carrier admits microlocal Hadamard two-point
distributions with signs $(+,-,-)$. This is a Krein carrier, not a positive
full-BV state or particle theorem.

## Why the newest result matters

The defective Schwarzschild resonance connects four descriptions:

```text
non-split differential module
  → nonzero resonant extension selector
  → length-two QNM root chain
  → second-order cut-off radial Green pole
```

The determinant alone sees only multiplicity two. The selector determines
whether that doubled zero is one defective chain or two semisimple roots.
The leading Green coefficient is rank one, and source and observer maps see
it precisely when their adjoint and Einstein-mode overlaps are nonzero.

This is scientifically interesting even if pure Weyl gravity ultimately
fails. It identifies a concrete, gauge-invariant spectral consequence of the
extension rather than merely counting fourth-order solutions.

## Where the strongest criticism should land

The vulnerable interfaces are now explicit:

1. **Certificate transparency.** Load-bearing exact and interval results
   must be reconstructible from immutable manifests, commands, hashes, and
   independent verifiers.
2. **Massive-system crosswalk.** The complete coupled massive axial
   first-jet factorization, factor-three normalization, endpoint-analytic
   Jost planes, and nonzero signed squared-mass QNM velocity are established
   at `REDUCED-MODE` level.
3. **Global causal domain.** The generalized endpoint state has weakened
   asymptotics. A closed global domain or augmented boundary pencil must
   support it.
4. **Retarded contour control.** High-frequency estimates, thresholds,
   branch cuts, and real causal data are needed before claiming observable
   ringdown.
5. **Polar and all-multipole scope.** The headline defective-resonance theorem
   is axial and $\ell=2$.
6. **Quantum interpretation.** A nilpotent classical or radial Green
   structure is not by itself a positive quantum theory.

## Paper ledger

- **Papers 01–03:** Pais–Uhlenbeck metrics, field representations, and the
  Krein/Jordan boundary.
- **Papers 04–06:** fourth-order gravity reduction and interaction
  obstructions.
- **Papers 07–08:** pure-Weyl residual cohomology and covariant causal
  transport.
- **Papers 09–13:** clocks, compact phase spaces, gravity–light transfer,
  anomaly, and nonlinear tangent cone.
- **[Paper 14](14-pure-weyl-black-hole-radiation.pdf):** initial black-hole
  architecture; later papers correct and supersede parts of its
  interpretation.
- **[Paper 15](15-four-level-ghost-classification-phase1-synthesis.pdf):**
  stable Phase-1 synthesis.
- **[Paper 16](16-lorentzian-endpoint-nonselection-pure-weyl.pdf):**
  Lorentzian endpoint non-selection theorem.
- **[Paper 17](17-pure-weyl-schwarzschild-extension-structure.pdf):**
  non-split self-extension, defective QNM, cut-off Green double pole, and
  global complex-scaled radial Fredholm realization.
- **[Paper 18](18-static-bach-flat-black-hole-thermodynamics.pdf):**
  residual-basic charge normalization and simultaneous signed horizon
  first-law identities on regular local quotient charts of the certified
  Mannheim--Kazanas family. This is an exact static and linear-spherical
  charge theorem, not a physical-process or radiative thermodynamics theorem.

## Research priorities

The next work with the highest scientific leverage is:

1. independently reproduce the Paper 17 selector and Green-pole certificate;
2. build a global causal Schwarzschild domain and justify inverse-Laplace
   deformation;
3. compute a real source overlap and detector-level asymptotic coefficient;
4. complete the polar and broader multipole analysis;
5. independently audit Paper 18's residual-basic normalization against the
   conformal-gravity thermodynamics literature;
6. construct, or rule out under explicit assumptions, a positive
   BRST-compatible Lorentzian quantum state.

## Method and release status

The project is an experiment in whether a non-domain-expert who knows how to
orchestrate AI can produce research useful to experts. The intended evidence
chain is

```text
claim
  → producer
  → machine-readable certificate
  → independent verifier
  → mutation test
  → paper with explicit non-claims
```

Not every historical result has reached every stage. The repository is a
pre-release archive without a DOI or repository-wide licence. Its claims
should be reviewed as claims, not accepted because they were generated by AI
or rejected merely for that reason.

The [public construction map](../certificate_graph/universe-building-dag.svg),
[technical certificate graph](../certificate_graph/certificate-dag.svg), and
[repository README](../README.md) provide the evidence and authorship
context.

## Bottom line

The current result is not “Weyl gravity is healthy.” It is:

> Pure Weyl gravity’s axial Schwarzschild system contains a non-split
> Regge–Wheeler self-extension. Standard Lorentzian radiation conditions do
> not remove its additional layer, and one ordinary Schwarzschild QNM becomes
> a defective resonance with a genuine second-order cut-off radial Green
> pole.

Whether that pole becomes an observable, globally causal ringdown signal—and
whether any quantum theory containing it is physically acceptable—remains
open.
