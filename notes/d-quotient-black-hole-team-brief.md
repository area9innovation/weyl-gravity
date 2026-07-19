# Black-hole team brief: horizons as the next physical boundary test

## Shared question

Direct every calculation toward the same question as the rest of the
programme:

\[
\boxed{
\text{Which Weyl-gravity black-hole perturbations are gauge, charged,
constrained, unstable, or genuinely physical?}
}
\]

Do not begin by trying to prove that conformal gravity has good black holes.
Construct the strongest counterexample to the proposed physical sector and
identify the first exact gate at which it passes or fails.

The first result must not be merely “this metric solves the Bach equation.”
A black hole in this programme requires a horizon phase space, differentiable
charges, causal perturbations, flux balance, branch classification, and a
declared physical metric seen by clocks and matter.

## Why this team exists

The cylinder and Berger calculations have no spatial boundary.  A black-hole
exterior has two physically important boundaries:

```text
future/past horizon  <---- exterior causal region ---->  infinity
```

That makes it a direct stress test of the central interpretation.  A
transformation that was null on a compact zero-charge sector may acquire a
horizon or asymptotic charge.  Likewise, a fourth-order mode absent from one
closed residual quotient may carry flux into the horizon or out to infinity.

This team therefore owns the first horizon version of the charge question:

\[
\Omega_\Sigma(\delta\phi,\mathcal L_\chi\phi)
=\int_{\partial\Sigma}
\left(\delta Q_\chi-i_\chi\theta\right)
=\delta H_\chi,
\]

where \(\chi\) is the actual horizon generator.  It is not automatically the
cylinder generator \(D\), Minkowski time translation, or dilation.  Keep all
of those generators in separate ledger rows until an explicit geometric map
identifies them.

## Claim boundary from the start

Every result must declare:

```text
(theory, background, conformal frame, generator, phase space,
 horizon condition, infinity condition, lifecycle)
```

In particular, keep these statements separate:

1. a metric is Bach-flat;
2. a hypersurface is a regular causal horizon;
3. the horizon is regular in the physical matter/clock frame;
4. the exterior initial-boundary problem is causal and closed;
5. a perturbation carries nonzero Lee--Wald flux or charge;
6. the perturbation survives the final gauge and boundary quotient;
7. a quasinormal frequency exists;
8. a quantum black-hole state or Hawking process exists.

No item implies the next one without a certificate.

## Starting laboratory

Start with four-dimensional pure-Weyl gravity,

\[
S_{\rm W}=\alpha\int d^4x\sqrt{-g}\,
C_{\mu\nu\rho\sigma}C^{\mu\nu\rho\sigma},
\]

in a static, spherically symmetric exterior.  Use ingoing
Eddington--Finkelstein or another horizon-regular chart for physical tests;
Schwarzschild coordinates may be used only as an algebraic chart with its
coordinate singularity recorded.

The first comparison family should contain:

- Schwarzschild and Schwarzschild--(A)dS as conformally Einstein controls;
- the complete static spherical Bach-vacuum family in a declared conformal
  gauge, including the Mannheim--Kazanas/Riegert parameters;
- one charged extension only after the vacuum conventions are frozen.

Do not start with Kerr.  Rotation should be activated only after the
spherical horizon charge, flux, and perturbation conventions pass.

## BH-0: reproduce and classify the background family

Construct the static spherical ansatz in a horizon-regular form and derive,
from the repository action and curvature conventions:

1. the Riemann, Ricci, Weyl, and Bach tensors;
2. the complete reduced Bach equations before gauge specialization;
3. the known closed-form vacuum family and its parameter constraints;
4. the Einstein subfamily and the complementary Bach-flat parameters;
5. horizon locations, multiplicities, surface gravities, curvature
   singularities, and conformal-frame singularities;
6. the action of residual diffeomorphisms and Weyl rescalings on every
   integration constant.

For each candidate horizon, decide whether the conformal factor is smooth and
nonzero there.  A singular Weyl rescaling must not be used to declare two
horizon geometries gauge-equivalent.

### Required independent reproduction

Reproduce one established static result in matched conventions before making
a new claim.  The preferred benchmark is the Mannheim--Kazanas/Riegert
vacuum family, with Schwarzschild as the mutation control.  Record the exact
dictionary between its parameters and ours.

