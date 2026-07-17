# Abstract cyclic causal-transfer theorem

## Theorem

Let `(C,q_C)` and `(E,q_E)` be finite-rank differential complexes over a
time-oriented globally hyperbolic spacetime.  Suppose there is a cyclic,
support-local strong deformation retract

```text
E --i--> C --p--> E,        p i = 1,
q_C h + h q_C = 1 - i p,
h^2 = h i = p h = 0.
```

Assume `i,p,h` are finite-order differential or pointwise maps.  If `E` has
advanced and retarded degree-minus-one homotopies `Lambda_E,+/-`, define

```text
Lambda_C,+/- = h + i Lambda_E,+/- p.
```

Then

```text
q_C Lambda_C,+/- + Lambda_C,+/- q_C = 1_C.
```

The same SDR also transfers a parent homotopy downward.  If `C` already has
`Lambda_C,+/-`, then

```text
Lambda_E,+/- = p Lambda_C,+/- i
```

satisfies

```text
q_E Lambda_E,+/- + Lambda_E,+/- q_E
  = p(q_C Lambda_C,+/- + Lambda_C,+/- q_C)i
  = p i = 1_E.
```

This is the direction used by tractor/BGG compression.

Moreover, `Lambda_C,+/-` has the same advanced or retarded support.  Indeed,
the endpoint term is a composition of support-local maps with a same-sided
causal map, while `supp(hf)` is contained in `supp(f)`, hence in both its
causal future and causal past.

Let `Sigma_C` and `Sigma_E` be the degreewise sign involutions induced by the
two graded pairings.  If

```text
Sigma_C i = i Sigma_E,     p Sigma_C = Sigma_E p,
i^sharp=p,                 p^sharp=i,
h^sharp = Sigma_C h Sigma_C^-1,
Lambda_E,+^sharp = Sigma_E Lambda_E,- Sigma_E^-1,
```

then

```text
Lambda_C,+^sharp = Sigma_C Lambda_C,- Sigma_C^-1.
```

Thus the complementary-degree advanced/retarded adjoint relation transfers
without assuming that one scalar sign works in every degree.

## Endpoint companion route

The endpoint homotopy need not be supplied independently.  Let `W` be a
finite-order degree-minus-one witness and

```text
P = q_E W + W q_E.
```

If `P` has degreewise advanced and retarded Green operators `G_P,+/-`, causal
uniqueness and `q_E P=P q_E` give `q_E G_P,+/-=G_P,+/- q_E`.  Therefore

```text
Lambda_E,+/- = W G_P,+/-
```

obeys the endpoint chain-homotopy identity.  This hypothesis concerns the
complex companion; it does not require a scalar-symbol factorization of every
reduced middle operator.

## Closure operations

Finite direct sums transfer componentwise.  If `U` is a finite-order
support-local chain isomorphism with a finite-order support-local inverse,
then

```text
q'             = U q U^-1,
Lambda'_+/-    = U Lambda_+/- U^-1
```

preserve the chain identity and same-sided support.  When `U^sharp=U^-1`, the
cyclic adjoint relation is preserved as well.  A filtration-nilpotent shear
`U=1+N` is a sufficient implementation because its inverse is a finite
Neumann polynomial.  The cyclic conclusion additionally requires the shear
to intertwine the degreewise sign involution.

## Portable consumer gate

Every new application must validate the strict consumer contract before any
coefficient search.  It requires typed complexes, operator domains, boundary
conditions, same-sided support, all cyclic SDR identities, pairing-derived
degreewise signs, a causal-input Green package, and a finite local inverse for
every shear.  Missing data produce a rejected preflight rather than an
inferred transfer theorem.

## Berger replay

The Berger cylinder is the first complete consumer:

```text
54 = 28 algebraic + 26 causal,
Lambda54,+/- = S_cl + iota_cl Lambda26,+/- pi_cl.
```

The Maxwell extension uses direct-sum closure before the same SDR formula:

```text
64 = 28 algebraic + (26 gravity-clock + 10 Maxwell),
Lambda64,+/-
  = S64 + iota64 (Lambda26,+/- direct-sum LambdaM,+/-) pi64.
```

The gauge-fixing shear is finite, nilpotent and BV-canonical.  All imported
row identities, support statements and cyclic adjoints replay exactly.  The
frozen unary generator is `K_Berger=D-omega R`, not raw affine `D`.

## Scope

This result is an abstract conditional theorem plus one complete `G2`
consumer.  It does not itself establish causal-input Green hyperbolicity.  It
does not cover pseudodifferential projectors, timelike-boundary domains,
Hadamard wavefront sets, renormalized products, interactions, or quantum
claims.  Downstream consumers are certified in their own acyclic artifacts;
a uniform `G3` background class remains open.
