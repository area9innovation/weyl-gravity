# Jacobi--axial stability preflight

Every diagonal `Sym^n` scalar mode factors exactly as

```text
D_(m,m)^(n/2)
  = (y0+i y3)^(n-2r) P_r^(0,n-2r)(1-2 y_perp^2),
    m=-n/2+r.
```

Coefficient comparison with the original formula passes for all 4,970
symmetry-unique rows through `two_j=139`.  Thus the published low rail is
preserved algebraically, and the central Legendre identity is the `n=2r`
special case.

The factorization does not by itself solve high-mode stability.  In the
declared termwise independent-moment evaluator through total order 50, the
extreme axial row `r=0` has partial interval width below `0.1` at
`two_j=974`, above `0.1` at the selected `two_j=975` witness, and above
`1,000` at `two_j=2047`.  An independently enclosed remainder can only widen
those intervals; the exact unitary fallback `[-1,1]` supplies no decay.

The next evaluator must preserve correlation in the axial oscillation.  No
noncentral/odd full rail, polarized tail, Green image, detector response,
recoil coefficient, cone restriction, physical-branch crosswalk, or quantum
claim is certified here.