### BH-0 output

Return one of:

```text
PURE_WEYL_STATIC_SPHERICAL_BACKGROUND_CLASSIFIED
PURE_WEYL_STATIC_SPHERICAL_COMPLETENESS_OBSTRUCTED
```

The certificate must include exact substitution into all independent Bach
rows, a residual-gauge rank calculation, a horizon-regular chart check, and
at least one mutation that spoils Bach flatness.

## BH-1: construct the horizon and infinity phase space

Use the action-derived symplectic potential and Lee--Wald current.  Do not
infer the physical form from a reduced radial equation alone.

For the selected background family:

1. state the exterior hypersurface \(\Sigma\), horizon cross-section, and
   outer boundary;
2. state falloffs and regularity in a horizon-penetrating chart;
3. compute the presymplectic flux through the horizon and infinity;
4. determine the boundary/corner term needed for differentiability, or prove
   that no local term in the declared family works;
5. compute the Hamiltonians for stationary time translation and, later,
   rotation;
6. identify which static integration constants are charges, fixed boundary
   data, moduli, or gauge;
7. compute the Iyer--Wald entropy and test the first law in the same
   normalization;
8. test invariance under every allowed smooth Weyl transformation.

Keep entropy, energy, and the sign of the perturbative symplectic form as
different objects.  A first law does not prove perturbative stability or a
positive state space.

### Binary charge criterion

For every candidate generator \(X\), report:

```text
proper gauge       H_X = 0 including horizon and infinity terms
charged symmetry   H_X != 0 on the admitted phase space
sector-dependent   H_X = 0 only after stated charge/boundary restrictions
ill-defined         no differentiable Hamiltonian on the proposed domain
```

### BH-1 output

```text
PURE_WEYL_STATIC_HORIZON_PHASE_SPACE_CERTIFIED
PURE_WEYL_STATIC_HORIZON_PHASE_SPACE_NO_GO
```

A no-go for one complete boundary-term/falloff ansatz is a useful result.  It
must not be broadened to all possible black-hole phase spaces.

## BH-2: build the linear exterior BV complex

Begin with odd-parity spherical perturbations.  They are the fastest route to
a radiative branch test with fewer constraint variables.  Then add even
parity.

Construct:

1. the linearized Diff \(\times\) Weyl BV complex in horizon-regular
   variables;
2. a complete gauge-invariant master carrier or an exact obstruction to the
   proposed carrier;
3. ingoing-horizon and outgoing/normalizable-infinity operator domains;
4. retarded and advanced Green homotopies, or the first exact failure of
   Green hyperbolicity;
5. the Einstein inclusion and the extra-Weyl quotient;
6. the action-derived symplectic/Lee--Wald flux matrix on both branches;
7. zero modes corresponding to mass, charge, angular momentum, large gauge,
   and parameter variation.

Use the abstract cyclic causal-transfer theorem only after its strict
consumer contract passes: typed complexes, domains, boundary preservation,
support-local cyclic SDR, degreewise sign involutions, endpoint Green data,
and finite local shears.  A horizon is a boundary-domain problem, not a
formal substitution into the Berger consumer.

### Central branch questions

Answer explicitly:

- Does the Einstein Regge--Wheeler/Zerilli branch inject into the Bach
  complex with the expected horizon and infinity conditions?
- Are there additional fourth-order ingoing solutions?
- Do they carry nonzero horizon or infinity flux?
- Is either extra direction radical, negative, growing, or excluded by a
  causal boundary condition?
- Does exclusion require conditions at both temporal ends and therefore fail
  as a causal initial-boundary prescription?
- Does the horizon generator become charged on the admitted quotient?

### BH-2 output

```text
PURE_WEYL_SPHERICAL_EXTERIOR_CAUSAL_COMPLEX_CERTIFIED
PURE_WEYL_SPHERICAL_EXTERIOR_FIRST_CAUSAL_OBSTRUCTION
```

## BH-3: stability and ringdown

Only after BH-2 closes may the team use the words *stable*, *ringdown*, or
*quasinormal mode* for gravitational perturbations.

