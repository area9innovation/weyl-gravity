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

## Shared relative-complex assignment

Use the canonical Einstein--Weyl spine in
[`universe-building-roadmap.md`](universe-building-roadmap.md).  The Einstein
team owns `EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1`, the authoritative
linear input for all other teams.

For each declared background, charge fibre, boundary condition, and global
mode domain:

1. construct \(\iota:\mathcal E_{\rm Einstein}\to\mathcal E_{\rm Weyl}\) on
   fields, ghosts, antifields, equations, and Noether identities;
2. decide whether it is an injective off-shell chain map, only an on-shell
   solution map, or obstructed, retaining the normalized chain-map defect;
3. construct the mapping cofiber regardless of whether a strict quotient
   bundle exists, and compute its cohomology in generic axial, polar,
   exceptional, global, and boundary sectors;
4. compare \(\Omega_{\rm Einstein}\), \(\iota^*\Omega_{\rm Weyl}\), and the
   cofiber form using the direct action/Lee--Wald current and all required
   boundary terms; and
5. package the quadratic extension bilinear
   \(\mathfrak O_2:H_{\rm Einstein}^{\otimes2}\to H(\operatorname{Cone}\iota)\)
   across fixed and variable charge fibres, with exact witnesses.

Use `STRICT_SHORT_EXACT_SEQUENCE` only after off-shell injectivity and global
domain closure are proved.  The already certified complete on-shell inclusion,
including curvature and background-flux mixing, is valuable but remains
`ONSHELL_MAP_ONLY` until that gate passes.  This relative theorem should be the
organizing spine of the Einstein-sector paper rather than an appendix assembled
from isolated mode results.

Use the shared row format:

| Setting | Map \(\iota\) | Cofiber | Relative pairing | \(\mathfrak O_2\) | Residual action | Observable map | Quantum lift |
|---|---|---|---|---|---|---|---|
| Explicit background/sector/boundaries | computed disposition | computed status | direct-current verdict | computed status | exported dependency | exported dependency | exported dependency |

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

Construct the reusable obstruction bilinear

\[
\mathfrak O:
H^0_{\rm lin}\times H^0_{\rm lin}\longrightarrow\operatorname{coker}L
\]

and identify its relation to the Taub moment map. The theorem must state how
the domain and cokernel change between fixed electric/magnetic charge fibres
and the phase space allowing the corresponding charge variations. Treat the
existing radion, duality, photon, graviton, and null calculations as fixtures
for this classification rather than as the theorem itself.

The first restricted object is now certified by
`EINSTEIN_MAXWELL_OBSTRUCTION_BILINEAR_G1`. On the declared compact span of
the radion, duality, `l=1` photon, and plus-branch `l=2` gravitational
fixtures, the constant-lapse component is the symmetric diagonal form

```text
diag(-2,-1/2,-16/3,-12sqrt(3)-72/5).
```

The `R,D` mixed entry is zero by direct full-tensor polarization; all
distinct-`ell` fixture entries vanish by `SO(3)` equivariance. Fixed magnetic
charge retains this relative Taub component, while admitting the second-order
magnetic coefficient removes it from the augmented cokernel. This is
`G1_DECLARED_FIXTURE_SPAN`, not the commissioned full harmonic theorem: the
complete `H^0_lin`, full cokernel, and every surviving equal-quantum-number
polarization block remain open.

The follow-up `COMPACT_HARMONIC_DOMAIN_AND_TAUB_DESCENT` certificate now fixes
the global domain and sharpens that charge statement.  On the rational
fixture, compact `U(1)` quantization gives

```text
N(epsilon)=2+2 epsilon^2 p.
```

Therefore a smooth family of connections on the same `N=2` bundle has `p=0`.
The augmented magnetic row belongs to an enlarged continuous de Rham-flux
family, not the same fixed-bundle phase space.  On fixed `P_N`, the obstruction
survives; electric-only variation still does not remove it at the purely
magnetic background.  The same certificate derives gauge descent and
Cauchy-slice conservation from the coupled action Noether identities, so the
fixture bilinear is now a well-defined relative Taub form on its declared
subspace of `H^0_lin` before residual quotient.  This still does not compute
the full harmonic coefficient table or full adjoint cokernel.

The next block preflight is now certified by
`COMPACT_EM_HARMONIC_AND_ADJOINT_BLOCK_PREFLIGHT`.  For the declared
homogeneous axial representative

```text
h_(x,a)=H(t)X_a^(ell,m),  a_x=q(t)Y_(ell,m),
```

the exact all-`(ell,m)` tower has

```text
K_ell=[[lambda_ell,2],[lambda_ell,lambda_ell]],
omega_+^2=lambda_ell+sqrt(2 lambda_ell),
omega_-^2=lambda_ell-sqrt(2 lambda_ell).
```

