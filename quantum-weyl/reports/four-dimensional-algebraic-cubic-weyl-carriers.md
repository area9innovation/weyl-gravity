# Four-dimensional algebraic cubic Weyl carriers

Date: 2026-07-18

Dependency tag: `LOCAL-ALGEBRAIC`

Result state:
`ALGEBRAIC_C3_CARRIERS_COMPLETE_NONLOCAL_CUBIC_FORM_FACTORS_OPEN`

## Outcome

The pointwise zero-derivative contractions of three algebraic Weyl tensors
are now exhaustive in four Euclidean dimensions.  On two-forms the Weyl
tensor splits into symmetric tracefree (3\times3) blocks (C_+) and
(C_-).  For either block, the exact complete-contraction enumeration is

```text
raw pairings of six block slots             15
identical-factor contraction orbits          3
orbits killed by tracefreeness                2
canonical nonzero orbit                       1
```

The surviving orbit is the triangle contraction

\[
 W_{ij}W_{ik}W_{jk}=\operatorname{tr}(W^3).
\]

The self-dual and anti-self-dual two-form projectors are orthogonal, so a
cross-chirality contraction edge vanishes. After block decomposition the two
mixed allocations therefore contain a lone tracefree block and vanish.
Consequently the chiral algebraic cubic space is exactly

\[
 \operatorname{span}\{\operatorname{tr}(C_+^3),
                       \operatorname{tr}(C_-^3)\}.
\]

In the parity basis this becomes one even and one odd carrier,

\[
 I_e=C_{ab}{}^{cd}C_{cd}{}^{ef}C_{ef}{}^{ab},
 \qquad
 I_o=({*C})_{ab}{}^{cd}C_{cd}{}^{ef}C_{ef}{}^{ab}.
\]

The exact crosswalk is

\[
 \binom{I_+}{I_-}
 =\frac12
  \begin{pmatrix}1&1\\1&-1\end{pmatrix}
  \binom{I_e}{I_o},
 \qquad
 \binom{I_e}{I_o}
 =\begin{pmatrix}1&1\\1&-1\end{pmatrix}
  \binom{I_+}{I_-}.
\]

Parity exchanges the chiral rows and acts diagonally as ((+1,-1)) on the
second basis.  Evaluating on the two exact samples

```text
(C+,C-)=(diag(1,1,-2),0)
(C+,C-)=(0,diag(1,1,-2))
```

gives the parity-basis matrix

\[
 \begin{pmatrix}-6&-6\\-6&6\end{pmatrix},
\]

of rank two.  The even tensor carrier also has exact coordinate (2/3) in
the previously certified Schouten-zero Weyl image, providing an independent
cross-check against the abstract-index quotient.

## What this closes

The earlier odd Hodge companion was only constructed, not exhaustive.  It is
now exhaustive for the algebraic, zero-derivative (C^3) sector.  This also
gives a deterministic parity/chiral carrier manifest for the next nonlocal
calculation.

## What remains open

This is not the third-curvature effective action.  A generic nonlocal term
has the form

\[
 \sum_m\int\Gamma_m(\Box_1,\Box_2,\Box_3)
 I_m[C_1,C_2,C_3].
\]

Derivative placements and labelled d'Alembertians prevent the unrestricted
integration-by-parts reduction used for local order-six scalars.  Therefore
the following remain `NOT_COMPUTED`:

- derivative-decorated cubic Weyl carriers;
- permutation and branch properties of the form factors;
- the functions \(\Gamma_m(\Box_1,\Box_2,\Box_3)\);
- all cubic coefficients;
- the complete finite \(\Gamma_1\) and renormalized \(Q_1\).

Moreover (C^3) has engineering dimension six.  It is not a new
dimension-four one-loop local counterterm without a nonlocal inverse power or
another scale.

The scope follows the primary third-curvature and conformal-decomposition
analyses in [arXiv:0911.1168](https://arxiv.org/abs/0911.1168),
[arXiv:gr-qc/9510037](https://arxiv.org/abs/gr-qc/9510037), and
[arXiv:hep-th/9510205](https://arxiv.org/abs/hep-th/9510205).  Those sources
motivate the nonlocal seam; they are not inputs to the exact contraction
enumeration.

## Receipts

- `quantum-weyl/transfer/certificates/FOUR_DIMENSIONAL_ALGEBRAIC_CUBIC_WEYL_CARRIERS.json`;
- `quantum-weyl/transfer/cubic_weyl_carrier_basis.py`;
- `quantum-weyl/transfer/verify_cubic_weyl_carrier_basis.py`;
- `quantum-weyl/transfer/tests/test_cubic_weyl_carrier_basis.py`.

## Next gate

Construct the derivative-decorated third-curvature Weyl carrier manifest
with labelled \(\Box_i\), quotient it only by identities compatible with
nonlocal form factors, and then bind the appropriate one-loop form-factor
functions.  Complete \(\Gamma_1\), \(Q_1\), and residual transfer remain
fail-closed.
