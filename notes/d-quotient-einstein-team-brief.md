# Einstein team brief: does the closed-cylinder quotient describe gravity with boundaries?

## Commission

Answer one question:

\[
\boxed{
\text{Is }D\text{ genuinely gauge after adding clocks, interactions, quantization, or boundaries?}
}
\]

Your task is **not** to export the closed-cylinder cohomology result to
scattering.  Construct the strongest asymptotic or causal counterexample to the
\(D\)-quotient, in a setting where time translation is expected to carry a
physical charge, and determine exactly which parts of the Weyl-gravity
construction survive.

The compact-cylinder Cartan contraction depends on a boundaryless phase space
and a strict residual action.  Neither property may be assumed at null or
timelike infinity.  The centered residual classes \([W_+^2]\) and
\([W_-^2]\) are deformation/vertex classes, not one-particle gravitons and not
surrogates for radiative scattering states.

Existing flat transverse-traceless reduced-mode and radial indicial results are
bootstrap inputs only.  They do not establish a full Lorentzian off-shell BV
propagator, support-compatible Green complex, null-infinity charge theorem, or
scattering equivalence.

## E-D1a status: generator identification completed

The exact seed certificate
`bridge/certificates/d_quotient_asymptotic_seed.json` corrects a necessary
ambiguity before the charge computation.  Three generators must be kept
separate:

```text
H_ESU = real Einstein-cylinder time translation d_T,
D_M   = real Lorentzian Minkowski dilation t d_t+r d_r,
D_rad = compact radial-quantization grading used in the residual module.
```

Under the real Penrose map, `H_ESU` becomes `(P_0+K_0)/2` in the stated
convention and crosses the null boundary of a fixed Minkowski patch.  It is
not a boundary-preserving generator there.  `D_M` is tangent to null infinity
and restricts to `u d_u`, but it is not `P_0=d_u`.  The compact identification
`D_rad=D_M` uses the radial-quantization Cayley/Wick continuation, not the
real Lorentzian Penrose push-forward.

Consequently “time-translation/`D` charge” must be split into distinct
charge questions.  Nonzero ADM/Bondi `P_0` charge does not compute the charge
of `D_M` or `H_ESU`.  The current asymptotically flat verdict is
`PHASE_SPACE_NOT_CLOSED`, not `D_GAUGE` or `D_CHARGED`; the Einstein verdict
is `EINSTEIN_OPEN`.  See `notes/conformal-d-quotient-asymptotic-seed.md` for
the exact dictionary, reduced shear/news action, and triangular `(h,chi)`
operator seed.

The subsequent flat TT Schwartz-core kill test adds a separate obstruction:
the pure-Weyl current restricts to zero on two Einstein wave tangents, while
the Einstein-Hilbert current has a nonzero Cauchy witness.  Local finite-jet
improvements cannot change this rank mismatch on the declared domain.  Thus
causal closure of `chi=0`, even if proved, is not sufficient for Einstein
scattering; a nondegenerate symplectic and charge comparison is independently
required.  The result is scoped and does not yet classify null-infinity
corners or compensator-generated Einstein-Hilbert terms.

## Work package E-D1: asymptotically flat Lorentzian BV--BFV complex

Construct the retarded/advanced linear BV complex with declared spaces and
falloffs at

\[
\mathscr I^-,\qquad i^0,\qquad \mathscr I^+.
\]

Include fields, ghosts, antifields, constraints, corner matching, soft/memory
data, Coulombic data, and the extra Cauchy data of the fourth-order Bach
operator.  Prove the mapping and support properties of the differential and
Green operators on the chosen weighted, Sobolev, or polyhomogeneous spaces.

Identify the actual asymptotic symmetry algebra from boundary preservation and
finite charge criteria.  Compute the renormalized charge variation, flux, and
algebra for the asymptotic transformation corresponding to cylinder \(D\):

\[
\delta H_D=\Omega_\Sigma(\delta\phi,\mathcal L_D\phi).
\]

Separate proper gauge parameters, whose normalized charges vanish, from BMS or
other asymptotic symmetries.  Include surface counterterms and corner terms.
Do not quotient time translation if it has ADM/Bondi charge or flux.

Then compute:

