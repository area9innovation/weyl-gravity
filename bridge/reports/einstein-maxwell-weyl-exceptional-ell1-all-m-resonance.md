# All-`m` exceptional `ell=1` resonance no-go

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

Write the axial and polar exceptional dipole amplitudes as complex Cartesian
vectors `a,p in C^3`. `SO(3)` multiplicity-one promotes the axisymmetric
resonant pairings to two spin-2 compatibility tensors. After rescaling

```text
q=(sqrt(3)/4)p,
```

they are

```text
E=STF(a a^T-q q^T),
F=STF(a q^T+q a^T).
```

If both vanish, then

```text
STF((a+i q)(a+i q)^T)=0,
STF((a-i q)(a-i q)^T)=0.
```

A rank-one outer product cannot equal a nonzero scalar multiple of the
three-dimensional identity. Hence each vector `a +/- i q` vanishes, and
therefore `a=p=0`.

An independent exact Gröbner calculation over
`Q[a0,a1,a2,q0,q1,q2]` gives a zero-dimensional ideal. Its triangular
witnesses begin with `q2^5`, then force `a2,q0,q1,a0,a1` to vanish. Thus the
rank argument and polynomial elimination agree over complex amplitudes.

Distinct-`m` interference therefore cannot cancel the positive-positive
`2omega_e` resonance. Every nonzero axial-plus-polar exceptional `ell=1,k=0`
tangent is second-order obstructed, even when standard homogeneous or twist
generalized-zero data cancel all background-stabilizer moment maps.

The remaining audit is whether a different sector can share the same
`omega_e^2=4/3` input frequency. All-orders, residual, causal, particle, and
quantum conclusions remain outside this theorem.
