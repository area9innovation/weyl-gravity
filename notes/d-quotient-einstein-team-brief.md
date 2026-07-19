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

### Relative linear triangle preflight

`EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_PREFLIGHT` now gives an exact partial
answer. The covariant principal-symbol map has a nilpotent mapping cone, and
the complete generic axial `ell>=2` Fourier-polynomial block admits a strict
off-shell chain map on ghosts, all six ungauged fields, equations, and Noether
identities. Its equation-row lift uses only constant denominators and does not
invert `k`, `omega`, or either dispersion factor. The already classified
two-copy axial solution cofiber and its direct nonradical Lee--Wald block
therefore belong to a genuine sectoral relative triangle, not merely to an
on-shell quotient.

This does not freeze the requested V1 theorem. The lower-order curved row
maps remain open in polar, exceptional, and global sectors. Until they are
constructed or obstructed, the global cone is a defect-marked precomplex
whose square is the normalized chain-map defect; it has no certified global
cohomology and does not satisfy the quantum import gate. The generic-axial
certificate remains a preflight and must not be renamed to the full result.

### Exact V1 consumer contract

The classical importer checks only these candidate paths:

```text
bridge/certificates/EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1.json
bridge/certificates/einstein_weyl_relative_linear_triangle_v1.json
```

The selected artifact must have

```text
result_id = EINSTEIN_WEYL_RELATIVE_LINEAR_TRIANGLE_V1
claim_status = CERTIFIED | THEOREM_FROZEN |
               CERTIFIED_OFF_SHELL_LINEAR_TRIANGLE
```

and must set all six flags exactly to `true`:

```text
OFF_SHELL_CHAIN_MAP_ALL_BV_ROWS
SUPPORT_LOCAL_MAPPING_COFIBER
GLOBAL_ENDPOINTS_INCLUDED
PAIRING_OR_CURRENT_COMPATIBLE
H_PRODUCT_EQUIVARIANT
INDEPENDENT_VERIFIER_PASS
```

The artifact, schema, producer and independent verifier must be committed
together. A principal-symbol theorem, generic-axial block, on-shell inclusion,
or certificate missing any flag is rejected rather than partially promoted.
See
`notes/einstein-weyl-relative-linear-triangle-preflight.md`.

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
interpolation lemma explicitly. Following the final internal referee pass,
the scoped mathematical claims are now `THEOREM_FROZEN` and ready for
external specialist review, subject to the documented final human
accountability pass. The literal unreduced four-dimensional quadratic
action-density expansion remains an optional audit, not a freeze gate.

`EINSTEIN_WEYL_POLAR_OFFSHELL_OPERATOR_PREFLIGHT` fixes the source Diff slice
`(A,B,C,K,U)` and the target Weyl contraction `(A+K,B,C-K,U)`. Its pure-Weyl
kernel `(-1,0,1,1,0)` has sphere-tracefree Einstein row `-1`, so it contains
no Einstein solution. `EINSTEIN_MAXWELL_WEYL_POLAR_FULL_TENSOR` now closes the
next off-shell gate. Independent four-dimensional `ell=2,3,4` Bach--Maxwell
linearizations reconstruct the generic degree-two-in-`lambda` target
operator. The action-normalized four-by-four Hessian is formally self-adjoint
and satisfies the exact polynomial square

```text
H_P S_P = J_P E_P
```

without dividing by `k`, `omega`, `lambda-2`, or either characteristic. Its
determinant is

```text
(9/16) lambda^3 (lambda-2) p^2 q,
p=omega^2-k^2-lambda+2/3,
q=(omega^2-k^2)^2-2lambda(omega^2-k^2)+lambda(lambda-2).
```

Over `Frac(Q(lambda,k))[omega]` the determinantal divisors are
`1,1,p,p^2 q`, so the invariant factors are `1,1,p,p q`. Since
`Res_omega(p,q)=4(9lambda-2)^2/81`, the physical `ell>=2` locus has the same
generic primary pattern as the axial block: two extra `p` summands and the
Einstein `q` summand.

`EINSTEIN_MAXWELL_WEYL_POLAR_PHYSICAL_COMPLETION` now removes the remaining
coefficient-ring and interpretation qualifications.  Over the physical
localization

```text
R_phys^P=Q[lambda,k,
 lambda^-1,(lambda-2)^-1,(3lambda-2)^-1,(3lambda-4)^-1,
 (5lambda+6)^-1,(9lambda+2)^-1,(9lambda-2)^-1]
```

explicit Bezout combinations of the two-by-two and three-by-three minors give

```text
I1=(1), I2=(1), I3=(p), I4=(p^2 q).
```

Every localization factor is nonzero for `lambda=ell(ell+1)>=6`; `k`,
`omega`, `p`, and `q` are not inverted.  Hence every allowed compact momentum,
including `k=0`, has fibrewise invariant factors `1,1,p,p q`.  At `k=0` two
explicit extra representatives have independence minor `3(3lambda-2)`.

The source master presentation has Smith factors `1,q`, so its module is
`K[omega]/(q)`.  The polynomial square maps it into the target, the preflight
kernel theorem makes that map injective, and `q` is a unit on the two
`p`-primary summands.  Since the source and target `q`-primary dimensions are
both `deg(q)=4`, the Einstein image equals the complete `q`-primary summand.
The polar extra quotient is therefore canonically
`(K[omega]/(p))^2` on every physical fibre.

Finally, the action row weights are no longer fixed only by formal
self-adjointness.  From

```text
delta S_WM=(1/2) integral sqrt(-g)(3B-T)_ab delta g^ab
           + integral partial_a(sqrt(-g)F^ab) delta A_b
```

the inverse-metric variations give `(-1,2,-1)` for `(00,01,11)`, while
`integral X_a X^a=lambda integral Y^2` gives `2lambda` for Maxwell after the
common `2 delta S` normalization.  Thus the four-dimensional harmonic
variation derives the action weights `(-1,2,-1,2lambda)` independently.

`EINSTEIN_MAXWELL_WEYL_POLAR_LEE_WALD_GATE` now closes the direct polar
pairing gate.  The action-normalized Green current was matched entry by entry
to independent four-dimensional Lee--Wald coordinate currents at
`ell=2,3,4`; the proved degree-two spectral bound promotes the zero remainder
to every physical `ell>=2`.  The direct rail deliberately isolates each
left/right amplitude before sphere integration.  Applying the symbolic
spherical normalizer to one unsplit amplitude polynomial is not a certified
linear operation and produced a false intermediate mismatch, so that route is
now explicitly excluded.

Two polynomial `p`-shell representatives remain independent at every allowed
compact momentum, including `k=0`.  Their direct positive-frequency
Hermitian-current Gram determinant is

```text
9 lambda^2 (lambda-2) (9 lambda-2)
  (3 k^2+3 lambda-2) (6 k^2+3 lambda-2)^2,
```

so the extra polar block is nonradical with inertia `(2,0)`.  Its mixed block
with the complete Einstein `q`-primary image vanishes modulo `p` and `q`.
Together with the Einstein inertia `(1,1)`, the complete generic polar target
has pre-residual stationary-current inertia `(3,1)`, exactly matching the
generic axial pattern.  The resulting coefficient extractors are conserved
spectral functionals on the local-gauge-reduced shell, not yet residual or
Peierls observables.

`EINSTEIN_MAXWELL_WEYL_POLAR_UNGAUGED_NOETHER_LIFT` now closes the generic
polar ungauged equation/Noether and local-Green gate.  On the eight fields
`(A,B,C,h_t,h_x,K,G,U)`, three source Diff ghosts contract exactly to the five
Einstein--Maxwell slice variables, while adjoining the Weyl ghost contracts
to the four target variables.  Explicit sections and homotopies use only the
constant denominators `2` and `4`; `k`, `omega`, `p`, and `q` remain
uninverted.  Thus zero momentum and zero frequency are retained.

The source raw tensor Euler map has three polynomial Bianchi rows.  The target
action Hessian has four Noether rows, including the Weyl identity.  The
gauge-fixed equation square lifts to an exact
ghost--field--equation--identity chain map, and the target ungauged Hessian is
formally self-adjoint.  Its coefficientwise local Green current has 184
temporal and 184 spatial terms with zero off-shell jet remainder.  Restriction
to the canonical target section reproduces exactly the 32+32-term reduced
current already matched to the direct four-dimensional Lee--Wald current.

The chain map is not degreewise injective on equation/identity rows and no
cyclic BV enhancement is certified.  Hence this is not yet a strict short
exact sequence and does not satisfy the quantum classical-import gate.  The
remaining polar gate is background-stabilizer/moment-map descent; cyclic
enhancement or an obstruction to it is a distinct parallel question.  No
causal, particle, quantum-ghost, or nonlinear-closure claim is made.

`EINSTEIN_MAXWELL_WEYL_PLEBANSKI_HACYAN_STABILIZER_DESCENT` corrects the
authority boundary for that next step.  The connected automorphism algebra of
the fixed-flux compactified Plebański--Hacyan background is

```text
R H direct-sum R P_x direct-sum so(3),
```

not the `SO(4,2)` algebra of the conformally flat vacuum cylinder.  The
nonzero product Weyl tensor fixes the factor splitting, the common conformal
factor vanishes, `S1` periodicity removes the flat boost, and the magnetic
field is preserved by the five surviving generators with the standard
patchwise rotational `U(1)` compensators.  There is no Weyl compensator.