- radiative BRST/BV cohomology;
- helicity-\(\pm2\) one-particle and wave-packet classes;
- the causal symplectic/Green pairing and its signature;
- the Einstein radiative branch and the generalized fourth-order/Weyl branch;
- the conventional ghost mode and any zero-norm or logarithmic partners.

The strongest counterexample is admissible finite-flux data for which \(D\) is
charged and an unavoidable extra branch has negative physical norm or a new
scattering channel.  If boundary conditions remove it, prove that those
conditions are local, causal, symplectic, and preserved.

## Work package E-D2: causal closure of the Einstein sector

Fourth-order Bach evolution needs more Cauchy data than Einstein evolution.
Define the proposed Einstein submanifold by local initial/boundary constraints
and prove or refute

\[
\text{Einstein data on }\Sigma
\Longrightarrow
\text{Einstein solution for all time}.
\]

At linear order and then at the first nonlinear order:

1. list the complete Bach Cauchy data and the proposed Einstein constraints;
2. prove constraint propagation using the hyperbolic evolution, not only a
   modewise polynomial identity;
3. test retarded and advanced support and compatibility with gauge fixing;
4. test preservation at \(\mathscr I^\pm\), \(i^0\), and any timelike boundary;
5. identify whether extra normal derivatives are fixed locally, elliptically on
   a slice, nonlocally, or by future boundary data;
6. compute the first nonlinear source for the transverse extra branch.

The target theorem is:

> There exists a local, causal set of initial or boundary conditions selecting
> the Einstein branch, and this branch is preserved by evolution.

If the conditions require future data, nonlocal projection, or loss of a
well-posed symplectic phase space, issue a no-go result instead of weakening the
meaning of “causal.”

### Compensated flat TT result

The separate certificate
`bridge/certificates/compensated_einstein_causal_subsector.json` proves the
target at source-free linear flat TT level in the constant-compensator phase.
The local conditions `chi=0` and `n.chi=0` propagate by massive Klein--Gordon
uniqueness, remove the massive Cauchy branch, and retain the nondegenerate
Einstein-Hilbert current and positive `P_0` energy for both helicities.  No
future boundary condition is used.

Keep the scope separate from pure Weyl gravity and from the full E-D2 target.
The full metric BV lift, arbitrary sources, nonlinear propagation, null
infinity, and scattering remain open.

The follow-on local-projector certificate
`bridge/certificates/compensated_einstein_local_projectors.json` constructs
the complementary on-shell differential projectors `Pi_E=1+Box/M^2` and
`Pi_M=-Box/M^2`.  They commute with free evolution, are support-nonincreasing,
and reproduce the symplectic block split.  Their locality begins only after TT
reduction, and the source audit shows that a generic source excites both
branches.

The sourced-defect preflight certificate
`bridge/certificates/compensated_einstein_sourced_defect_preflight.json` now
derives the unreduced flat tensor obstruction.  For
`c1 G1+2 alpha B1=T`, a solution of the conventional same-source Einstein
equation `c1 G1=T` solves Einstein--Weyl gravity if and only if `Q(T)=0`.
Conservation and the compensator Weyl Ward identity do not imply this; an
exact conserved traceless counterexample is certified.  Arbitrary same-source
closure is therefore refuted at linearized flat level.

Do not call a fixed-external-source solution locus a BV subcomplex: it is
affine.  The certificate
`bridge/certificates/compensated_quadratic_minimal_bv.json` now constructs the
local minimal compensated complex in invariant variables and proves exact
nilpotency, formal cyclicity, and contraction of the Weyl Stueckelberg doublet.
It reduces to the 28-dimensional Einstein--Weyl metric--Diff minimal complex.

The actual operators are now available in the independently consumed canonical
export `bridge/certificates/compensated_minimal_bv_operator_export.json`.
The scoped snapshot
`bridge/certificates/compensated_nonzero_characteristic_snapshot.json`
constructs exact representatives, `pi_cl` projections, homotopies, and
momentum-reversing odd BV pairings.  Its nonzero null fiber has
`(H^-1,H^0,H^1,H^2)=(0,2,2,0)`, while the extra root has `(0,5,5,0)`.

The two null degree-zero classes are where the usual helicity-`+/-2` local
waves live before the final residual quotient.  Their existence is compatible
with vanishing absolute one-particle residual cohomology on the closed
cylinder: the latter is an additional compact global `SO(4,2)` reduction, not
a claim that local or asymptotically flat radiative solutions are absent.

