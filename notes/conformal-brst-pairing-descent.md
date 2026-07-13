# C2g-P: finite-dimensional BRST pairing descent

## Scope

This note gives the exact linear-algebra conditions needed to descend the
indefinite cylinder oscillator form through a future finite-dimensional global
BRST complex. It does **not** construct that physical complex. In particular,
the existing algebra-only Chevalley--Eilenberg rail does not yet supply a ghost
Fock pairing, oscillator charge matrices, local Diff `x` Weyl ghosts, or a
physical cohomology.

## The required adjoint

Let the complete oscillator-plus-ghost state space carry a nondegenerate
Hermitian form

\[
(x,y)_G=x^\dagger G y,
\qquad G^\dagger=G,
\qquad \det G\ne0.
\]

The BRST adjoint is the Krein adjoint

\[
Q^\sharp=G^{-1}Q^\dagger G.
\]

For the standard Hermitian BRST-charge convention, the required identity is

\[
\boxed{Q^\sharp=Q}
\qquad\Longleftrightarrow\qquad
Q^\dagger G=GQ.
\]

Using an anti-Hermitian differential changes the right-hand side to
`Q^sharp=-Q` and none of the orthogonality conclusions below. Nilpotency by
itself is insufficient.

Although `Q` raises ghost number, this relation is consistent because the
ghost form does not normally preserve ghost number. More generally, if it
pairs degree `r` with degree `nu-r`, then

\[
N_{\rm gh}^\sharp=\nu I-N_{\rm gh},
\qquad [N_{\rm gh},Q]=Q,
\]

and conjugation by `G` turns the ordinary degree-lowering adjoint back into a
degree-raising operator. The centered ghost number
`N_gh-nu I/2` is `G`-skew. A block-diagonal, ghost-number-preserving positive
form cannot satisfy the same relation for a nonzero degree-raising `Q`.

Accordingly, the induced BRST pairing naturally pairs `H^r` with
`H^(nu-r)`. A same-ghost-number physical Gram matrix requires the physical
degree to be the middle degree, or an explicit ghost-vacuum/insertion
convention that shifts `nu` so the physical cohomology is centered at zero.
For an exterior algebra of fifteen uncentered CE ghosts, the top-form pairing
would have `nu=15`, not zero. This centering datum is absent from the current
prototype and must not be silently assumed.

In the complex conformal basis this also requires an explicit star structure.
In particular, lowering and raising conformal generators, and their ghosts,
must be exchanged by the adjoint. The algebra-only complex currently does not
construct this operation. Its geometric cylinder generator is `T`, while the
Hermitian compact-energy generator is `D=iT`; consequently even the time
generator carries a nontrivial factor of `i` when one passes from the vector-
field Lie algebra to quantum charge operators. One must fix this operator
basis before assigning ghost adjoints or factors of `i` in the quantum BRST
charge.

## Why exact states are null against closed states

Let

\[
Z=\ker Q,
\qquad B=\operatorname{im}Q.
\]

For `b=Qa` and `z` closed,

\[
(b,z)_G=(Qa,z)_G=(a,Q^\sharp z)_G=0.
\]

Thus

\[
B\subseteq Z^\perp.
\]

In finite dimension, nondegeneracy of `G` gives

\[
(\ker Q)^\perp=\operatorname{im}Q^\sharp.
\]

If `Q^sharp=+/-Q`, then

\[
Z^\perp=B.
\]

Nilpotency gives `B subset Z`, so the radical of the closed-state Gram matrix
is exactly

\[
\boxed{\operatorname{rad}(G|_Z)=B.}
\]

Consequently the form induced on

\[
H(Q)=Z/B
\]

is well-defined and nondegenerate. Notice that an exact state is null against
every closed state; it need not be orthogonal to arbitrary nonclosed states.
That cross pairing is what keeps the full oscillator-plus-ghost form
nondegenerate.

## Degreewise formulation

At one ghost number, suppose the complex is

\[
C^{n-1}\xrightarrow{d_{n-1}}C^n\xrightarrow{d_n}C^{n+1}.
\]

If only a same-degree Gram matrix `G_n` is available, the necessary and
sufficient descent condition is the direct matrix identity

