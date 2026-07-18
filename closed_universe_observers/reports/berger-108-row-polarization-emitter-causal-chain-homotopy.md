# 108-row polarization-emitter causal chain homotopy

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

The causal-chain witness is the direct extension

```text
W_108 = W_84 direct_sum W_K0 direct_sum W_K1,
W_Kb(K_b_plus) = K_b.
```

Thus `P_108=q_108 W_108+W_108 q_108` contains the exact massive two-form
Euler operators on its new diagonal blocks and the reciprocal Maxwell--emitter
couplings off diagonal.  Starting from the imported same-sided apparatus and
emitter Green operators, the formal inverse is

```text
G_Pg = G_P0 - g G_P0 U G_P0 + g^2 G_P0 U G_P0 U G_P0 + O(g^3),
Lambda_108,+/- = W_108 G_Pg,+/-.
```

Locality of `W_108` and `U` preserves the advanced or retarded side in every
displayed finite composition.  A ten-channel fixture includes the Maxwell
ghost, gauge and physical potential components, both emitters, every dual,
and the Maxwell ghost antifield.  It verifies `q^2=0`, both inverse orders,
degree minus one for `Lambda`, and
`q Lambda+Lambda q=1` through `g^2`.  Deleting the quadratic Green coefficient
or one emitter witness is detected.

This is a coefficientwise theorem over the imported apparatus first-jet ring,
not a finite-parameter or all-orders Green-hyperbolicity result.  Actual
localized free-emitter Cauchy preparations and their detector response matrix
are the next gate; detector recoil integration and emitter stress remain open.
