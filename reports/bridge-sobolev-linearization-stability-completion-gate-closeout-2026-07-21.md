# Bridge Sobolev linearization-stability completion gate close-out

Disposition: exact first failed hypothesis.

## Declared analytic category

The attempted completion is the unweighted full-time Sobolev realization on

```text
R_t x S1_L x S2,
fixed magnetic bundle P_N with N=2,
one complemented local-gauge-reduced generic p-primary master block,
P_e : H^(s+2)(R_t) -> H^s(R_t), any real s.
```

No global covariant Sobolev gauge slice is asserted.  One complemented
reducing block is sufficient to falsify closed range for the corresponding
block-diagonal full realization.

## Exact obstruction

At `ell=2`, `lambda=6`, `k=0`, either certified generic parity contains an
extra p-primary coordinate with

```text
omega_e^2 = k^2 + lambda - 2/3 = 16/3,
P_e = partial_t^2 + 16/3.
```

Conjugating `P_e:H^(s+2)->H^s` by Bessel-potential isometries gives the
bounded `L2` multiplier

```text
a(xi) = (16/3-xi^2)/(1+xi^2).
```

The multiplier is nonzero almost everywhere, so both its kernel and adjoint
kernel are zero and its range is dense.  Normalized Fourier packets supported
on `I_n=[omega_e,omega_e+1/n]` obey

```text
||A u_n|| <= (8*sqrt(3)*n+3)/(19*n^2) -> 0.
```

An injective bounded operator with closed range would be bounded below.  The
packets contradict that estimate.  Hence the range is dense but not closed;
the realization is not Fredholm and has no bounded generalized inverse.

The independent rail rederives this multiplier and estimate without
importing the producer.  Its decisive mutation replaces the numerator by
`19/3-xi^2`, whose value at the original shell is `3/19`; the original packet
witness then fails, as required.

## Relation to the finite theorem

The frozen finite exponential-polynomial theorem is unchanged.  Its secular
primitives and exactly five zero-factor covectors remain valid in that
declared carrier.  They do not become a bounded Sobolev inverse by density.

The Hilbert-space orthogonal cokernel of the witnessed full-time block is
zero, despite its nonclosed range.  It therefore cannot be identified with
the five Taub covectors.  This is a type distinction, not a contradiction.

## Arms--Marsden--Moncrief/Fischer--Marsden boundary

The classical momentum-map and linearization-stability theorems concern an
elliptic constraint map on compact Cauchy data.  The operator obstructed here
is instead an unweighted full-time hyperbolic realization.  A compact-Cauchy
Weyl--Maxwell theorem remains open and requires:

- a complete constraint map on a declared fixed-bundle Sobolev slice;
- Douglis--Nirenberg ellipticity and closed range;
- identification of the full adjoint kernel with exactly the five lifted
  stabilizers;
- smooth or tame nonlinear estimates and a compatible slice theorem.

Thus this result blocks one proposed completion without ruling out the
correct compact-Cauchy route.

Delivered:

- exact content-hash imports of the five finite-harmonic inputs;
- strict schema and fail-closed machine-readable certificate;
- independent Fourier-multiplier verifier and decisive mutations;
- eleven focused tests and a generated residual-atlas row;
- exact separation of the finite EP, full-time Sobolev, compact-Cauchy and
  causal/retarded categories.

Not delivered:

- a compact-Cauchy constraint-map Fredholm theorem;
- weighted, radiation, finite-slab or causal/retarded solvability;
- a global Sobolev gauge slice or a nonlinear momentum-map normal form;
- nonlinear existence, stability, observable, particle, scattering or
  quantum claims.

CLOSE-OUT: OBSTRUCTED — the unweighted full-time Sobolev p-primary realization has dense nonclosed range, so the Fredholm and bounded-inverse hypotheses fail before a Sobolev momentum-map normal form can be invoked
EVIDENCE: bridge/certificates/EINSTEIN_MAXWELL_WEYL_SOBOLEV_LINEARIZATION_STABILITY_GATE_V1.json
