# Four-dimensional third-curvature Weyl carrier manifest

## Result

The parity-even pure-gravity third-curvature sector now has a precise carrier
manifest in the declared Euclidean, asymptotically flat, scalar-flat conformal
representative.  The source tensor is

\[
K_{\mu\nu}=\frac{2}{\Box}\nabla^\beta\nabla^\alpha
C_{\alpha\mu\beta\nu}.
\]

This `K` is a derived nonlocal symmetric tensor.  It is not the four-index
Weyl tensor and must not be identified with the unrelated kinetic or gauge
operators that also use the letter `K` elsewhere in the repository.

The five carrier labels are:

| carrier | schematic tensor structure | explicit derivatives | label stabilizer | generic label orbit |
| --- | --- | ---: | --- | ---: |
| `I10` | `tr(K1 K2 K3)` | 0 | `S3` | 1 |
| `I24` | `K1 ∇K2 ∇K3` | 2 | `S2(23)` | 3 |
| `I25` | `K1 ∇K2 ∇K3` with crossed derivative indices | 2 | `S2(23)` | 3 |
| `I28` | `∇K1 ∇K2 ∇∇K3` | 4 | `S2(12)` | 3 |
| `I29` | `∇∇K1 ∇∇K2 ∇∇K3` | 6 | `C3` | 2 |

The generic labelled permutation module therefore has dimension

\[
1+3+3+3+2=12.
\]

Its exact `S3` character is `(12,4,3)` on the identity, transposition and
three-cycle conjugacy classes, hence

\[
V_{\rm raw}\cong5\mathbf1\oplus\mathbf1_{\rm sign}
\oplus3\mathbf2_{\rm std}.
\]

## Four-dimensional identity

Appendix (A.35) of Covariant Perturbation Theory IV gives one integrated
four-dimensional identity for an arbitrary completely symmetric function of
the three labelled d'Alembertians.  In the pure-`K`, scalar-flat sector its
coefficients multiply `I10`, `I24`, `I25` and `I28`; `I29` is absent.  Choosing
a section of the quotient by removing the fully symmetric component of
`I28` gives

\[
\dim V_{4d}=11,
\qquad
V_{4d}\cong4\mathbf1\oplus\mathbf1_{\rm sign}
\oplus3\mathbf2_{\rm std}.
\]

This statement should not be paraphrased as “eleven form factors.”  There are
five carrier-labelled functions with different stabilizers and one arbitrary
fully symmetric functional relation.  Eleven is the dimension of the generic
label permutation module after that relation, before analytic functions of
the labelled operators are selected.

`I29` is ineliminable under this identity and is the source row whose local
limit has the unique parity-even algebraic `C³` lineage.  The normalization
between those two conventions has not been computed.  The earlier exact
algebraic receipt also contains one parity-odd `C³` direction; this new
manifest is parity-even only and does not classify a derivative-decorated odd
sector.

## Claim boundary

This is an `EUCLIDEAN-SPECTRAL` carrier and permutation-quotient result.  It
does not compute the five repository form-factor functions or any coefficient.
It does not fix the finite `C²` constant, the absolute dressed
`R(ĝ)²` normalization, global inverse data, renormalized products, complete
`Γ₁` or `Q₁`, a residual transfer, or a Lorentzian QME.  In particular, it
does not convert a nonlocal effective-action carrier into a particle state or
a local anomaly class.

## Sources

- A. O. Barvinsky, Yu. V. Gusev, G. A. Vilkovisky and V. V. Zhytnikov,
  *Covariant Perturbation Theory (IV). Third Order in the Curvature*,
  arXiv:0911.1168, especially equations (2.55), (2.69), (2.70), (2.73),
  (2.74) and (A.35).
- A. O. Barvinsky and G. A. Vilkovisky, *Conformal Decomposition of the
  Effective Action and Covariant Curvature Expansion*, arXiv:gr-qc/9510037,
  especially equations (29), (33) and (41).
- A. O. Barvinsky et al., *Partial Summation of the Nonlocal Expansion for
  the Gravitational Effective Action in 4 Dimensions*, arXiv:hep-th/9510205.

## Replay

```text
PYTHONPATH=quantum-weyl python3 -m transfer.third_curvature_weyl_manifest --check
PYTHONPATH=quantum-weyl python3 -m transfer.verify_third_curvature_weyl_manifest
PYTHONPATH=quantum-weyl python3 -m unittest \
  transfer.tests.test_third_curvature_weyl_manifest
```
