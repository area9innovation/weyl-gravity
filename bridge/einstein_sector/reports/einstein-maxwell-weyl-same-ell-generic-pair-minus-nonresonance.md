# Generic oscillator pairs cannot land on a minus shell

The existing cross-`ell` theorem removes every pair with distinct generic
input angular momenta.  For equal input `ell`, the remaining arithmetic is
controlled by two sharp brackets.

Every nonzero branch difference is smaller than the lowest generic minus
frequency.  For `ell>=3`,

```text
omega_plus(ell)-omega_minus(ell) < 159/100
                                    < omega_minus(2),
```

and `ell=2` follows from the exact witness `18-10sqrt(3)>0`.  For sums,
`2*omega_minus(ell)` lies strictly between the consecutive shells
`omega_minus(2ell-1)` and `omega_minus(2ell)`.  Every other branch sum is
larger than `2ell-1/5`, while the largest angularly allowed target is smaller
than that value.

Consequently no pair of generic `k=0` p/q oscillators—at equal or distinct
input `ell`—can screen a generic minus-shell functional.  The only remaining
frequency competitor is an exceptional dipole paired with a generic mode.
