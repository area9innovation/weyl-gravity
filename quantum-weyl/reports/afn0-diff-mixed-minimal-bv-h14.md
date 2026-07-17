# AFN0 Diff/mixed and minimal-BV H14 quotient

The four-dimensional minimal-BV anomaly quotient is complete on the imported
regular Bach-locus coordinate chart. Its even/odd dimensions are `2/1`, with

```text
even: ANOM_OMEGA_C2, ANOM_OMEGA_E4
odd:  ANOM_OMEGA_C_DUAL_C
exact: ANOM_OMEGA_BOX_R
```

There is no additional pure-diffeomorphism class and no independent mixed
Diff--Weyl class. Mixed lower-form terms remain present as the required
universal Diff completion of the Weyl representatives; “no independent mixed
class” does not mean those descendants vanish.

## Why the raw graph inventory is not expanded

The earlier ambient receipt counts 720 refined signatures and
2,860,932,903 raw contraction graphs across the neighboring total degrees.
Expanding them would replay coordinate presentations of a comparison theorem
rather than compute a new quotient.

The reduction instead has two exact parts:

1. The checked-in horizontal bicomplex verifies the universal Diff tower
   coefficientwise on a generic strict density and its Weyl-ghost lift. The
   Euler representative has its independently verified intrinsic and Diff
   completion. The Stora total-form comparison therefore reduces the
   covariant tensor sector to the already complete Weyl top-form quotient.
2. A non-covariant pure-gravity anomaly could escape that reduction only
   through the degree-three Chern--Weil invariant-polynomial sector. The new
   small-algebra calculation constructs the six generators of `so(4)` in the
   vector representation, derives all commutators, and solves the adjoint
   invariance equations on symmetric tensors exactly over `Q`.

The resulting invariant dimensions in degrees one through four are

```text
0, 2, 0, 3.
```

The degree-three matrix has 56 columns and exact rank 56. Three independent
finite-field eliminations at primes 101, 103, and 107 also return rank 56;
full rank modulo any one of them already implies full rank over `Q`. Hence the
six-dimensional anomaly polynomial needed for a four-dimensional pure
gravitational anomaly is absent. The nonzero degree-two and degree-four
spaces are retained as controls, preventing a vacuous-zero implementation.
The Lorentzian algebra has the same complexification as the rational `so(4)`
realization used for this invariant-polynomial dimension.

This application follows the total-differential and generalized-connection
classification in Boulanger,
[arXiv:0704.2472](https://arxiv.org/abs/0704.2472), and the antifield/local
gravity classification of Barnich, Brandt, and Henneaux,
[arXiv:hep-th/9505173](https://arxiv.org/abs/hep-th/9505173). The repository
does not merely cite the dimensional conclusion: it independently computes
the finite invariant-polynomial obstruction space and binds the result to the
generated Diff and Euler towers.

## Minimal antifields

The imported positive-antifield columns are already acyclic by the exact
Koszul--Tate contraction. Combining that contraction with the completed AFN0
total complex gives the same `2/1` quotient for the minimal BV complex on the
regular Bach locus.

## Claim boundary

This is `LOCAL-ALGEBRAIC`. The general local nonminimal and gauge-fixed
doublets have not yet been imported and explicitly contracted, so the full G2
promotion remains open. This result computes no anomaly coefficient,
Slavnov breaking, restored QME, residual transfer, Hadamard state, Lorentzian
time-ordered product, or quantum theory.

The machine receipt is
[`AFN0_DIFF_MIXED_MINIMAL_BV_H14.json`](../local_bv/certificates/AFN0_DIFF_MIXED_MINIMAL_BV_H14.json).
