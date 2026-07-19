# Fixed-ell constant-twist factorization

For every integer `ell>=2`, rotational covariance reduces each constant-twist
resonance map to

```text
R_(ell,branch)(A) = (A_hat dot J_ell) tensor Q_(ell,branch).
```

The reason is exact: `V_ell` occurs with multiplicity one in
`V_1 tensor V_ell`.  After rotating nonzero `A` to the `z` axis, the angular
factor has eigenvalues `-m/sqrt(ell*(ell+1))`.  Its kernel is precisely the
axisymmetric `m_A=0` line.

Thus the unresolved all-`m` problem is reduced to two `2x2` Einstein matrices
`Q_(ell,+/-)` and one `4x4` extra matrix `P_ell`.  If a multiplicity matrix
`Q:M_in->M_out` has rank `r`, the full resonance kernel has dimension

```text
dim(M_in) + 2*ell*(dim(M_in)-r).
```

The `ell=2` regressions reproduce the certified Einstein kernel dimension two
on each shell and extra kernel dimension twelve.  No generic-`ell` matrix rank
is asserted here.  The bounded cone remains `OPEN`, and the causal row remains
`NO_CERTIFIED_MAP`, until the three finite matrices are computed and their
physical-fibre ranks proved.
