# The first weak-base certificate: energy-2 free BV

## Result

`FOUNDATIONAL_FREE_BV_ENERGY2_PRA_SDR_V1` is the first theorem-level result of
the reverse-foundations stream.  It has dependency tag `LOCAL-ALGEBRAIC` and
two deliberately narrow classifications:

```text
PRA  SUFFICIENT_OVER_BASE  fixed energy-2 integer SDR
explicit p,j,h  AVOIDED_BY_REFORMULATION  Hahn--Banach/complement selection
```

Here PRA is Primitive Recursive Arithmetic.  The result says that PRA is
sufficient to verify one fixed finite witness.  It does not say that PRA is
the weakest possible base, and it is not a reversal.

## Selected source claim

The classical source is the split free pure-Weyl BV fixture emitted by
`symbolic/verify_conformal_free_bv_complex.py`.  At cylinder energy two its
certificate reports a 230-dimensional full block with ten-dimensional
cohomology.  The source is an algebraic `D x SO(4)`-finite normal form.  It is
not the complete field-derived gauge-fixed domain, the all-energy Fock lift,
or a quantum classical-import freeze.

The energy-2 coordinate ranges are:

| Field slice | Half-open range | Dimension |
|---|---:|---:|
| diffeomorphism ghost | `[0,80)` | 80 |
| Weyl ghost | `[80,90)` | 10 |
| metric trace | `[90,100)` | 10 |
| trace-free metric | `[100,190)` | 90 |
| metric antifield | `[190,190)` | 0 |
| diffeomorphism-ghost antifield | `[190,190)` | 0 |
| trace antifield | `[190,200)` | 10 |
| Weyl-ghost antifield | `[200,210)` | 10 |
| antighost | `[210,220)` | 10 |
| multiplier | `[220,230)` | 10 |

The physical interval is `[180,190)`, the last ten trace-free metric
coordinates.  The remaining coordinates form four explicitly paired blocks:

| Pair | Source | Target | Size |
|---|---:|---:|---:|
| diffeomorphism/gauge | `[0,80)` | `[100,180)` | 80 |
| Weyl/trace | `[80,90)` | `[90,100)` | 10 |
| trace-antifield dual | `[190,200)` | `[200,210)` | 10 |
| nonminimal | `[210,220)` | `[220,230)` | 10 |

On each pair, `q` maps source to target with coefficient one and `h` maps
target back to source with coefficient one.  The inclusion `j` and projection
`p` identify the ten physical coordinates with a separate copy of
`Z^10`.  Thus the proof data is

```text
110 contractible sources + 110 contractible targets + 10 physical = 230.
```

No matrix entry requires division.  The witness is therefore defined over
the integers before choosing real, complex, Hilbert, or Krein scalar data.

## Exact identities

The dependency-minimal checker expands the four interval maps into sparse
integer dictionaries and proves

```text
q^2=0,          h^2=0,
pj=1,           jp=1-qh-hq,
qj=0,  pq=0,    hj=0,  ph=0.
```

The expanded nonzero counts are

```text
q:110, h:110, j:10, p:10
```

and the canonical digest of the four expanded matrices is

```text
cfab94dad9444a71614c2361d8863c1bf56155e340838931f39aa854cf6d0049.
```

The independent checker imports no source BV code and no algebra package.  It
uses fixed-size exact integer addition and multiplication only.  In
particular, it has no SymPy, NumPy, floating point, rank, nullspace,
eigendecomposition, solver, theorem-prover, or network dependency.

## Why cohomology follows without a basis theorem

Let `x` be closed.  The contraction identity gives

```text
x - j p x = q h x + h q x = q h x.
```

Hence every cohomology class has the explicit representative `j p x`.  If
`j z=q y` is exact, applying `p` gives

```text
z = p j z = p q y = 0.
```

Thus `j` and `p` induce mutually inverse maps

```text
H(C,q) <-> Z^10.
```

This proof never asks for a basis of a kernel, extends no independent set,
and chooses no complementary subspace.  The complement is already part of
the data in the form of `p`, `j`, and `h`.

