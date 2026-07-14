# Lorentzian cylinder Cauchy--Sobolev realization

This package supplies the next analytic layer after
`analytic_completion/`.  It starts from the reduced Lorentzian metric
fields on `R x S^3`, proves the local tensor/vector wave factorization,
derives the branch symplectic residues from the quadratic Weyl action, and
identifies the resulting Cauchy spaces with the completed `E/A/L` mode
module.

Four layers are now certified:

1. exact tensor-curl factorization and an all-energy field-theoretic
   `E/A/L` dictionary;
2. a branch Cauchy--Sobolev completion Krein-unitarily equivalent to the
   existing energy-mode one-particle completion;
3. the exact local third-order ghost companion and its biwave factorization;
4. an exact ordinary-derivative four-row symbol witness and an exact
   `66 -> 30` Fourier-complex generalized-auxiliary retract whose formulas
   are finite differential or pointwise maps.

The fourth statement uses the explicitly permitted auxiliary-field route.
The complete curved first/zeroth-order witness and retract identities,
covariant integration-by-parts adjoint check, and auxiliary Green-current comparison
remain separate obligations.  It also does **not** claim a direct
same-bundle factorization of `H=B_lin+K T/2`.

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
`-C0.C2-C1^2/2`.  Consequently

```text
P_field=J_aux^{-1} E_aux+K_aux C_aux
```

has principal symbol `zeta^2 I_24`; both `J_aux` and the ghost pairing
`Y_ghost` are nondegenerate.  Thus the wave symbol, its normalization, and
formal adjointness are solved simultaneously rather than guessed.  These
scalar metric principal symbols are the necessary normally-hyperbolic
symbols.  The repository does not promote them to a curved Green theorem
until the complete first- and zeroth-order cylinder coefficients and their
integration-by-parts adjoints have been reconstructed as global differential
operators.

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

For the auxiliary BV complex the modified de Donder companion, inverse
field pairing, and formal adjoint form a graded self-adjoint witness
`W_aux`.  The emitted 66-by-66 four-row symbol matrices verify exactly
`Q_aux^2=0`, `P_aux=Q_aux W_aux+W_aux Q_aux`, and
`W_aux^sharp=W_aux`.  Every diagonal symbol is scalar metric.  Once the
curved lower-order operators and adjoints are certified as global
differential operators, normal hyperbolicity supplies unique causal Green operators
`G_plus/minus`,

```text
Lambda_plus/minus=W_aux G_plus/minus
```

formally obeys `Q Lambda+Lambda Q=1` once the curved degreewise Green
operators have been constructed.  This is the exact Green-witness
recognition identity, not yet the missing curved coefficient certificate.

The stronger Fourier-complex equivalence statement is also exact.  Shifting the
auxiliary tensor by its pointwise equation-of-motion solution block
diagonalizes the Hessian and makes the shifted tensor gauge invariant.  With
`eta=xi_0-d sigma`, the remaining added cotangent sector consists of the
three arrows `eta -> -v`, `f_hat -> M f_hat^*`, and
`v^* -> -eta^*`.  Explicit `66 x 30` inclusion/projection matrices and a
36-dimensional homotopy verify both chain-map identities and
`i p-1=Qk+kQ`.  All formulas are finite differential or pointwise maps and
therefore preserve compact, spacelike-compact, and unrestricted smooth
support.  Their complete curved lower-order chain identities remain in the
global certificate.  The trace/Weyl and
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
`generated/final_claim_dependencies.md`.  The graph distinguishes proved
structural facts from three still-false curved lemmas:

```text
curved_operator_identity       = false
curved_deformation_retract     = false
curved_current_comparison      = false
```

Every downstream claim is the conjunction of its declared dependencies.
In particular, `complete_bv_green_hyperbolicity`,
`support_preserving_metric_equivalence`, `pairing_compatibility`, and
`final_covariant_H4` remain false until their inputs are certified.  The
already-proved algebraic and energy-mode result `H4 = C^2`, `G = I2` is an
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
and causal_quasi_isomorphism
and CKV_recovery
and residual_no_duplication
and energy_H4_is_C2
and energy_gram_is_I2.
```

The last two inputs are already true; the terminal value remains false while
any curved or causal input is false.

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
the cylinder curvature identities, and a canonical parallel-curvature
derivative normal form.  It does **not** yet claim the full curved Hessian,
companion, witness identity, adjoint table, or exhaustive globalization.

The retract workstream proves the exact nonlinear auxiliary completion of the
square, its local BV-canonical cotangent lift, a universal shifted auxiliary
SDR, and support preservation.  It does **not** yet claim that the complete
curved four-row `Q` has been conjugated into this split or that every trace and
nonminimal row has been reattached.

The current workstream derives exact action/Fourier Green currents for the
auxiliary and eliminated metric Hessians, the full differential-inclusion
chain-rule current, and an explicit antisymmetric improvement whose Cauchy
time component differs by a spatial divergence.  It does **not** yet replace
the missing curved presymplectic potentials or prove the curved off-shell
`d + Q` and Green/current identities.

These exact partial results appear as true scaffold nodes in the generated
dependency report.  The four requested terminal flags remain false until the
remaining operator-level certificates pass; no flag is manually editable.
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

For pure Weyl gravity the symbol-level recognition identities and the exact
Fourier-complex auxiliary retract with support-local formulas are now
discharged.  Two
programme-specific analytic tasks remain before the Green-complex theorem:
the curved lower-order witness/retract/adjoint reconstruction and the complete
cohomological comparison of the resulting causal pairing with the fixed-time
BV pairing and the already-certified energy-mode Krein form.  A direct
same-bundle metric factorization is an optional strengthening, not an input
to the auxiliary route.

This package does not claim arbitrary backgrounds, a direct same-bundle
factorization of `H`, a local TT projector, a causal `E/L` branch split, a
Hadamard theorem, positivity, or an interacting Cauchy problem.
