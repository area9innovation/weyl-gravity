# Exact detector smearings and advanced emitter covectors

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

The detector functions are no longer arbitrary normalized bumps.  Their
clock factors use the standard flat bump and have unit clock integral with
supports `[11/64,13/64]` and `[23/64,25/64]`.  Their spatial factors use the
radial three-dimensional flat bump

```text
B3(y)=exp(1-1/(1-|y|^2)), |y|<1,
rho_a(R)=B3((R-c_a)/epsilon_a)/(epsilon_a^3 C_B3).
```

Thus `integral rho_a d^3R=1`.  The exact family retains
`0<epsilon_a<r_chart,a<=1/64`: the inverse-function theorem certifies a
nonzero local chart but does not supply a numerical injectivity radius, so
choosing one would be unsupported new data.

Formal Green adjunction now gives a concrete operator-valued Cauchy covector:

```text
A_a^adv = G_A,adv delta(chi_a P_a),
w_a     = g_a h_a d A_a^adv,
V_a^adv = G_Ea,adv w_a,
ell_a(u)=omega_Ea(Cauchy(V_a^adv),u).
```

This is the correct object against which the emitter preparation must be
selected.  The Maxwell and massive-two-form Green images have not yet been
evaluated, so no coordinate-level `u_a` or absolute-`g^3` detector
coefficient is claimed.