New full-tensor `ell=3,4` checks and an arbitrary-eigenvalue harmonic-identity
reduction certify the formula.  The `ell=1` minus branch is locally gauge but
its generator is nonperiodic around `S1`, so it is a retained global twist
tangent rather than a removable periodic gauge direction.  The universal
compact stabilizer projectors are time translation, `S1` translation, and
three rotations, with the electric harmonic-flux row tracked separately.
Possible additional fourth-order adjoint classes remain open.  Do not begin
bulk source enumeration until the nonzero-momentum axial and polar master
complexes, covariant symplectic matching, and blockwise extra-adjoint problem
are closed.

`COMPACT_EM_AXIAL_MASTER_COMPLEX` now closes the nonzero-`S1`-momentum part of
that gate for the complete standard axial harmonic decomposition.  After
Regge--Wheeler and Maxwell-angular gauge fixing, the `ell>=2` block has two
transverse masters with

```text
omega^2=k_n^2+lambda_ell+/-sqrt(2 lambda_ell).
```

The arbitrary-`lambda`, arbitrary-`k`, arbitrary-`omega` tensor calculation
certifies every equation and constraint.  At `ell=1`, the determinant's
`lambda-2` factor is the residual gauge vector: it is removed by periodic
gauge for nonzero Fourier modes, while the constant zero-block twist remains
because its required generator is proportional to `x`.  The master system
has a local conserved reduced current with `W=diag(lambda,2)`, but covariant
symplectic normalization is still open.  The next block is the polar/even
master complex, followed by symplectic matching and the extra fourth-order
adjoint problem.

`COMPACT_EM_POLAR_MASTER_PREFLIGHT` now supplies the complementary generic
`ell>=2` polar coefficient matrix. Retaining the first-order variation of
`sqrt(-g)` in the Maxwell divergence is essential: it produces the corrected
row

```text
(A-C)/2+K+(omega^2-k^2-lambda)U=0.
```

After the polar constraints are solved, the two masters `(K,U)` have matrix

```text
[[lambda,-2lambda],[-1,lambda]],
```

and hence the same two dispersions
`omega^2=k_n^2+lambda+/-sqrt(2lambda)` as the axial masters. An exact full
tensor `ell=2` plus-branch fixture, including the perturbed volume density,
has zero Einstein and Maxwell residuals. This remains a preflight: the
arbitrary-`lambda` full-tensor identity, exceptional polar `ell=0,1` blocks,
and covariant symplectic matching are open. Do not promote it to the full
polar theorem or begin unrestricted source enumeration yet.

The promotion `COMPACT_EM_POLAR_MASTER_COMPLEX` now replaces that preflight
for the full `ell>=2` polar tower. A column-by-column full-tensor derivation
uses only the abstract harmonic identity

```text
Y''+cot(theta)Y'+lambda Y=0
```

and proves the declared matrix for arbitrary `lambda`, `k`, and `omega`. By
`SO(3)` equivariance this is the same multiplicity-space matrix for every
`m`. The polar Regge--Wheeler gauge is complete because the tracefree tensor
harmonic has norm factor `lambda(lambda-2)/2`; the polar diffeomorphism also
shifts the axial Maxwell coefficient by `delta U=-xi` through the background
magnetic flux. Finally, the reconstruction locus `s=omega^2-k^2=0` has the
nonzero five-row minor

```text
lambda^3(lambda-2)/8,
```

so no lightlike or zero-block solution was divided away for `ell>=2`. The
polar and axial towers are therefore exactly isospectral for every
`(n,ell,m)` with `ell>=2`. Exceptional polar `ell=0,1`, covariant symplectic
matching, and extra fourth-order adjoint classes remain open; these are now
the only compact linear gates before full harmonic source enumeration.

`COMPACT_EM_POLAR_EXCEPTIONAL_COMPLEX` now closes the remaining polar
`ell=0,1` gate on fixed `P_N`. Every nonzero `ell=0` Fourier block is pure
gauge, while the generalized homogeneous block contains the radion and `S1`
circumference Jordan pairs plus constant electric charge; uniform magnetic
variation is excluded by the fixed Chern class. At `ell=1`, the invariant
master `Psi=U-K/2` has `omega^2=k_n^2+4`, while the apparent zero branch is
exactly the smooth residual diffeomorphism. The standard polar linear complex
is therefore complete for all `ell`; symplectic matching and extra adjoint
blocks are the remaining compact linear gates.

`COMPACT_EM_RADIATIVE_SYMPLECTIC_MATCHING` now closes the radiative part of
the symplectic gate.  The exact arbitrary-function second variation gives the
polar action matrix

```text
G_P=(N_lm/2)[[1,-2],[-2,2lambda]],
```

