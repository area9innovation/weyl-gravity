# Second-order parent flux certificate

This package certifies the `LOCAL-ALGEBRAIC` auxiliary-tensor parent
formulation of the quadratic pure-Weyl system on a four-dimensional
Ricci-flat background and its `REDUCED-MODE` consequences.

The certified statements are:

- eliminating the auxiliary symmetric tensor returns the Ricci-factorized
  quadratic Weyl action modulo the Euler density;
- the parent Euler--Lagrange equations are `deltaG[f]=0` and `f=q[h]`;
- the parent presymplectic current is the off-diagonal linearized-Einstein
  Green current, modulo the independently certified Euler transgression;
- every nondegenerate source/target spin-two block admits a null lift and is
  hyperbolic;
- the triangular Evans determinant has divisor `2 div(D2)+div(D1)`, so the
  extension changes Smith/Jordan structure but not algebraic root count.

The package explicitly does **not** promote generic radial nonsplitting to a
time-Jordan theorem, the certified connection EP2 to a Green-resolvent pole,
or threshold asymptotics to an all-frequency reflection theorem.

Run:

```bash
python3 produce.py
python3 verify.py
python3 -m unittest -v test_parent.py
```
