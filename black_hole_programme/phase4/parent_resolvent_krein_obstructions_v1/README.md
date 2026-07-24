# Parent resolvent and Krein-obstruction certificate

This package separates four exact statements from two conditional
applications.

Exact:

- direct inversion of the gauge-fixed parent Hessian;
- the rank-one algebra for the double Laurent coefficient;
- the characteristic-zero involution lemma for a nonsplit self-extension of
  a **simple** differential module;
- the endpoint positive-graph and cotangent-duality consequences.

Conditional:

- the physical QNM pole formula requires an analytic Fredholm realization;
- the stronger “only `C=±1`” Bach-module corollary requires a certificate
  that the generic Regge--Wheeler differential module is simple (or an
  equivalent endomorphism-ring computation).

The package also specifies, but does not execute, the parent-overlap QNM
audit and sequential retarded-convolution experiment.

Run:

```bash
python3 produce.py
python3 verify.py
python3 -m unittest -v test_resolvent.py
```
