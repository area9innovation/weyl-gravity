# Lorentzian cylinder Cauchy--Sobolev realization

This package supplies the next analytic layer after
`analytic_completion/`.  It starts from the reduced Lorentzian metric
fields on `R x S^3`, proves the local tensor/vector wave factorization,
derives the branch symplectic residues from the quadratic Weyl action, and
identifies the resulting Cauchy spaces with the completed `E/A/L` mode
module.

Five layers are now certified:

1. exact tensor-curl factorization and an all-energy field-theoretic
   `E/A/L` dictionary;
2. a branch Cauchy--Sobolev completion Krein-unitarily equivalent to the
   existing energy-mode one-particle completion;
3. the exact local third-order ghost companion and its biwave factorization;
4. an exact ordinary-derivative four-row symbol witness and an exact
   `66 -> 30` Fourier-complex generalized-auxiliary retract whose formulas
   are finite differential or pointwise maps;
5. the exact curved Hessian/operator identities, local BV-canonical all-row
   retract, and off-shell presymplectic-current comparison.

The fifth layer includes the exact scalar-wave no-go theorem, the reduced
helicity-two Weyl-symbol isomorphism, the exact 26-state Weyl--Cotton system,
the symbolic all-level `E/A/L` curvature audit, and the formally integrable
constraint-adjusted symmetric-hyperbolic realization with compatible
sources.  It does **not** yet include the complete prolonged Green witness or
an actual BV Green homotopy, residual endpoint recovery, equivariant
transport, or prolonged current comparison.  The complete support-local
all-row prolongation retract and prolonged BV differential are already
exact.  This package also does not claim a
direct same-bundle factorization of `H=B_lin+K T/2`.

## Exact minimal ghost witness

On the complete trace-free metric bundle, not merely on harmonics, the
action-normalized local operators obey

```text
T = Box delta-(1/3)d delta^2+(R/3)delta-Ric o delta
    +(1/3)d<Ric,h>,
T K = Box(Box+2),
B_lin K = 0,
H = B_lin+(1/2)K T,
H K = (1/2)K Box(Box+2).
```

The first identity is exhausted on every one-form four-jet at one point;
the Bach operator is reconstructed independently from `C_1^sharp C_1`, and
`C_1 K=0` is exhausted on every third jet.  Homogeneity, parallel cylinder
curvature, and isotropy covariance globalize these finite-order jet
identities.  They are not finite harmonic-cutoff tests.

The ghost operator factors exactly as

```text
Box(Box+2)=(Box-Ric+2)(Box+Ric),
```

because `nabla Ric=0` and `Ric^2=2 Ric` on the unit cylinder.  Both factors
are normally hyperbolic.  The action normalization matters in the graded
witness: choosing backward blocks `(T,2 sharp^{-1},T^sharp)` gives

```text
P_min=diag(TK, 2B+KT, 2B+T^sharp K^sharp, K^sharp T^sharp).
```

Thus the field block is `2H`; this avoids silently losing a factor two.

## Auxiliary symbol witness and support-local retract