On every generic physical axial and polar fibre, the five-generator action
preserves both the Einstein `q`-primary summand and the two-copy extra
`p`-primary quotient.  It also preserves the direct Lee--Wald form.  This is
an equivariance theorem, not permission to quotient: the nondegenerate extra
blocks give explicit nonzero `H`, nonzero-`k` `P_x`, and nonzero-`m` rotation
moment-map matrix elements.  Thus the stabilizers are not universal
presymplectic-radical directions on the full generic phase space.  They remain
global symmetries until a common moment-map/Taub-zero derived sector is
constructed and a null subalgebra is proved.

Accordingly every older phrase ``final residual `SO(4,2)` quotient'' attached
to this product fixture is superseded by the sequence

```text
local gauge quotient
 -> five-generator background-stabilizer representation
 -> common moment-map/Taub-zero locus
 -> quotient only by a certified null subalgebra.
```

The vacuum-cylinder absolute `SO(4,2)` theorem is unchanged in its own phase
space.  No absolute residual CE cohomology is presently authorized for the
Plebański--Hacyan wave modules.

`EINSTEIN_MAXWELL_WEYL_MOMENT_MAP_TAUB_BRIDGE` now identifies the missing
covariant bridge.  For every background automorphism `X` and generic on-shell
tangent `u`, twice differentiating the action Noether current and integrating
over the closed slice gives, in the repository convention,

```text
<zeta_X,(1/2)D^2 E_WM[u,u]>
 = mu_X(u)
 = (1/2) Omega_WM(u,L_X u).
```

The sign and real-mode factor are not left formal.  The prediction from the
direct four-dimensional Lee--Wald current matches three independent exact
tensor Taub coefficients at `ell=2,k=0`: the complete two-dimensional axial
extra block and the axial and polar Einstein-minus fixtures.  For
`Phi=Re(c exp(-i omega t))`,

```text
mu_H=-(L N_ell_m/4) omega^2 c^dagger G c.
```

The same complex-to-real calculation gives

```text
mu_Px=(L/4) k omega c^dagger (G tensor W_ell)c,
mu_Ja=(L/4) omega c^dagger (G tensor W_ell T_a)c.
```

This also sharpens the angular selection rule: after the complete covariant
Noether sum, rotations preserve `ell` because they commute with the sphere
Laplacian.  `J_1,J_2` connect only `m` to `m+/-1` inside the same irrep; raw
adjacent-`ell` source terms cancel in the integrated charge.

The immediate nonlinear consequence is stronger than the earlier fixtures.
Both axial and polar generic extra `p`-primary Gram matrices are positive
definite for every physical `ell>=2` and compact `k`, while
`omega_e^2=k^2+lambda-2/3>0`.  Therefore the fixed-bundle constant-lapse Taub
form is negative definite on every nonzero real pure-extra generic tangent,
including finite or rapidly decreasing finite-energy superpositions.  No such
tangent extends to second order within the declared fixed-`P_N` Weyl--Maxwell
phase space.  Electric variation cannot absorb this component at the purely
magnetic background, and continuous magnetic variation belongs to a different
bundle family.

This is linearization instability of the pure-extra generic sector, not
absence of its certified linear solutions.  Mixed Einstein--extra amplitudes
remain open because the Einstein `q`-primary contribution is indefinite and
can cancel the scalar `H` component.  Exceptional/Jordan blocks and the full
common `H,P_x,J_i` zero locus also remain open.

`EINSTEIN_MAXWELL_WEYL_MIXED_MOMENT_MAP_ZERO_LOCUS` and
`EINSTEIN_MAXWELL_WEYL_BALANCED_ELL0_SECOND_ORDER` now resolve the first mixed
component.  In a single fixed nonzero-`k` travelling block, simultaneous
`H=P_x=0` is possible only for the zero tangent.  After Gram factorization the
eliminated equation is

```text
omega_plus(omega_plus-omega_minus) A_plus
 + omega_extra(omega_extra-omega_minus) A_extra = 0,
```

and both coefficients and occupations are nonnegative.  This no-go does not
cover cancellations between distinct momenta.

At `k=0`, a nonzero common-zero tangent does exist.  Take the axial
`ell=2,m=0` Einstein-minus representative with unit cosine amplitude and the
second axial extra representative with

```text
|a_extra|^2=(27/52)(5 sqrt(3)-6).
```

Its `H`, `P_x`, and all three rotation moment maps vanish.  This is additive
charge balance between the diagonal `q` and `p` primaries, not a mixed
Lee--Wald interference term.

The complete quadratic extension test passes for this tangent.  Axial times
axial produces only polar `ell=0,2,4` outputs at frequencies `0`,
`2 omega_minus`, `2 omega_extra`, and `omega_extra +/- omega_minus`.  The two
homogeneous zero-frequency sources cancel in every independent row.  Every
nonzero homogeneous channel has an explicit exact correction, and every
`ell=2,4` channel is off both target shells and is removed by the stored exact
action-Hessian inverse.  All operator remainders vanish.  Thus a complete
finite `Phi^(2)` exists for this declared real tangent.

The completeness gate is now explicit rather than interpretive.  In target
ungauged equation order `(A,B,C,h_t,h_x,K,G,U)`, stack the selectors for the
four solved action equations `(A,B,C,U)` with the four certified target
Noether identities at `k=0`.  The resulting `8 x 8` matrix has determinant
`-4`, a unit independent of `omega` and `lambda`.  Since the second variation
of `N(Phi)E(Phi)=0` reduces to `N^(0)E^(2)=0` when the background and declared
first-order tangent are on shell, all dependent polar tensor rows follow,
including at zero frequency.  The certificate also derives the real-channel
factors (`1/8` for self-sums and `1/4` for self-zero and mixed channels),
imports every polar operator/Noether dependency by hash, and checks that no
magnetic, stationary electric-charge, or Wilson-line zero-mode shift is
hidden in the correction.

This proves one mixed second-order extension, not general nonlinear closure
or integration to an exact all-orders family.  The next nonlinear target is
the full `k=0` common-zero cone, followed by opposite-momentum standing-wave
balances and the exceptional/global blocks.

Those three next layers are now separated and certified.  First,
`EINSTEIN_MAXWELL_WEYL_FULL_GENERIC_K0_MOMENT_MAP_CONE` classifies the entire
finite-harmonic generic `k=0` common-zero set.  After exact Gram
factorization, the amplitudes are equivalently positive-semidefinite spin
density matrices

```text
rho_plus,ell >= 0, rank <= 2,
rho_extra,ell >= 0, rank <= 4,
rho_minus,ell >= 0, rank <= 2.
```

The cone is exactly the inverse image of `H=J_1=J_2=J_3=0` in the product of
these rank strata; `P_x` vanishes identically.  This retains every `m`, both
parities, both extra polarizations, and cross-`ell` charge cancellation.  In
particular every fixed `ell>=2` has a two-parameter rotationally neutral face
supported on `m=0`, with

```text
a_minus=(omega_plus^2 a_plus+omega_extra^2 a_extra)/omega_minus^2.
```

The Paper 91 ray is the `ell=2,a_plus=0` boundary of this face, not an
isolated Taub-zero direction.

Second, the full quadratic source has now been tested on the larger axial
`ell=2,m=0` three-branch face.  The Einstein-plus, extra, and Einstein-minus
homogeneous zero-frequency source vectors obey the exact rank-one identity

```text
S_s(0)=tau_s (1,0,1/2,0),
```

where `tau_s` is the same branch coefficient that appears in the
constant-lapse Taub form.  Consequently the full homogeneous cokernel source
cancels on the entire two-parameter positive quadrant whenever `H=0`, not
only on the Paper 91 boundary ray.  All nine nonzero self/cross
sum--difference channel types are off shell at polar output `ell=2,4`, with
exact minimal-polynomial nonzero witnesses for both `p` and `q`; their
homogeneous corrections are explicit.  The zero-frequency `ell=2,4` sources
also have exact inverse corrections.  Therefore every point of this declared
face, with arbitrary constant relative phases, has a spatially periodic
finite-quasiperiodic second-order correction.  That axisymmetric fixture by
itself did not settle other `m`, parity, the second extra polarization, or
higher-`ell` faces; the next certificates close the first three at `ell=2`.

The extra-polarization and angular gates are now sharper.  A second direct
four-dimensional fixture for the axial `ell=2,m=0,k=0` extra basis gives

```text
S_e1(0)=(-1728/5,0,-864/5,0),
S_e1,e2(0)=0.
```

Together with the previously used second extra vector, the internal extra
source matrix is diagonal and is proportional to the direct Lee--Wald Gram
matrix.  The complete axial axisymmetric face therefore has three independent
nonnegative occupations `(a_plus,a_e1,a_e2)`, balanced by `a_minus`; its
zero-frequency source still has one spacetime row and every nonzero block is
off shell.

Non-axisymmetric axial data introduce the odd output harmonics omitted by the
axisymmetric calculation.  Direct specialization of the raw axial target
operator at `ell=1,k=0` discovers, besides the twist and standard shells, an
exceptional fourth-order primary

