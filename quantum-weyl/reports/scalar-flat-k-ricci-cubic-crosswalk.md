# Scalar-flat K/Ricci cubic crosswalk

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

## Result

The third-curvature carrier convention uses

\[
K_{\mu\nu}=\frac{2}{\Box}\nabla^\beta\nabla^\alpha
C_{\alpha\mu\beta\nu}.
\]

In four dimensions the contracted Weyl identity has coefficient
\((d-3)/(d-2)=1/2\). On the declared scalar-flat source-complement domain,
the contracted Bianchi identity and
\([\nabla,\nabla]\operatorname{Ric}=O(\mathcal R^2)\) give

\[
\nabla^\beta\nabla^\alpha C_{\alpha\mu\beta\nu}
=\frac12\Box R_{\mu\nu}+O(\mathcal R^2),
\]

and hence

\[
\boxed{K_{\mu\nu}=R_{\mu\nu}+O(\mathcal R^2).}
\]

The independent verifier also evaluates a nontrivial exact flat-TT tensor
fixture and checks componentwise

\[
k^\alpha k^\beta C_{\alpha\mu\beta\nu}
=\frac12 k^2R_{\mu\nu},
\]

so the sign and contracted-index order are not accepted from the scalar
coefficient arithmetic alone.

The first error in replacing a cubic product of three K tensors by three
Ricci tensors has order \(2+1+1=4\). The replacement is therefore exact for
the third-curvature calculation modulo \(O(\mathcal R^4)\).

## Five-carrier target

The normalization crosswalk does not perform the tensor decomposition. The
generic Endo triangle contains longitudinal projector sectors with up to six
external derivatives, so its possible carrier targets are:

| explicit derivatives | carriers |
| ---: | --- |
| 0 | `I10` |
| 2 | `I24`, `I25` |
| 4 | `I28` |
| 6 | `I29` |

Thus the next gate is a decomposition of the twenty exact simplex/Wick rows
in the full five-carrier basis, followed by the curved-Endo one- and two-
insertion traces. No repository form-factor function or coefficient is
claimed yet.

## Replay

```bash
PYTHONPATH=quantum-weyl python3 -m transfer.scalar_flat_k_ricci_crosswalk --emit
PYTHONPATH=quantum-weyl python3 -m transfer.scalar_flat_k_ricci_crosswalk --check
PYTHONPATH=quantum-weyl python3 -m transfer.verify_scalar_flat_k_ricci_crosswalk
PYTHONPATH=quantum-weyl python3 -m unittest transfer.tests.test_scalar_flat_k_ricci_crosswalk
```