and the axial transverse-coefficient matrix
`W_A=(N_lm/2)diag(lambda,2)`.  Because the certified axial potentials enter
through the covariant curl, their action-normalized master form is

```text
G_A=(N_lm/2)W_A M_A
   =(N_lm/2)[[lambda^2,2lambda],[2lambda,2lambda]].
```

Both forms are positive for every `ell>=2`.  At `ell=1` they become rank one
with exactly the respective residual gauge branch as kernel, leaving a
positive quotient kinetic form.  A direct full Lee--Wald calculation retains
arbitrary symbolic `k` and matches both parities without a global cylinder
boost.  On the closed Cauchy surface their Wronskians
equal the integrated Einstein--Maxwell Lee--Wald form; fixed-bundle Maxwell
variations are global one-forms, so no Cech corner term occurs.  This also
corrects the provisional polar `Psi` weight to bracket weight `4`, or
`2N_1m` after the common factor.

This is kinetic positivity, not yet a one-particle Hilbert norm; the latter
requires a declared positive-frequency complex structure.

Do not infer a Weyl--Maxwell symplectic embedding from this result alone.  The
homogeneous `ell=0` and axial `ell=1` twist pullbacks have now closed in the
complete standard-harmonic theorem below.  The remaining compact target gate
is the complementary fourth-order adjoint block.

`COMPACT_EM_EXCEPTIONAL_GLOBAL_SYMPLECTIC` now closes the remaining global
pairing gate on the generalized zero-frequency space.  For

```text
K=a+b t,
C=a t^2+(b/3)t^3+c+d t,
A_x=W_x+Q_e t,
```

the exact form is

```text
Omega_ell0
 = -2 pi L[da wedge db+da wedge dd-db wedge dc
            +2 dQ_e wedge dW_x].
```

It has rank six.  The named radion and circumference labels mix: with
`beta=b+d`, the gravitational block is
`-2piL da wedge d beta+2piL db wedge dc`.  The field-strength-invisible flat
holonomy `W_x` is the canonical partner of electric charge and does not alter
`c1(P_N)`.

For every real axial `ell=1` harmonic, the constant twist `A_m` and its
time-linear generalized solution `B_m t` form the block

```text
Omega_twist=2L N_1m dA_m wedge dB_m.
```

Thus the standard fixed-bundle Einstein--Maxwell harmonic symplectic phase
space is now complete before final residual quotient.  This statement permits
polynomial-in-time Jordan solutions; a bounded-in-time phase space would be a
different theorem.  The next compact gate is the Weyl--Maxwell Lee--Wald
restriction on radiative and global blocks separately.

`EINSTEIN_MAXWELL_WEYL_SYMPLECTIC_PREFLIGHT` now freezes that gate as a
linear tangent restriction, not a nonlinear solution-space pullback.  The
distinction is mandatory because linear on-shell inclusion is complete while
fixed-flux second-order extension already fails for declared tangents.

The same preflight closes quotient injectivity.  If an Einstein class becomes
target `Diff x Weyl x U(1)` gauge, subtracting its common `Diff x U(1)` part
leaves `(h_ab,a_a)=(2 sigma gbar_ab,0)`.  The linearized Einstein--Maxwell
rows imply

```text
-3 Delta_S2 sigma+2 sigma=0.
```

Since `Delta_S2 Y_lm=-ell(ell+1)Y_lm`, every coefficient is multiplied by
`3 ell(ell+1)+2`, so smoothness forces `sigma=0`.  The induced linear tangent
quotient map is therefore injective.  Target Weyl gauge cannot explain a
vanishing restriction; any degeneration must instead come from the
Weyl--Maxwell Lee--Wald pairing itself.  The calculation must retain full
background-flux metric/potential mixing, reproduce the flat zero-gravitational
restriction control, and evaluate the radiative, physical `ell=1`, rank-six
homogeneous, and axial-twist blocks separately.

The first restriction kill test is now exact.  For the axial
`ell=2,m=0` representative at arbitrary periodic momentum `k`, the literal
Weyl--Maxwell curvature-momentum current gives

```text
omega_WM^t
 =-8 i pi omega (k^2-omega^2)
   [9 H^2 k^2-9 H^2 omega^2+51 H^2-Q^2]/5.
```

The independent Einstein--Maxwell current is

```text
omega_EM^t=8 i pi omega(3H^2+Q^2)(k^2-omega^2)/5.
```

On the two physical `lambda=6` branches, their exact ratios are

```text
r_+=1+3 sqrt(3),
r_-=1-3 sqrt(3).
```

Both are nonzero, so the axial `ell=2` restriction is nondegenerate; but the
factors differ and have opposite signs.  Therefore the identity tangent
inclusion is already not a single action-normalized symplectic copy of
Einstein--Maxwell on this scoped block.  This is a pairing statement, not a
solution or gauge-removal statement.  The current engine reproduces the
Einstein--Maxwell Lee--Wald current pointwise, the certified Bach convention,
the flat TT zero restriction, a pure-Weyl gauge kernel, and exact current
conservation.

