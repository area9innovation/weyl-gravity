# Prolonged Green-witness design audit

## Fixed input

The comparison starts after the exact odd BV mapping cylinder has been put in
split coordinates.  Its differential is the direct sum of the auxiliary
four-row complex and two contractible copies of the curvature compatibility
complex

```text
U[26] --(L,K)--> F[26] + C[14] --(-R,S)--> I[14],
S K = R L,
```

together with the Koszul cotangent dual.  Here `L` is the exact
constraint-adjusted Weyl--Cotton evolution and `S` is its fourteen-state
subsidiary evolution.  Both are symmetric hyperbolic with metric-causal
characteristics.  Compatible-source Green operators for `L` are obtained by
restriction using `S K=R L`; no projector onto `ker K_src` is used.

The canonical direct-sum witness is local, has degree `-1`, and satisfies
`P=QW+WQ` exactly.  Fourteen of its sixteen split diagonal blocks are Green.
The two exceptions are the auxiliary field block

```text
D_aux = E_aux + K C
```

and its cotangent copy.  The null-symbol rank theorem rules out a scalar-wave
realization of these blocks.  Because split `Q` is block diagonal, adding a
one-way or block-triangular relative term to `W` cannot change these diagonal
entries.

## Route A: replace the auxiliary diagonal witness

This route would construct a new degree-`-1` witness entirely on the original
24-field auxiliary bundle and prove its field block Green hyperbolic without
using the curvature cone.

It is logically possible, but it is not the economical route:

- the pointwise-pairing/first-order-companion scalar target is already ruled
  out;
- the two physical null directions are detected by the differential Weyl map,
  which has no support-local inverse on metric potentials;
- separating those directions inside the 24-field block by TT, helicity, or
  constraint projectors would introduce an inverse curl or inverse Laplacian;
- a mixed-order local replacement which avoids those projectors would in
  effect rebuild the existing Weyl--Cotton prolongation inside the auxiliary
  diagonal, while making its relation to the action current less transparent.

This route should remain a fallback only if an explicit full-bundle local
factorization is found.  Its acceptance test is not a physical-mode
factorization: it must give advanced and retarded inverses for every compact
source in the complete auxiliary field and cotangent rows, with the paired
adjoint relation and without a nonlocal decomposition of the source.

### Mixed-order square-root acceptance criterion

The precise usable statement from `BaerGreenHyperbolic` is stronger than the
prenormal symbol identity.  Let

```text
P : Gamma(E1) -> Gamma(E2),
D : Gamma(E2) -> Gamma(E1)
```

be local differential operators.  To infer that `P` is Green hyperbolic, the
full operator products `D P` on `E1` and `P D` on `E2` must both be Green
hyperbolic.  In Bär's definition this means that each product **and its formal
dual** has advanced and retarded Green operators satisfying both inverse
identities on compact sections and metric-causal support.  Principal-symbol
divisibility, a one-sided parametrix, or a Green inverse only on compatible
sources is insufficient.

A sufficient certificate in the present ansatz is the pair of exact operator
identities

```text
D P = L_minus L_plus,
P D = R_minus R_plus,
```

where every displayed second-order factor is normally hyperbolic (or is
independently Green hyperbolic), and the same is true for the reversed formal
dual products.  Bär's Corollary 3.13 then gives Green operators for `D P` and
`P D`;
for example the Green operator of `L_minus L_plus` is the causally ordered
composition `G_Lplus^+/- G_Lminus^+/-`, using the standard extension to
past/future-compact sections.

Indeed, on `E1 direct_sum E2` set

```text
A = [ 0  D ]
    [ P  0 ].
```

Then `A^2=diag(D P,P D)` is Green hyperbolic by Lemma 3.17, so the square-root
result, Corollary 3.15, makes `A` Green hyperbolic.  The upper-right block of
`G_A^+/-` is a two-sided Green operator for `P`; equivalently,

```text
G_P^+/- = D G_PD^+/- = G_DP^+/- D,
```

with equality understood on the extended support spaces.  Locality of `D`
does not enlarge support, so these maps inherit the required `J^+/-` support.
The lower-left block similarly gives the Green operators of `D`.

There is one terminology mismatch to keep out of certificates: Bär calls the
`J^+`-supported operator "advanced", whereas this repository calls
`G_plus`, supported in `J^+`, retarded and calls `G_minus` advanced.  Every
identity here is indexed by the support sign, not by that word choice.

