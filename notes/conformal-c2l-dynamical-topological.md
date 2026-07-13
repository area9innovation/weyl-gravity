# C2l-P: dynamical/topological splitting of the residual sector

## Statement

Let

\[
e={W_+^2+W_-^2\over\sqrt2}\sim C^2,
\qquad
o={W_+^2-W_-^2\over\sqrt2}\sim C\widetilde C,
\]

with the orientation-dependent factor of $i$ restored in Lorentz signature.
C2g and C2j-D give

\[
H^4_{\rm residual}=\operatorname{span}\{e,o\},
\qquad G=I_2.
\]

The two directions have different Euler--Lagrange status.  Define

\[
{\cal E}:H^4_{\rm residual}
\longrightarrow
\{\text{local equation/gauge deformations}\}
\]

by varying the corresponding integrated local functional.  With conventional
normalizations,

\[
{\cal E}(e)=\lambda_B B_{\mu\nu},
\qquad
{\cal E}(o)=0,
\qquad \lambda_B\ne0.
\]

The first identity is the standard Weyl-square variation.  Under locality,
smoothness, Lorentz invariance, and the four-derivative bound,
Boulanger--Henneaux show that it supplies the unique nontrivial consistent
self-interaction of a single linear conformal graviton, modulo equivalences
and dynamically inert additions
([hep-th/0106065](https://arxiv.org/abs/hep-th/0106065)).

The second identity follows from Chern--Weil transgression.

## Exact Pontryagin transgression

For the matrix-valued connection one-form $\Gamma$ in a chosen local frame,

\[
R=d\Gamma+\Gamma\wedge\Gamma,
\]

and

\[
P_4=\operatorname{tr}(R\wedge R)
=dQ_3(\Gamma),
\]

where

\[
Q_3(\Gamma)=\operatorname{tr}\left(
\Gamma\wedge d\Gamma
+{2\over3}\Gamma\wedge\Gamma\wedge\Gamma
\right).
\]

The exact symbolic certificate proves this local identity in a graded-cyclic
trace algebra.  In particular, graded cyclicity kills the apparent
$\operatorname{tr}\Gamma^4$ term and combines the mixed terms correctly.
The Chern--Simons form is not globally frame-invariant and need not exist as
a single global three-form on an arbitrary bundle.

The variation is

\[
\delta P_4
=2\,d\operatorname{tr}(\delta\Gamma\wedge R),
\]

after the Bianchi identity $DR=0$.  Hence on
$M=[t_1,t_2]\times S^3$, after choosing its global frame trivialization,

\[
\int_M P_4
=\operatorname{CS}[\Gamma(t_2)]
-\operatorname{CS}[\Gamma(t_1)].
\]

The identity holds order by order around the cylinder.  In particular,

\[
\int_M C^{(1)}\widetilde C^{(1)}
=\operatorname{CS}^{(2)}(t_2)-\operatorname{CS}^{(2)}(t_1)
\]

up to the density normalization; equivalently, the Ricci pieces cancel from
the four-dimensional Pontryagin density.  Fixed-endpoint or compactly
supported variations therefore produce no bulk Euler--Lagrange derivative.
The certificate proves the general order-by-order consequence, not an
explicit harmonic formula for $\operatorname{CS}^{(2)}$.

## Exact sequence and quotient pairing

The residual map has the exact sequence

\[
0\longrightarrow\operatorname{span}\{o\}
\longrightarrow H^4_{\rm residual}
\mathop{\longrightarrow}^{\cal E}
\operatorname{span}\{B_{\mu\nu}\}
\longrightarrow0.
\]

Quotienting by variationally trivial local functionals gives

\[
H^4_{\rm dyn}
=H^4_{\rm residual}/\ker{\cal E}
\cong\operatorname{span}\{[C^2]\}.
\]

Because $(e,o)$ is an orthonormal basis of the residual $I_2$, the orthogonal
representative of the quotient gives

\[
\boxed{G_{\rm dyn}=I_1.}
\]

Thus the accurate positive statement is

\[
\boxed{I_2=I_1^{\rm dynamical}\oplus I_1^{\rm topological}.}
\]

It is a positive metric on two classical theory-space/vertex directions,
only one of which changes the local equations.  It is not a two-particle or
two-species Hilbert-space result.

## Canonical meaning of the theta direction

Adding

\[
S_\theta=S_0+\theta\int_M P_4
\]

shifts the canonical potential by

\[
\Theta_{\rm can}\mapsto
\Theta_{\rm can}+\theta\,\delta\operatorname{CS}.
\]

Therefore

\[
p\mapsto p+\theta{\delta\operatorname{CS}\over\delta q},
\qquad
\Omega=\delta\Theta_{\rm can}\mapsto\Omega.
\]

The certificate verifies the corresponding exact symplectic shear for a
general symmetric Hessian.  For real $\theta$ the local quantum
transformation

\[
\Psi_\theta[q]
=e^{i\theta\operatorname{CS}[q]}\Psi_0[q]
\]

is a scalar phase and hence is unitary for both the Dirac product and any
fixed Krein form with which it commutes.

This is only a **local/canonical** equivalence.  A gravitational theta term
can still affect nontrivial topology, boundaries, horizons, large frame or
gauge transformations, and contact terms.  For an explicit horizon and
boundary example see
[Fischler--Kundu, arXiv:1612.06010](https://arxiv.org/abs/1612.06010).

## Deformation--obstruction diagram

The literature-seeded parity-preserving type-B target has the same
one-dimensional support:

\[
\pi_B\mathfrak O_1(e)
={199\over30}[c_{\rm W}C^2],
\qquad
\pi_B\mathfrak O_1(o)=0.
\]

As C2k emphasizes, the coefficient becomes a BV theorem only after a direct
quantum-master-equation projection in the repository conventions.  The
structural rank-one alignment is nevertheless exact:

\[
\begin{array}{c|c|c}
\text{direction}&\text{classical status}&\text{type-B target}\\ \hline
e\sim C^2&\text{unique local dynamics}&\text{nonzero/running}\\
o\sim C\widetilde C&\text{topological theta direction}&\text{zero if parity is preserved}
\end{array}
\]

The dynamical direction is precisely the one exposed to the type-B
coefficient; the locally unobstructed direction is precisely the one that
does not generate local dynamics.

## Certificate boundary

Run

```bash
python3 symbolic/verify_conformal_dynamical_topological.py
```

It verifies:

1. $dQ_3=\operatorname{tr}(R\wedge R)$ in exact graded algebra;
2. the boundary-only variation after the Bianchi identity;
3. the order-two finite-cylinder endpoint identity;
4. the rank-one Euler--Lagrange map and positive quotient $I_1$;
5. alignment with the projected type-B row;
6. symplecticity of the theta momentum shift; and
7. local $J$-unitarity of the real theta phase.

It deliberately rejects global triviality, absence of all theta effects,
two independent local dynamics, a machine derivation of the nonlinear Bach
variation, and an explicit mode-expanded $\operatorname{CS}^{(2)}$ formula.