This is still not the global classical import freeze.  The `p=0` global modes,
covariant characteristic bundle, physical radiative pairing, gauge-fixed
nonminimal domain, and causal Green data remain open.  E-D2 should next lift
the sourced-defect map through a declared dynamical matter BV complex at a
common Einstein--matter/Weyl--matter background.
A higher-derivative dressed source is a separately labelled coupling, not
conventional Einstein equivalence.

The universal part of that gate is now complete in
`bridge/certificates/compensated_sourced_defect_chain_map.json`.  It constructs
the external `(T_mn,J_phi)` Ward complex, the exact `Q(T)` obstruction chain
map, the affine Einstein-defect map, and compatible-source kernel
representatives.  At a generic symbol, only one of six Ward cycles is
Einstein-compatible; at a nonzero null symbol, five of six are.  The next E-D2
gate is narrower and model-dependent: select a matter action, construct its
full BV complex, and prove its stress/source realization maps into this
universal Ward complex while preserving `ker Q`.

The Berger rail now supplies an exact positive-energy rotating clock, the
scoped `D_GAUGE` verdict, the clock SDR, and the complete coefficientwise
cyclic 26-row retained minimal `q1`.  It is neither identified with the flat
Stueckelberg compensator nor inserted into the compensated BV differential.

The new `BERGER_EINSTEIN_INCIDENCE` certificate classifies the background
itself.  It is not Einstein, not conformally Einstein because `B_00` is
nonzero, and not Einstein with the same clock stress for any constants
`kappa,Lambda`.  The exact trace-free-Ricci/Bach minor is
`-q(1-q)/(8a^6)`.  Hence this is a genuine non-Einstein Weyl--matter branch;
a same-base-point Einstein tangent inclusion is `NOT_APPLICABLE`, not merely
open.  The classical Berger rail continues independently with nonminimal and
causal completion.

### Common-background replacement selected

The exact `EINSTEIN_MAXWELL_PRODUCT_INCIDENCE` certificate now supplies the
different common background required by the Berger non-incidence result. An
aligned Maxwell field on `M_2(k_1) x Sigma_2(k_2)` solves both frozen
Einstein--Maxwell and pure Weyl--Maxwell equations with the same metric and
field on the branch

```text
Lambda=(k_1+k_2)/2
rho=(k_2-k_1)/(2*kappa)
alpha_B*kappa*(k_1+k_2)=3.
```

The positive flat specialization `R^(1,1) x S^2` admits a smooth spatial
`S^1` quotient with compact Cauchy topology `S^1 x S^2`. This is a
`LOCAL-ALGEBRAIC`, lifecycle-`CLASSIFIED` background theorem. It is not a
clock or asymptotically flat background.

The principal part of that comparison is now certified by
`EINSTEIN_MAXWELL_PRODUCT_TANGENT_PREFLIGHT`. Both four-stage minimal layouts,
including the Maxwell ghost and identity, are frozen, and the exact
action-normalized symbol chain map uses
`diag(alpha_B kappa Q_p,identity_Maxwell)` on equation rows. The
ordinary null Einstein symbol cohomology has two metric and two photon classes
and injects into Weyl--Maxwell with a two-dimensional additional metric
cokernel.

The subsequent `EINSTEIN_MAXWELL_CHEVRETON_TANGENT` certificate closes the
complete lower-order comparison **on shell**. The Einstein--Maxwell
Bach/Chevreton defect is quadratic in `nabla F`, while the aligned product
flux is parallel. Its value and first variation therefore vanish, and the
certified coupling tuning makes every complete linearized
Einstein--Maxwell solution a complete linearized Weyl--Maxwell solution with
the same `(h,a)`. The graviton-plus-photon tangent sector thus survives before
the residual quotient. E-D2 must still construct the curved off-shell
equation/identity row maps, cyclic pairing, magnetic-bundle patching,
presymplectic comparison, and prolonged fourth-order characteristic complex.
Nonlinear closure is not certified; the first possible Chevreton obstruction
is at second order.