A direct product `H=H_-H_+` on every trace-free metric component remains
uncertified.  Even the TT polynomial rules out two scalar
curvature-shifted wave factors: its time and spatial coefficients would
require `a+b=-8` and `a+b=-4` simultaneously.  A direct factor would need a
nontrivial first-order curl and longitudinal extension.  This is kept as a
fail-closed route; the Einstein-background obstruction for the
gauge-invariant conformal wave operator is relevant context, but is not
misused as a no-go theorem for the gauge-completed `H`; see
[Nutma and Taronna](https://arxiv.org/abs/1404.7452).

Instead the repository implements the ordinary-derivative
tensor--tensor--vector realization of
[Metsaev](https://arxiv.org/abs/0707.4437).  Its fields are
`(h_ab,f_ab,v_a)` and its modified de Donder conditions satisfy exactly

```text
delta C0_a=Box xi_-2_a-xi_0_a,
delta C2_a=Box xi_0_a,
delta C1=Box sigma.
```

Hence the combined ghost principal symbol is `zeta^2 I_9`.  The
24-component quadratic Hessian is now reconstructed from the exact
ordinary-derivative action, rather than supplied only through its expected
principal part.  In Fourier-symbol notation it satisfies

```text
E_aux(-zeta)^T=E_aux(zeta),
E_aux(zeta) K_aux(zeta)=0,
Y_ghost C_aux(zeta)=K_aux(-zeta)^T J_aux.
```

The modified de Donder gauge-fixing density is
`-C0.C2-C1^2/2`.  In the earlier Fourier symbol model the proposed completion
was

```text
P_field=J_aux^{-1} E_aux+K_aux C_aux
```

with a scalar-symbol target.  The exact action-derived curved Hessian below
shows that this target cannot be realized on the present 24-field/9-gauge
bundle.  The Fourier contraction remains a useful algebraic model, but is
not promoted as the curved Green witness.

The local unipotent change

```text
eta=xi_0-d sigma,
f_hat=f+2 d_(a v_b)
```

isolates the exact Stueckelberg doublet `Qv=-eta`.  The remaining auxiliary
tensor has the pointwise equation

```text
f_hat=-2G^v+(2/3)g tr(G^v),
```

and substitution returns `Ric^2-R^2/3` in the `v=0` gauge.  Both the change
and its inverse are finite differential maps, while the only inverse in the
auxiliary elimination is pointwise algebraic.  They therefore preserve
compact and spacelike-compact support.

For the flat auxiliary BV complex the modified de Donder companion, inverse
field pairing, and formal adjoint form a graded self-adjoint witness
`W_aux`.  The emitted 66-by-66 symbol matrices verify exactly
`Q_aux^2=0`, `P_aux=Q_aux W_aux+W_aux Q_aux`, and
`W_aux^sharp=W_aux`, with scalar metric diagonal symbols.  The analogous
curved scalar-symbol claim is now known to be impossible for the present
24-field/9-gauge bundle: at a null covector `rank(E2)=11` but `rank(K1)=9`,
so no term `K1 C1` can cancel the Hessian symbol for any pointwise
nondegenerate fibre identification.  A repaired Green-hyperbolic operator
would still supply unique causal Green operators `G_plus/minus`, after which

```text
Lambda_plus/minus=W_aux G_plus/minus
```

formally obeys `Q Lambda+Lambda Q=1`.  The recognition identity is exact in
the flat witness model; the preferred missing curved input is a local
Weyl-curvature prolongation with causal Green evolution, not another scalar
completion of the original field bundle.

The stronger Fourier-complex equivalence statement is also exact.  Shifting the
auxiliary tensor by its pointwise equation-of-motion solution block
diagonalizes the Hessian and makes the shifted tensor gauge invariant.  With
`eta=xi_0-d sigma`, the remaining added cotangent sector consists of the
three arrows `eta -> -v`, `f_hat -> M f_hat^*`, and
`v^* -> -eta^*`.  Explicit `66 x 30` inclusion/projection matrices and a
36-dimensional homotopy verify both chain-map identities and
`i p-1=Qk+kQ`.  All formulas are finite differential or pointwise maps and
therefore preserve compact, spacelike-compact, and unrestricted smooth
support.  Their complete curved lower-order chain identities are included in
the global certificate.  The trace/Weyl and
nonminimal doublets attach as the previously certified pointwise summands.
No local conformal-Killing projector is used.

## Curl identities and reduced Green operators

On unit `S^3`, with repository curvature convention,

```text
C_2^dagger=C_2,   C_2^2=-D^2+3     on TT tensors,
C_1^dagger=C_1,   C_1^2=-D^2+2     on transverse one-forms.
```

The exact Lorentzian reduced operators are

```text
P_minus = d_t^2+(C_2-1)^2,
P_plus  = d_t^2+(C_2+1)^2,
B_TT    = P_minus P_plus,
P_A     = d_t^2+C_1^2.
```

Each second-order factor has wave principal part and only first- or
zeroth-order corrections.  The tensor factors preserve the TT constraint,
and the vector factor preserves transversality.  Thus the reduced physical
blocks have advanced and retarded Green operators.  For
`B_TT=P_minus o P_plus`, the ordered composition is
`G_B=G_Pplus o G_Pminus`.  Closure of Green-hyperbolic operators under
composition and direct sum is the external theorem used here; see
[Bär](https://arxiv.org/abs/1310.0738).

The local `C_2` factorization and the spectral `|C_2|` split have different
roles.  Local factors establish propagation.  The spectral operators

```text
A_E=|C_2|-1,   A_L=|C_2|+1,   A_A=|C_1|
```

define polarization and Sobolev topology.  The `E/L` split is spatially
nonlocal and is not asserted to preserve causal support.

## Exact field origin of the towers

At compact energy `N`, including both chiralities,

```text
E: lower TT,          2(N-1)(N+3),  N>=2,
A: transverse vector,2(N-1)(N+1),  N>=3,
L: upper TT,          2(N-3)(N+1),  N>=4.
```

The full transverse-vector curl spectrum contains an energy-two Killing
band.  It is absent from the metric `A` branch because the symmetrized
gradient of a Killing field vanishes.  Consequently the physical `A`
spectrum starts at three, not two.

The Euclidean operator and harmonic frequencies agree with the Weyl-graviton
calculation of
[Beccaria, Bekaert, and Tseytlin](https://arxiv.org/abs/1406.3542), but the
Lorentzian signs, curl identities, constraints, and symplectic residues are
certified independently here.

## Field residues and Sobolev orders

For `S=-alpha_g integral C^2`, `alpha_g>0`, the reduced metric-field action
gives the positive residue magnitudes

```text
R_E=4|C_2|,       sign +,
R_A=2(A_A^2-4),  sign -,
R_L=4|C_2|,       sign -.
```

The vector residue is elliptic of order two.  This corrects the tentative
order-zero possibility in the project brief.  Since every branch energy
operator has order one, the Cauchy spaces are

```text
E: H^1_TT     + L^2_TT,
A: H^(3/2)_T + H^(1/2)_T,
L: H^1_TT     + L^2_TT.
```

For each branch,

```text
z = 2^(-1/2) [sqrt(RA) q + i sqrt(R/A) p].
```

The certified cylinder mode normalizations satisfy
`2 R(N) N |mode(N)|^2=1`.  Hence the harmonic transform sends the
field-induced positive norm to the normalized mode `l2` norm and intertwines
the field signs with `J_conf=+1_E-1_A-1_L`.  Density and the exact
all-energy multiplicity match extend this map to a Krein-unitary
isomorphism onto the one-particle space in `analytic_completion/`.

Raw fourth-order TT data use the pullback graph norm under the exact branch
map.  No standard product-Sobolev description of
`(h,h_dot,h_ddot,h^(3))` is asserted.

## Reproduce

```bash
python3 symbolic/verify_conformal_covariant_completion.py --emit --guards
```

Generated theorem text is in `covariant_completion/generated/`; exact proof
summaries are in `covariant_completion/certificates/`.

The final-claim dependency graph is generated separately:

```bash
python3 symbolic/verify_conformal_covariant_dependency_report.py --emit --guards
```

Its machine-readable form is
`certificates/final_claim_dependencies.json`; the human report is
`generated/final_claim_dependencies.md`.  The graph distinguishes the three
proved curved lemmas from the remaining terminal transport gate:

```text
curved_operator_identity       = true
curved_deformation_retract     = true
curved_current_comparison      = true
final_covariant_H4             = false
```

Every downstream claim is computed from its declared dependencies.
`support_preserving_metric_equivalence` is already true;
`complete_bv_green_hyperbolicity`, `pairing_compatibility`, and
`final_covariant_H4` remain false until a non-scalar Green realization is
certified.  The already-proved algebraic and energy-mode result
`H4 = C^2`, `G = I2` is an
independent theorem and is not downgraded by this covariant status report.

The terminal layer is transport-only:

```bash
python3 symbolic/verify_conformal_final_covariant_transport.py --emit --guards
```

It does not recompute cohomology in the 24-component auxiliary variables.
Its `final_covariant_H4` value is computed from exactly

```text
curved_operator_identity
and curved_deformation_retract
and curved_current_comparison
and scalar_wave_witness_no_go
and weyl_symbol_helicity_isomorphism
and curved_EB_equations
and curved_EB_first_order_closure
and curved_EB_symmetric_hyperbolicity
and curved_sourced_constraint_identity
and curved_constraint_propagation
and EAL_curvature_spectrum_match
and support_local_prolongation_retract
and prolonged_BV_operator_identity
and prolonged_green_witness
and curvature_causal_green_operators
and causal_green_homotopy
and causal_quasi_isomorphism
and residual_endpoint_recovery
and SO42_equivariant_transport
and prolonged_current_comparison
and residual_H4_is_C2
and residual_gram_is_I2.
```

The algebraic residual theorem, curved operator/retract/current lemmas,
scalar-wave no-go, reduced Weyl-symbol theorem, exact curved `E/B` equations,
their 26-state Weyl--Cotton first-order closure, and the symbolic all-level
`E/A/L` curvature spectrum theorem are already true.  The
first-order theorem is backed by a 34-by-26 exact covariant coefficient table
and exhaustive 150/150 Weyl two-jet globalization.  The apparent rank-six
pointwise row defect is exactly generated by the six secondary constraints,
so the covariant and adjusted differential ideals coincide.  Symmetric
hyperbolicity, sourced compatibility, constraint propagation, and the
all-level spectrum are true.  The coefficientwise graded mapping cylinder now
also proves the complete all-row support-local prolongation and prolonged BV
operator identity.  Conjugating the canonical direct-sum witness gives an
exact degree-minus-one operator identity and fourteen certified Green split
blocks, but the auxiliary field block `E_aux+K C` and its cotangent copy retain
the scalar-wave obstruction.  Closing the witness therefore requires a
genuinely coupled two-way relative auxiliary--curvature block, unless the
auxiliary diagonal is independently replaced by a Green-hyperbolic witness.

The generic prenormal-symbol diagnostic is nevertheless exact.  Writing
`q=g^{-1}(zeta,zeta)` and `P2=J_act^{-1} E2+K1 C1`, it proves
`(P2-q I24)^2=0` and the polynomial inverse identity
`(2q I24-P2)P2=P2(2q I24-P2)=q^2 I24`.  The Smith ledger is exactly
`6/12/6`: six algebraic, twelve wave, and six biwave factors.  This does not
yet globalize to a local operator factorization.  The naive frozen completion
`2q I-P` has nonzero lower-order remainders (orders zero, one, and two), so
only that literal completion is rejected; corrected first-order factors and
the full covariant composition remain open.

The complete invariant lower-order ansatz makes that remaining question
finite.  Cylinder holonomy gives `dim D0=38` and `dim D1=93` for
`D=D_naive+X1^mu nabla_mu+X0`.  Exact simultaneous cubic divisibility of both
`D P` and `P D` leaves a 45-parameter family, hence there is no cubic
obstruction.  The full curvature-corrected problem is now assembled as an
exact sparse quadratic symmetrized-PBW system.  Its derivative-order row
ledger is `240/960/2484` at orders zero/one/two, with no residual cubic or
quartic rows after the cubic parameterization.  This gate still proves
neither factorization nor Green hyperbolicity because the projected
polynomial equations have not been solved.

The cubic kernel is not the complete nonlinear variable space.  The cubic
equations see only the sums of the two first-order factor coefficients.
Restoring one 93-parameter splitting for each of `D P` and `P D`, plus the
38-parameter `X0` and four independent 38-parameter factor potentials, gives
`45+2*93+5*38=421` unknowns after the cubic gate.  The normalization of each
factor principal symbol to `q I24` is without loss for invariant factors: a
parallel invertible `q H/q H^-1` pair can be redistributed algebraically.
The general 421-variable system has an exact order-two Schur gate.  The
fixed algebraic matrix has shape `2484 x 190`, rank 100 and cokernel
dimension 2384, so 90 algebraic variables remain free.  Projecting against
that cokernel produces 2,130 nonzero polynomial constraints, 365 up to
scale, and no constant polynomial obstruction.  Orders one and zero also
remain to be solved.

An independent backend audit corrected the covector curvature action from a
four-dimensional delta to the required raised spatial projector; mixed
time--space curvature now vanishes and the exact coordinate-jet commutator
and `div symgrad=Box+grad div+Ric` identities pass.  Symmetrized order-two
conversion and focused vector/tensor `Box^2` coordinate-jet compositions also
pass.  Exact triangular symmetrized-jet PBW inversion exhausts the 1,680
four-jet basis elements, passes 504 ordered-word round trips and certifies
associativity, so the quadratic-factor composition backend is ready.
However, componentwise transpose/reversal of an already sorted `Box^2` table
leaves 48 entries.  This diagnoses an invalid naive adjoint—the sorted
coefficient matrices do not individually retain their derivative-index
slots—not an independent counterexample to primal composition.  The required
pairing-aware adjoint is now implemented on the symmetrized-PBW coefficient
tensors.  It verifies `P^sharp=P`, `D_naive^sharp=D_naive`, and
`(DP)^sharp=PD` exactly.  Requiring `D^sharp=D` reduces the invariant
first-order family from 93 to 44 dimensions and the algebraic family from 38
to 24; the exact cubic matrix has shape `11520 x 137`, rank 116 and a
21-dimensional solution.  With `R_minus=L_plus^sharp` and
`R_plus=L_minus^sharp`, the right equations are adjoints rather than
independent unknowns.  The resulting sharp branch has 214 nonlinear
parameters.  Its exact order-two gate contains 1,242 rows.  The 100
algebraic variables have rank 52, leaving 48 free directions, and exact
cokernel projection gives 1,050 nonzero constraints (179 up to scale) with
no constant obstruction.  The projected quadratic constraints and orders
one and zero remain unsolved and unpromoted.  Exact span reduction confirms
that all 179 normalized constraints have maximal degree two.  Their 1,497
quadratic monomials have rank 124; the resulting 55 left-kernel combinations
have identically zero affine part, so no variable is eliminated without a
genuinely nonlinear ideal calculation.

The exact bare-`Box` subfamily is now decided.  For each of the four choices
of whether the bare wave factor is inner or outer in `D P` and `P D`, the
complete symmetrized-PBW system has 159 unknowns, coefficient rank 159 and
augmented rank 160.  A common one-row left-null certificate is the
`nabla_(0)nabla_(1)` coefficient `f_01 -> f_00`: its right-hand side is `-8`
and all 159 correction columns are zero.  This is a scoped no-go only.  The
general branch has nonzero first-order terms in both factors, and the
quadratic `A_minus A_plus` contribution has now been shown to repair that row
together with its full `SO(3)` orbit `f_0i -> f_00`.  The support-minimal
rational repair has zero first-order sum and uses two invariant basis
directions.  Fixing precisely that split does not solve the rest of order
two: after exhausting all 190 invariant algebraic variables, the
simultaneous system has shape `1377 x 190`, rank 100 and augmented rank 101.
Its one-row left-null witness is `nabla_(0)nabla_(1): h_22 -> f_01` with
required value 16.  This rejects only the fixed minimal split; other splits,
the general 421-variable system and the 214-parameter sharp branch remain
open.

The exact degree-one Macaulay screen for this sharp branch has 136,585 rows
and 20,585 columns.  An exact modular minor over a denominator-safe prime
proves `12861 <= rank_Q(degree 3) <= 14136`.  Full rational ranks were not
computed, so neither constant ideal membership nor exact low-degree
elimination dimensions are inferred.

The exhaustive relative-incidence search also identifies, without promoting
a flag, the smallest reciprocal saddle: odd-adjoint pairs 4 and 5.  On the
core ordered as `(M_aux,X_U,Y_U_sharp)` its degree-zero block is

```text
[ E_aux+K C    R             S           ]
[ Ssharp E_aux L_26          0           ]
[ Rsharp E_aux 0             L_26sharp   ]
```

No single allowed pair is two-way.  Eliminating the curvature diagonal gives
an exact finite-block Schur formula, but its complement contains the Green
operators of `L_26` and `L_26sharp`, hence is nonlocal and is not an accepted
support-local witness proof.  The unreduced saddle has order two; explicit
coefficient tables for a more general `R,S` family and a local first-order
reduction of every `E_aux` occurrence are still required.  In particular, the
natural exact choice `A_F=p_F A_equation`, `S=A_F^sharp`,
`R=A_F^sharp J_U` fails the balanced Douglis timelike test.  The complete
degree-zero principal matrix has rank at most `107/116` (defect at least
nine), so its temporal characteristic leading coefficient is zero and no
positive temporal symmetrizer exists.  This is an exact no-go only for that
smallest pair-4+5 realization; it does not exclude larger relative witnesses
or an added support-local first-order prolongation.

The expanded-relative incidence problem is coefficientwise complete.  Exact
rotation generators in the actual component bases of all sixteen blocks give
the nine commutant nullities `4/18/4/36/14/14/22/36/14`, hence a
162-dimensional Hom family, and
exact incidence finds three minimal reciprocal two-pair candidates: `1+6`,
`1+7`, and `2+7`.  Even after all reciprocal curvature partners are included,
the maximum ranks on the two 24-dimensional central auxiliary blocks are
21, so three rotation-scalar directions remain uncovered in each.  Thus any
ansatz which makes the complete central auxiliary diagonal subprincipal has
temporal rank defect at least three.  A viable expanded witness must retain
or support-locally prolong those scalar directions.  Coefficients,
characteristics and a symmetrizer remain open; no Green flag is promoted.
The explicit pair-`1+6` maps and the `K`, `Ncurvsharp`, vector-projector and
scalar-diagonal coefficients all have zero rotation-generator defect.
The three uncovered scalar coordinates are exactly `h_00`, `f_00`, and
`v_0`.  Restricting the existing `K C` coefficient to them gives a rank-three
triangular matrix of determinant `-1`.  For pair `1+6`, explicit local
coefficient maps verify
`K R1 Ncurvsharp R6sharp = -Pi_vector` coefficientwise; the sign is the
first-order compact-support adjoint sign.  The actual temporal
curvature diagonal is
`D(dt)=diag(I_26,-I_40,-I_26)`, so `D^-1=D` and the exact saddle Schur term is
`B D^-1 C=+Pi_vector`, so the field Schur block is
`Eaux_2+Dscalar-Pi_vector`.  After retaining the scalar diagonal, the assembled
`116 x 116` temporal Douglis symbol has exact rank 116 and determinant one.
This is a temporal-invertibility certificate only: `R6sharp` still needs its
three spatial first-order coefficients, the rank-three diagonal still needs
a cyclic all-row witness lift, and the arbitrary-covector
characteristics, a positive symmetrizer, lower-order coefficients and every
BV degree remain open.

The exact equivariant completion has dimensions 22 (temporal) and 46
(spatial-vector).  Fixing the certified temporal coefficient leaves all 46
spatial parameters, but their direct intrinsic pencil sensitivities on
`a0=2 f_23`, `a1=h_23` vanish identically.  Every regular member therefore
retains the length-two root at `z=1`; this fixed-temporal pair-`1+6`, cyclic
`-2 Pi` family cannot furnish a semisimple faithful strong reduction or a
positive symmetrizer.  No broader Green-hyperbolicity no-go is claimed.

The Jordan chain is now classified homologically: `2 f_23` lies in the
existing shifted-auxiliary contraction, whereas `h_23` is the physical Weyl
helicity-two class.  The extension splits after the support-local BV shift.
On the aligned physical principal block it is a triangular biwave and has
the exact recursive same-sided Green formula `[[G,0],[-G R G,G]]`; hence the
Jordan chain itself is causal, not a Green obstruction.  Refining the
operator support ledger leaves one reciprocal rank-34 `(h,f,Csharp)` block
plus a rank-four vector singleton.  Exposing their physical quotient by
local curvature/Bianchi maps, with full lower-order coefficients and no
helicity projector, is the current Route-A gate.  Pairs `1+7` and `2+7`
have nonzero intrinsic sensitivity (joint rank 16) and remain live Route-B
incidences.  The smallest temporally regular slices for both have determinant
`8` and real causal roots but fail semisimplicity at `0,+1,-1`; the first
direct-sensitive spatial correction does not fix either slice.  The full
alternative families remain open.  The minimal 16-parameter subfamily that
surjects onto the complete sensitivity image is now ruled out uniformly as
well: the zero-root valuation/kernel bounds are `40/33` for pair `1+7` and
`48/47` for pair `2+7`.  This is not a no-go for the raw 122-parameter
families or for generalized Green extensions.

For the aligned channel the support-local BV shift itself is also explicit:
with `L=1-z^2`, the complex block becomes `diag(L^2,-1)`, while the fixed
witness remains `[[L,0],[4,L]]` and has exact same-sided inverse
`[[G,0],[-4 G^2,G]]`.  This separates the retained physical biwave from the
pointwise auxiliary contraction without using a nonlocal projector; the
remaining gate is its full 116-row local exact-extension realization.

The exact TT-plus-`fhat` operator subcomplex now warrants the scoped positive
flags `physical_biwave_block_green_hyperbolic=true` and
`physical_Jordan_extension_causal=true`.  Its witness is
`diag(B_TT,1,B_TT,1)` and its restricted Green homotopy identity is exact.
The complete prolonged flags remain false because arbitrary-source local
access to this block and inverses for the rank-34 and rank-four blocks have
not yet been constructed.

The rank-34 reciprocal block now has a projector-free differential
filtration.  Its rank-12 gauge/subsidiary submodule has an exact recursive
Green inverse, and the rank-22 quotient contains a closed rank-8
symmetric-hyperbolic constraint quotient plus an unresolved rank-14 field
cokernel.  Curvature descends to the latter by `(C1,div C1) K=0`; the induced
biwave quotient intertwiner remains open.  The raw coupling ideal is not
nilpotent, excluding the simplest finite-Neumann shortcut.

The separate rank-four vector singleton is solved exactly as the shifted
`(eta,v,vsharp,etasharp)` contraction.  A replacement witness yields
`P=I_16`, same-sided inverses `G_+=G_-=I_16`, and exact homotopies
`Lambda_+=Lambda_-=W`; its causal propagator is zero.  The corresponding
scoped atomic flags are true.  Only the rank-14 field cokernel and all-row
assembly remain on this filtration.

The all-row assembly is now an exact conditional theorem.  Its rank ledgers
`116=34+4+26+26+26` and `34=12+8+14` cover every analytic component once;
all 16 mapping-cylinder BV rows, cotangent tails and the canonical shear are
bound coefficientwise.  Conditional on the rank-14 curved operator/adjoint,
compatible-source Green maps and two source-lift equations, the formal
assembly proves two-sided `G`, chain commutation and the complete Green
homotopy identity.  No other analytic block is missing.

The final input package is
`certificates/curved_rank14_weyl_cotton_input_manifest.json`.  It references,
by path and SHA-256, the exact quotient maps, full 26-state evolution/lower
tables, 14 constraints and subsidiary system, source compatibility,
symmetrizers, BV row order, adjoints and current conventions.  Large matrices
remain single-source rather than being copied into the manifest.

The principal rank-14 quotient is now explicit and projector free.  It has a
local rank-10 wave/rank-4 temporal filtration, exact same-sided Green algebra
and causal source lifting modulo the certified gauge image.  The direct
curvature map nevertheless has symbol rank `5` and kernel rank `9`, while
the compatible Weyl--Cotton source kernel has rank `12`.  The raw curvature
image is not a submodule of that kernel off shell: the generic defect of the
weighted compatibility symbol has rank `3`, falling to rank `1` on the
aligned null cone.  Consequently `K12/I5` is not a legitimate rank-seven
quotient.  The exact operator chain-square replacement is the equation cone
`That=(T,E_aux)`, `Khat=(K_state,-A_C)`, with `Khat That=0`; the full bridge
must be an SDR of the complete `(L_WC,K_state)` equation complex.  The full
graded audit restores the incoming gauge row, giving ranks
`9 -> 24 -> 50 -> 49 -> 14`, and uses the ordinary BV identity layer rather
than the Green-witness companion.  The exact curved identity differs by a
rank-four background block that must be placed by the same Rees filtration.
With the currently mixed principal extractions, the internal cone squares
have ranks `11,4` generically and `7,4` at null.  They are not yet a symbol
complex, so no cone cohomology is claimed.  The next gate is a common
componentwise Douglis/Rees filtration.  Its integer weight constraints are
feasible; what remains is the complete associated-graded coefficient
extraction, especially lower `A` and weighted zeroth WC blocks.  Curved
lower terms, `V14`, cotangent adjoints, the equation SDR and all-row Green
insertion remain open.

The remaining six flags isolate that prolonged Green witness, the actual
causal chain homotopy, residual endpoint recovery, and `SO(4,2)` equivariance.
The all-row prolonged current transport is exact off shell; its equality with
the Green pairing remains a downstream causal consequence.
The terminal stage transports the existing `H4 = C^2`, `G = I2`; it must not
recompute the residual CE complex.

### Four-flag closure workstreams

The repository now has separate, fail-closed implementations for the three
curved lemmas feeding that terminal conjunction:

```bash
python3 symbolic/verify_conformal_curved_operator_workstream.py --emit --guards
python3 symbolic/verify_conformal_curved_retract.py --emit --guards
python3 symbolic/verify_conformal_curved_current.py --emit --guards
```

The operator workstream derives the covariant auxiliary action, the exact
curved `24 x 9` gauge map (including the background-auxiliary Lie derivative),
the complete canonical coefficient table of the curved Hessian, and exact
formal adjoints.  All 630 potentially surviving order-three/four jets vanish.
It also records a decisive negative result: at the null covector
`(1,1,0,0)`, the Hessian principal symbol has rank 11 while the gauge symbol
has rank 9.  Hence no pointwise nondegenerate fibre form and no first-order
companion can give the current 24-field system scalar wave symbol.  The
normalized obstruction quotient is two-dimensional and is represented by
the transverse helicity-two pair `f_22-f_33`, `f_23`.  The associated metric
domain pair is `h_22-h_33`, `h_23`, the physical Hessian block is `4 I2`, and
the little-group generator has weights `+2i,-2i`.

The linearized Weyl symbol supplies the positive replacement at symbol
level.  It induces `(1/4) I2` between the exact reduced Hessian quotient and
the two-dimensional Weyl quotient, hence is an isomorphism on the physical
helicity-two module.  This is deliberately stated on the reduced quotient:
the repository does not claim `ker(W_2)=im(K_1)` on the full field bundle,
where auxiliary and contractible directions remain.

The original electric/magnetic principal-symbol seed lives on
`STF_2(S^3)_E + STF_2(S^3)_B` and has the schematic form

```text
partial_t E-curl_2 B=lower order,
partial_t B+curl_2 E=lower order
```

Its principal divergence identity
`div(curl_2 h)=(1/2)curl_1(div h)` is now only a regression seed.  Exact
decomposition of the curved Bianchi/Bach equations requires the ten `E/B`
components plus sixteen Cotton components.  The resulting 26-state system,
all lower-order cylinder terms, constraint-adjusted positive symmetrizer,
sourced subsidiary identity, and propagation of all fourteen constraints
are certified from the covariant equations rather than inferred from this
principal block.

The retract workstream proves the exact nonlinear auxiliary completion of the
square, its local BV-canonical cotangent lift, conjugation of the complete
curved four-row `Q`, the all-row SDR (including trace and nonminimal rows), and
support preservation in all three support categories.

The current workstream derives both curved presymplectic potentials and the
exact off-shell `d + Q` improvement under the same BV-canonical shift.  The
Cauchy current and `E/A/L` regression close; the Green/current equality
remains downstream of whichever Green-hyperbolic repair replaces the
impossible scalar-symbol witness.

These exact results appear as true scaffold nodes in the generated dependency
report.  Three requested flags are true; only `final_covariant_H4` remains
false.  The certified local Weyl-curvature prolongation propagates the
helicity-two quotient rather than cancelling it as gauge.  What is missing is
its complete causal BV Green realization, not the curvature propagation
theorem.  The curvature compatibility complex and cotangent adjoint, the
BV-canonical Weyl/Cotton graph SDR, and the analytic block witness are also
exact.  The local equation and identity chain maps are now exact as well:
the equation square is exhaustive on all 700 metric four-jets, and the
sparse identity square retains the differentially generated secondary rows.
Their common degree/sign-resolved odd BV mapping cylinder, Koszul adjoints,
nilpotent differential, and support-local SDR are now exact.  The same odd
cyclic pairing gives a coefficientwise complete quadratic BV parent on all
sixteen blocks and the local off-shell identity
`I^* omega_prol-omega_aux=d beta+Q gamma`.  The prolonged Green witness and
homotopy, residual endpoints, and equivariance remain open.  A genuinely
curvature-prolonged realization is now the selected final dependency gate.

The compact four-flag view is reproduced with

```bash
python3 symbolic/verify_conformal_four_flag_closure.py --emit --guards
```

and is stored in `certificates/four_flag_closure_status.json`.

## Remaining covariant comparison

The general Green-hyperbolic-complex framework says that a local Green's
witness yields retarded/advanced Green homotopies and comparison of
covariant and fixed-time Poisson structures up to homotopy; see
[Benini, Musante, and Schenkel](https://arxiv.org/abs/2207.04069).

For pure Weyl gravity the curved operator identities, support-local retract,
and off-shell current comparison are discharged.  The remaining analytic
task is to construct a local curvature-prolonged complex and prove a
pairing-compatible causal BV bridge, not merely causal evolution of its
physical Weyl helicities.  The electric/magnetic candidate has now been
derived as the exact 26-state Weyl--Cotton system; its curved lower-order
terms, sourced constraints, formal integrability, and all-level `E/A/L`
audit and all-row BV-canonical mapping cylinder are exact.  The remaining
work is the Green witness and homotopy, endpoint
recovery, equivariant transport, and prolonged current comparison.  Only
after that theorem can the causal
quasi-isomorphism and Green/current pairing equality be promoted.  A
direct same-bundle metric factorization is an optional strengthening, not an
input to the prolongation route.

This package does not claim arbitrary backgrounds, a direct same-bundle
factorization of `H`, a local TT projector, a causal `E/L` branch split, a
Hadamard theorem, positivity, or an interacting Cauchy problem.