The arbitrary-`ell` axial restriction is now also exact.  A direct current
with arbitrary `Y(theta)`, reduced only by the harmonic ODE and a certified
pole-vanishing total derivative, gives

```text
G_EM,A(lambda,mu)=diag(lambda,2),
G_WM,A(lambda,mu)=diag(lambda(3mu-3lambda+1),2),
mu=omega^2-k^2.
```

On the two physical branches this yields

```text
r_+=1+(3/2)sqrt(2lambda),
r_-=1-(3/2)sqrt(2lambda).
```

For every `lambda=ell(ell+1)>=6`, both factors are nonzero and have opposite
signs.  Thus the complete regular axial `ell>=2` restriction has rank two in
each harmonic block and relative signature `(1,1)`.  The result is not a
finite-`ell` interpolation and the old `ell=2` fixture is reproduced exactly.
At `ell=1`, the formal minus row has `mu_-=0`, matching the certified nonzero
momentum gauge degeneration; this does not compute the separate physical
`ell=1` or global `n=0` twist representatives. Those exceptional blocks are
computed directly below rather than by continuation.

The complete regular polar restriction is now exact as well. With
`mu=omega^2-k^2`, the arbitrary-harmonic direct current and solved quadratic
normal form give

```text
G_EM,P=[[1,-2],[-2,2lambda]],
G_WM,P=[[4(mu-lambda),5lambda-4mu],
        [5lambda-4mu,4(mu-lambda)]].
```

On the two physical polar branches, the exact relative factors reduce to the
same values as in the axial parity:

```text
r_+=1+(3/2)sqrt(2lambda),
r_-=1-(3/2)sqrt(2lambda).
```

Hence every standard polar `ell>=2` block is nondegenerate with relative
signature `(1,1)`, and axial--polar isospectrality extends to the on-shell
relative weights. The off-shell matrices remain different. The apparent
`mu=0` reconstruction hole is closed by the independent full-rank minor
`lambda^3(lambda-2)/8`, so it contains only the zero gauge-fixed field for
`lambda>=6`. Physical `ell=1`, homogeneous, and twist blocks are closed by
separate direct currents below; extra fourth-order target blocks remain open.

`EINSTEIN_MAXWELL_WEYL_STANDARD_HARMONIC_SYMPLECTIC_INCLUSION` now assembles
the full fixed-bundle standard tangent.  The direct homogeneous current is
conserved coefficientwise on the complete polynomial representatives and has
rank six.  Relative to the Einstein--Maxwell form its endomorphism is

```text
R=I+N,  rank(N)=2,  N^2=0,
```

with the explicit determinant-one shear `S=I+N/2` satisfying
`S^T Omega_EM S=Omega_WM`.  The flat `S1` holonomy `W_x` is retained.  Each
real axial twist pair is also nondegenerate and obeys

```text
Omega_WM|twist=-2 Omega_EM|twist.
```

This twist identity comes from the direct `A+B t` current, not a formal
`mu->0` radiative limit.  Combining these global blocks with standard
`ell>=2` radiation and physical `ell=1` gives zero target-pullback kernel on
the complete certified standard Einstein--Maxwell tangent before the final
residual quotient.  It does not make the identity inclusion symplectic or
classify the complementary fourth-order Weyl--Maxwell solutions.

The mixed-block audit is now direct at the sole shared-label collision.  For
the axial twist against the physical axial `ell=1,n=0` oscillator,

```text
int_S2 omega_WM^t
 = -2 i pi omega p (omega^2-4)
   [omega(A+B t)-iB] exp(-i omega t),
```

so both the constant twist and its Jordan partner are orthogonal on the
physical shell.  All other standard cross blocks vanish by harmonic, Fourier,
parity, or distinct-master-eigenvalue orthogonality.

`EINSTEIN_MAXWELL_WEYL_EXTRA_BRANCH_PREFLIGHT` freezes the next object as the
canonical quotient `Q_extra=H^0(C_WM^full)/i_*H^0(C_EM^std)`.  It forbids
defining the extra sector by an arbitrary complement and keeps solution
classes, adjoint cokernels, presymplectic radicals, and gauge classes separate.
The first solve is the complete generic axial target block at symbolic
`lambda,k`, including its full Einstein/extra Lee--Wald matrix.

