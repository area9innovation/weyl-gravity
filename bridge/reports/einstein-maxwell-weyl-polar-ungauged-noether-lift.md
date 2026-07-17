# Polar ungauged equation/Noether lift

Result:
`POLAR_UNGAUGED_DIFF_WEYL_EQUATION_NOETHER_COMPLEX_AND_CHAIN_MAP_CERTIFIED`.

The eight ungauged polar coefficients are ordered as

```text
(A,B,C,h_t,h_x,K,G,U).
```

Here `U` multiplies the coexact sphere one-form.  The exact scalar `U(1)`
gauge variation belongs to the complementary exact-potential harmonic block,
so no `U(1)` ghost acts inside this closed coefficient complex; the scalar
Diff ghost still shifts `U` through contraction with the magnetic background.

Three source Diff ghosts contract these fields to the five certified
Einstein–Maxwell slice variables.  Adding the Weyl ghost contracts them to the
four target variables `(A_t,B,C_t,U)`.  Explicit sections and homotopies obey

```text
P_s G_s=0,        P_t G_t=0,
P_s J_s=I_5,      P_t J_t=I_4,
J_s P_s-I_8=G_s H_s,
J_t P_t-I_8=G_t H_t,
P_t=S_P P_s.
```

Only the constants `2` and `4` are divided out.  In particular `k`, `omega`,
`p`, and `q` remain uninverted, so zero momentum and zero frequency are not
discarded.

The source raw tensor Euler map has three exact Bianchi rows.  The target
action Hessian has four Noether rows, the fourth coming from Weyl symmetry.
The gauge-fixed equation square lifts to all eight fields:

```text
L_t^ung = J_E E_s^ung.
```

Together with the natural Diff ghost embedding and the zero identity-row map,
this gives an exact polynomial ghost–field–equation–identity chain map.  It is
not degreewise injective at equations/identities and is not claimed to be a
cyclic BV morphism or strict short exact sequence.

The target operator is formally self-adjoint and its coefficientwise local
Green current has 184 temporal and 184 spatial terms.  The complete off-shell
jet remainder vanishes.  Restricting to the canonical target section gives
exactly the 32+32-term reduced current already matched to the direct
four-dimensional Lee–Wald current.

This closes the generic polar ungauged equation/Noether and local-current
gate.  It does not perform the final residual quotient, construct a Peierls
observable, establish a causal phase space, or satisfy the classical import
gate for quantum use.

Verification:

```text
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_polar_ungauged_noether_lift --verify bridge/certificates/einstein_maxwell_weyl_polar_ungauged_noether_lift.json
python3 -m bridge.einstein_sector.verify_einstein_maxwell_weyl_polar_ungauged_noether_lift
python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_polar_ungauged_noether_lift
```

Tier 0 completed in `0.04` seconds and Tier 1 in `9.54` seconds, both with
status `PASS`.  No upstream content-addressed operator changed, so there was
no additional affected-chain rebuild.  Tier 3 was not run because this result
does not freeze a paper theorem, change shared core algebra, prepare a release,
or promote a causal or quantum lifecycle state.