That second-order test is now partially closed by
`EINSTEIN_MAXWELL_SECOND_ORDER_INCLUSION_TEST`. On the compact product at
fixed magnetic flux, the constant radion and Maxwell duality tangent have
explicit constant-lapse adjoint pairings, so no periodic second-order
correction exists. Both become extendible when their required magnetic-flux
shift is admitted. On the universal cover, a null radiative tangent has
nonzero pure-null `C_Ch^(2)` and nevertheless admits an explicit local metric
correction. The result is therefore charge- and tangent-dependent: it is
neither general nonlinear closure nor a general no-go. E-D2 should next test
periodic nonzero-frequency graviton and photon harmonics at fixed electric and
magnetic charges.

The photon half of that gate is now closed for one explicit physical mode by
`EINSTEIN_MAXWELL_PERIODIC_PHOTON_SECOND_ORDER`. The smooth axisymmetric
`l=1` mode

```text
a1=cos(2t)cos(theta)dx,
h1=2cos(2t)sin(theta)^2 dx dphi
```

solves the complete coupled linearized Einstein--Maxwell equations and has
zero first-order electric and magnetic charge variations. Its nonzero
Chevreton coefficient has normalized sphere-averaged `tt` component `-8/3`,
while the quadratic Weyl--Maxwell `tt` projection has normalized average
`-16/3`. The constant-lapse adjoint witness therefore excludes every smooth
periodic second-order correction at fixed charges. This proves a physical
nonzero-frequency obstruction, not a general photon no-go. E-D2 should next
test one periodic helicity-two harmonic.

That remaining compact mode gate is now closed for one declared branch by
`EINSTEIN_MAXWELL_PERIODIC_GRAVITON_SECOND_ORDER`. The smooth odd-parity
`l=2` metric harmonic and its flux-forced Maxwell dressing obey

```text
H''+6H+2q=0,
q''+6q+6H=0,
```

with `omega^2=6+/-2sqrt(3)`. The certified plus branch is non-gauge, has zero
first-order electric and magnetic charge variations, and has normalized
quadratic `tt` source pairing `-(12/5)(6+5sqrt(3))` at `t=0`. The constant
lapse therefore excludes every smooth periodic second-order correction for
that branch at fixed charges. This is a compact `l=2` representative of the
local metric/helicity-two sector, not an asymptotic helicity theorem and not a
classification of the minus branch. The next gate is paper assembly.

## Work package E-D3: observables, charges, and scattering

Compare the selected sector with Einstein gravity by constructing explicit
maps of phase spaces and observables.  Determine whether it reproduces:

- Einstein radiative phase space and helicity states;
- Bondi shear and news;
- ADM and Bondi energy-momentum;
- BMS and soft-graviton charges, memory, and flux laws;
- the Einstein covariant symplectic form;
- tree-level three- and four-point helicity amplitudes;
- factorization and unitarity on the selected external states.

For every extra Weyl mode classify it as excluded, pure gauge, non-radiative,
zero norm, negative norm, logarithmic/generalized, or an additional scattering
channel.  Supply the relevant cocycle, norm, charge, or amplitude; do not infer
its status from the closed-cylinder disappearance of one-particle residual
cohomology.

Compute whether the boundary time-translation charge agrees with ADM/Bondi
energy on the selected sector.  A nonzero agreement means \(D\) is a physical
symmetry there, even if its compact-cylinder counterpart was gauged.

## Work package E-D4: Lorentzian dS and AdS

Repeat the causal and symplectic analysis for:

1. Lorentzian dS with past/future conformal boundaries and a declared patch;
2. global Lorentzian AdS with reflecting, transparent, and any admissible mixed
   boundary conditions considered separately.

For each choice identify the generator corresponding to \(D\), calculate its
charge, and determine whether it is proper gauge, a physical Hamiltonian, or
sector-dependent.  Prove real-time preservation of the Einstein selection and
compatibility with the symplectic flux.  Euclidean AdS determinants or EAdS/dS
continuations are cross-checks only; they are not causal certificates.

Track boundary gravitons, normalizable versus non-normalizable modes, alternate
quantizations, zero modes, and possible logarithmic branches.  Do not select a
sector solely by imposing conditions at both temporal ends unless the resulting
problem has an explicit causal interpretation.

## Scalar-clock challenge

Add a conformally coupled scalar clock before Yang--Mills.  Determine whether
total \(D\) remains a constraint on compact slices while boundary time
translation remains charged, and construct relational observables

