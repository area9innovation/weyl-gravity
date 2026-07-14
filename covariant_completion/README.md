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
helicity-two Weyl-symbol isomorphism, and the symmetric-hyperbolic algebra
and principal constraint closure of the candidate electric/magnetic Weyl
evolution.  It does **not** yet include the curved Bianchi/Bach lower-order terms, full constraint propagation, the local
prolongation retract, or causal Green operators, and it does not claim a
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
and curved_EB_equations
and curved_EB_symmetric_hyperbolicity
and curved_constraint_propagation
and support_local_prolongation_retract
and curvature_causal_green_operators
and causal_quasi_isomorphism
and CKV_recovery
and residual_no_duplication
and energy_H4_is_C2
and energy_gram_is_I2.
```

All algebraic, operator, retract, current, and energy inputs are now true.
The five displayed curvature-propagation flags remain false.  They isolate
the exact E/B equations, symmetric hyperbolicity, full constraint evolution,
support-local prolongation retract, and causal Green operators.

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

The candidate electric/magnetic Weyl evolution has also passed its internal
principal-symbol test.  On
`STF_2(S^3)_E + STF_2(S^3)_B`, the ten-component system

```text
partial_t E-curl_2 B=lower order,
partial_t B+curl_2 E=lower order
```

has `A0=I_10`, a positive STF symmetrizer, symmetric spatial symbol after
symmetrization, and physical characteristic speeds `+1,-1`.  Its principal
divergence constraints close exactly through
`div(curl_2 h)=(1/2)curl_1(div h)`.  This proves principal symmetric
hyperbolicity and principal constraint propagation only; it does not derive
this block from the curved Bianchi/Bach equations, nor their lower-order
terms or full constraint evolution.

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
false.  The preferred missing construction is a local Weyl-curvature
prolongation with a certified causal Green realization.  Such a prolongation
must propagate the helicity-two quotient rather than cancel it as gauge; no
complete curvature propagation theorem is claimed here.  The principal
candidate symmetric-hyperbolicity and constraint-closure tests have passed,
but derivation from the prolonged equations, their lower-order terms, full
constraints, prolongation SDR, and Green operators remain open.  A genuinely
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
task is to construct a local curvature-prolonged complex and prove causal
Green evolution of its physical Weyl helicities.  The electric/magnetic principal
candidate block is already symmetric hyperbolic and its principal constraints
close; the remaining work is to derive it from the prolonged equations and
complete the curved lower-order terms, full constraint propagation, local equivalence,
and Green construction.  Only after that theorem can the causal
quasi-isomorphism and Green/current pairing equality be promoted.  A
direct same-bundle metric factorization is an optional strengthening, not an
input to the prolongation route.

This package does not claim arbitrary backgrounds, a direct same-bundle
factorization of `H`, a local TT projector, a causal `E/L` branch split, a
Hadamard theorem, positivity, or an interacting Cauchy problem.