```text
omega^2=4/3,   representative (h_t,h_x,q_t,q_x)=(0,1,0,-3).
```

At zero frequency the only physical left-cokernel row is the twist adjoint,
in three `SO(3)` copies; by the Taub--Lee--Wald bridge these are exactly the
three rotation moment maps.  Exact minimal-polynomial checks show that every
nonzero quadratic frequency misses the `ell=1` twist, extra, and standard
shells, while the `ell=3` outputs miss both generic `p` and `q` shells.
Consequently every finite real axial `ell=2,k=0` tangent with all `m`, both
extra polarizations, and `H=J_1=J_2=J_3=0` has a complete second-order
correction.  This is the full axial `ell=2` cone, not yet a statement about
polar input, axial--polar cross terms, or general `ell`.

The matching pure-polar `ell=2` gate now also closes.  Five direct
four-dimensional Hermitian fixtures, in the basis
`(Einstein-plus,Einstein-minus,extra-e1,extra-e2)`, give a rank-one
homogeneous source matrix with common spacetime row

```text
(1,0,1/2,0),
```

and scalar columns

```text
-864(11+7 sqrt(3))/5,
 864(-11+7 sqrt(3))/5,
-12/5,
-29952/5.
```

The `extra-e1/extra-e2` interference column vanishes exactly.  The apparently
small `-12/5` entry is a basis issue, not a current mismatch: the unit
`B`-representative has current weight `9`, while the published Lee--Wald basis
vector is `16 omega_e` times that unit vector.  Schur's lemma promotes this
internal matrix from `m=0` to all `m`, so `H=0` cancels every homogeneous row.
The odd `L=1,3` and nonzero-frequency output analysis is the same exact target
ledger as in the axial theorem.  Hence every finite real pure-polar
`ell=2,k=0` tangent with all `m`, both extra polarizations, and
`H=J_1=J_2=J_3=0` also has a complete second-order correction.

The proof dependency has now been normalized: the common even-total-parity
angular and nine-frequency resonance calculation lives in the parity-neutral
certificate
`EINSTEIN_MAXWELL_WEYL_ELL2_SAME_PARITY_OUTPUT_RESONANCE`, consumed directly
by both pure-sector theorems.

The axial--polar gate also closes.  At polar `L=1,k=0`, the vanishing
tracefree tensor harmonic leaves one residual scalar gauge column on
`(A_t,B,C_t,U)`,

```text
(2(omega^2-1),0,2,-1).
```

The unit `U` entry makes `U=0` a complete slice.  Its reduced determinant is

```text
(omega^2-4)(3 omega^2-4)/2.
```

Thus polar `L=1` has the standard and fourth-order shells at `omega^2=4` and
`4/3`, but no physical zero-frequency cokernel.  An axial `ell=2` mode times a
polar `ell=2` mode has odd total parity, so its only outputs are polar
`L=1,3` and axial `L=2,4`; axial `L=0` is absent.  Every zero-frequency block
is invertible, and exact algebraic witnesses show that all nine nonzero
frequency types miss both target shells in every block.  Cross-source
coefficients therefore cannot impose a new quadratic constraint.

Consequently the complete finite generic `ell=2,k=0`, all-`m`, both-parity
cone satisfying total

```text
H=J_1=J_2=J_3=0
```

is second-order extendible.  This includes cancellation of moment maps
between axial and polar components, because their cross moment maps vanish by
parity.  The pure source obstructions add to the total `H,J_i`, while every
cross source lies in an invertible quotient block.  At this fixture the
second-order tangent cone is exactly as large as the stabilizer moment-map
test permits.  General `ell`, opposite momentum, exceptional/global tangents,
and all-orders integration remain open.

The nonzero-frequency part is now promoted exactly to every generic input
`ell>=2` at `k=0`.  Shell ordering reduces the nine sum/difference frequency
types to candidates at `L=2ell`, `L=2ell-1`, and one finite
`L=2ell-1`, `2<=ell<=7` mixed family.  Exact `p`/`q` resultants are nonzero
on the complete candidate set.  The three differences lie below the first
generic shell, while the two largest sums lie above the angularly allowed
top shell.  Exceptional `L=1` roots are included in the same `{0,4/3,4}`
audit, and actual nonzero `L=0` sources are solved by the exact homogeneous
Noether completion.  Thus any failure of the all-`ell` second-order cone must
occur in the zero-frequency source/cokernel map, not through a nonzero target
resonance.  The complete all-`ell` cone remains fail-closed pending that
source theorem.

The first raw four-dimensional `ell=3` extra-self source replay was stopped
after approximately 30 minutes and 6.5 GB resident memory without emitting a
coefficient.  It also exposed and removed a type error in the proposed
fixture: the `Omega!=0` homogeneous left-null relation cannot be imposed on
the zero-frequency block.  No mathematical counterexample follows.  The
next source calculation should differentiate the arbitrary-`lambda` reduced
quadratic action with respect to homogeneous background parameters and use a
cached direct tensor replay only as an audit.

That reduced-action route now closes the fixed-`ell` theorem.  For every one
fixed generic `ell>=2` at `k=0`, with all `m`, both parities, both Einstein
branches, and both extra polarizations, the complete common
`H=J_1=J_2=J_3=0` cone is second-order extendible.  Each `p`/`q` primary is a
regular `1+1` Lorentz-scalar action polynomial.  A constant circle-metric
variation gives only an on-shell polynomial term and a term proportional to
`k^2`, so the rest-frame zero-frequency `E11` source vanishes.  Weyl
tracelessness and the integrated Maxwell total-derivative identity then force
the full scalar source row to `(1,0,1/2,0)`, whose coefficient is exactly the
constant-lapse moment map.  The `L=1` axial cokernel is exactly the rotation
triplet and every remaining zero or nonzero block is invertible.  An exact
`ell=3` axial-extra fixture gives

```text
S_E00=diag(-73440/7,-7208/63),
S_E11=0,
S_sphere=S_E00/2,
S_Maxwell1=0.
```

The generic formula reproduces both the direct full-row `ell=2` `e1` source
and the complete direct `ell=2` Taub matrix.  Cross-`ell` superpositions are
not covered because they introduce new mixed frequency arithmetic.

Verification receipt (2026-07-17): scoped compilation passed in `0.03 s`;
six deterministic certificate replays passed in `2.32 s`; six independent
verifiers and 18 scoped tests passed in `2.17 s`; and the complete
Einstein-sector Tier-3 rail passed all 446 tests in `304.151 s` (`305.24 s`
wall time).

Verification receipt (2026-07-17): scoped compilation passed in `0.04 s`;
four deterministic certificate replays passed in `2.69 s`; five independent
verifiers and 13 unit tests passed in `3.11 s`; and the full direct
four-dimensional polar Einstein-minus source replay passed in `840.06 s`.
Tier 3 was not run because no shared core operator or programme-wide freeze
changed; the complete affected certificate chain and direct source gate were
run.

Third, `EINSTEIN_MAXWELL_WEYL_OPPOSITE_MOMENTUM_COMMON_ZERO_CONE` classifies a
fixed generic `(ell,|k|)` pair.  Independent positive-frequency density
matrices at `+k` and `-k` obey five additive linear charge equations.  Equal
opposite-momentum branch densities cancel `P_x`; rank-one `m=0` densities and
the same energy balance above give a nonzero two-parameter standing-wave
Taub-zero face for every allowed nonzero `|k|`.  This does not contradict the
single-travelling-block no-go.  Relative `+k/-k` phases are invisible to the
moment maps and remain the load-bearing full-source gate.

Finally,
`EINSTEIN_MAXWELL_WEYL_STANDARD_EXCEPTIONAL_GLOBAL_MOMENT_MAPS` classifies
the already certified standard exceptional blocks.  Physical `ell=1`
oscillators are sign-definite and have only the origin as their isolated
common-zero locus.  In homogeneous coordinates
`(a,b,c,d,Q_e,W_x)`, after removing the common positive factor `2*pi*L`,

```text
mu_H=-a^2-b^2+b*d-Q_e^2,
mu_Px=mu_Ja=0.
```

Thus the homogeneous block has an indefinite quadric, with static
circumference `c` and flat holonomy `W_x` as spectators.  On the three twist
pairs, `mu_H=2|B|^2` and `mu_J=-4 A cross B`; the isolated common-zero locus
is the constant twist family `B=0`, tangent to exact lifted-rotation mapping
tori.  Electric charge variation contributes `-Q_e^2`, the same sign as the
positive-current extra sector, so it cannot rescue a pure-extra obstruction
by itself.  It can participate in balances with Einstein-minus or
twist-velocity data, but only when present at first order: a second-order
charge shift cannot alter an adjoint-cokernel pairing.  Exceptional
fourth-order target modes and the full source on the combined global cone
remain open.

Complete every cell established by your work; write `OPEN`, `NOT TESTED`, or
`NOT APPLICABLE` rather than extrapolating.

