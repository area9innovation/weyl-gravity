# Berger downstream Maxwell detector dual norms

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

The detector lapse is now resolved exactly.  With `Theta=3t/4`, the factor
`4/3` in the spacetime measure cancels the factor `3/4` in the electric
pairing with `dTheta`.  Because each clock bump has unit `dTheta` integral,
the detector energy dual is the spatial `L2` norm of `rho_a J_a dR_aI`.

Using `J dSigma=d3R`, the validated radial `B` and `B^2` integrals, and the
exact rod derivative matrix gives

```text
D0 <= 1.2031e3,
D1 <= 2.5363e3.
```

The rational squared norms and outward-rounded dyadic norm uppers are stored
in the certificate.  Composing with the Maxwell retarded energy estimate and
the massive finite-slab theorem certifies, for all `a,b in {0,1}` and
`m_b>0`,

```text
|Q_a[d G_A,ret delta(h_b K_b)]|
  <= D_a (3 H_b^2/m_b^2 + 8 H_b/(3m_b)) E_A.
```

These are four symbolic tail radii, not four evaluated recoil intervals.
Numerical masses/couplings, a declared stopping goal, and the complete
modewise scalar integrand remain open and are not inferred from the bound.