`EINSTEIN_MAXWELL_WEYL_AXIAL_OPERATOR_MODULE_PREFLIGHT` now freezes that first
solve over `Q[I,lambda,k][D]`, with `D=partial_t`.  For `ell>=2` the ungauged
coefficient module `(h_t,h_x,h_2,q_t,q_x,b)` contracts exactly to four
gauge-invariant coefficients.  The identities `KG=0`, `KJ=I`, `I-JK=GH`, and
`HG=I` hold with only the constant denominator `2`; neither `D` nor `k` is
inverted.  The target Hessian must next pass independent equation, Noether,
formal-adjoint, off-shell Green, source-image, pivot-stratification, and full
tensor `Y_20` replay rails before any frequency root is interpreted.

`EINSTEIN_MAXWELL_WEYL_AXIAL_OPERATOR` now closes the operator, Noether,
formal-adjoint, source-image, Smith-module, and independent full-tensor rails.
The direct `Y_20` coordinate replay retains arbitrary off-shell `(omega,k)`,
all unlisted rows vanish, and exact `ell=3,4` samples uniquely reconstruct the
degree-at-most-two `lambda` dependence.  Over
`F[omega]`, `F=Frac(Q(lambda,k))`, the target invariant factors are

```text
1, 1, p, p*q,
p=omega^2-k^2-lambda+2/3,
q=(omega^2-k^2-lambda)^2-2lambda.
```

Here `q` is the certified Einstein--Maxwell master factor.  The polynomial
identity `P_W=(3lambda-2-3s)E_EM-6M_EM`, with
`s=omega^2-k^2`, replays the complete Einstein image.  Away from the
nonphysical collision `lambda=2/9`, the canonical generic axial quotient is
therefore

```text
Q_extra_ax=(F[omega]/(p))^2.
```

This proves two additional algebraic target solution polarizations before the
final residual quotient; it does not certify two particles or ghosts.  At
this operator stage the direct four-dimensional action Hessian and complete
Einstein/extra Lee--Wald matrix remained open.  The later Lee--Wald completion
below now proves nonradicality and the compact classical signs; the
action-density cross-check and one-particle interpretation remain open.

`EINSTEIN_MAXWELL_WEYL_AXIAL_GREEN_CURRENT` now closes the off-shell local
Green-identity rail on both the four invariant coefficients and the six-field
ungauged lift.  A coefficientwise multivariate Lagrange construction gives
explicit `J^t,J^x` satisfying

```text
partial_t J^t+partial_x J^x=u^T L v-(L u)^T v
```

for arbitrary off-shell jets, without using a dispersion relation or
inverting `D`, `k`, or `omega`.  This is not a Green-function or causal
propagator theorem.  At this stage the direct four-dimensional Lee--Wald
comparison and the action-density Hessian were the remaining local pairing
gates; the former is completed below.

`EINSTEIN_MAXWELL_WEYL_AXIAL_EXTRA_GREEN_PAIRING` evaluates the certified
local current on the two extra representatives.  With
`N_extra=J^t/(-i*omega)`, its determinant reduces on the extra shell to

```text
lambda^4*(lambda-2)*(9lambda-2)/3.
```

The first principal minor and determinant are positive for every physical
`lambda>=6`.  Hence the generic extra module is nonradical, with signature
`(2,0)`, in the reduced-Hessian Green convention.  This is not yet the direct
four-dimensional Lee--Wald norm: the action-Hessian/current match remains the
last barrier before any physical sign or ghost interpretation.

`EINSTEIN_MAXWELL_WEYL_AXIAL_LEE_WALD_COMPLETION` now matches the complete
off-shell reduced current to the directly varied four-dimensional
Weyl--Maxwell Lee--Wald current.  Exact `ell=2,3,4` coordinate matrices retain
independent frequencies and satisfy

```text
integral_(S2) J^t_4D=N_(ell,m) J^t_reduced,
N_(ell,m)>0.
```

The spectral degree-two bound and `SO(3)` irreducibility promote this to every
`ell>=2,m`.  Both Einstein/extra mixed blocks vanish directly on their exact
primary shells, without a frequency inverse.  In the normalized direct-current
convention the Einstein branches have signature `(1,1)`, the two extra
directions have `(2,0)`, and the complete generic axial target has `(3,1)`.

Therefore the extra directions do not disappear under the direct compact
Lee--Wald pairing and are not its negative direction.  The negative target
direction lies on one Einstein-image master branch.  This is not yet a
one-particle ghost theorem: final residual descent, causal boundary
admissibility, a positive-frequency Hilbert space, and quantum unitarity remain
open.

Keep three forms separate.  `Omega_EM` is the source form obtained from the
independent Einstein--Maxwell action.  The pullback `iota^*Omega_WM` is the
Weyl--Maxwell form evaluated on the Einstein image; relative to `Omega_EM` its
two regular branches carry factors
`1 +/- (3/2)sqrt(2lambda)`, so the identity inclusion is not symplectic.
Finally, `Omega_WM` on the full target adds the orthogonal extra block and has
signature `(3,1)`.  The negative sign is therefore a classical target-current
sign, not an automatic negative norm in the independent Einstein--Maxwell
theory and not a quantum ghost certificate.