Since all equations are integral polynomial identities, scalar extension
preserves them over every nonzero unital commutative ring.  This is stronger
than merely rechecking the matrices over `Q` or `C`, but it remains a result
about the displayed split normal form.

## Why PRA is sufficient

The formal input consists of fixed natural-number endpoints no larger than
230 and coefficients in `{0,1}`.  Finite sequences can be encoded by standard
primitive-recursive pairing.  Expanding interval maps, composing sparse
matrices, and comparing their entries are bounded primitive-recursive
computations.  The human proof above is likewise a bounded case split among
contractible sources, contractible targets, and physical coordinates.

Therefore Primitive Recursive Arithmetic proves the closed computation and
the equational consequences for this fixed witness.  This establishes
`SUFFICIENT_OVER_BASE` at the certificate-checker level.

Three boundaries matter:

1. no formal proof-assistant development of PRA is supplied;
2. no claim is made that PRA is the weakest adequate theory;
3. no converse derives PRA, induction, or a set-existence principle from the
   BV statement.

The result is consequently sufficiency, not necessity or equivalence.

## Hahn--Banach avoidance control

In an abstract presentation one might establish the dimension of cohomology
by computing kernels and images, choose a complement, or invoke a generic
separation or extension theorem elsewhere in an analytic argument.  None of
that occurs in this certificate.  Its conclusion is obtained from the
retained coordinate projection, inclusion, and contracting homotopy.

The relation is therefore `AVOIDED_BY_REFORMULATION`: for this displayed
energy-2 certificate, the explicit SDR replaces

- Hahn--Banach;
- geometric separation;
- Zorn's lemma;
- extension to a basis;
- existential complement choice; and
- rank/nullspace computation.

This is not the claim that Hahn--Banach is false, weak, or absent from all
physics.  It is a proof that this particular finite conclusion has a route
which does not use it.  It is also stronger than a keyword census: the exact
derivation is displayed and independently checked.

## Proof-dependency cut

```text
field intervals ----+
pair intervals -----+--> finite partition --> q,h,j,p identities
physical interval --+                           |
                                                 v
                                      explicit cohomology isomorphism
                                           /               \
                                          v                 v
                               scalar extension      avoidance result
```

This locates the first foundational cut.  The energy-2 algebra does not yet
need real-number completeness, actual infinity, countable choice, Hilbert or
Krein completion, spectral theory, or Green operators.  Those assumptions
enter only when the programme moves outward from the finite block.

## Provenance and independent rails

The source certificate, its producer, the `FreeBVBlock` implementation, and
the pre-existing paper-verification checksum ledger are content-pinned in the
machine certificate.  The lightweight verifier additionally checks that the
ten field names and dimensions agree with the published energy-2 metadata.

The two rails remain distinct:

- the source producer constructs the original all-energy split fixture with
  SymPy;
- the new primitive checker independently verifies the emitted compact
  energy-2 witness without importing that implementation.

Hash agreement and metadata agreement do not prove that the complete source
producer is correct.  The source's all-energy claim and quantum import gate
remain outside this result.

## What was established

- a fixed integral strong deformation retract of the 230-coordinate energy-2
  split free-BV block onto ten physical coordinates;
- PRA sufficiency for checking that fixed witness;
- scalar stability of the SDR over nonzero unital commutative rings; and
- explicit avoidance of Hahn--Banach, complement selection, rank, and
  nullspace machinery for this certificate.

## What was not established

This result is not the weakest-base theorem, a reversal, an all-energy
classification, a full classical freeze, a constructive Weyl QFT, a
choice-free infinite completion, a state or probability construction, or a
`LORENTZIAN-CAUSAL` result.  It promotes no quantum lifecycle state.

## Next gate

The next low-hanging case is the explicit Krein fundamental symmetry.  The
finite truncations can be treated by the same integral interval method.  The
scientifically interesting boundary is then the first additional principle
needed to pass from the explicit finite grading to the countable `ell^2`
completion and its bosonic Fock space.
