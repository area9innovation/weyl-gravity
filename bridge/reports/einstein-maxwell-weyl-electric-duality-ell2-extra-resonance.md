# Electric duality crossed with `ell=2` extra modes

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

In four Lorentzian dimensions, `star^2=-1` on two-forms and

```text
F_theta=cos(theta)F+sin(theta) star_g F
```

rotates the pair `(dF,d star F)` while leaving the Maxwell stress tensor
unchanged.  The Weyl-Maxwell equations are therefore duality covariant.

At the magnetic fixture, the infinitesimal duality direction is
`star F_bar=dt wedge dx`, precisely the homogeneous electric `Q_e` tangent.
For any extra Jacobi field `(h,f)`, differentiating its duality transport gives
the mixed correction

```text
f_cross=star_bar f+(D_g star)[h]F_bar.
```

It removes the `Q_e`-times-wave quadratic source.  Its sphere period vanishes
because it has `ell=2` support, so it is exact on
`R x S1 x S2` and lifts to a global fixed-bundle connection correction.

This statement concerns the mixed coefficient only.  A finite duality orbit
changes magnetic flux at second order, consistently with the known pure
`Q_e` fixed-bundle obstruction.  The remaining positive-sum source matrix now
contains only `a,b,d` and the twist position/velocity vectors.