If `D=P^sharp` (on this degree-zero block, after the project's nondegenerate
fibre identification), this is exactly Bär's Corollary 3.19: both
`P^sharp P` and `P P^sharp` must be Green hyperbolic.  The current project does
not yet have `D=P^sharp`; its complement is an independent mixed-order
operator.  The block argument still proves Green hyperbolicity of `P` once
both products and their formal duals pass, but it does not by itself give BV
self-adjointness or the current pairing.  Those require the repository's
Koszul `sharp` convention separately.  With `P^sharp=P`, formal-dual
uniqueness gives the project relation `G_plus^sharp=G_minus`; without that
identity an explicitly paired adjoint witness is required.

Thus the open quadratic/lower-order solve must emit exact `D P` and `P D`
factorizations, certify all primal and formal-dual factors, and check both
left/right Green identities and causal support.  The existing 45-parameter
cubic family satisfies none of these analytic conclusions by itself.

The backend audit found and fixed one real sign defect: the covector
commutator had used a four-dimensional delta on a raised curvature index
where the cylinder requires the spatial projector.  Mixed time--space
curvature now vanishes.  Independent coordinate-jet commutators,
`div symgrad=Box+grad div+Ric`, symmetrized order-two conversion, and focused
vector/tensor `Box^2` compositions pass.  Frozen Fourier multiplication still
misses the genuine order-two and order-zero curvature terms.

Exact triangular symmetrized-jet PBW inversion now exhausts all 1,680
four-jet basis elements, passes 504 ordered-word round trips and certifies
associativity.  Thus the quadratic-factor composition backend is ready.  If the
already sorted `Box^2` component table is naively transposed and its words
reversed, its putative adjoint differs in 48 entries.  This does not prove
that the primal composition is nonconfluent: the sorted coefficient matrices
have suppressed derivative-index slots and therefore are not individually
parallel endomorphisms to which that adjoint rule may be applied.  It does
prove that a pairing-aware formal adjoint must be formed before reduction, or
inside the symmetrized-jet/PBW representation.  The remaining backend gap is
therefore the general pairing-aware adjoint, not composition; the
quadratic/lower outputs also remain provisional until the 421-variable
coefficient system is assembled and solved.

One exact linear slice of that system has been exhausted.  If one factor in
each of `D P` and `P D` is the literal rough `Box`, all four inner/outer
orientations reduce to 159-variable rational systems.  Their coefficient
ranks are 159 and their augmented ranks are 160.  The same one-row left-null
witness appears in every orientation: the symmetrized
`nabla_(0)nabla_(1)` coefficient `f_01 -> f_00` is `-8` on the required
right-hand side and zero in every correction column.  The two-nontrivial-
factor branch is not constrained by this result because its
`A_minus A_plus` term contributes at quadratic order.

The nonlinear variable ledger is also larger than the cubic kernel.  The
45-dimensional kernel describes `X1` and the two factor *sums*.  Independent
left and right splittings contribute `2*93` variables, while `X0` and the
four factor potentials contribute `5*38`.  Thus the full post-cubic solve has
`45+2*93+5*38=421` unknowns.  The principal normalization to `q I` is without
loss for invariant factors because a parallel invertible `q H/q H^-1` pair
can be redistributed.  Formal adjoints add no variables, but require the
missing pairing-aware backend.

The conditional promotion theorem itself has landed.  If a future
coefficient certificate proves exact global `D P=L_minus L_plus` and
`P D=R_minus R_plus`, with all factors and formal duals Green hyperbolic, the
B\"ar construction gives

```text
G_P^+/- = G_Lplus^+/- G_Lminus^+/- D
         = D G_Rplus^+/- G_Rminus^+/-.
```

The two-sided identities, metric-causal support, reversed formal adjoints and
insertion into all sixteen split BV blocks are already certified
conditionally.  Only after the missing coefficient certificate passes may
`prolonged_green_witness`, `curvature_causal_green_operators`, and
`causal_green_homotopy` promote; all three remain false now.

## Route B: a two-way auxiliary--curvature saddle

The preferred route is to add relative degree-`-1` entries to the witness and
prove the resulting coupled operator Green hyperbolic.  The relative entries
must occur in both directions.  Schematically the physical part of
`P=QW+WQ` must become a saddle

```text
[ D_aux       R_sharp ]
[ R            L_WC   ]
```

rather than a triangular perturbation of `D_aux direct_sum L_WC`.  The
uncancelled helicity-two symbol is then carried into the curvature evolution
instead of being projected out.

In the sixteen-block degree ledger, the central relative witness entries can
only map degree one to degree zero.  Representative primal placements are

```text
Ebar_aux[1] -> X_U[0],
X_Eq[1]     -> M_aux[0],
```

