# Exact normalized emitter switch profiles

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

The two relational switches are now serialized rather than left as arbitrary
compact functions.  Let

```text
B(s)=exp(1-1/(1-s^2))  for |s|<1, and B(s)=0 otherwise,
C_B=integral_-1^1 B(s) ds.
```

For clock center `c_b` and radius `r_b`, define

```text
h_b(Theta)=B((Theta-c_b)/r_b)/(r_b C_B).
```

Each switch is nonnegative, compactly supported, flat to all orders at its
boundary, and has unit integral in `Theta`.  The certified clock rate is
`dTheta/dt=3/4`, so the exact supports are:

| switch | physical-time support | clock-phase support |
|---|---|---|
| `h_0` | `(7/48,9/48)` | `(7/64,9/64)` |
| `h_1` | `(5/16,7/16)` | `(15/64,21/64)` |

The detector windows are `[11/48,13/48]` and `[23/48,25/48]` in physical
time.  The three relevant strict gaps are all `1/24`, equivalently `1/32`
in clock phase.  Thus `h_0` is before `D0`, while `h_1` is after `D0` and
before `D1` with exact positive margins.

This closes only the switch part of the recoil input gate.  The compact
massive-two-form Cauchy profiles must still be selected against the actual
advanced detector covectors; an arbitrary explicit bump could lie in their
kernel.  Their massive Green images, detector recoil integrals, PBW payload,
backreacted branch, finite-parameter Green theory, full Dirac algebra, and
quantum theory remain open.
