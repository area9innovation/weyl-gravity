# Global spectators crossed with `ell=2` extra modes

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

Two directions in the generalized-zero global block cannot contribute a new
exceptional adjoint defect.

For the Wilson coordinate,

```text
A_W=A_bar+W_x dx,   F_W=F_bar.
```

The Weyl-Maxwell Euler operator depends on the Abelian connection only through
`F`, so every `W_x` cross-source vanishes identically.

For the circumference coordinate, use the exact family

```text
g_R=-dt^2+R^2 dx^2+dOmega_2^2,   R^2=1+eta*c.
```

Every `k=0` extra Jacobi field transports along this family by multiplying
each covariant `x` component by `R`.  Differentiating `L_R u_R=0` gives an
explicit mixed correction: `(c/2)` times the logarithmic radius derivative of
the transported representative.  Hence the `c` cross-source lies in the
linear image and all adjoint-cokernel pairings vanish.

This holds for both parities, both extra-primary representatives, and all
`m`.  The remaining positive-sum gate contains `a,b,d,Q_e` and the twist
position/velocity vectors.
