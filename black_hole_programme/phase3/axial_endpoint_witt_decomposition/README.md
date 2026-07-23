# Axial endpoint Witt decomposition

This package independently pulls the two oriented endpoint Hermitian forms
from
`black_hole_programme/phase3/axial_null_flux_gram/formal-grams.json` and
certifies explicit Witt-adapted bases on
\(\omega\in[1/2,3/4]\).

The calculation is exact over \(\mathbb Q(i,\omega)\).  It proves that each
normalized endpoint form splits as a nondegenerate plane of inertia
\((1,1)\) orthogonal to a negative line of inertia \((0,1)\).  Hence the full
endpoint form has inertia \((1,2,0)\).

This is an algebraic decomposition of the endpoint flux forms.  The chosen
vectors resemble combinations that can occur in generalized-mode
calculations, but the certificate does **not** infer a radial Jordan chain,
a time-translation Jordan chain, a repeated scalar factor, or a globally
populated scattering channel.

Run:

```bash
python3 -m black_hole_programme.phase3.axial_endpoint_witt_decomposition.verify
python3 -m unittest -v \
  black_hole_programme.phase3.axial_endpoint_witt_decomposition.tests.test_witt
```
