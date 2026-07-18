# Homogeneous nonzero-frequency Weyl-Maxwell operator

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

For `ell=0`, `k=0`, and `omega!=0`, use time diffeomorphisms, circle
diffeomorphisms, and `U(1)` gauge to impose

```text
h_tt=h_tx=a_t=0.
```

The remaining coefficients are the circle metric coefficient `C`, the sphere
trace coefficient `K`, and the circle connection `A_x`.  A residual combined
Weyl/time-diffeomorphism shifts `C` and `K` equally, so the complete gauge
invariants are `C-K` and `A_x`.

Direct four-dimensional linearization gives

```text
E_11       = -(omega^4/2)(C-K),
E_sphere   =  (omega^4/4)(C-K),
Maxwell_1  =   omega^2 A_x,
```

with the remaining displayed rows zero.  At nonzero frequency both invariants
therefore vanish, and the homogeneous physical quotient is empty.  There is
no hidden homogeneous fourth-order oscillator; all genuine homogeneous data
belong to the separately certified generalized zero-frequency block.