Compute the odd-parity spectrum first and separate:

```text
Einstein-like modes | extra Weyl modes | gauge/parameter modes
```

For each mode record frequency, boundary conditions, current/flux sign,
Jordan structure, completeness limitation, and sensitivity to the conformal
frame.  Numerical roots require interval/complex-ball validation or an exact
residual bound; a plotted spectrum is not a certificate.

Do not use scalar or electromagnetic probe stability as evidence for
gravitational stability.  Probe calculations may be reproduced as external
benchmarks only.

The decisive first result is one of:

```text
EXTRA_WEYL_HORIZON_MODE_EXCLUDED_CAUSALLY
EXTRA_WEYL_HORIZON_MODE_PHYSICAL_WITH_SIGN
EXTRA_WEYL_HORIZON_MODE_UNSTABLE
SPHERICAL_RINGDOWN_PHASE_SPACE_NOT_CLOSED
```

## BH-4: nonlinear horizon selection

Once the linear branches and fluxes are known, compute the first nonlinear
source that can mix them.  Transfer \(q_2\) and the first required \(q_3\)
onto the accepted exterior carrier and ask:

- Do two Einstein ringdown modes source an extra-Weyl mode?
- Does an extra mode decay into Einstein radiation or horizon flux?
- Does horizon absorption move the mass/charge parameters and thereby mix
  the branches?
- Is the Einstein exterior sector closed through the tested order?
- Is a dangerous source BRST exact, removable by an admissible cyclic field
  redefinition, or genuinely nonzero on cohomology?
- Is there an exterior analogue of the compact Taub selection rule, now
  expressed as horizon-plus-infinity charge/flux balance?

The desired object is the black-hole version of the programme's branch
extension:

\[
0\longrightarrow E_{\rm Einstein}^{\rm ext}
\longrightarrow E_{\rm Weyl}^{\rm ext}
\longrightarrow E_{\rm extra}^{\rm ext}
\longrightarrow0,
\]

together with its horizon/infinity symplectic forms and mixed transferred
brackets.

## BH-5: observable bridge

After causal perturbations exist, construct one observable outsiders can
recognize:

1. a gauge-invariant tidal response or absorption coefficient;
2. a ringdown frequency and damping-time comparison;
3. a light-deflection or shadow fixture using the same physical metric as
   the clock/matter sector;
4. a horizon redshift between a localized emitter and distant observer.

The first observable should compare the Einstein subfamily and one admitted
extra-Weyl deformation without changing the boundary conditions silently.

Coordinate photon spheres, coordinate frequencies, and null geodesics alone
are not relational observables.  State the emitter, receiver, rods/clocks,
and conformal frame.

## BH-6: rotation and thermodynamics

Activate Kerr or a rotating Weyl family only after BH-0 through the linear
part of BH-3 are stable.  Then repeat:

- horizon regularity and conformal-frame audit;
- mass and angular-momentum charges;
- first law and entropy;
- superradiant boundary conditions;
- Einstein/extra-Weyl perturbation split;
- mode flux signs and stability.

Hawking radiation, evaporation, information loss, and microscopic entropy
are quantum projects.  Classical Iyer--Wald entropy and surface gravity are
inputs, not solutions to those questions.

## Shared test matrix

| Setting | Bach-flat | Regular physical horizon | Differentiable charges | Causal exterior complex | Einstein/extra split | Flux sign | Stability |
|---|---:|---:|---:|---:|---:|---:|---:|
| Schwarzschild control | expected | expected | open in repository conventions | open | open | open | open |
| Schwarzschild--(A)dS control | expected | boundary-dependent | open | open | open | open | open |
| Static Mannheim--Kazanas/Riegert family | known target to reproduce | parameter/frame-dependent | open | open | open | open | open |
| Charged static family | later | parameter/frame-dependent | open | open | open | open | open |
| Rotating family | deferred | deferred | deferred | deferred | deferred | deferred | deferred |

“Expected” and “known target” are reproduction targets, not repository
certificates.

## Immediate overnight goal

Do BH-0 and the BH-1 preflight only:

1. freeze action, curvature, orientation, conformal, and charge conventions;
2. derive the static spherical Bach equations independently;
3. reproduce Schwarzschild--(A)dS and the complete declared
   Mannheim--Kazanas/Riegert family;
