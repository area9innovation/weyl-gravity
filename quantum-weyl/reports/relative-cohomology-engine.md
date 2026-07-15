# Exact relative-cohomology engine receipt

Date: 2026-07-15

Dependency tag: `LOCAL-ALGEBRAIC`

Result state: `ENGINE_VERIFIED_PRODUCTION_BASES_PENDING`

## Outcome

The local algebra now contains an exact sparse bicomplex and mapping-cone
engine.  A finite input supplies labelled spaces `V^p_g` and row-by-column
matrices for

```text
Q:   V^p_g -> V^p_(g+1)
d_h: V^p_g -> V^(p+1)_g.
```

The coordinate convention is `Q d_h = d_h Q`.  Totalization inserts the
grading sign

```text
D = Q + (-1)^ghost_number d_h,
```

and independently verifies `D^2=0`.  At a requested total degree the engine
computes, with exact rational arithmetic:

- the total ansatz basis and reproducible hash;
- the cocycle matrix rank and kernel basis;
- the coboundary matrix rank;
- the quotient dimension;
- deterministic representative coordinates; and
- complete descent lifts as closure witnesses;
- normalized dual functionals that annihilate the boundary space and pair to
  one with each selected representative; and
- a proof hash binding the adjacent differentials and representatives.

Rank and nullspace elimination now operate directly on sparse exact rows.
Quotient construction maintains one incremental exact row space instead of
rerunning a dense rank computation for every candidate.  Fill-in can still
occur, so production basis sizes and elimination density must be benchmarked,
but the engine no longer densifies the input matrices merely to begin.

The anchored API additionally takes a requested `(ghost_number, form_degree)`.
It truncates the total complex at that form degree, projects complete total
cocycles and coboundaries to the requested top component, and reports the
quotient of those projected spaces.  Complete total-cohomology classes with
zero top component are counted as `lower_only_total_class_dimension` and
cannot be promoted to `H^{g,p}(Q|d_h)`.

The certification fixture is a commuting square with one isolated top class
and one isolated lower-form class.  Its total-degree-one cohomology has
dimension two.  Anchoring at `(g,p)=(0,1)` gives quotient dimension one and
reports the other total class as lower-only.  Anchoring at `(1,0)` instead
recovers that lower class.  A deliberately noncommuting square fails closed.

## Claim boundary

The receipt
`quantum-weyl/local_bv/certificates/RELATIVE_COHOMOLOGY_ENGINE_CERTIFICATE.json`
certifies the linear-algebra engine and the top-component projection, not a
pure-Weyl cohomology result.  Still
`NOT_COMPUTED` are the production derivative-bounded bases, production `Q`
and `d_h` matrices, the dimensions of `H^{0,4}(s|d)` and `H^{1,4}(s|d)`, and
the antifield-dependent quotient.  `NONTRIVIAL` will be emitted only after a
candidate survives the complete production coboundary space.

If the boundary rows are `B` and the representative is `a`, the engine stores
exact coordinates for `lambda` with `B lambda = 0` and `lambda(a) = 1`.
The default label is `TRUNCATED_NONMEMBERSHIP_WITNESS`: it proves only
non-membership in the supplied boundary space.  There is no caller-controlled
`EXHAUSTIVE` switch.  The API emits `COMPLETE_NONTRIVIALITY_WITNESS` only when
it receives a verified `BasisExhaustivenessProof`.  That proof is hash-bound
to the previous, current, and next total-degree bases and their incoming,
cocycle, and outgoing differentials.  It separately binds the declared
bounds, generator algebra, grading solutions, index-orbit enumeration,
identity quotient, and proof artifact.

## Next input

The top curvature-carrier production run has started under the explicit
`AFN0_ONLY` scope.  Generate the remaining lower-form ghost and generalized-
connection bases at fixed ghost number, form degree, engineering dimension,
and antifield number.  The Koszul--Tate blocks attach only after a classical
export passes the antifield preflight.
