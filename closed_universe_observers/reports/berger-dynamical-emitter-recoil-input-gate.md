# Dynamical-emitter recoil input gate

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, `LORENTZIAN-CAUSAL`.

The localized theorem fixes two external conserved currents, not the matter
that carries them.  This distinction becomes observable at recoil order.
For example, take a real polarization two-form `K` with

```text
L_m = P_2 + m^2,
S_int = -g <K,dA>,
J = g delta K.
```

Both cross blocks come from one local action and are formal adjoints.  For a
fixed background `Kbar` with `delta Kbar=J`, the drive
`f_m=L_m Kbar-g dAbar` makes every mass compatible with the same already
certified external current.  The old handoff contains neither `L_m` nor
`f_m`.  Yet eliminating the emitter gives
`Sigma_m=g^2 delta G_m,ret d`.  On the exact specialization `lambda=1`, the
choices `m^2=1` and `m^2=4` yield `1/2` and `1/5`, differing by `3/10`.
Therefore the recoil coefficient is not determined by the existing current.

There is nevertheless a model-independent formal result.  For any compatible
completion,

```text
M(epsilon)=M0+epsilon M1+...,
det M(epsilon)=-40 S0 C1/9+O(epsilon).
```

The constant term is nonzero, so the two-record map remains rank two over the
formal recoil ring.  Selecting a physical emitter carrier, constructing its
BV complex, and computing the recoil coefficient require a new handoff; none
is silently chosen here.