\[
\mathcal O_A(\tau)=\text{``the value of }A\text{ when }T=\tau\text{.''}
\]

Check clock monotonicity, gauge invariance, boundary falloffs, scalar flux, and
the total symplectic form.  This rail must distinguish “relational evolution
with a zero total constraint” from “evolution generated by a nonzero asymptotic
Hamiltonian.”

### Constant compensator is not the shared clock

The separate certificate
`bridge/certificates/compensator_einstein_phase.json` proves that a Weyl
Stueckelberg scalar in the constant frame `phi=v!=0` generates an
Einstein-Hilbert coefficient and repairs the flat TT Einstein-root pairing.
It also proves that the gauge-fixed theory remains Einstein--Weyl, with an
opposite-residue massive spin-2 branch.

Do not register that result as `compact_scalar_clock`.  A constant compensator
is not monotone and supplies no relational time.  The classical team's
`SCALAR_CLOCK_VERTICAL_SLICE` certificate is now imported by the compensator
certificate: it proves local clock charts but obstructs a nonzero homogeneous
one-scalar clock on the exact vacuum cylinder.  The classical team has since
passed `BACKREACTED_OR_COMPOSITE_CLOCK_MODEL` in the distinct homogeneous
neutral two-field sector, with internal signature `(+,-)` and scoped verdict
`D_GAUGE`.  The current shared gate is
`FULL_NEUTRAL_CLOCK_PAIR_BV_COMPLETION`; any later total `D` calculation must
continue to import the classical action and BV data by hash.

## Generalization programme

Begin this rail after the current paper-improvement investigation and its
immediate certificate repairs are frozen.

Promote Einstein-sector results through these levels:

```text
G0  explicit tangent or obstruction fixture
G1  complete harmonic/invariant sector on one background
G2  full linearized on-shell/BV comparison on one background
G3  geometric background and charge-sector theorem
G4  nonlinear causal preservation of the Einstein sector
G5  asymptotic observables and scattering equivalence
```

The radion, duality, null, and periodic-mode calculations are exact `G0/G1`
results.  They establish sector dependence, not a general Einstein--Maxwell
classification.

### Work package E-G1: harmonic obstruction theorem

On the compact product background, classify every periodic graviton and
photon harmonic in every allowed electric/magnetic charge sector.  Compute

\[
L\Phi_2=-\frac12D^2E[\Phi_1,\Phi_1]
\]

and return an explicit correction or adjoint-cokernel witness.  Derive exact
selection rules in frequency, angular momentum, polarization, and charge.

### Work package E-G2: geometric Chevreton inclusion theorem

Generalize the linear inclusion from the product fixture to a declared class
of Einstein--Maxwell backgrounds.  Determine whether parallel flux, product
geometry, algebraic curvature type, and the coupling relation are necessary
or sufficient for the Chevreton defect and its first variation to vanish.
Give a theorem for the maximal class reached and a counterexample immediately
outside it.

### Work package E-G3: charge-sector nonlinear stability

Promote the fixed/variable flux examples to a theorem over charge fibres.
Identify whether each obstruction is a Taub moment map, a boundary/flux
constraint, or another adjoint cokernel.  Then compute the first third-order
or mixed-harmonic obstruction needed to distinguish a second-order pass from
formal nonlinear closure.

### Work package E-G4: open background classes and scattering

Repeat the comparison on conformally Einstein and Bach-flat globally
hyperbolic backgrounds, Lorentzian dS/AdS, and the asymptotically flat full
Bach phase space.  Only after causal and boundary closure compare Bondi news,
ADM/Bondi energy, soft charges, and tree amplitudes.

### External bridge E-X: make the result legible to adjacent programmes

Build explicit bridges to Maldacena boundary selection, Lü--Pope critical
gravity, and Einstein--Maxwell/Chevreton work.  Each bridge must include:

1. matched action, coupling, boundary, flux, and symplectic conventions;
2. exact reproduction of one benchmark solution, mode, or charge;
3. the present inclusion/obstruction result translated into their variables;
4. one new consequence they can test without accepting the (D)-quotient.