`EINSTEIN_MAXWELL_WEYL_AXIAL_REDUCED_ACTION_HESSIAN` now reconstructs the
exact reduced quadratic Fourier action from the certified self-adjoint
operator. Its mixed Hessian equals the operator, which generates the local
Green current already matched to the direct four-dimensional Lee--Wald
current. This closes the reduced normalization triangle. It does not replace
the still-open literal second expansion of the four-dimensional action
density.

`EINSTEIN_MAXWELL_WEYL_AXIAL_EXTRA_DETECTOR` uses the inverse extra Lee--Wald
Gram matrix to define two conserved reduced-mode coefficient observables.
They return the two extra coordinates exactly and annihilate the complete
certified generic axial Einstein image. Final `SO(4,2)`, relational, causal,
and asymptotic descent remain open.

The scoped compact linear manuscript is now assembled at
paper/10-compact-einstein-maxwell-weyl-phase-space.tex. It states the
complete standard Einstein--Maxwell harmonic inclusion theorem and the
complete generic axial extra-branch theorem in one narrative, while keeping
the polar extra branch, final residual descent, literal four-dimensional
action-density expansion, nonlinear closure, causal scattering, and quantum
ghost interpretation explicit as nonclaims. Its fail-closed input ledger is
paper/10-compact-einstein-maxwell-weyl-phase-space-claim-map.json.

The first quadratic self-extension test is now exact on the full real
`ell=2,k=0` extra span. With

```text
e_1=(-6,0,6,0), e_2=(0,-2/3,0,6), omega^2=16/3,
```

the Hermitian mode-plus-conjugate source has constant-lapse Taub matrix

```text
T_X=diag(-1728/5,-832/45).
```

It is negative definite. Fixed bundle topology forces the second-order
magnetic coefficient to vanish, so every nonzero real combination has a
nonzero adjoint-cokernel pairing and admits no smooth periodic second-order
correction at fixed electric and magnetic charges. The extra block therefore
exists and is measurable at the linear level but is linearization-unstable on
this declared compact fixture. This does not classify generic `ell`, nonzero
`k`, varying charge fibre, or causal/asymptotic extra branches. Quadratic
source projection must also respect parity: the present axial-by-axial `XX`
source is even and is detected by the scalar constant-lapse class.

The nonlinear-projection preflight now separates three objects that must not
be conflated. `EINSTEIN_MAXWELL_WEYL_TARGET_CONSTANT_LAPSE_ADJOINT_WITNESS`
extracts the fixed-bundle constant-lapse target cokernel class independently
of any named Einstein fixture and records that its constraint pairing is
unchanged by allowing secular time dependence. The separate
`EINSTEIN_MAXWELL_WEYL_AXIAL_EXTRA_PROJECTOR` is the exact rank-two shell map

```text
Pi_X=E_X D_X,   Pi_X^2=Pi_X,
```

which is invariant under `E_X -> E_X S`, `D_X -> S^(-1)D_X`, fixes the extra
image, and kills the certified Einstein image. It is only a normal-mode shell
projector, not an off-shell or nonlinear projection.

`EINSTEIN_MAXWELL_WEYL_AXIAL_QUADRATIC_CHANNEL_PREFLIGHT` then imposes the
correct parity channel: axial target data from two Einstein modes require an
axial-by-polar `EE` input, not axial-by-axial. An exact squarefree-radical scan
of 97,848 branch/sign cases with `2<=ell_A,ell_P,ell_X<=8` and
`|k_A|,|k_P|<=4` finds no exact axial-extra temporal resonance. For the lowest
allowed `ell_A=ell_P=ell_X=2`, `m_A=m_P=m_X=0`, `k_A=k_P=0` minus-branch sum
channel, both target factors are nonzero and the full four-by-four target
Hessian has an exact displayed inverse. Hence every source vector in this one
output block has a unique algebraic second-order correction. A nonzero defect
in this block would therefore be removable, not a Taub obstruction. The mixed
full-tensor replay has now evaluated all four independent gauge-fixed axial
rows. In the density-weighted
`(lambda metric_t,-lambda metric_x,Maxwell_t,Maxwell_x)` order its
source is

```text
(0,-72(-187+111 sqrt(3))/7,0,-24(-17+5 sqrt(3))/7),
```

and the exact correction is

```text
(H_t^(2),H_x^(2),Q_t^(2),Q_x^(2))
=(0,-4(-1+2 sqrt(3))/21,0,4(5 sqrt(3)+24)/21).
```

The target remainder is exactly zero. Thus the first explicit parity-correct
`EE` component is nonzero but removable; it does not create an extra
homogeneous normal mode.

The Hermitian completion now decides the fixed-bundle real-tangent question
without computing every remaining output block. For