4. classify regular horizons and singular conformal frames exactly;
5. derive the unrenormalized Lee--Wald surface form at the horizon and
   infinity;
6. return the minimal boundary-term/falloff ansatz for the first
   differentiability solve.

Do not start quasinormal numerics tonight unless all six items pass.

## Interface with the existing teams

### Status ledger (2026-07-18)

| Gate | Verdict | Certificate |
|---|---|---|
| BH-0 | `PURE_WEYL_STATIC_SPHERICAL_BACKGROUND_CLASSIFIED` | `black_hole_programme/certificates/BH0_STATIC_SPHERICAL_BACKGROUND.json` |
| BH-1 preflight | `BH1_PREFLIGHT_COMPLETE_BARE_FORM_NONINTEGRABLE` | `black_hole_programme/certificates/BH1_LEE_WALD_PREFLIGHT.json` |
| BH-1A | `BH1_NONINTEGRABILITY_REMOVED_BY_FIELD_DEPENDENT_GENERATOR` | `black_hole_programme/certificates/BH1A_NORMALIZED_GENERATOR.json` |
| BH-1B | `BH1_DYNAMICAL_HORIZON_PHASE_SPACE_CERTIFIED` (linear charge level; `l=0` dynamical sector complete) | `black_hole_programme/certificates/BH1B_DYNAMICAL_EXTENSION.json` |
| BH-2A stage 1 | `BH2A_AXIAL_L2_OPERATOR_AND_BRANCH_SPLIT_CLASSIFIED`: axial `l=2` operator; Regge--Wheeler reproduced exactly; branch-split `delta B = (1/2) Box dRic + C.dRic` (extra branch = second-order Lichnerowicz-type carrier `psi = dRic`); split OBSTRUCTED off Einstein backgrounds | `black_hole_programme/certificates/BH2A_AXIAL_OPERATOR.json` |
| BH-2A stage 2 | `BH2A_EXTRA_BRANCH_REACHES_HORIZON_LINEAR_MODE_LEVEL`: two-parameter ingoing-regular extra-branch family at every frequency (EF chart, regular singular point, kernel rank 2); horizon regularity cannot exclude the extra branch -- exclusion must be outer-boundary, causal, or flux/sign | `black_hole_programme/certificates/BH2A_HORIZON_REACH.json` |
| BH-2A stage 3 | `BH2A_FLUX_MATRIX_STAGE1_RW_BRANCH_SYMPLECTICALLY_NULL`: exact axial Lee--Wald bilinear with the off-shell `4 alpha` identity; the Einstein/RW branch carries ZERO symplectic flux for conjugate pairs -- all pairing lives in the Einstein x extra cross-block | `black_hole_programme/certificates/BH2A_FLUX_MATRIX.json` |
| BH-2A stage 4 | `BH2A_CROSS_BLOCK_NONZERO_HORIZON_FLUX_FIXTURES`: extra-branch Hermitian horizon-flux norm nonzero (`i F^r = +|v| pi alpha > 0` for `alpha > 0`) and Einstein x extra cross pairing nonzero at three frequency fixtures (RW-null control < 1e-12); all horizon flux lives in the mixed/extra sectors | `black_hole_programme/certificates/BH2A_CROSS_FLUX.json` |
| BH-2A stage 5 | `BH2A_AXIAL_CAUSAL_DISPOSITION_EXTRA_BRANCH_UNAVOIDABLE`: extra branch propagates on Einstein characteristics with no growing asymptotics at real frequencies; no causal boundary prescription excludes it -- **BH-2A closed at the axial `l=2` mode level** (polar, general `l`, complex-frequency, well-posedness remain open; BH-3 vocabulary stays locked pending those and coordinator review) | `black_hole_programme/certificates/BH2A_CAUSAL_DISPOSITION.json` |
| BH-2B stage 1 | `BH2B_GENERAL_BRANCH_SPLIT_IDENTITY_CLASSIFIED`: general split `delta B = (1/2)Box dRic + C.dRic - (1/6)grad grad dR - (1/12)g Box dR` exact, polar `l=2` included; polar extra branch = trace-coupled second-order Lichnerowicz system | `black_hole_programme/certificates/BH2B_POLAR_SPLIT.json` |
| BH-2B stage 2 | `BH2B_POLAR_EXTRA_BRANCH_REACHES_HORIZON_LINEAR_MODE_LEVEL`: polar trace-coupled carrier reduces (via exact traceless + divergence operator identities) to 3 equations in 4 functions with the underdeterminacy = linearized CONFORMAL gauge (absent axially); on the traceless slice `r = 2m` is regular singular with residue spectrum `{0 (x3), 1-4imw, -1-4imw, -3-4imw}`; two-parameter physical ingoing-regular family modulo conformal gauge at every real `omega != 0` -- horizon regularity cannot exclude the extra branch in EITHER parity sector of `l=2` (Zerilli benchmark, polar flux, disposition, `omega = 0` remain open) | `black_hole_programme/certificates/BH2B_POLAR_REACH.json` |
| BH-2B stage 3 | `BH2B_POLAR_EINSTEIN_BRANCH_REDUCED_TWO_DIMENSIONAL`: t-chart RW polar gauge, `l=2`: W-sector row `= (H0-H2)/2` forces `H2 = H0`; exact reduction to the 2-dim system `dY/dr = M(r)Y`, `Y = (K, H1)` with algebraic `H0` and full consistency; horizon benchmark in adapted variables `(K, B H1)`: t-chart exponents `{+-2imw}`, ingoing `{0, -4imw}` -- identical to the axial RW benchmark. FAIL-CLOSED: Schroedinger-form master scalar (Zerilli anchor) NOT found within the searched bounded rational ansatz classes; remains OPEN, nothing depends on it | `black_hole_programme/certificates/BH2B_POLAR_EINSTEIN.json` |
| BH-2B stage 4 | `BH2B_POLAR_FLUX_STAGE1_EINSTEIN_BRANCH_SYMPLECTICALLY_NULL`: general polar Lee--Wald bilinear (F^t, F^r) + off-shell `4 alpha` identity certified; Einstein-branch block on shell of the stage-3 system: all four bilinear coefficients carry `(omega1 + omega2)` -- the polar Einstein branch carries ZERO symplectic flux for conjugate pairs (even-parity twin of the axial RW-null theorem); the conformal direction `Phi g` is an exact OFF-SHELL degeneracy of the sphere-integrated presymplectic form (no conformal quotient needed at the bilinear level). Extra/cross polar blocks and signs remain OPEN | `black_hole_programme/certificates/BH2B_POLAR_FLUX.json` |
| BH-2B stage 5 | `BH2B_POLAR_CROSS_BLOCK_NONZERO_HORIZON_FLUX_FIXTURES`: `delta Ric[h] = psi` composition certified in the EF polar class -- the realized-Ricci-image conditions close on the FULL 3-dim analytic carrier space (every ingoing-regular polar carrier mode lifts; all seven rows verified on every composed mode; conformal-gauge direction lifts as `Phi g`). Fixture flux matrix (`omega = 3/5`, radii 1/4 and 1/2, r-independent to truncation): Einstein x extra cross pairing NONZERO (representative-independent since the Einstein block is null); extra-block Hermitian norms POSITIVE at the canonical composed representatives (`i F^r/(pi alpha) ~ +81, +53, +62`); Einstein-null + conformal-degeneracy controls separated by >= 8 orders. FAIL-CLOSED: invariant extra-block sign theory (null-quotient pairing) and symbolic frequency remain OPEN | `black_hole_programme/certificates/BH2B_POLAR_CROSS_FLUX.json` |
| BH-2B stage 6 | `BH2B_POLAR_CAUSAL_DISPOSITION_EXTRA_BRANCH_UNAVOIDABLE`: asymptotics of the polar carrier (traceless slice): dispersion `(lambda^2 - omega^2)^3` -- Einstein characteristics; t-chart `sigma in {+-2iw-1, -2, -3}` -- Coulomb phases, amplitude falloffs `r^-1, r^-2, r^-3`, ALL DECAYING (stronger than axial); Einstein K-scalar control `(lambda^2-omega^2)`, `sigma = +-2iw`; gauge scalar control matches one carrier branch. Combined with reach + flux: no causal boundary prescription excludes the polar extra branch -- **BH-2 CLOSED at the l=2 linear mode level in BOTH parities** (complex frequency, general l, well-posedness, stability remain open; BH-3 vocabulary stays locked pending coordinator review) | `black_hole_programme/certificates/BH2B_POLAR_DISPOSITION.json` |
| BH-4 stage 1 | `BH4_HAWKING_MONODROMY_TEMPERATURE_UNIVERSAL_ACROSS_BRANCHES` (LOCAL-ALGEBRAIC + REDUCED-MODE): kappa = 1/(4m), T_H = 1/(8 pi m), consistent with the certified first law (geometric clock); all four ingoing horizon spectra re-derived + hash-matched; Damour--Ruffini monodromy `rho -> e^{2 pi i} rho`: every certified exponent has factor 1 or `e^{omega/T_H}`, every family (both parities, both branches) contains thermal exponents -- **the Boltzmann ratio e^{-omega/T_H} is UNIVERSAL: the extra branch is thermally weighted at exactly the Hawking temperature**, and with the certified nonzero extra-branch flux the mode-level Hawking process radiates into the extra sector. FAIL-CLOSED: no Hadamard state, renormalized stress tensor, grey-body/luminosity, back-reaction, or LORENTZIAN-CAUSAL Hawking theorem | `black_hole_programme/certificates/BH4_HAWKING_MONODROMY.json` |

