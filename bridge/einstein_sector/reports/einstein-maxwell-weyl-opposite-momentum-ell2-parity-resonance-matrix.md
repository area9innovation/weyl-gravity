# Tuned opposite-momentum parity resonance matrix

At the certified tuned `ell=2` fibre, the complete `L=4,K=0,Omega=2omega_-`
sum-frequency resonance matrix is now direct in both input parities.

Writing the axial Einstein-minus coefficients as `a_+,a_-` and the polar
coefficients as `p_+,p_-`, its two nonzero adjoint functionals are

```text
R_polar = A*(a_+*a_- - 3*p_+*p_-),
R_axial = C*(a_+*p_- - a_-*p_+),
```

where

```text
A = -1152*(-265+149*sqrt(3))/203 != 0,
C = 864*sqrt(-7+12*sqrt(3))*(-11*sqrt(6)+19*sqrt(2))/7 != 0.
```

Thus pure axial and pure polar standing waves are individually obstructed,
but the `L=4` matrix has the exact mixed null face

```text
a_+ = sigma*sqrt(3)*p_+,
a_- = sigma*sqrt(3)*p_-,
sigma in {+1,-1}.
```

This is a candidate bounded mixed-parity face, not yet a bounded extension.
Every remaining output block, including those involving the Einstein-plus
balance coefficients, must still be evaluated on this locus.  Smooth secular
extension remains certified; causal propagation has no certified map.
