# Repaired a/d polynomial zero locus

Combining the full-time radion sources with the restored circumference-
velocity coefficient gives the complete positive-degree cross ideal on the
`ell=2,k=0` extra block:

```text
a*z_ax1 = a*z_ax2 = a*z_pol1 = a*z_pol2 = d*z_pol2 = 0.
```

The four `a` equations follow from independent leading rows of the direct
four-dimensional source.  The last equation is the repaired polar
`d*z_pol2*t` coefficient.  These generators already form the exact Groebner
basis in the declared amplitude order.

The zero locus has three useful faces:

1. no extra wave, with `a,d` unrestricted by this cross ledger;
2. `a=0,z_pol2=0`, allowing `d` and the two axial plus first polar modes;
3. `a=d=0`, allowing all four extra modes.

The previously classified nonzero-extra common-zero cone survives the repair
because it already has `a=b=d=0`; its separate twist-velocity polynomial
obstruction is unchanged.  Constant shell resonances and moment maps on the
new faces remain to be solved.