```text
Phi^(1)=Re[(z_A Phi_A+z_P Phi_P) exp(-i omega t)],
omega^2=6-2 sqrt(3),
```

the exact averaged Chevreton and full Weyl--Maxwell cosine-amplitude matrices
are respectively

```text
C_Ch^(2)=diag(144(-1+sqrt(3))/5, 48(-3+2sqrt(3))/5),
T_H=diag(48(-6+5sqrt(3))/5, 24(-11+7sqrt(3))/5).
```

Both mixed entries vanish directly, as required by axial--polar parity. Slice
conservation and time-translation invariance lift `T_H` to the four real
cosine/sine quadratures by repeating each diagonal entry. Since
`5 sqrt(3)>6` and `7 sqrt(3)>11`, this real Taub form is positive definite.
The fixed compact bundle forbids the magnetic second-order lift, so every
nonzero real combination of this degenerate axial--polar minus pair is
obstructed. The removable `AP` sum-frequency block and this real-tangent
no-go are therefore consistent: the obstruction comes from the conjugate
self-products in the zero-frequency scalar channel. The even `AA` and `PP`
outputs and other frequency blocks are no longer needed for this fixed-bundle
no-go, but remain necessary for a charge-relaxed extension theorem. This is
still not an all-harmonic or causal nonlinear Einstein-sector theorem.

### Work package E-G4: open background classes and scattering

Repeat the comparison on conformally Einstein and Bach-flat globally
hyperbolic backgrounds, Lorentzian dS/AdS, and the asymptotically flat full
Bach phase space.  Only after causal and boundary closure compare Bondi news,
ADM/Bondi energy, soft charges, and tree amplitudes.

### Work package E-G5: asymptotic Bach/BMS phase space

Construct a closed asymptotic phase space for the Bach equation from a finite
action principle, symplectic form, and flux. Determine radiative, Coulombic,
soft, memory, corner, and extra-branch data; differentiable charges and their
algebra; and the sign of the radiative pairing. Keep \(H_{\rm ESU}\), \(D_M\),
\(D_{\rm rad}\), and \(P_0\) in separate rows. If a restricted
polyhomogeneous sector is used first, prove that evolution and the declared
asymptotic symmetries preserve it.

Report whether the extra Bach branch reaches \(\mathscr I^\pm\), whether a
causal boundary condition removes it, and whether the selected Einstein sector
reproduces Bondi news and flux. A boundary condition imposed at both temporal
ends is not causal closure without an independent well-posedness theorem.

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

Frame the resulting paper as a Lorentzian and nonlinear complement to
Einstein-from-conformal boundary selection, not as a refutation of the
Euclidean or on-shell result. Use
the adjacent-work portfolio in
[`universe-building-roadmap.md`](universe-building-roadmap.md) for the staged portfolio
and [`adjacency-bridge-note-template.md`](adjacency-bridge-note-template.md)
for each external comparison.

## Common background matrix

### 2026-07-17 Paper A referee repair: physical coefficient ring

The generic axial fraction-field Smith calculation has been narrowed to its
proper generic role.  The all-momentum theorem is now supported separately by
`EINSTEIN_MAXWELL_WEYL_AXIAL_PHYSICAL_RING` over

```text
R_phys=Q[lambda,k,lambda^-1,(lambda-2)^-1,(9lambda-2)^-1].
```

The exact unit minor `-lambda^2`, Schur factorization `Schur=p*T`, and Bezout
witness for the entries of `T` give Fitting ideals

```text
(1), (1), (p), (p^2*q).
```

No `k`, `omega`, `p`, or `q` is inverted.  Every physical
`lambda=ell(ell+1)`, `ell>=2`, and every compact momentum, including `k=0`,
therefore has fibrewise Smith factors `1,1,p,p*q` and canonical extra quotient
`(K[omega]/(p))^2`.  At `k=0` the two displayed extra representatives have
independence minor `lambda^2`.  Explicit global unimodular Smith
transformations over the multivariate ring remain unclaimed.

The module bridge is now explicit: the source axial module is
`K[omega]/(q)`, its injective image is `q`-annihilated and hence cannot have a
component in either `p`-primary summand, and its dimension `deg(q)=4` equals
the full target `q`-primary dimension.  The Einstein image is therefore the
complete `q`-primary summand, so the quotient is exactly the two remaining
`p`-summands.

`EINSTEIN_MAXWELL_CHEVRETON_FORMAL_LINEARIZATION` closes the linearization-
instability loophole in the inclusion theorem.  An arbitrary Jacobi field is
an exact Einstein--Maxwell solution over the dual numbers
`R[epsilon]/(epsilon^2)`.  Repeating the natural Bergqvist--Eriksson tensor
derivation over that algebra proves the linear Bach--Chevreton identity for
all formal linearized solutions, not only tangents to actual nonlinear
families.  This does not construct the stronger explicit off-shell BV row
factorization and makes no nonlinear closure claim.

