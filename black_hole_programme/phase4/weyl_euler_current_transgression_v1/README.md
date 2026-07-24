# Weyl/Euler current transgression v1

This exact package separates the literal four-dimensional \(C^2\)
presymplectic current from the Ricci-factorized bulk current.

It certifies:

- \(C^2=E_4+2R_{ab}R^{ab}-2R^2/3\);
- the connection-form Euler transgression
  \(\omega_{E_4}=d k_{E_4}\);
- \(\omega_{C^2}-\omega_{\mathrm{Ric}}=d k_{E_4}\);
- the exact axial Einstein cut identity
  \(F^r_{EE}=\partial_t Q_{EE}\);
- zero integrated Einstein--Einstein flux at finite radius for the declared
  smooth compact-frequency wave-packet core.

The certificate does **not** assert pointwise vanishing of the literal
monochromatic current, unconditional endpoint-limit interchange, or Euler
exactness of the mixed Einstein/additional pairing.

Run:

```bash
python3 produce.py
python3 verify.py
python3 -m unittest -v test_transgression.py
```
