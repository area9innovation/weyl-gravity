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

## Adjoint and support requirements

The positive symmetrizers of `L` and `S` are PDE energy forms; they are not the
action/Krein pairing.  The formal BV/Krein adjoint convention is encoded by
the oriented odd incidence form, so the relative witness can preserve it by
construction.  This algebraic cyclicity does not by itself prove the open
prolonged-current comparison.  A successful coupled operator should first
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