| Setting | \(D\) charge | Cartan contraction | Causal homotopy | One-particle sector | Pairing | Einstein sector |
|---|---|---|---|---|---|---|
| Vacuum cylinder | known target; boundaryless scope | known target | proved baseline | zero in stated absolute residual complex | \(I_2\) on centered degree-four classes | proper solution sector |
| Cylinder + scalar clock | open | open | open | open | open | open |
| Positive Berger clock | `D_GAUGE` on fixed-coupling linearized phase space | minimal clock SDR and retained `q1` complete; arity two open | principal endpoint factors only; curved/Green gates open | open | minimal cyclic pairing exact | `NOT_APPLICABLE` at this base point: certified non-Einstein Weyl--matter branch |
| Cylinder + Yang--Mills | open | open | open | open | open | open |
| Weakly deformed background | open | open | open | open | open | stability open |
| Compact Einstein--Maxwell product | sector-indexed; generic `k=0`, fixed `(ell,|k|)` opposite-momentum, and standard exceptional/global common-zero cones classified; no absolute quotient authorized | five-generator stabilizer action preserves generic axial/polar `q` and `p` primaries; for every fixed generic `ell>=2` at `k=0`, the all-`m`, both-parity common-zero cone is second-order extendible; cross-`ell`, opposite-momentum phase sources, and exceptional/global source cones remain open | `NOT TESTED` | no positive-frequency Hilbert space constructed | complete standard-harmonic pullback is nondegenerate: relative radiative inertia `(2,2)`, physical `ell=1` factor `4`, homogeneous unipotent shear, twist factor `-2` | every certified standard harmonic Einstein--Maxwell tangent survives before any optional stabilizer reduction; identity inclusion is not symplectic |
| Lorentzian dS/AdS | boundary-dependent; compute | open | open | open | open | selected sector to certify |
| Asymptotically flat | `PHASE_SPACE_NOT_CLOSED`; `H_ESU` crosses fixed \(\mathscr I\), `D_M` charge open | `NOT APPLICABLE` until a boundary-preserving generator and phase space are chosen | formal triangular seed only; causal complex open | `OPEN` | `OPEN` | `EINSTEIN_OPEN`; reduced `chi=0` seed only |

## Priority and stop/go decisions

1. Extend the now complete fixed-`ell`, `k=0` theorem to products between
   distinct input `ell` values; separately retain relative phases in
   opposite-momentum standing waves.  A mixed-frequency resonance or new
   adjoint component is the expected mechanism cutting the full Taub-zero
   density cone beyond the certified blockwise theorem.

   The first exact cross-`ell` census is now complete.  For every distinct
   `2<=ell_1<ell_2<=96`, all three input primaries, all three target
   primaries, both sum/difference channels, and an angular superset covering
   both parity choices have no exact frequency collision or target-shell
   resonance.  The exact radical audit contains `40,185` collision checks
   and `723,330` squared-resonance checks.  The closest channel is the
   nonzero `(ell_1,ell_2;L)=(5,34;30)`
   `extra x Einstein-plus -> Einstein-minus` difference near-miss.  This is
   a `G2` finite-window result, not the unbounded theorem.  The next step is
   the uniform six-offset Diophantine proof followed by the cross-`ell`
   source/cokernel calculation.

   The generic-output part is now unbounded.  Exact branch-offset bounds
   reduce every possible resonance with all three angular degrees at least
   two to five saturated families.  Three are sign-separated.  The two
   remaining radical families stay nonzero even when their squarefree parts
   coincide or become rational; the extra shell's `2/3` offset excludes the
   fully rational Pell cases.  Hence every distinct generic input pair at
   `k=0` misses every generic target shell `L>=2`.  The only remaining
   spectral gate is adjacent-input coupling to exceptional `L=1`; after
   that, the cross-`ell` source/cokernel projection is load-bearing.

   The exceptional spectral gate is also closed.  `L=1` requires adjacent
   inputs `(ell,ell+1)` and has root set `omega^2 in {0,4/3,4}`.  Cross-branch
   intervals exclude all six mixed branch pairs.  The extra-extra candidate
   has squared-resonance polynomial `-4(ell-1)(ell+3)/3`; the two same-q
   candidates are excluded exactly in the squarefree radical basis,
   including equal and rational inner-root cases.  Therefore the complete
   unbounded distinct-`ell`, `k=0` nonzero-output resonance gate is closed.
   The next load-bearing object is now the mixed quadratic source itself.

   In fact, source coefficients are not needed for the finite-harmonic
   existence theorem.  Distinct-`ell` pairs have no zero-frequency collision,
   cannot output `L=0`, and are off shell in every generic or exceptional
   nonzero block.  Only same-`ell` zero-frequency pieces remain, and their
   complete cokernel projection is already the total `H,J_i` moment map.
   Therefore every real finite generic-harmonic `k=0` sum on the common
   stabilizer-zero cone is second-order extendible.  The detailed cross-`ell`
   source changes the correction but not existence.  Infinite-mode
   completion, opposite-momentum phases, and exceptional/global inputs remain
   open.

   Opposite momentum has a genuine correction-space split.  For shell
   offsets `A,B,C`, every sum/difference channel has an exact linear divisor
   formula for `k^2`.  The divisor is nonempty for every `ell`: two
   Einstein-minus waves at `+k,-k` drive the polar extra shell at `L=2ell`
   when

   ```text
   k^2=sqrt(2ell(ell+1))-ell/2-1/6.
   ```

   The top Gaunt coefficient is nonzero, so angular selection does not remove
   the channel; any nonzero bilinear projection retains the relative
   standing-wave phase.  Therefore the moment-map cone alone cannot imply a
   bounded or finite-quasiperiodic correction.  In the smooth-global class,
   generic nonzero resonances are removable by exponential-polynomial
   secular inverses using the certified Smith factors.  The remaining
   smooth-global phase gate is the exceptional static `L=0,K=2k` target
   block; do not infer it from the generic polar operator.

   That remaining smooth-global gate is now closed, together with a hidden
   exceptional `L=1` seam.  Direct four-dimensional `L=0` linearization gives
   a rank-two action Hessian whose four-dimensional kernel is exactly
   `Diff x Weyl x U(1)` for every nonzero Fourier pair.  At the static phase
   channel a compatible source has the explicit correction
   `A=K=-S_A/K^4`, `T=-S_T/K^2`.  Direct axial and polar `L=1` replays at
   arbitrary Fourier momentum give only the reduced shells
   `Omega^2-K^2=4,4/3`; their static nonzero-momentum rank witnesses are
   strictly positive, and resonant forcing has the same finite secular
   inverse.

   Therefore the complete common-zero cone in one fixed generic
   `(ell,|k|)` paired-momentum block is second-order extendible for arbitrary
   relative phases in the smooth-global, spatially periodic,
   exponential-polynomial temporal class.  This is a genuine promotion from
   the phase-divisor result.  It is not a bounded or finite-quasiperiodic
   theorem: the universal resonance family remains, and its dynamical source
   projection is the separate bounded gate.  The next nonlinear enlargement
   is exceptional/global input data (homogeneous and twist velocities,
   Wilson line, charge, physical `ell=1`), followed by distinct `|k|` fibres.
