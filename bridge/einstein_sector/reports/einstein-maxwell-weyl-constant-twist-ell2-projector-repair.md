# Constant-twist ell=2 projector repair

The former nonzero twist-position resonance used the axial test pair
`(-i/sqrt(1-z^2),-z*sqrt(1-z^2))`.  This is exactly `*dY_11`, with angular
eigenvalue `lambda=2`, but it was paired with adjoint operators specialized to
`lambda=6`.  The correctly typed `*dY_21` pair is

```text
(-i*z/sqrt(1-z^2), (1-2*z^2)*sqrt(1-z^2)).
```

Direct four-dimensional replay with this projector makes every Einstein and
extra same-shell twist-position pairing vanish.  All remaining `L=1,3`
outputs are off shell with invertible reduced operators.  Hence

```text
Z2_bounded(A,wave) = R_A^3 x {wave: H=J_1=J_2=J_3=0}.
```

The previous counterexample and nonzero-`A` incidence restrictions are
superseded.  This repair is restricted to `ell=2,k=0`; it is not a causal or
all-orders statement.
