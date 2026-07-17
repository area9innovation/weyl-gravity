# Exceptional `L=1` cross-ell nonresonance

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

A distinct generic input pair can couple to `L=1` only when its angular
degrees are adjacent, `(ell,ell+1)`.  The complete exceptional target root
set is

```text
omega^2 in {0,4/3,4}.
```

Exact branch-offset intervals exclude all six cross-branch pairs.  For the
three same-branch pairs, the only interval-compatible candidate is
`omega=2/sqrt(3)`.  The extra-extra squared-resonance polynomial is

```text
-4*(ell-1)*(ell+3)/3,
```

so it never vanishes for `ell>=2`.  The two equal-q-branch cases are reduced
in the squarefree radical basis.  Distinct squarefree parts have a unique
nonzero product-root coefficient.  Equal squarefree parts would require a
rational ratio whose squared remainder is

```text
2*(3*ell^2+6*ell-1)>0.
```

One or two rational inner roots are excluded respectively by a nonintegral
coefficient equation and the `4/3` target denominator.

Together with the generic-output theorem, this closes the complete
unbounded distinct-`ell`, `k=0` output-resonance gate.  The next question is
no longer spectral: it is the mixed quadratic source and its adjoint-cokernel
projection on common moment-map-zero data.

## Verification receipt

Date: 2026-07-18.  Tier 0 scoped compilation, JSON, and diff checks passed
in `0.05 s`; Tier 1 replay, independent verifier, and four tests passed in
`1.0 s`.  Tiers 2 and 3 were not run because no shared operator changed and
the mixed source remains explicitly open.
