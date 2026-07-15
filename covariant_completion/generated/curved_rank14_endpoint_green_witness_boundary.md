# Rank-14 endpoint generalized-witness boundary

The corrected five-term equation cone has an exact support-local operator
`P = D H + H D` using only the certified backward maps.  Its endpoint blocks
are the gauge wave `Caux Kaux` and subsidiary `N iC` operators.

| Block | Forced diagonal | Green status |
|---|---|---|
| G | `Caux Kaux` | yes |
| M | `Eaux+Kaux Caux` | open |
| U | `pF Ewc=L_26` | yes |
| E | `Eaux+Kaux Caux` | open |
| Q | `Ewc pF+iC N=diag(L_26,S_14)` | yes |
| I | `Caux Kaux` | yes |
| J | `N iC=S_14` | yes |

The two remaining blocks are both `Eaux+Kaux Caux`.  The exact scalar-wave
realization of this operator is ruled out, and no independent mixed-order
Green theorem is currently certified.  The nonzero local triangular
couplings `pF A-T` and `iC B-A K` do not change that diagonal obstruction.
Consequently this certificate establishes the generalized-witness identity
and the exact analytic boundary, but does not promote the rank-14 Green
operators or causal homotopy.

There is also an exact role-separation obstruction: both required endpoint
blocks have nonzero idempotency defects, so this Green-witness anticommutator
cannot be the algebraic chain projector.  The endpoint restrictions give
full-operator rank lower bounds 23, 14, and 10 at the generic, null, and zero
samples; their leading defects have generic ranks 9 and 14.  The correct architecture uses a
separate local `P_alg=D H_alg+H_alg D`, sets `P_end=1-P_alg`, and constructs
`L_end=D W_end+W_end D` only on the residual complex.  `L_end` is a Green
operator target, not a projector.  The five-term carrier is not self-dual,
so cyclic adjointness must be checked only after adjoining its cotangent-dual
cone.

That algebraic half is now exact on the completed mapping cylinder:
`H_alg=-H_cone`, `P_alg=1-IP`, and `P_end=IP` are complementary, idempotent,
chain-commuting, and cyclic-adjoint.  Here `P_end` retains the 66-component
auxiliary base; it is not the 30-component metric-core projector.  The
separate composite-projector certificate performs that further contraction.
The remaining construction is the
separate `W_end` and its finite triangular Green inverse on `im(P_end)`.

Checks: schema, complex, witness_identity, endpoint_green, five_known_two_open, projector_incompatibility, two_operator_roles, no_false_promotion, fail_closed.
