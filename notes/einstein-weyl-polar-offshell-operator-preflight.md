# Polar off-shell Einstein--Weyl preflight

The polar sector cannot reuse the axial field map verbatim. After fixing the
three polar diffeomorphisms, the Einstein--Maxwell coefficients are

```text
(A,B,C,K,U).
```

The Weyl target has one additional scalar gauge parameter. On this source
slice it acts in the direction `(-1,0,1,1,0)`. Fixing the target Weyl gauge by
setting the transformed sphere trace to zero gives the polynomial map

```text
S_P(A,B,C,K,U)=(A+K,B,C-K,U).
```

Its kernel is precisely the pure-Weyl direction. The certified
Einstein--Maxwell equation matrix sends that vector to a row whose
sphere-tracefree component is `-1`; hence the kernel contains no Einstein
solution. This proves injectivity of the field contraction on the Einstein
solution kernel without dividing by momentum, frequency, or a shell factor.

The missing object is now precise. The existing direct polar Weyl--Maxwell
current is a two-by-two form after substitution of Einstein master
representatives. It is not the four-by-four target Euler operator and cannot
determine the extra characteristic or the off-shell equation-row map.

The next equation is

```text
L_WM^P S_P = J_P E_P,
```

where `E_P` is the certified eight-by-five Einstein polar equation matrix,
`L_WM^P` is the independently derived four-by-four target Hessian on
`(A+K,B,C-K,U)`, and `J_P` must be polynomial with no physical inversions.
Only after this square and its ungauged Noether lift pass does the polar
mapping cone exist as a complex.
