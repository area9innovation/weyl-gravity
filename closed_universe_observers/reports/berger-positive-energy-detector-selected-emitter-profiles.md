# Positive-energy detector-selected emitter profiles

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

Let `v_a=(q_a,p_a)` be the Cauchy data of the exact operator-defined advanced
emitter field.  On the co-closed massive two-form sector set

```text
L_a = Delta_(2,Sigma)^co-closed + m_a^2,
u_a = (-p_a,L_a q_a).
```

With the canonical Cauchy symplectic form,

```text
ell_a(u_a)=omega(v_a,u_a)
          = ||p_a||^2 + <q_a,L_a q_a> > 0
```

for nonzero `v_a`, because `m_a^2>0`.  This fixes the preparation without
normalizing by its forward response.  The differential operator `L_a`
preserves both support and the co-closed constraint.  The chosen Cauchy slices
are exactly `1/48` in physical time before the corresponding switch support.

The profiles are explicit as operator expressions, but their Berger harmonic
coefficients and advanced Green images have not been evaluated.  Consequently
the absolute-`g^3` recoil coefficient remains open.