2. Test the homogeneous quadric and twist-velocity mixed balances against the
   complete quadratic source, and classify exceptional fourth-order target
   modes.  Only after these gates should any null-subalgebra quotient be
   attempted.  In parallel, prove or obstruct a polynomial cyclic BV
   enhancement without inverting `k`, `omega`, `p`, or `q`.

   The complete standard homogeneous quadric is now closed at second order.
   For `(a,b,c,d,Q_e,W_x)`, the direct constraint source is exactly
   `-(a^2+b^2-b*d+Q_e^2)/2`; the dependent sphere row carries the same factor,
   and `c,W_x` are absent.  On the common-zero quadric, explicit polynomial
   `K^(2)` and `A_x^(2)` corrections remove every remaining row.  This
   includes the nontrivial face `a=Q_e=0,b=d`, but not the isolated constant
   radion, which remains off-cone and obstructed at fixed bundle topology.
   The next exceptional/global gate is therefore twist velocity (and then
   physical `ell=1` input), not the homogeneous sector.

   The first nonzero twist-velocity face also extends.  For the direct
   `Y_10=cos(theta)` normalization, the common-zero ratio is
   `3a^2=4B^2` between homogeneous radion-position/Jordan data and a twist
   velocity with zero twist position.  Its complete quadratic source splits
   into homogeneous `L=0`, polar `L=2`, and axial `L=1` channels.  Explicit
   polynomial corrections solve all four homogeneous rows, all eight polar
   rows, and all six axial rows.  This proves that twist velocity is
   cone-constrained rather than automatically obstructed.  The full
   SO(3)-covariant twist cone with nonzero collinear twist position remains
   the next refinement.

   By exact `SO(3)` equivariance this is already the complete `A=0`
   twist-velocity orbit, not only an `m=0` ray.  In the Cartesian real
   harmonic basis the Gram matrix is `(4*pi/3)I`, so every vector `B` obeying
   `3a^2=4|B|^2` rotates to the certified axisymmetric fixture, and the full
   correction rotates back.  The nonzero-position refinement is now closed
   as well.  A direct four-dimensional source calculation with arbitrary
   collinear `A,B`, arbitrary homogeneous `c,d`, and `3a^2=4|B|^2` has an
   explicit zero-remainder correction in every `L=0`, polar `L=2`, and axial
   `L=1` output row.  This is strictly larger than a time-translation orbit:
   `c` drops out, while `d` is absorbed by an additional axial polynomial
   correction.  Since the moment map already requires `A cross B=0`, `SO(3)`
   covariance promotes the axis calculation to the complete standard
   collinear vector face, including its `B=0` boundary.  The next compact
   gate was physical and exceptional fourth-order `ell=1` input data.  That
   isolated block is now classified: the axial and polar extra shell is
   `omega^2=4/3`, with normalized Hermitian current Gram `diag(16,3)`.  The
   constant-lapse Taub form is therefore negative definite on every nonzero
   real pure-extra dipole tangent.  Standard physical `ell=1` oscillators are
   orthogonal and carry the same sign, so they cannot balance the exceptional
   modes; the combined isolated common-zero locus is only the origin.  The
   next nontrivial fixture must import an Einstein-minus or other opposite-sign
   sector.  The enlarged homogeneous `b,Q_e,W_x` slice remains separate.

   The first opposite-sign fixture is already decisive.  A collinear standard
   twist velocity balances one axial exceptional `ell=1,m=0` mode at
   `B^2=(8/3)e^2`, so all five stabilizer moment maps vanish.  Nevertheless
   the exceptional positive-positive self-source lands at
   `Omega^2=16/3`, exactly the polar `L=2` extra shell.  The target matrix has
   rank two, the augmented matrix rank three, and two exact adjoint-cokernel
   rows pair with the source as `-2/3` and `4/3`.  Hence this nonzero
   common-zero tangent has no second-order correction.  Twist terms cannot
   alter the channel because their temporal support is at generalized zero
   frequency or `omega_e`, not `2omega_e`.  This separates global Taub
   cancellation from dynamical resonant solvability and makes cancellation by
   polar exceptional or Einstein-minus input the next cone-classification
   question.

   Polar exceptional input has now been tested on the complete axisymmetric
   two-polarization cone.  Its self-source pairings are `(1/8,-1/4)`, exactly
   `-3/16` times the axial pairings, so the even-parity resonances would cancel
   at `|a_p|^2=(16/3)|a_x|^2`.  The required interior combination, however,
   has a nonzero axial--polar cross-source in the axial `L=2` extra shell; an
   exact adjoint row pairs with it as `-8sqrt(3)/9`.  If either amplitude is
   zero, the corresponding self-source obstruction returns.  Thus every
   nonzero `m=0` exceptional two-polarization tangent is second-order
   obstructed, including the twist-balanced common-zero family.  The next
   genuine question is whether distinct-`m` interference can cancel the full
   `L=2` adjoint tensor, not another axisymmetric amplitude ratio.

   The distinct-`m` question is now closed.  In the Cartesian real `ell=1`
   basis, `SO(3)` multiplicity-one promotes the axis fixtures to
   `E=STF(a a^T-(3/16)p p^T)` and
   `F=STF(a p^T+p a^T)`.  After rescaling `q=(sqrt(3)/4)p`, `E=F=0` makes the
   STF parts of `(a+iq)(a+iq)^T` and `(a-iq)(a-iq)^T` vanish.  Rank one versus
   the three-dimensional identity forces both vectors to vanish.  An exact
   zero-dimensional Gröbner basis independently gives the same origin-only
   variety.  Hence no interference among `m=-1,0,1` rescues a nonzero
   exceptional dipole.  The only remaining scope audit before freezing the
   complete exceptional `ell=1` fixed-bundle no-go is whether another sector
   shares the same input frequency `omega^2=4/3`.

   That final same-frequency audit is now closed.  At `k=0`, generic
   `ell>=2` extra modes have `omega_X^2>=16/3`, the Einstein-minus branch has
   `omega_-^2>=6-2sqrt(3)>4/3`, the physical `ell=1` shell is `omega^2=4`,
   and the standard homogeneous/twist blocks are generalized zero-frequency
   data.  The axial and polar exceptional operators show that the complete
   `ell>=1`, `omega^2=4/3` eigenspace is precisely the all-`m` block already
   proved obstructed.  Angular selection also makes any unclassified `ell=0`
   target irrelevant to the resonant `L=2` channel without an `ell=2` partner.
   Hence the pure exceptional `ell=1,k=0` second-order no-go is frozen against
   every same-frequency `k=0` augmentation.  Unequal-frequency pairs summing
   to `2omega_e` and opposite nonzero momenta remain explicitly open.

   The positive-sum part of that broader resonance census is also exact now.
   A direct four-dimensional `ell=0,k=0,omega!=0` linearization gives the
   complete invariants `C-K,A_x` with equations
   `omega^4(C-K)=omega^2 A_x=0`; hence the homogeneous target contains no
   hidden nonzero-frequency oscillator.  Two nonzero positive-frequency
   inputs can therefore sum to `2omega_e` only if both are exceptional
   dipoles, already covered above.  If one input is a
   generalized zero-frequency global direction, the other must have
   `omega^2=16/3`.  The unique physical `k=0` block with that frequency is the
   generic `ell=2` extra primary: `lambda-2/3=16/3` forces `lambda=6`, while
   neither Einstein branch has a physical root.  The next direct source gate
   is therefore sharply finite: cross every homogeneous/twist global
   direction with the axial and polar `ell=2` extra-primary block and pair the
   resulting `L=2,Omega=2omega_e` source with the exceptional adjoint
   cokernel.  Difference-frequency and opposite-momentum channels remain
   separate after that.

   Two columns of that finite source matrix are now removed without a heavy
   tensor calculation.  `W_x` is a flat-connection spectator, so its cross
   source vanishes identically.  The circumference coordinate `c` is tangent
   to the exact radius family
   `g_R=-dt^2+R^2 dx^2+dOmega_2^2`.  Every `k=0` extra mode transports along
   this family; differentiating `L_R u_R=0` supplies an explicit mixed
   correction and proves that the `c` cross source lies in the linear image.
   Thus neither `c` nor `W_x` can cancel the exceptional adjoint defect, for
   either parity or any `m`.  The live positive-sum matrix is reduced to the
   homogeneous `a,b,d,Q_e` directions and the twist position/velocity vectors
   crossed with the axial/polar `ell=2` extra block.

   The `Q_e` column is removed as well, but for a different reason.
   Four-dimensional electromagnetic duality rotates `(dF,d star F)` and
   leaves the Maxwell stress tensor invariant.  Its infinitesimal action on
   the magnetic fixture is exactly the declared homogeneous electric tangent.
   Transporting an arbitrary `ell=2` extra Jacobi field and differentiating
   gives the explicit mixed correction
   `f_cross=star f+(D_g star)[h]F_bar`.  This correction has zero sphere period
   by `ell=2` orthogonality and therefore lifts to a global connection
   difference on the fixed bundle.  Hence the `Q_e` cross source lies in the
   linear image and cannot cancel the exceptional defect.  This does not make
   the pure electric direction all-orders extendible at fixed magnetic flux;
   only its mixed wave coefficient is settled.  The live matrix is now
   `a,b,d` plus twist position/velocity against the axial/polar `ell=2` extra
   block.

   The first genuinely dynamical column, `d`, is now computed on the complete
   axial extra multiplicity space.  Direct four-dimensional bivariate sources
   are
   `S(d,e1)=(-72 i sqrt(3),0,0,0)` and
   `S(d,e2)=(0,-4 i sqrt(3)/3,0,-4 i sqrt(3))` in action-row order.  Against
   the complete axial p-shell adjoint basis their pairing matrix is diagonal
   with determinant `832`.  Hence, for `d!=0`, the two axial `ell=2` extra
   amplitudes can cancel an arbitrary axial resonant defect.  `SO(3)`
   equivariance promotes the multiplicity-space isomorphism to every `m`.
   The polar column is now complete as well.  In reduced polar action rows,
   `S(d,e1)=(0,-6 i sqrt(3),0,0)` and
   `S(d,e2)=(-376 i sqrt(3),0,-632 i sqrt(3)/9,384 i sqrt(3))`.
   The complete polar p-shell adjoint pairing is diagonal with determinant
   `9936`; combined with the axial determinant, the parity-block determinant
   is `8266752`.  Thus the complete `d` cross map is an isomorphism in both
   parities for every `m`.  This is still a bounded/finite-quasiperiodic
   compatibility theorem, not a full extension: stabilizer moment maps,
   nonresonant rows, and the remaining `a,b` and twist columns are required.

   The remaining twist columns are now complete.  An axisymmetric fixture
   cannot see them because the `m_1=m_2=M=0` Clebsch--Gordan coefficient
   vanishes, so the direct replay uses
   `m_twist=1,m_extra=0 -> M=1`, whose normalized coefficient is
   `sqrt(2)/2`.  This fixes the unique `V_1 tensor V_2 -> V_2` map by
   `SO(3)` equivariance.  Projected onto the two axial and two polar p-shell
   adjoint rows, the twist-position matrix has rank two.  The twist-velocity
   matrix has

   ```text
   det M_B(t)=4129056(72 t^2+34 sqrt(3) i t+3),
   ```

   which is nonzero for every real `t`; its pointwise rank is four.  Together
   with the `a,b,d` chains and the removable `c,W_x,Q_e` columns, this closes
   the declared homogeneous/twist-times-`ell=2` bounded-resonance source
   matrix.  It does not yet solve the bilinearly factorized common zero locus
   with all five stabilizer moment maps.
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

## Generated residual atlas and tangent-cone handoff