Examples include whether a Maldacena-type boundary condition is Lagrangian
and causally preserved in Lorentzian signature, whether critical log modes
survive Taub and flux constraints, and whether the Chevreton second-order
obstruction classifies a broader family of parallel-flux backgrounds.  State
clearly that Euclidean branch selection is not Lorentzian causal closure and
that boundary exclusion is not gauge quotienting.

## Common background matrix

Complete every cell established by your work; write `OPEN`, `NOT TESTED`, or
`NOT APPLICABLE` rather than extrapolating.

| Setting | \(D\) charge | Cartan contraction | Causal homotopy | One-particle sector | Pairing | Einstein sector |
|---|---|---|---|---|---|---|
| Vacuum cylinder | known target; boundaryless scope | known target | proved baseline | zero in stated absolute residual complex | \(I_2\) on centered degree-four classes | proper solution sector |
| Cylinder + scalar clock | open | open | open | open | open | open |
| Positive Berger clock | `D_GAUGE` on fixed-coupling linearized phase space | minimal clock SDR and retained `q1` complete; arity two open | principal endpoint factors only; curved/Green gates open | open | minimal cyclic pairing exact | `NOT_APPLICABLE` at this base point: certified non-Einstein Weyl--matter branch |
| Cylinder + Yang--Mills | open | open | open | open | open | open |
| Weakly deformed background | open | open | open | open | open | stability open |
| Lorentzian dS/AdS | boundary-dependent; compute | open | open | open | open | selected sector to certify |
| Asymptotically flat | `PHASE_SPACE_NOT_CLOSED`; `H_ESU` crosses fixed \(\mathscr I\), `D_M` charge open | `NOT APPLICABLE` until a boundary-preserving generator and phase space are chosen | formal triangular seed only; causal complex open | `OPEN` | `OPEN` | `EINSTEIN_OPEN`; reduced `chi=0` seed only |

## Priority and stop/go decisions

1. Complete the asymptotically flat linear causal complex and boundary phase
   space.
2. Choose a real boundary-preserving image, then compute its charge separately
   from the ADM/Bondi time-translation charge and radiative pairing.
3. Prove or refute linear causal preservation of the Einstein branch.
4. Classify the extra radiative branch and its norm.
5. Compare Bondi observables and tree amplitudes.
6. Seek a different common scalar background for an Einstein--matter tangent
   comparison; retain the Berger clock as the certified non-Einstein control
   branch.  Add Yang--Mills only after that distinction is stable.

Escalate immediately if the Einstein selection is nonlocal or future-dependent,
if a negative-norm radiative mode is unavoidable, or if the selected sector
fails to reproduce the Einstein symplectic/charge structure.  These are
successful counterexample results.

## Required handoff

Deliver one human-readable report and machine-readable certificates containing:

- the `G0`--`G5` generality level and exact evidence for every promotion;
- the adjacent-work convention dictionary, reproduced boundary/mode/charge
  benchmark, and the new consequence stated in that programme's variables;
- exact field/ghost spaces, falloffs, boundary and corner conditions;
- operator domains, support properties, and retarded/advanced Green checks;
- covariant phase-space charge, flux, integrability, and charge-algebra data;
- radiative cohomology representatives and exact/symbolic pairing matrices;
- local causal Einstein-sector constraints and propagation witnesses or no-go
  certificates;
- observable, Bondi, soft, and amplitude comparison maps;
- the strongest attempted counterexample in every setting;
- hashes, provenance, exact commands, elapsed times, and test tiers;
- explicit assumptions, open fields, and fail-closed flags;
- one verdict per setting: `D_GAUGE`, `D_CHARGED`, `SECTOR_DEPENDENT`, or
  `PHASE_SPACE_NOT_CLOSED`, plus `EINSTEIN_CAUSAL`,
  `EINSTEIN_NONCAUSAL`, or `EINSTEIN_OPEN`.

Every material result must carry at least one exact dependency tag:
`LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`, `REDUCED-MODE`, or
`LORENTZIAN-CAUSAL`.  Only an explicit `LORENTZIAN-CAUSAL` certificate may
support causal propagation or scattering claims.

## Cross-team contribution contract

Submit new results through the generator and phase-space registries in
[`d_quotient_programme/`](../d_quotient_programme/README.md).  In particular,
keep `H_ESU`, `D_M`, `D_rad`, and `P_0` in distinct ledger rows unless an
explicit phase-space-preserving intertwiner has been certified.