\[
\boxed{
(\operatorname{im}d_{n-1})^\dagger G_n(\ker d_n)=0.}
\]

Equivalently, every incoming exact state is orthogonal to every outgoing
closed state. This condition should be checked directly unless it has been
derived from a complete ghost-number-reflecting form and `Q^sharp=+/-Q`.

The quotient can still have a radical larger than the exact subspace. The
induced form is nondegenerate precisely when

\[
\operatorname{rad}(G_n|_{\ker d_n})=\operatorname{im}d_{n-1}.
\]

## Exact quotient algorithm

For exact matrices `d_prev`, `d_next`, and `G_n`:

1. Verify `d_next d_prev=0` and `G_n^dagger=G_n`.
2. Form exact column bases
   \[
   Z=\ker d_{\rm next},\qquad B=\operatorname{im}d_{\rm prev}.
   \]
3. Verify the descent matrix `B^dagger G_n Z` is exactly zero.
4. Compute the restricted Gram matrix
   \[
   K=Z^\dagger G_nZ.
   \]
5. Express `B=Z C_B` and compute `R=ker K`. Check whether
   `span(C_B)=span(R)`. Failure means that the quotient pairing is still
   degenerate.
6. Extend the columns of `C_B` to a basis `[C_B,H]` of the closed-coordinate
   space. Representatives for cohomology are `Z H`.
7. Compute
   \[
   G_H=(ZH)^\dagger G_n(ZH).
   \]
   Shifting `ZH -> ZH+B X` leaves this matrix unchanged.
8. Determine its inertia by exact Hermitian congruence with one-by-one and
   two-by-two pivots. Do not infer the signature from floating-point
   eigenvalues near a null direction.

The executable
`symbolic/verify_conformal_brst_pairing_descent.py` implements this algorithm
and includes three fixtures:

- a ghost-number-reflected BRST quartet plus one positive- and one
  negative-norm physical state, whose quotient signature is exactly `(1,1)`;
- a complex for which exacts are orthogonal to closed states but do not exhaust
  the restricted radical, leaving one exactly zero quotient direction; and
- a nilpotent differential with the identity Gram matrix, for which exacts are
  not null against closed states and the form therefore does not descend.

## Audit of the current global-BRST prototype

`symbolic/verify_conformal_global_brst.py` is correct within its stated
algebra-only scope: it checks the `so(4,2)` structure constants, the CE
differential, the formal adjoint module, and the classical minimal BFV
polynomial. Its fail-closed statements are important.

It must not yet be used for a physical pairing claim, for four separate
reasons:

1. It gives no representation of the fifteen generators on the complete
   oscillator, auxiliary, local-ghost, and contractible state space.
2. It gives no ghost Hermitian form or star operation. In the complex basis,
   `K+` and `K-` and their ghosts must be paired by the adjoint. Therefore the
   prototype cannot test `Q^sharp=Q`.
3. A CE complex for a global symmetry and a BFV complex for first-class gauge
   constraints are not automatically the same physical construction. The
   fifteen Taub moment maps must first be shown to be the relevant first-class
   constraints, including any background-energy shift, reducibility, central
   term, and finite-cutoff boundary issue.
4. The oscillator form cannot simply be restricted to invariant states. The
   ghost pairing and the BRST quartet structure are what make exact states the
   radical of the closed-state form.

There is also a classical/quantum distinction. The displayed minimal BFV
polynomial is a correct formal classical expression, but its quantum operator
ordering and Hermiticity depend on the ghost anticommutators, the real form,
and possible trace/normal-ordering terms. For `so(4,2)` the adjoint trace
vanishes algebraically, but a physical oscillator realization can still carry
an intercept, anomaly, or cutoff boundary term. Nilpotency of the abstract CE
complex does not test those effects.

The phrase `formal constraints` in the current executable is therefore
appropriate. The next representation-level certificate should add, in this
order:

1. exact oscillator-plus-ghost matrices `Q` and `G_total`;
2. `Q^2=0` and `Q^dagger G_total=G_total Q`;
3. the exact `Z`, `B`, restricted radical, and quotient Gram matrix;
4. the exact quotient signature on the complete compact-energy block.

## Reproduction

```bash
python3 symbolic/verify_conformal_brst_pairing_descent.py
```
