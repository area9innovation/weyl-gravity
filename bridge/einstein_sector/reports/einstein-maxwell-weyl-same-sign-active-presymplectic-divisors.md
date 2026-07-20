# Smooth active presymplectic divisors on candidates 17, 18 and 20

## Result

Let a smooth active resonance variety be cut out by a full-row-rank
constraint Jacobian `J` inside a finite-dimensional harmonic carrier with
invertible ambient Lee--Wald Hermitian current `H`.  The restricted-current
radical is controlled exactly by the conormal matrix

```text
K = J H^{-1} J^dagger.
```

The map `lambda -> H^{-1} J^dagger lambda` identifies `ker(K)` with the
radical of `H` on `ker(J)`.  Hence the complete smooth degeneracy locus is
`det(K)=0`, higher-corank strata are its determinantal strata, and
`ker(J)/rad` carries an induced nondegenerate current.

For candidates 17 and 20, each transformed parity factor is the smooth
third-transvectant variety `T3(f,g)=0`.  Its divisor is

```text
Delta_3(f,g) = det(J_3 H_3^{-1} J_3^dagger) = 0.
```

The two-parity divisor is the union of the two factor divisors.  At the
previous exact smooth bounded witness the conormal matrix is

```text
[[24, 0, 24],
 [ 0,30,  0],
 [24, 0, 24]],
```

so the tangent current has a one-complex-dimensional radical.
The exact smooth point

```text
f=(-2,-2,-2,-2,-1),  g=(12,12,11,9,0)
```

has `det(K_3)=8293671904`, proving that this determinant does not vanish
identically and that the degeneracy locus is proper.

For candidate 18, the two rank-one quartic factors are treated on every
regular determinantal chart.  Their eight-row conormal matrix gives the
complete smooth divisor `det(K_18)=0`, independently of chart.  On the
aligned section used by the bounded witnesses, the divisor factors as

```text
(2 b r-w_y)(6 b r-w_x) = 0,
```

where `r=|t|^2` and `b=6 h_minus`.  The two branches are precisely the
symmetric and antisymmetric current eigenlines.  Each has conormal nullity
four and therefore a four-complex-dimensional affine current radical.  The
ten current-orthogonal spectators remain nondegenerate, so the affine
presymplectic quotient has complex dimension 18 there.

## Boundary

This is a complete tangent-space quotient theorem on the smooth active
resonance varieties.  It does not establish a Hausdorff global quotient,
constant-rank gluing across the divisor, a quotient on singular loci,
occupation-stratum gluing, all-orders integration, or causal, residual,
observational or quantum transport.