The Einstein team owns the common fragment schema at
`residual_atlas/schema/residual-atlas-fragment-v1.schema.json`.  The initial
compact-product ledger is generated, rather than manually curated, at
`bridge/einstein_sector/atlas/einstein-compact-product-atlas-fragment.json`.
Every entry carries the full mode scope, the five fail-closed description
statuses, and separate dispersion, Lee--Wald, Taub, resonance, and
second-order fields.  Correction verdicts are separate for bounded or
finite-quasiperiodic, smooth-secular, and causal/retarded classes.  The
generic validator is `residual_atlas/validate_fragment.py`.

The atlas records the exact second-order convention

\[
L_{\bar\Phi}v=-\frac12D^2E_{\bar\Phi}[u,u].
\]

It imports the certified abstract finite-harmonic image/cokernel theorem
`FINITE_HARMONIC_SECOND_ORDER_TANGENT_CONE_THEOREM_V1` without treating that
abstract result as a compact-product classification.  In each declared
correction class, the background-specific gate remains

\[
\mathcal Z_2^{\mathcal C}
=\{u:\mu_X(u)=0,\ R_j^{\mathcal C}(u)=0\ \text{for every complete output block}\}.
\]

The twist-balanced exceptional fixture is the required independence witness:
all stabilizer moment maps vanish while a polar `ell=2` bounded resonant
functional is nonzero.  Conversely, the balanced Einstein--extra `ell=2`
fixture has an explicit complete finite-quasiperiodic correction.  The new
`d`-cross parity completion shows that both resonant projections are
cancellable, but its atlas nonlinear status remains `OPEN` because the
nonresonant and simultaneous stabilizer conditions are not yet closed.  No compact-product
causal/retarded Green theorem or cross-background mode map is certified.

Bridge priority 1 is the active Einstein--classical bridge.  Its generated
same-background artifact is `EINSTEIN_WEYL_RELATIVE_BRANCH_DICTIONARY_V1`.
The exact global map lifecycle is `ONSHELL_MAP_ONLY`, and its activation gate
remains `OPEN`.  Both generic parities have certified polynomial derived
cofiber triangles, solution quotients and direct action-derived pairings.
The exceptional `ell=1,k=0` solution cofiber now has explicit CRT projectors
and a nonradical direct current.  The complete homogeneous target quotient is
also exhausted by the Einstein--Maxwell image, so its solution cofiber is
zero despite the nontrivial nilpotent relative symplectic shear.  Strict
cyclicity of the generic axial and polar maps with their fixed identity field
inclusion is now obstructed by a nonradical solution-pairing defect; corrected
nonidentity or chain-homotopy cyclic morphisms remain open.  Exceptional
off-shell/nonzero-`k` maps, global off-shell
endpoints, charge endpoints and the boundary carrier remain
explicit `NO_CERTIFIED_MAP` fields.
The generalized-zero twist primary is likewise exhausted by the Einstein
image: its CRT projector is explicit, its solution cofiber is zero, and its
identity pullback still has relative operator `-2I`.  Its off-shell complex,
finite holonomy-moduli quotient and final residual descent remain open.
The fail-closed atlas row is
`einstein.ph.bridge.relative_branch_dictionary_v1`.  It does not identify any
similarly named mode on another background.

## Required handoff

### Current assignment (2026-07-18)

The active task is the background-specific completion of the finite-harmonic
tangent cone.  The homogeneous/twist-times-`ell=2` extra-primary bounded-
resonance source matrix is now complete.  Next decompose every
Noether-compatible adjoint cokernel into the five
stabilizer covectors plus complementary resonant functionals, and prove
necessity and sufficiency separately in each correction class.  The current
matrix has removed the circumference, Wilson-line and electric spectator
columns and has certified the complete axial-plus-polar `a,b,d` polynomial
source submatrix.  Every parity/polarization `a,b,d` chain has coefficient
rank three; the twist-position block has rank two and the twist-velocity block
has pointwise rank four for real time.  This is input to bridge 1 and the
tangent-cone theorem, not their completion.  The simultaneous stabilizer plus
resonance zero locus, opposite momenta and phases, and multiple `|k|` fibres
remain open.  Update the generated atlas after each background-specific gate
rather than promoting the abstract theorem.

The first exact intersection with the stabilizer cone is now certified, but
it is deliberately narrower than the requested full zero-locus theorem.  Put
an arbitrary nonzero four-component extra-primary amplitude on the shared-axis
`ell=2,m=0,k=0` harmonic and take collinear twist position and velocity.  The
unique `V1 tensor V2 -> V2` resonant map vanishes because
`<1,0;2,0|2,0>=0`; the branchwise `a,b,d` rank-three gates force
`a=b=d=0`.  With orthonormal harmonics,

```text
X=1296|x_a1|^2+(208/3)|x_a2|^2+22464|x_p1|^2+12288|x_p2|^2,
B_z^2=(2/3)X,
```

so `mu_H=0`, while `mu_Px=0` and all three rotations vanish by `m=0` and
`A cross B=0`.  Thus this is a nonzero simultaneous stabilizer and completed
bounded-resonance common-zero face.  It is not yet a second-order extension:
the nonresonant polynomial cross channels and their bounded versus smooth-
secular right inverses remain open, as does the complete off-axis zero locus.
The fail-closed atlas row is
`einstein.ph.wm.mixed.aligned_twist_ell2_extra_compatibility_face`.
The classical team has now closed the full necessary zero locus in this
declared carrier.  Exact coefficient elimination gives `a=b=d=0`; rank
stratification and `mu_J` then force every solution to be an `SO(3)` rotation
of the aligned face, with the electric extension
`B^2=Q_e^2/2+(2/3)X`.  No additional off-axis branch exists.  The active gate
is no longer zero-locus classification: it is the complete nonresonant `q2`
source plus content-addressed bounded/smooth right inverses and their
Noether/gauge completion.  Causal/retarded sufficiency remains
`NO_CERTIFIED_MAP`.

The bounded correction class is now fully obstructed on this orbit.  The
energy balance forces `B!=0` whenever `X>0`, while the directly certified
zero-frequency polar `L=2` source contains `-7*B^2*t^2` in the `metric_00`
row.  Extra conjugate-self and electric sources are time independent in that
channel, and the mixed/sum sources have nonzero frequency, so the quadratic
coefficient cannot cancel.  Since the stationary linearized operator maps
bounded finite-quasiperiodic corrections to bounded sources, no such
correction exists.  This does not obstruct the smooth exponential-polynomial
class; its complete mixed right inverse is now the sole local nonlinear gate.

That smooth gate is now closed coefficientwise on the complete declared
shared-axis orbit.  The
quadratic source has finite closure in `L=0,...,4` and frequencies
`0,+/-omega_e,+/-2*omega_e`.  The aligned twist--extra cross has only `L=1,3`
and is off shell; the `ell=0`--extra `L=2` channel is p-resonant but admits a
finite secular inverse.  After gauge/Noether reduction every nonstabilizer
Smith factor is surjective on finite exponential-polynomial coefficients,
while the remaining five stabilizer pairings vanish on the certified orbit.
Thus every orbit point has a smooth spatially periodic finite exponential-
polynomial second-order correction.  Bounded remains `OBSTRUCTED` and
causal/retarded remains `NO_CERTIFIED_MAP`.

The coefficient gate is now complete in this carrier.  A direct
four-dimensional global/global fixture exposes the electric--twist polar
`L=1` source and removes it with
`(A_t,C_t,U)=(-B Q_e,B Q_e,0)`; the polar `L=2` twist self-correction is also
printed on all eight rows.  A second direct four-dimensional producer
computes all twenty independent complex bilinear generators of the canonical
`C^4` extra multiplicity vector: ten positive-frequency sums and ten
Hermitian zero-frequency generators.  Same-parity products give polar
`L=0,2,4`; mixed-parity products give axial `L=2,4`.  The complete allowed
harmonic basis and an unused angular node are audited, arbitrary relative
phases are retained, and every nonstabilizer block has a printed exact
correction with zero remainder.

The normalization bridge is explicit:

```text
B_raw^2=(3/2) beta^2,
|x_raw|^2=(5/2)|x|^2,
S_00^global+S_00^extra=beta^2-Q_e^2/2-(2/3)X=0.
```

Thus the direct homogeneous source cancels exactly by the certified cone
equation `beta^2=Q_e^2/2+(2/3)X`.  Together with the already printed sixteen
twist--extra channels (thirteen nonzero corrections and three zero sources),
this makes the complete declared one-fibre shared-axis `SO(3)` orbit
coefficient-explicit at second order in the smooth exponential-polynomial
class.

The fail-closed atlas row remains
`einstein.ph.wm.mixed.aligned_twist_ell2_extra_compatibility_face`: its
smooth-secular status is `CERTIFIED` with the complete coefficient ledger.
Bridge 1 remains activated only at its separately certified compact-product
noncyclic linear triangle lifecycle; this nonlinear result does not certify a
relative `q2/q3` morphism.

The separate finite-generic enlargement is now complete in the smooth
exponential-polynomial correction class.  Every finite sum of generic
`ell>=2` axial/polar Einstein and extra primaries may carry arbitrary allowed
compact momenta, `m` values and phases.  With output blocks kept distinct as
`(L,M,K,Omega,parity)`, all nonzero Fourier blocks have algebraic or finite
secular inverses.  The zero-block reduced adjoint cokernel is exactly the five
stabilizer covectors, hence

