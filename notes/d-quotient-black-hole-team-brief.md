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
| BH-2 omega=0 | `BH2_OMEGA_ZERO_STATIC_SECTOR_CLASSIFIED`: static sectors of both carriers log-classified -- axial: residue `{0 (alg 3, geo 2), -2}` (Jordan log) with a TWO-parameter log-free family; polar: `{0 (3,3), +1, -1, -3}` with two `+1`-resonance log obstructions and a TWO-parameter log-free family; RW control clean; the certified polar Einstein `(K,H1)` system DEGENERATES at `omega = 0` (1/omega coefficients; static-adapted reduction = missing object). Closes the `omega = 0` caveat of the reach certificates at classification level | `black_hole_programme/certificates/BH2_OMEGA_ZERO.json` |
| BH-2C stage 1 | `BH2C_ASYMPTOTIC_FORMAL_SYSTEM_LOG_FREE_BOTH_PARITIES` (planning-directive gate): the integer-spaced exponent resonances at `r -> infinity` are CONSISTENT in every characteristic sector -- axial (symbolic omega, both sectors) and polar (`mu = 0` symbolic; `mu = -2 omega` fixtures 3/5, 2/7): log-free formal fundamental systems, NO Jordan blocks at the formal level. Remaining BH-2C stations: metric reconstruction at infinity, finite-flux boundary class, claim repair (rigorous flux bounds, static-sheet wording) | `black_hole_programme/certificates/BH2C_ASYMPTOTIC_JORDAN.json` |
| BH-2C stage 2 | `BH2C_METRIC_RECONSTRUCTION_LEADING_ORDER_CLASSIFIED`: the sourced composition h-systems are rank-1 RESONANT in both characteristic sectors and both parities -- composed metric perturbations gain AT MOST ONE power of `r` over the carrier at infinity; the certified axial Lee--Wald `F^t` has leading symbol `(96/5) pi i alpha (lam - omega)^2 (lam + 2 omega) r^{p1+p2}` -- it VANISHES ON-CHARACTERISTIC (double zero), so radiative pairs have subleading symplectic density and the finite-slice-norm class is decided at subleading order (recorded OPEN with the all-orders reconstruction and the polar flux symbol) | `black_hole_programme/certificates/BH2C_METRIC_LEADING.json` |
| BH-2C stage 3 | `BH2C_FINITE_FLUX_BOUNDARY_CLASS_EINSTEIN_SELECTED_AT_INFINITY` (axial `l=2`, `omega=3/5` fixture): composed metric has LOG TAILS at infinity (pure-power ansatz inconsistent, single-log consistent with nonzero log part, both sectors -- the inhomogeneous realization of the repeated root; homogeneous systems stay log-free); flux power table: `E x E ~ r^-2` (slice norm FINITE) vs `E x X ~ r^0, r^1` and `X x X ~ r^0 ln r, r^2` (DIVERGENT, Einstein-shift invariant) -- **the finite-slice-norm phase space at infinity is exactly the Einstein sector**: the extra branch, causally unavoidable at the horizon, is excluded at infinity by symplectic-norm finiteness (a normalization, not a boundary condition). Symbolic frequency, polar table, summability, phase-space construction, general `l` remain OPEN | `black_hole_programme/certificates/BH2C_FLUX_CLASS.json` |
| BH-2C stage 4 | `BH2C_POLAR_NORM_SELECTION_EINSTEIN_SELECTED_AT_INFINITY` (polar `l=2`, `omega=3/5` fixture): composed-lift classes per leading carrier jet -- `mu=0` all (extra=1, nlog=1) at `s_base=1` (ONE POWER ENHANCEMENT + single log; the inhomogeneous realization of the certified rank-1 resonance; exact conformal-gauge jet classifies (0,0) as control) and `mu=-2 omega` all (0,0) at `s_base=-12i/5` (oscillatory pure power -- parity contrast with the axial single-log both-sector result); flux power table with truncation noise floors: Einstein pairs FINITE (E0xE0 identically zero in the slice density -- an extra mu=0 degeneracy; E2xE2 ~ r^-2, exactly the axial Einstein behavior; the certified BH2B_POLAR_FLUX conjugate-pair nullness concerns the RADIAL flux F^r, a separate exact statement) vs `E x X ~ r^1, r^3` and `X x X ~ r^2, r^4` (DIVERGENT, all jet combinations) -- **two-parity norm selection complete at the fixture level: the finite-slice-norm phase space at infinity is exactly the Einstein sector in BOTH parities**. Methodological receipt: derived carrier sources carry r-weights up to 4, so depth-4 jets corrupt the staircase (spurious inconsistency at every log order); depth-12 column-parametric jets + the gauge-control anchor repaired it, and the axial certificate was re-verified unchanged at depth 12. Symbolic frequency, summability, phase-space construction, general `l`, norm signs remain OPEN | `black_hole_programme/certificates/BH2C_POLAR_FLUX_CLASS.json` |
| Cauchy truncation | `BH_LOCAL_CAUCHY_TRUNCATION_SELECTS_EINSTEIN_MODULO_CONFORMAL_GAUGE` (coordinator bypass item, CLOSE-OUT DONE): on the globally hyperbolic Schwarzschild exterior (`Sigma = {t=const, r>2m}`, smooth `l=2` classes) zero Cauchy data `psi|_Sigma = 0`, `nabla_n psi|_Sigma = 0` propagates `psi = 0` AXIALLY unconditionally (operator exactly `(1/2)Box + C∘`, trace identically zero on the class; exact constraint transport `div(L psi) = (1/2) Box B`); POLAR: `trace(L) = 0` identically -- `psi_conf(t^4 chi P2)` is an exact zero-data nonuniqueness witness -- and via the certified `S(psi_conf(Phi)) = -3 Box Phi` the gauge subtraction proves selection EXACTLY MODULO the conformal orbit (exact on the traceless slice). Exact sequence stated with no direct-sum/surjectivity assertion; endpoint nonselection explicitly contrasted (local Cauchy selects; endpoint regularity does not); dropped-datum mutation rejected via a time-odd mode witness. No sourced-flux inputs used | `black_hole_programme/certificates/BH_LOCAL_EINSTEIN_CAUCHY_TRUNCATION.json` |
| Composed repair | `BH2A_COMPOSED_LIFT_CORRECTED_EXACT_CONSTANT_FLUX`: supersedes the BH2A_CROSS_FLUX fixture values and its on-shell r-independence language (append-only; three documented pipeline defects: dropped X' source term, missing n=0 Frobenius balance, incomplete row system). Corrected composition = Bianchi-cascade `H1` (algebraic) + the `(v,phi)` row; level-2 block exactly rank 1 with `K2 = L.b` a pure source-compatibility identity (vanishes exactly on the carrier); the lift EXISTS in RW gauge, zero n=0 cokernel, log-free, all three dRic rows exactly zero through `rho^8`. EXACT CONSTANT fluxes (`rho^1..rho^8` identically zero; series route validated against the independent rational route): control exactly 0; cross `-10893744/129625+780048i/25925` (3/5), `-15606912/844025+1283712i/120575` (2/7); extra-extra `284488128i/648125` (3/5), `206883648i/5908175` (2/7). FREQUENCY-ROBUST SIGN FLIP: corrected extra-block constants positive-imaginary (superseded were negative) => negative extra-block pairing under the superseded `i*F^r/(pi*alpha)` convention at both fixtures. The old exact `T(0)` constants are re-scoped as diagnostics of the defective row pair. Five sympy verification tool-traps documented in the report. Symbolic omega, general l, polar repair, invariant sign theory OPEN | `black_hole_programme/certificates/BH2A_COMPOSED_REPAIR.json` |
| Polar composed repair | `BH2B_POLAR_COMPOSED_LIFT_AUDITED_EXACT_CONSTANT_FLUX`: polar counterpart of the axial repair. NO horizon pipeline defect (the certified polar composition already imposed all seven dRic rows) -- the repair is a STRENGTHENING: exact rational constants replace the radius-sampled numerical matrix and the 5e-2 r-independence tolerance of BH2B_POLAR_CROSS_FLUX (values superseded, theorems CONFIRMED). All 9 conformal-gauge pairs and `E|E` identically zero at every window key; all 15 physical pairs constant with keys `rho^1..rho^7` identically zero; Hermiticity and extra-block positivity now EXACT rational identities. All analytic carrier modes lift; ambiguity = span(Einstein, conformal gauge). Invariance: conformal shifts move NO entry; Einstein shifts move only the extra block (cross constants INVARIANT since `E|E`=0 exactly, extra block representative-dependent). GENUINE CORRECTION TO BH2C (mu0 Einstein row only): the `vv`/`vr` rows were never imposed; `vr` is clean everywhere and the -2w jet is clean on both, but ALL THREE mu0 power jets fail `vv` -- the shipped `E0` representative (terminating jet `(A,C,K)=(r,0,-5i/3)`) fails with exact closed-form residual `(2r+3)/r^2`, so it is not a linearized Einstein solution. The unique vv-clean combination (nullspace dim 1, all three jets participating) gives `E0true|E0true` class `(-2,0)` = the certified `E2|E2` class, replacing 'identically zero (extra mu0 degeneracy)'. `E|X` and `X|X` classes and the Einstein norm-selection verdict SURVIVE and are strengthened (both parities now identical). Mutations: M1 the superseded representative's exact vv residual; M2 an off-shell truncated pseudo-mode drifts, so the constancy assert is decisive. Symbolic omega, general l, invariant null-quotient sign theory OPEN | `black_hole_programme/certificates/BH2B_COMPOSED_REPAIR.json` |
| Symbolic-frequency indicial layer | `BH2C_SYMBOLIC_INDICIAL_EXCEPTIONAL_SET_IS_OMEGA_ZERO`: first SPLIT of the asymptotic-Jordan item; EXTENDS (supersedes nothing) BH2C_ASYMPTOTIC_JORDAN by lifting the polar mu = -2 omega sector from fixture-only to SYMBOLIC omega. Polar carrier charpoly `lam^3(lam+2I omega)^3`, both oscillatory sectors semisimple (geometric = algebraic = 3, by explicit nullspace dimension -- never inferred from the characteristic polynomial) for every omega != 0; exponents `-1,-2,-3` (mu=0) and `-4I omega-1,-2,-3` (mu=-2 omega). Axial: cascade coefficient `omega^2/4 - 1/r^2 + 2/r^3`, level-2 (H0'',H2'') block rank 1 (determinant IDENTICALLY zero -- symbolic confirmation of the BH2A_COMPOSED_REPAIR structure), RW-gauge charpoly `lam(lam+2I omega)` with exponents `+1` and `-4I omega+1` (metric-level growth r^1, matching the certified hom h-jets). RESONANCE DOES NOT MOVE WITH FREQUENCY: within-sector exponent differences are the integers {1,2} independent of omega; cross-sector differences `4I omega + k` are integral only for imaginary omega; and Re(sigma) = -1,-2,-3 in both oscillatory sectors for every real omega (reality is a DECLARED hypothesis, applied explicitly). EXCEPTIONAL SET (real frequencies) = {0}, by two independent mechanisms (eigenvalue collision 0 = -2I omega; cascade leading coefficient omega^2/4 -> 0); omega = 0 is separately classified by BH2_OMEGA_ZERO. Cross-validated: the leading exponents are exactly the sigma0 values the certified BH2C producers feed to column_jets. Mutations: M1 at omega = 0 the charpoly collapses to lam^6 with geometric multiplicity 3 < 6 (genuine Jordan degeneration); M2 the cascade coefficient vanishes only at omega = 0. TOOL NOTE: the closed-form symbolic reduction HANGS (killed at 65 min); exact 1/r Laurent series does the same job in under a second. NOT established (successor splits): all-orders metric reconstruction maps; the symbolic-frequency finite-flux power table (frequency-independent Einstein selection is PLAUSIBLE from the omega-independent Re(sigma) but is NOT computed or claimed); the assembled endpoint-nonselection theorem; general l; summability | `black_hole_programme/certificates/BH2C_SYMBOLIC_INDICIAL.json` |
| Polar metric-side indicial + shearing obstruction | `BH2C_POLAR_METRIC_INDICIAL_MU0_REQUIRES_SHEARING`: SECOND split of the asymptotic-Jordan item; metric-side counterpart of BH2C_SYMBOLIC_INDICIAL. ESTABLISHED: polar h-system leading charpoly `lam^3(lam+2I omega)` symbolically, reducing to the certified fixture `lam^3(5 lam+6I)/5` at omega=3/5; sector `mu=-2I omega` semisimple with exponent `-4I omega+1` = EXACTLY the sigma0 the certified BH2C_POLAR_FLUX_CLASS producer feeds to column_jets (POSITIVE CONTROL). OBSTRUCTION: sector `mu=0` has algebraic multiplicity 3 but geometric multiplicity 1 -- kernel staircase `[1,2,3]`, a single Jordan chain of length 3. A non-semisimple leading matrix INVALIDATES the projection of A1 onto the generalized eigenspace (that step presupposes diagonalizability); the singularity is irregular and a MOSER/TURRITTIN SHEARING is required, ramified exponents admissible a priori. Self-diagnosing: the same method reproduces certified sigma0 exactly in the semisimple sector and FAILS to reproduce sigma0=1 in the Jordan sector (NEGATIVE CONTROL), so its domain of validity is established rather than assumed. The mu=0 metric exponents are NOT established; the extracted {-3,0,0} are recorded as a REFUTED artifact, never as a result. EXPLICITLY NOT CLAIMED: the Jordan chain does NOT explain the composed-metric log tails of BH2C_FLUX_CLASS -- the exponent matrix is semisimple in every sector (log-factor count 0), consistent with the certified log-free verdict; the tails arise in the SOURCED composition. An earlier working hypothesis to the contrary was tested and dropped. Discipline: Jordan structure from the kernel dimension staircase, never inferred from the characteristic polynomial (the work item forbids that inference). NOT established: the shearing analysis and hence the mu=0 exponents; all-orders reconstruction maps; symbolic flux table; endpoint-nonselection theorem; general l | `black_hole_programme/certificates/BH2C_POLAR_METRIC_INDICIAL.json` |
| Symplectic extension normal form | `BH2_SYMPLECTIC_EXTENSION_HYPERBOLIC_NORMAL_FORM` (LOCAL-ALGEBRAIC): proof-first classification of `0 -> E_Einstein -> E_Weyl -> E_extra -> 0` under the Hermitian Lee-Wald pairing `K = i F^r/(pi alpha)`, NO canonical splitting assumed. THEOREM (a = K(E,X) != 0): a is INVARIANT under the full lift ambiguity `X -> X + beta E + gamma G`; the extra self-pairing obeys `d -> d + 2 Re(conj(beta) a)` which is ONTO R, so EVERY extra self-pairing datum is removable -- explicit witness `beta* = -d a/(2|a|^2)` sets d = 0. The Einstein-extra block is the HYPERBOLIC PLANE: `det = -|a|^2 < 0`, rank 2, inertia (1,1) (both invariant), E is LAGRANGIAN (maximal isotropic) in the block, and on span(E,X,G) the radical is exactly span(G) with hyperbolic-plane quotient. DEGENERATION a = 0: the shear action collapses, d becomes INVARIANT and its SIGN is meaningful, E joins the radical, rank <= 1 -- a qualitatively distinct branch, stated conditionally as the item requires. **RESOLVES THE OPEN INVARIANT-EXTRA-BLOCK-SIGN QUESTION, NEGATIVELY**: for a != 0 there is nothing to certify, since every candidate datum is a lift artifact; the invariants are (rank, inertia) = (2,(1,1)) and the cross class of a. This also explains structurally the BH2B_COMPOSED_REPAIR pattern (cross invariant, extra block representative-dependent). Fixture controls: certified repaired constants satisfy E|E = 0 and cross != 0 at both parities and both frequencies, so a != 0 is the realised branch. Mutations: M1 arbitrary shears move d but fix a/det; M2 at a = 0 shears CANNOT move d. Independent rail is METHOD-DISTINCT (symbolic shear algebra vs exact rational numerical linear algebra, 144 shear trials). NOTE: a conjugation error was caught by the producer's own assert -- the law carries `conj(beta)`, not `beta`. NOT established: the symbolic-frequency VALUE of a (now the only invariant left to compute, and a sharply targeted calculation); general l; any dynamical/Hilbert-space/particle/unitarity reading | `black_hole_programme/certificates/BH2_SYMPLECTIC_NORMAL_FORM.json` |
| All-orders metric reconstruction | `BH2C_METRIC_ALL_ORDERS_ONE_POWER_POLYNOMIAL_LOG_FREE` (LOCAL-ALGEBRAIC + REDUCED-MODE, real omega != 0, l=2, BOTH parities): THIRD split of the asymptotic-Jordan item; all-orders successor of BH2C_POLAR_METRIC_INDICIAL, resolving its three missing_objects (mu=0 shearing, mu=0 metric exponents, all-orders maps). UNIFICATION: the polar h-system (state [Ah,Ch,Ch',Kh]) collapses to an AUTONOMOUS 2nd-order ODE for Ch (Kh, Ah columns of the exact rational Mh vanish except Mh[0,3]=I omega, so Kh, Ah are pure quadratures); the axial h-system (state [H0,H1,H1']) collapses, after eliminating the quadrature H0, to a 3rd-order ODE for H1 with NO undifferentiated H1 term, so U=H1' obeys the SAME operator. Built from independent curvature rows, the two parities give the IDENTICAL master ODE `(r^2-2r)F'' + (2I omega r^2+2r+2)F' + (6I omega r-6)F = 0`. This retires the length-3 (polar) / length-2 (axial) Jordan block of BH2C_POLAR_METRIC_INDICIAL as a first-order-framing artifact. EXACT EXPONENTS (irregular rank-1 point at infinity): `F ~ r^-3` (lam=0) and `F ~ exp(-2I omega r) r^{-4I omega+1}` (lam=-2I omega); the oscillatory exponent reproduces the certified sigma0 (POSITIVE CONTROL). RECURRENCE THEOREM: the lam=0 diagonal recursion coefficient is exactly `-2I omega (k-3)`, nonzero for every integer k>=4 when omega != 0 -- every 1/r coefficient is uniquely fixed, so the series is ALL-ORDERS, not a truncation (k=3 is the indicial root; `c3=1, c4=0, c5=15I/(2 omega), c6=35/(2 omega^2)`). THE mu=0 RESONANCE IS A POLYNOMIAL, NOT A LOG OR A RAMIFICATION: the resonant sector produces one generalized-eigenmode whose only non-decaying content is ONE extra power of r (polar `Ch=0, Kh=kappa => Ah = I omega kappa r`; axial `H1=const => H0 = -I omega r + O(1)`, degree 1) with NO log and NO fractional power at all orders -- the exact all-orders form of BH2C_METRIC_LEADING's leading-order one-power bound, SATURATED and never exceeded; the a-priori-admissible ramified exponents of BH2C_POLAR_METRIC_INDICIAL are decided NEGATIVELY. OMEGA=0 EXCEPTION: the recursion coefficient vanishes identically, the rates collide (0 = -2I omega), and the indicial degenerates to `(s-2)(s+3)` -- integer-separated with r^+2 growth, one-power bound BROKEN, log admissible; omega=0 is the certified exceptional carrier (BH2C_SYMBOLIC_INDICIAL exceptional set {0}) and is EXCLUDED. Independent VbGeo rail reproduces every object and both leading matrices = BH2C_METRIC_LEADING B0h. Fast rail (11 tests) includes wrong-exponent and omitted-log mutations. NOT claimed: convergence/Borel summability; finite-flux/radiative/spectral/dynamical/physical readings; general l; sourced-composition reconstruction (the BH2C_FLUX_CLASS log tails are a distinct object) | `black_hole_programme/certificates/BH2C_METRIC_ALL_ORDERS.json` |

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
