# Nonzero-momentum constant-twist bounded mixed column

For every fixed generic `ell>=2`, every allowed nonzero compact momentum and
every axial/polar `q/p` primary, the constant-twist bilinear source has an
exact action-normalized same-shell projection.  With the twist direction as
the quantization axis, it is

```text
q_minus: (A_hat dot J_ell) tensor ( 4*k*sqrt(2*lambda)*G_q_minus),
q_plus:  (A_hat dot J_ell) tensor (-4*k*sqrt(2*lambda)*G_q_plus),
p:       (A_hat dot J_ell) tensor (-2*k*G_p).
```

The action Grams are nondegenerate on every physical fibre.  Consequently,
for nonzero twist and `k!=0`, the common same-shell kernel is exactly

```text
V_(ell,m_A=0) tensor (M_q_minus direct sum M_q_plus direct sum M_p).
```

This is the sharp contrast with the rest frame.  Flat lifted `SO(3)`
covariantization replaces `k` by `k+alpha*(A_hat dot J_ell)`.  The `p` and `q`
primaries are even in this momentum, so their first derivative vanishes at
`k=0`; at nonzero `k` it is the nonzero scalar displayed above.  The `-k`
operator changes sign and has the same kernel, so the statement is compatible
with the conjugate momentum pair required by a real field.

This also closes the neighboring angular outputs.  The twist has zero circle
momentum, so every mixed output retains `K=k`; after writing
`s=omega^2-k^2`, all `L=ell-1,ell+1` target factors are exactly the already
certified momentum-independent neighbor ledger.  The exceptional
`ell=2 -> L=1` lower channel is separately off shell relative to the certified
nonzero-`k` exceptional invariants `s=4,4/3`.  Therefore the complete
constant-twist-times-wave bilinear source has a bounded correction precisely
on the `m_A=0` face.

The theorem does not solve wave--wave terms, classify opposite-momentum
quadratic cross terms, solve the other global constraints, or establish
causal/retarded propagation.