```text
Z2^smooth={u:mu_H=mu_Px=mu_J1=mu_J2=mu_J3=0}.
```

This includes opposite momenta, non-aligned generic harmonic
superpositions, and multiple `|k|` fibres.  The bounded category remains
separate: its exact finite resonance ledger `R_(j,a)` is defined and gives a
necessary-and-sufficient formula with the moment maps, but its coefficientwise
zero locus is `OPEN`.  The finite-generic fail-closed atlas row is
`einstein.ph.wm.mixed.finite_generic_all_momenta_smooth_cone`.

The exceptional/global enlargement is now complete as a separate theorem.
The branch dictionary exhausts the certified finite target by adjoining the
standard/extra `ell=1` blocks at every compact momentum, the three axial twist
Jordan pairs, and the six-coordinate homogeneous block.  Their quadratic
sources have temporal degree at most six.  The explicit monomial primitives
for `D''''` and `A_x''`, the exceptional `L=0,1` operator complexes, and the
generic Smith factors prove

```text
coker L_smooth=span{zeta_H,zeta_Px,zeta_J1,zeta_J2,zeta_J3}
```

on the complete finite carrier.  Therefore the five moment maps are necessary
and sufficient for a real smooth spatially periodic finite exponential-
polynomial correction.  The bounded ledger is strictly larger:
`mu_X=P_(j,r)=R_(j,a)=0`, with independent certified polynomial and resonant
witnesses, but its coefficientwise common zero locus is `OPEN`.  The active
Bridge 1 lifecycle remains the noncyclic linear triangle; this nonlinear
theorem is an input and does not promote a relative `q2/q3` morphism.  The
fail-closed row is
`einstein.ph.wm.complete_finite_harmonic_smooth_cone`.  Causal/retarded
transport is `NO_CERTIFIED_MAP`; infinite-mode completion, all-orders
integration, final residual descent, observational maps and quantum transfer
remain open.

The bounded polynomial ledger now has its first complete base stratum.  For
the complete standard generalized-zero input
`(a,b,c,d,Q_e,W_x;A,B)`, exact leading coefficients give

```text
(15/2)b^2 t^2 in homogeneous E11,
STF(B tensor B)t^2 in polar L=2,
Q_e*a*t after b=B=0.
```

Thus `P=0` is exactly `b=B=0, Q_e*a=0`.  Intersecting with the five moment
maps forces `a=Q_e=0`, and the complete bounded cone in this carrier is
`(c,d,W_x,A)`.  Its correction is bounded: the homogeneous source vanishes,
and constant `A` uses the certified time-independent polar `L=2` correction.
Moreover `b=B=0` and `Q_e*a=0` are universal for every complete
finite-support bounded candidate because no bounded oscillator product can
occupy those zero-frequency polynomial coefficients.  The fail-closed atlas row is
`einstein.ph.wm.standard.global_bounded_cone`.  The active next gate is the
residual global-times-oscillator map.

That gate has now been reduced further by a complete transport theorem.
Electromagnetic duality transports every certified nonzero-frequency
standard `q`-primary and extra `p`-primary mode, including exceptional
`ell=1`, both parities, all `m`, and every allowed compact momentum.  The
mixed correction is

```text
h_cross=0,
f_cross=star_bar f+(D_g star)[h]F_bar.
```

It has the same bounded quasiperiodic time dependence as the oscillator and
zero `S2` period, hence lifts on the fixed magnetic bundle.  Thus every
`Q_e`-times-oscillator source is a bounded linear image.  The flat Wilson
direction has `delta F=0`, so every `W_x` mixed source vanishes.  Atlas row
`einstein.ph.wm.interaction.electric_wilson_complete_oscillator_transport`
records these claims with causal transport still `NO_CERTIFIED_MAP`.

The circumference column is now completely classified as well.  Along the
exact family `R^2=1+eta*c`, every shell has
`omega_R^2=k^2/R^2+m_branch^2`.  At `k=0`, index transport is an ordinary
bounded correction.  At `k!=0`, differentiation gives

```text
partial_eta exp(-i*omega_eta*t)|_0
  = i*c*k^2*t*exp(-i*omega*t)/(2*omega).
```

Thus the source is bounded but resonant: the nonradical Lee--Wald current
proves a nonzero `R_(j,a)` for every nonzero mode when `c*k!=0`, while the
displayed secular term proves smooth extension.  This is not a
`P_(j,r)` coefficient.  The complete `c` cross column is bounded-compatible
exactly when `c=0` or oscillator support is contained in `k=0`.  Atlas row
`einstein.ph.wm.interaction.circumference_complete_oscillator_column`
records the two momentum strata without merging them.

The active positive-degree gate is therefore `a` and `d` crossed with all
oscillators.  A full-time audit of the existing `ell=2,k=0` extra fixtures
found that the direct `d` producers substitute `t=0`.  Their four-column
adjoint map remains an exact constant-term resonance isomorphism, but
locality restores the omitted coefficient

```text
S[d*t,u](t)=t*S[c,u](t)+S[d*t,u](0).
```

The axial columns and first polar column have zero `t` coefficient.  The
second polar column has the nonzero eight-row vector
`d*z2*(-36,0,164,-8*sqrt(3)*i,0,-100,-24,-20)`.  Thus its isolated
polynomial condition is `d*z2=0`.  The old `a,b,d` and homogeneous/twist
bounded-matrix completeness claims are superseded pending a joint `a/d`
polynomial solve; their printed `a,b`, twist and `t=0 d` data remain valid.

The repaired joint cross ideal is now solved exactly.  In amplitude order
`(z_ax1,z_ax2,z_pol1,z_pol2)`, its generators are

```text
a*z_ax1, a*z_ax2, a*z_pol1, a*z_pol2, d*z_pol2.
```

They already form the exact Groebner basis.  The three faces are: no extra
wave with `a,d` free in this cross ledger; `a=0,z_pol2=0` with `d` and the
two axial plus first polar amplitudes free; and `a=d=0` with all four extra
amplitudes free.  Atlas row
`einstein.ph.wm.interaction.ad_ell2_extra_polynomial_zero_locus` records the
complete scoped `P_(j,r)` theorem.  The old nonzero-extra common-zero cone is
unchanged because it already has `a=b=d=0`; its independent twist-velocity
bounded obstruction also remains.

For the complete homogeneous/twist plus `ell=2,k=0` extra carrier, the next
step simplifies before any constant-matrix elimination.  Boundedness already
forces `b=B=0`; the Hamiltonian moment map then reads

```text
mu_H=-a^2-Q_e^2-(4/3)X,
X=1296|x_ax1|^2+(208/3)|x_ax2|^2
  +22464|x_pol1|^2+12288|x_pol2|^2.
```

It is strictly negative away from `a=Q_e=x_extra=0`.  Hence the complete
bounded cone on this enlarged carrier is exactly the standard cone
`(c,d,W_x,A)`; adjoining the linearly genuine extra block does not enlarge
it.  Atlas row
`einstein.ph.wm.mixed.complete_global_ell2_extra_bounded_cone` records
necessity and sufficiency.  The old nonzero-extra common-zero orbit uses
`B!=0` for its opposite sign and is removed by the independent twist-velocity
polynomial obstruction.

The first opposite-sign enlargement is now classified on the aligned axial
`ell=2,m=0,k=0` face.  A direct four-dimensional source replay for the
Einstein-minus representative gives a triangular shell pairing: the `b`
coefficient has a nonzero `t^2` pivot, `a` has a nonzero `t` pivot after
`b=0`, and `d` has a nonzero constant pivot after `a=b=0`.  Thus every
nonzero bounded wave forces `a=b=d=0`.

The full zero-frequency source supplies a second, independent refinement.
Although Einstein-minus can cancel the electric contribution to `mu_H`, the
electric self-source retains `E11=Q_e^2/2`; the bounded homogeneous operator
has zero image at frequency zero.  Hence `Q_e=0`.  The complete declared cone
is the union of the static `(c,d,W_x,A_z)` branch and the nonzero wave branch

```text
a=b=d=Q_e=B_z=0,
x_minus=(972*x_e1+52*x_e2)/(27*(-6+5*sqrt(3))),
```

with `c,W_x,A_z` and the relative wave phases arbitrary.  Atlas row
`einstein.ph.wm.mixed.aligned_global_axial_ell2_minus_extra_bounded_cone`
records necessity and sufficiency.

The axial result now holds for every `m=-2,...,2`.  Since `a,b,d` are
rotational scalars, each shell coefficient is an `SO(3)` intertwiner
`V_2 -> V_2`; Schur's lemma promotes the direct `m=0` pivots to scalar
identities, so distinct `m` components cannot cancel them.  The only possible
all-`m` boundedness caveat was the zero-frequency axial `L=1` output.  After
the three rotation moment maps vanish, its source is
`(S0,S1,S0,S1)` and the constant coefficient correction
`(S0/2,-S1/2,0,0)` solves the exact rank-two target operator.  No Jordan
growth is needed.

