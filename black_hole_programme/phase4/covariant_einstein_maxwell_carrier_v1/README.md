# Covariant Schouten--Einstein/Maxwell carrier

This exact package verifies that, on a four-dimensional Ricci-flat
background,

```text
q_ab[h] = deltaR_ab[h] - g_ab deltaR[h]/6
deltaB_ab[h] = -deltaG_ab[q[h]]
div(q) = d trace(q).
```

When the target Einstein carrier is a target diffeomorphism
`q=L_eta g`, the constraint is the source-free Maxwell equation for
`F=2 d eta`.  A source Weyl transformation shifts `eta` by a gradient and
leaves `F` unchanged.  The quadratic pure-Weyl bulk action on this layer is
`2 alpha Integral(F^2)`, or `-8 alpha` times the conventional Maxwell action,
modulo the Euler and explicit divergence boundary terms.

The certified axial `ell=2` spin-one quotient is therefore the Maxwell
gauge-vector layer of the target Einstein carrier.  The all-`ell` lift and
extension theorem remains open.

Run:

```bash
python3 produce.py
python3 verify.py
python3 -m unittest -v test_carrier.py
```