Headline exact facts now certified: normalized generator `chi = u d_t`
forced by basicness (`u = beta(2-3 beta gamma)`, unique up to component
sign and `f(J)`), `H = -16 pi alpha beta^2 D2` with `J = -u^2 D1 D2`,
Wald entropy `S = 64 pi^2 alpha beta (2 - 3 beta gamma + gamma r_h)/r_h`,
first law `dH = T dS` at every simple horizon, and linear-level
frame-independence (time-dependent conformal and `l=0` diffeo directions
carry exactly zero charge and flux; entropy conformally invariant on the
symbolic family).  The atlas fragment lives at
`black_hole_programme/atlas/black-hole-atlas-fragment.json` (generated,
fail-closed, shared-validator checked).  Radiative `l>=2` fields are
`OPEN`: the next gate is **BH-2A** (odd-parity horizon-regular
Diff x Weyl complex, Einstein/extra branch split, ingoing/outgoing
domains, bilinear horizon and boundary flux matrix, causal disposition of
the extra branch).  The tangent-cone horizon analogue (global charges +
horizon/boundary flux constraints + resonant or stationary cokernel) is
deferred until the BH-2A linear phase space and adjoint problem exist;
the compact moment-map theorem is not imported as a horizon theorem.

### Active bridge (ladder stage 6; see roadmap "Bridge priority ladder")

