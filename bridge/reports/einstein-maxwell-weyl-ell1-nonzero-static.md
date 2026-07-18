# Exceptional `ell=1` nonzero-momentum target

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

Direct axial and polar `Y_10` coordinate replays retain arbitrary Fourier
`(omega,k)` while omitting only the tensor-harmonic equation that vanishes
identically at `ell=1`.  This is not a proof by continuation from symbolic
`lambda`.

Both parities have one polynomial residual-gauge column.  The greatest common
divisor of their three-by-three minors is, up to the harmless polar factor
`1/3`,

```text
(k^2-omega^2+4)*(3*k^2-3*omega^2+4).
```

Thus the only reduced shells are the standard `omega^2-k^2=4` shell and the
extra `omega^2-k^2=4/3` shell.  A resonant Noether-compatible source has a
finite exponential-polynomial secular inverse in the smooth-global class.

At `omega=0`, `k!=0`, the axial and polar rank-three witnesses are

```text
k^2*(k^2+4)*(3k^2+4),
(k^2+4)*(3k^2+4)/2.
```

They are strictly positive.  Each static kernel is precisely its residual
gauge line, so neither parity supplies a physical adjoint obstruction to the
standing-wave phase source.

## Boundary

The `k=0,omega=0` axial twist cokernel is not removed by this result; it is the
separate rotation moment-map block.  Bounded resonant source projections also
remain separate.
