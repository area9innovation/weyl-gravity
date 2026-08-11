# Explicit Krein symmetry: where infinity enters and Choice does not

## Result

`FOUNDATIONAL_KREIN_EXPLICIT_J_ZF_V1` classifies the repository's displayed
one-particle Krein carrier and its bosonic Fock lift.  The result has exactly
the dependency tags `LOCAL-ALGEBRAIC` and `REDUCED-MODE`.

The answer is sharper than the initial question suggested.  The fundamental
decomposition and orthonormal basis are not existential choices in this
model.  Energy, family, chirality, and magnetic coordinate already name every
mode.  Consequently:

| Layer | Sufficient base used | Relation | Choice status |
|---|---|---|---|
| each finite cutoff and its diagonal `J_N` | Primitive Recursive Arithmetic | `SUFFICIENT_OVER_BASE` | no choice operation |
| complete one-particle `ell^2(I)` and coordinate `J` | ZF | `SUFFICIENT_OVER_BASE` | Countable Choice not used |
| occupation-number Fock carrier and `Gamma_s(J)` | ZF | `SUFFICIENT_OVER_BASE` | Countable Choice not used |

The first commitment beyond the previous finite BV rail is therefore actual
countable infinity, real or complex summability, and canonical completion.
It is not the Axiom of Choice.  ZF is a sufficient external set theory here;
this result does not prove it is the weakest adequate theory.
Equivalently, ZF is sufficient here but explicitly not the weakest base
claimed by this certificate.

## The finite mode formula

For energy `n`, chirality `chi` and family `F`, the source dimensions are

```text
d_E(n)=(n+3)(n-1),  n>=2,   sign +1,
d_A(n)=(n+1)(n-1),  n>=3,   sign -1,
d_L(n)=(n+1)(n-3),  n>=4,   sign -1.
```

Both chiralities occur.  Thus the complete coordinate index is

```text
I={(n,chi,F,k): n>=n_min(F), chi in {+1,-1}, 0<=k<d_F(n)}.
```

Nested Cantor pairing maps these data injectively to natural numbers.  Every
cutoff is a primitive-recursive finite list, and `J_N` is just multiplication
by the family sign.  Exact natural-number checking therefore proves
`J_N^2=1`, `J_N^*=J_N`, and norm one without a basis search or an
eigendecomposition.

At cutoff 12 the independently expanded witness has

```text
positive dimension: 1540
negative dimension: 2200
total dimension:    3740
digest: df7cbe8ea3017f6b0ea5e2069107530705c601bca4d5b99d5932ab3b3fbd9ca6
```

These numbers reproduce the existing source certificate, but the checker
does not import its SymPy producer.

## The one-particle completion in ZF

Let the positive Hilbert product be the coordinate product on `ell^2(I)` and
define

```text
(Jx)_i = sign(F_i) x_i,
[x,y] = (x,Jy)_0.
```

The coordinate equation immediately gives `J^2=1`, `J^*=J`, and
`[x,Jy]=(x,y)_0`.  The `E` coordinates supply the positive subspace, while
the `A` and `L` coordinates supply the negative subspace.  Explicit modes at
arbitrarily high energies witness that both indices are infinite.

The nontrivial foundational step is completion.  Blackadar, Farah and
Karagila develop Hilbert spaces in ZF without Countable Choice.  Their
Theorem 1.0.2 separates several completeness notions, Corollary 1.0.3 gives a
canonical sigma-completion without Choice, and Proposition 3.0.4 proves that
`ell^2(X)` is sigma-complete for every set `X`.  Applying Proposition 3.0.4
to this already-defined `I` gives the required carrier in ZF.  No sequence of
nonempty sets is presented from which representatives must be chosen.

The source paper also explains why this explicit/separable situation must
not be confused with arbitrary families of Hilbert spaces in ZF.  Familiar
theorems about selecting bases in every member of a countable family can
hide Countable Choice.  That is not the construction used here.

## The Fock lift in ZF

Write `Occ(I)` for the finite-support maps from `I` to the natural numbers.
Using the fixed injection of `I` into the naturals, every occupation is coded
by a sorted finite sequence of mode codes, with repetition.  Proposition
5.1.3 of the pinned paper supplies the relevant ZF fact that finite sequences
of natural numbers are countable.  The normalized occupation presentation is
therefore the explicit carrier

```text
Gamma_s(ell^2(I)) = ell^2(Occ(I)).
```

On this basis the Fock fundamental symmetry is the coordinate sign

```text
Gamma_s(J)|m> = (-1)^(total A/L occupancy) |m>.
```

It is self-adjoint, involutive, norm one, and particle-number preserving by
inspection.  The finite controls reproduce dimension 55 for the symmetric
square of the ten-dimensional energy-two block and signs `[+1,-1,+1]` for
the two-mode symmetric-square fixture.

## What the physics changes

The compact-cylinder physical encoding does real foundational work: it
supplies a canonical energy grading and named finite multiplicity spaces.
That explicit labeling gives an `AVOIDED_BY_REFORMULATION` result for the
displayed carriers.  It replaces:

- selection of an unspecified fundamental decomposition;
- selection of an orthonormal basis;
- Zorn's lemma for extending an independent set; and
- a choice of bases across an arbitrary countable family.

This does not mean a physical postulate logically implies ZF, Infinity, the
Axiom of Choice, or its negation.  The physical representation supplies data
inside the mathematical foundation we selected.  Keeping those two arrows
separate is the central point of this programme.

## Exact boundary

The certificate constructs structural carriers and coordinate involutions.
It does not construct a state, trace-class density operator, generalized Born
functional, positive graviton Hilbert space, interacting implementer, or
physical probability rule.  It also does not classify the all-real-order
Sobolev scale, generator domains, exponentiation, or arbitrary Krein spaces.

In particular this is not a `LORENTZIAN-CAUSAL` result and says nothing about
a covariant off-shell BV propagator, Hadamard state, time-ordered products, or
the Lorentzian quantum master equation.

The relation is sufficiency, not a reversal.  A coded reverse-mathematics
treatment in `RCA_0`, or a constructive-analysis realization of completion,
may lower or refine the stated base.  That weakest-subsystem problem remains
open.

## Next gate

The next low-hanging boundary is no longer “does Fock space need Choice?”
For this explicit carrier it does not.  The sharper audit is the first
state-level bridge: separate finite-rank algebraic trace, normal trace-class
state, semifinite weight, and physical Born functional, and compare each to
the repository's existing thermodynamic obstructions.

## Source

The ZF Hilbert-space facts are pinned to Bruce Blackadar, Ilijas Farah and
Asaf Karagila, *Hilbert Spaces Without The Countable Axiom of Choice*,
[arXiv:2304.09602](https://arxiv.org/abs/2304.09602).  The occupation-space
application is the derivation made here, not a theorem attributed to that
paper.
