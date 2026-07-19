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

The repaired `ell=2` regression gives rank zero in every branch: Einstein
kernel dimension ten on each shell and extra kernel dimension twenty.  The
former nonzero ranks used `*dY_11` against `ell=2` adjoints and are superseded.
No generic-`ell` matrix rank is asserted here.  The bounded cone remains
`OPEN`, and the causal row remains `NO_CERTIFIED_MAP`, until the three finite
matrices are computed with correctly typed carriers and their physical-fibre
ranks proved.