Paper A has also been revised to name the compactified Plebański--Hacyan
fixture, display the Bach/action and on-shell Chevreton normalizations, give a
complete exceptional-stratum table, make the relative endomorphism `R` the
phase-space comparison invariant, replace symplectic ``signature'' by
positive-frequency Hermitian-current inertia, globalize the magnetic-bundle
gauge action and large-gauge holonomy, and state the three-point spectral
interpolation lemma explicitly.  This remains `CLASSIFIED`, not
`THEOREM_FROZEN`; the literal unreduced four-dimensional quadratic
action-density expansion is still an open normalization audit.

Complete every cell established by your work; write `OPEN`, `NOT TESTED`, or
`NOT APPLICABLE` rather than extrapolating.

| Setting | \(D\) charge | Cartan contraction | Causal homotopy | One-particle sector | Pairing | Einstein sector |
|---|---|---|---|---|---|---|
| Vacuum cylinder | known target; boundaryless scope | known target | proved baseline | zero in stated absolute residual complex | \(I_2\) on centered degree-four classes | proper solution sector |
| Cylinder + scalar clock | open | open | open | open | open | open |
| Positive Berger clock | `D_GAUGE` on fixed-coupling linearized phase space | minimal clock SDR and retained `q1` complete; arity two open | principal endpoint factors only; curved/Green gates open | open | minimal cyclic pairing exact | `NOT_APPLICABLE` at this base point: certified non-Einstein Weyl--matter branch |
| Cylinder + Yang--Mills | open | open | open | open | open | open |
| Weakly deformed background | open | open | open | open | open | stability open |
| Compact Einstein--Maxwell product | sector-indexed; not a universal D verdict | `OPEN` | `NOT TESTED` | no positive-frequency Hilbert space constructed | complete standard-harmonic pullback is nondegenerate: relative radiative inertia `(2,2)`, physical `ell=1` factor `4`, homogeneous unipotent shear, twist factor `-2` | every certified standard harmonic Einstein--Maxwell tangent survives before final residual quotient; identity inclusion is not symplectic |
| Lorentzian dS/AdS | boundary-dependent; compute | open | open | open | open | selected sector to certify |
| Asymptotically flat | `PHASE_SPACE_NOT_CLOSED`; `H_ESU` crosses fixed \(\mathscr I\), `D_M` charge open | `NOT APPLICABLE` until a boundary-preserving generator and phase space are chosen | formal triangular seed only; causal complex open | `OPEN` | `OPEN` | `EINSTEIN_OPEN`; reduced `chi=0` seed only |

## Priority and stop/go decisions

1. Extend the completed generic axial extra classification to the polar target
   block and perform final residual descent.
2. Extend the certified axial detector and negative-definite `ell=2,k=0`
   extra Taub test to nonzero momentum, higher harmonics, and parity-compatible
   `EE`, `EX`, and `XX` source channels; then construct a relational or
   geodesic-deviation realization of the reduced detector.
3. Complete the asymptotically flat linear causal complex and boundary phase
   space without importing the compact result as a boundary theorem.
4. Choose a real boundary-preserving image, then compute its charge separately
   from the ADM/Bondi time-translation charge and radiative pairing.
5. Prove or refute linear causal preservation of the Einstein branch, classify
   the extra asymptotic branch, and only then compare Bondi observables, black
   holes, and tree amplitudes.
6. Seek a different common scalar background for an Einstein--matter tangent
   comparison; retain the Berger clock as the certified non-Einstein control
   branch.  Add Yang--Mills only after that distinction is stable.

The regular compact radiative modes, physical `ell=1` quotient, and generalized
global modes have a certified Einstein--Maxwell covariant pairing.  The
Weyl--Maxwell pullback is closed on the complete standard axial-plus-polar
`ell>=2` block by the common spectral operator
`1+(3/2)(M-lambda)`: all such modes remain nonnull, but the relative
branch-coefficient inertia is `(2,2)` and the identity inclusion is not
symplectic.  The physical `ell=1` quotient is also closed by a separate direct
exceptional current: both gauge rows vanish and the normalized pullback is
exactly four times the Einstein--Maxwell form.  The homogeneous pullback is a
nondegenerate rank-two unipotent shear and each axial twist pair has factor
`-2`.  Thus the complete standard fixed-bundle harmonic pullback is
nondegenerate before final residual quotient, although the identity inclusion
is not symplectic.  This is not a one-particle or quantum theorem.  Extra
fourth-order target branches are the nearest compact gate; black holes and
scattering require their own boundary phase space.  The handoff criteria are
recorded in
[`universe-building-roadmap.md`](universe-building-roadmap.md).

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