The former product with arbitrary constant twist `A` does **not** survive the
all-`m` promotion.  The exact twist-position matrix has rank two, and the
fixture with twist `m=1`, rotationally neutral wave `m=0`, and axial extra
representative `e1` has adjoint coefficient `24*sqrt(3)` at `omega_extra`.
The twist--Einstein-minus term lies at a distinct frequency and cannot cancel
it.  This gives the required independence witness

```text
mu_H=mu_J1=mu_J2=mu_J3=mu_Px=0,
R_twist-position=24*sqrt(3) != 0.
```

Accordingly the certified result is the wave-free static branch with
arbitrary `(c,d,W_x,A)` together with the complete `A=0` axial wave-density
subcone (`a=b=d=Q_e=0`, `A=B=0`, and `H=J_i=0`).  The nonzero-`A` wave zero
locus is open.  Atlas rows
`einstein.ph.wm.interaction.constant_twist_wave_counterexample` and
`einstein.ph.wm.mixed.global_axial_ell2_all_m_minus_extra_bounded_cone`
record the obstruction and corrected lifecycle.

The replacement extra-shell incidence theorem is now complete.  The unique
`SO(3)` map `V_1 tensor V_2 -> V_2` reduces every nonzero real twist to an
axis calculation.  In the frame `A=|A| z`, its angular coefficient is

```text
<1,0;2,m|2,m>=-m/sqrt(6).
```

The internal four-by-four position matrix has rank two and kernel

```text
span{polar_e1, -4*sqrt(3)*axial_e1+15*polar_e2}.
```

Therefore the complete twist-position resonance-zero space on the
positive-frequency `ell=2` extra shell has complex dimension twelve: the
`m=0` internal coefficient is arbitrary, while every `m=+/-1,+/-2`
coefficient must lie in that two-dimensional kernel.  This simultaneously
contains the aligned face and excludes the off-axis counterexample.  Atlas
row `einstein.ph.wm.interaction.constant_twist_ell2_extra_position_zero_locus`
records necessity and sufficiency for this one resonance family.  The
Einstein-plus/minus matrices are now also direct.  On each shell their
axial/polar incidence matrix is

```text
Q_minus=Q_plus=[[0,216/5],[432/5,0]],
det(Q_plus/minus)=-93312/25.
```

The two matrices are invertible, so their only angular kernel is `m=0`:
axial and polar coefficients survive there on each shell, giving four complex
Einstein directions across both frequencies.  Atlas row
`einstein.ph.wm.interaction.constant_twist_ell2_einstein_position_zero_locus`
records the theorem.  Intersecting these four directions and the twelve
extra-shell directions with the common moment cone is now complete on the
declared constant-twist-plus-`ell=2,k=0` carrier.  For nonzero `A`, rotate to
its axis and impose

```text
E_plus[:,m]=E_minus[:,m]=0                  for m != 0,
X_extra[:,m] in span{polar_e1,
                     -4*sqrt(3)*axial_e1+15*polar_e2}  for m != 0,
mu_H=mu_J1=mu_J2=mu_J3=0.
```

These equations are necessary and sufficient for a bounded second-order
correction in that carrier.  Sufficiency follows by separating the source
into wave--wave, twist--wave and twist--twist pieces: the first and last are
already certified, the displayed kernels remove every `L=2` cross resonance,
and all `L=1,3` cross outputs are strictly off both `p` and `q` shells.  This
last step uses the exact exceptional axial/polar `L=1` quotient determinants,
the generic `L=3` physical-ring determinant `p^2 q`, and the quadratic
expansion of the ungauged Noether identity to place every source in the
compatible quotient source space.  The
cone is strictly larger than the aligned face: equal `polar_e1` amplitudes at
`m=+2,-2` have zero angular moment and are balanced by an Einstein-minus
`m=0` occupation.  Atlas row
`einstein.ph.wm.mixed.constant_twist_ell2_complete_bounded_cone` records the
theorem.

The twist-velocity enlargement is now closed without a new shell inversion.
For the full finite carrier the direct polar `L=2` source contains

```text
STF(B tensor B)*t^2,
|STF(B tensor B)|^2 = (2/3)*|B|^4.
```

No bounded oscillator product can cancel this positive polynomial degree, so
every bounded second-order correction forces the complete real twist velocity
vector `B=0`.  The `A,B` plus complete `ell=2,k=0` cone therefore equals the
constant-position cone displayed above, including its nonaxisymmetric
`m=+/-2` survivor.  Atlas row
`einstein.ph.wm.mixed.twist_position_velocity_ell2_complete_bounded_cone`
records the necessity-and-sufficiency theorem.  Other homogeneous tangents,
other `ell`, nonzero momentum, the unrestricted secular class and
causal/all-orders lifecycles remain open.

The polar Einstein-minus cross source is now also direct and exact.  Its
first action row has successive nonzero pivots `66*b*z`, `198*a*z`, and
`198*d*z`, so Schur promotion gives the same `a=b=d=0` conclusion for every
polar `m`.  Combining both parities with the complete `ell=2` common-zero
theorem still certifies every axial/polar Einstein-plus, Einstein-minus, and
both extra-primary coefficient for all `m` on the `A=0` wave face.  Its wave
equations are

```text
mu_H=mu_J1=mu_J2=mu_J3=0,
a=b=d=Q_e=0,
A=B=0,
```

with arbitrary `(c,W_x)`.  The exact constant `L=1` right inverse removes the
last secular/Jordan caveat on that face.  The wave-free static branch retains
arbitrary `(c,d,W_x,A)`, but the complete nonzero-`A` wave locus is open.
Atlas row
`einstein.ph.wm.mixed.global_ell2_all_m_both_parity_bounded_cone` records
this corrected split.

The first symbolic-`ell` gate now has an exact multi-fibre fixture ledger.
The direct four-dimensional helpers use the generic representatives

```text
axial: (0,-2,0,sqrt(2*lambda)),
polar: (2*lambda,0,2*lambda*(1-sqrt(2*lambda)),lambda).
```

Complete `a,b,d` triangular pivots replay at `ell=2,3` in both parities, and
the leading `b` pivot replays at `ell=4`.  They reconstruct the candidates

```text
C_A=3*i*omega_minus*(1-3*sqrt(2*lambda)),
C_P=lambda^2*(2*lambda-1)/6,
```

with axial ratios `(a,b,d)=(2,1,1)` and polar ratios `(3,1,3)`.  Atlas row
`einstein.ph.wm.interaction.abd_times_generic_k0_einstein_minus_pivot_fixtures`
records those certified fixtures.

The promotion gate is now closed without interpolation.  A direct
four-dimensional Bach--Maxwell calculation uses formal Legendre jets at the
regular point `z=0`, with all higher derivatives fixed by the Legendre ODE
while `lambda` remains symbolic.  It gives exactly

```text
C_A=-3*i*omega_minus*(3*sqrt(2*lambda)-1),
C_P=lambda^2*(2*lambda-1)/6.
```

Both are nonzero for every `lambda=ell(ell+1)>=6`.  Locality supplies the
complete triangular ratios, and `SO(3)` multiplicity one promotes them to all
`m`.  Combining this theorem with the existing every-fixed-`ell` common-zero
wave theorem certifies, for every fixed generic `ell` at `k=0`, the wave-free
static branch and the `A=0` wave subcone
`mu_H=mu_J1=mu_J2=mu_J3=0`, `a=b=d=Q_e=0`, `A=B=0`, with `(c,W_x)` arbitrary.
It does not solve the constant-twist resonance map at general `ell`.  Atlas
row `einstein.ph.wm.mixed.global_fixed_ell_k0_bounded_cone` is therefore
`OPEN` for the complete bounded cone while retaining those certified
subcones.

The wave-only cross-`ell` gate is closed for arbitrary finite generic sums at
`k=0`: every wave-only source is removable on the total `H,J_i` zero cone,
and the symbolic `a,b,d` pivots cannot be screened by another angular block.
After global data are adjoined, however, only the `A=0` finite-wave subcone
and the wave-free static branch are certified.  The complete nonzero-`A`
constant-twist resonance zero locus remains open.  Atlas row
`einstein.ph.wm.mixed.global_finite_harmonic_k0_bounded_cone` records this
fail-closed distinction.  Infinite harmonic completion, nonzero compact
momentum and exceptional `ell=1` wave inputs remain fail-closed.

The exceptional `ell=1,k=0` frequency census has nevertheless advanced.  For
the obstructing `L=2`, `2*omega_e=4/sqrt(3)` shell, angular selection reduces
generic difference-frequency inputs to 27 branch/offset families.  Exact
resultant elimination produces integer polynomials with no integer root
`ell>=2`.  Physical or exceptional dipoles paired with a generic input reduce
to twelve `ell=2,3` cases, whose exact residual minimal polynomials all have
nonzero constant term.  Thus unequal-frequency rest-frame oscillators cannot
feed the exceptional resonance.  Atlas row
`einstein.ph.wm.interaction.exceptional_ell1_k0_difference_frequency_census`
keeps the remaining live global-times-`ell2`-extra coefficient and opposite
nonzero momenta explicitly open.

These nonlinear results are inputs to active Bridge 1; they do not promote
the linear relative triangle to a nonlinear morphism.
See the authoritative queue in
[`universe-building-roadmap.md`](universe-building-roadmap.md#coordinated-eight-hour-work-queue--2026-07-17).

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