**Bridge:** compact branch data to black-hole/asymptotic radiation
(black hole + Einstein).  **Status: INACTIVE.**

**Activation gate:** an independently closed exterior/asymptotic phase
space with boundary-preserving generators, charges and fluxes — i.e. the
BH-2A odd-parity (then polar) exterior complex, horizon-plus-outer-boundary
phase space, charges, fluxes and pairings, built natively on the black-hole
background.  Only after those native modes exist may invariant branch
factors, Lee--Wald signs and limiting data be *compared* with compact
results.  The compact Taub cone is never imported as a horizon theorem, and
modes are never identified across backgrounds by matching names.

**Fail-closed atlas row:** `bh.bridge.compact-branch-comparison` in
`black_hole_programme/atlas/black-hole-atlas-fragment.json` — all
description axes `NO_CERTIFIED_MAP` until the activation gate closes and an
explicit crosswalk certificate exists.

### Current eight-hour assignment (2026-07-17; supersedes the BH-0 preflight queue)

BH-0 and the bare BH-1 preflight are certified.  Do **BH-1A normalized
generator and boundary ensemble**, not BH-2 ringdown.  Audit whether the
residual `c`-map and dilation are globally admissible proper gauge on the
selected exterior; replace chart-fixed `partial_t` by the boundary-
normalized field-dependent generator and include its covariant charge
correction; require both horizontality and invariance before descending a
charge form.  Close one Einstein control ensemble and one physically defined
extra-Weyl ensemble, then compute integrability, entropy and first law in the
same normalization.  A surviving obstruction must be interpreted as boundary
source--response/symplectic-flux data.  The exact fallback verdicts and
morning handoff are in
[`universe-building-roadmap.md`](universe-building-roadmap.md#coordinated-eight-hour-work-queue--2026-07-17).

- **Einstein team:** owns the asymptotic Bach/BMS phase space and the compact
  Einstein--extra branch dictionary.  Import its conventions; do not build a
  competing Bondi complex.  The black-hole team owns the horizon and exterior
  domain.
- **Classical team:** supplies the abstract causal-transfer theorem and local
  BV conventions.  Import them only through their consumer gates.
- **Nonlinear team:** receives the accepted exterior carrier and branch
  projector before transferring horizon interactions.
- **Quantum team:** receives the classical exterior BV complex, state-domain
  and charge data.  No Hawking or quantum-entropy claim precedes the local QME
  and Hadamard gates.
- **Observer team:** should later supply localized rods, clocks, emitter and
  detector morphisms for redshift, shadow, and ringdown records.

Create new implementation under `black_hole_programme/`.  Do not edit active
Einstein, observer, classical, nonlinear, or quantum producers merely to make
an import pass.  Pin imported certificates by path, result ID, hash, and
commit.

## Decision tree

The black-hole route is substantially obstructed if any of the following is
certified:

- no differentiable horizon-plus-infinity Hamiltonian exists in the complete
  declared boundary ansatz;
- the exterior fourth-order initial-boundary problem is not causally closed;
- removing the extra branch requires a future boundary condition;
- an unavoidable extra mode has negative physical flux or exponential
  growth;
- Einstein ringdown data necessarily source that mode at the first nonlinear
  order;
- the candidate physical conformal frame is singular at the horizon.

The programme is substantially strengthened if instead:

- a regular horizon phase space with a first law and flux balance exists;
- the Einstein branch embeds with the expected charges and causal response;
- every extra branch is either causally excluded, constrained nonlinearly, or
  admitted with a controlled physical sign;
- the selected exterior sector is stable through the first interaction;
- one relational ringdown, absorption, redshift, or shadow observable is
  certified.

Either outcome is valuable.  A precise horizon no-go would locate where the
candidate universe stops.  A pass would connect the programme to strong-field
gravity and gravitational-wave astronomy.

## Required receipts

Every promoted result must leave:

- a machine-readable certificate and strict schema;
- an action-derived producer and structurally independent verifier;
- exact or validated-numeric arithmetic appropriate to the claim;
- mutation tests for the background, horizon and charge identities;
- an assumptions and missing-object ledger;
- dependency tags distinguishing `LOCAL-ALGEBRAIC`, `REDUCED-MODE`,
  `LORENTZIAN-CAUSAL`, and any later quantum claim;
- a human-readable report stating what was **not** proved.

## Primary comparison spine

Begin the literature dictionary with:

- Riegert's static spherical Bach-vacuum classification and the
  Mannheim--Kazanas exact exterior solution;
- the Iyer--Wald covariant Noether-charge and first-law construction for
  higher-derivative Lagrangians;
- Lü, Perkins, Pope and Stelle's non-Schwarzschild higher-derivative black
  holes as an adjacent, not identical, branch-selection benchmark;
- modern black-hole perturbation/current work only after matching its theory,
  conformal frame and boundary domain.

Useful starting links:

- [Mannheim--Kazanas exact vacuum solution](https://ntrs.nasa.gov/citations/19890058282)
- [Iyer--Wald Noether charge and dynamical entropy](https://arxiv.org/abs/gr-qc/9403028)
- [Lü--Perkins--Pope--Stelle higher-derivative black holes](https://arxiv.org/abs/1502.01028)
- [Conserved currents for Kerr perturbations](https://arxiv.org/abs/2210.15935)

The literature audit must distinguish pure-Weyl gravity from Einstein--Weyl,
critical gravity, conformally related effective-matter models, and probe-field
calculations.  Similar-looking metrics do not imply identical field equations,
phase spaces, or physical observables.