and their odd-incidence adjoints are respectively

```text
X_U_sharp[1] -> M_aux[0],
Ebar_aux[1]  -> X_Eq_sharp[0].
```

The exact ansatz may also require the shifted `Y` copy, but every added entry
must satisfy the degree-`-1` cyclic condition

```text
DeltaW^(T,formal) Omega - D Omega DeltaW = 0,
D_jj = (-1)^degree(j),
```

so its Koszul-adjoint partner is generated rather than normalized
independently.  Candidate coefficients should be built only from the emitted
local maps `T`, `A_eq`, `B_id`, `pF`, `iC` and their formal adjoints.  No
inverse Weyl map, inverse constraint operator, harmonic projector, inverse
curl, or inverse Laplacian belongs in `W`.

The full compatibility rows must be retained.  In particular, the analytic
construction should use the unconstrained `L` block together with `K`, `R`
and `S`, not first project sources into `ker K_src`.  The identity `S K=R L`
then proves that compatible sources evolve into constrained fields, while the
equation and identity rows handle arbitrary compact sources in the complete
BV operator.

### Scoped no-go for the smallest instantiated saddle

The coefficient-free pair-4+5 incidence can be instantiated from the exact
chain map without a fit:

```text
A_F = pF A_eq,
S   = A_F^sharp,
R   = A_F^sharp J_U,
```

where `J_U` is the positive pointwise Weyl--Cotton symmetrizer used only as a
fibre identification.  This concrete local ansatz fails the required
principal test.  The balanced Douglis weights retain the order-two reciprocal
blocks, the order-four adjoint--Hessian blocks and the first-order curvature
evolution, but push the old auxiliary diagonal below principal order.  At
`zeta=dt` the curvature temporal blocks have rank 52, while the field Schur
block factors through the rank-15 auxiliary Hessian.  Including the
independently invertible 40-component equation-dual block gives

```text
rank sigma_DN(dt) <= 40 + 52 + 15 = 107 < 116.
```

Thus the temporal rank defect is at least nine, the leading temporal
coefficient of the Douglis characteristic determinant is zero, and no
positive temporal symmetrizer exists for this realization.  This is an exact
no-go only for the smallest pair-4+5 ansatz with the displayed `R,S`.  It is
not a no-go for a larger relative witness, different local relative maps, or
an additional support-local first-order prolongation.  No flag follows.

## Adjoint and support requirements

The positive symmetrizers of `L` and `S` are PDE energy forms; they are not the
action/Krein pairing.  The formal BV/Krein adjoint convention is encoded by
the oriented odd incidence form.  Together with the coefficientwise complete
mapping-cylinder differential, this now defines the local quadratic parent
`S_prol=<Phi,D Omega Q_prol Phi>/2`; its finite canonical transgression proves
the prolonged/auxiliary current comparison off shell.  It does not by itself
prove equality with a causal Green pairing.  A successful coupled operator should first
prove, with the repository orientation conventions,

```text
P_sharp = P
```

or provide an explicitly paired adjoint witness.  Only then may uniqueness be
used to obtain the advanced/retarded adjoint relation needed by the current
pairing.

All entries of `Q`, `W`, and the mapping-cylinder changes must remain finite
differential operators or pointwise inverses, hence support-local.  Green
operators are not support-local maps; their required statement is metric
causal support.  A Schur-complement formula involving `G_L^+/-` may be used in
the proof of the causal inverse, but it must not be smuggled into the local
witness or retract, and both left- and right-inverse identities must be
checked.

Because the coupled system mixes first-, second-, and third-order entries, its
principal test should use an explicit Douglis--Nirenberg weight ledger.  The
first go/no-go certificate should verify:

1. every relative block has degree `-1` and its forced odd adjoint;
2. `P=QW+WQ` and the paired formal-adjoint identity;
3. invertibility for a timelike covector and only metric-causal real
   characteristics in the weighted principal symbol;
4. a local row/column reduction to known symmetric- or normally-hyperbolic
   blocks, or an independent symmetrizer for the full saddle;
5. advanced and retarded inverses on all degreewise compact sources, followed
   by `QG_plus/minus=G_plus/minus Q` and the Green-homotopy identity.

## Recommendation

Implement Route B first.  It uses the already-certified analytic carrier of
the two physical helicities, retains every source-compatibility and cotangent
row, can preserve the formal BV/Krein adjoint relations through forced Koszul
partners, and needs no nonlocal potential reconstruction.  Route A should be kept only as a
fail-closed fallback.  This audit promotes no theorem flag.
