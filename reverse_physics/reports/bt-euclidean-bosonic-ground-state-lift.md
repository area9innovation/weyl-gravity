# BT Euclidean bosonic ground-state lift

Certificate:
`REVERSE_PHYSICS_BT_EUCLIDEAN_BOSONIC_GROUND_STATE_LIFT_V1`

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`

## Result

The inverse determinant in the exact flat-potential BT law has a positive
auxiliary-field representation. It is not the same positive measure as the
supersymmetric hyperbolic sigma model used for vertex-reinforced jump
processes (VRJP), but it does put BT in direct contact with pinned Gaussian
free fields and killed random walks in a random conductance environment.

Let $K$ be the ground-shifted Schrödinger operator from the certified
flat-potential pushforward. Thus $K$ is symmetric, positive semidefinite,
has rank $N-1$, and has a strictly positive null vector $\Omega$. For a
root $o$, define

\[
 q_o={\Omega_o^2\over\|\Omega\|_2^2}
\]

and let $K^{(o)}$ denote the positive principal minor obtained by deleting
row and column $o$. The adjugate identity gives

\[
 \det K^{(o)}=q_o\det{}'K.
\]

The standard finite-dimensional Gaussian integral, used twice, now gives
the exact identity

\[
 \boxed{
 {1\over\det{}'K}
 =q_o\int_{\mathbb R^{2(N-1)}}
 \exp\!\left[-{1\over2}
   \left(\xi^T K^{(o)}\xi+\eta^T K^{(o)}\eta\right)\right]
 {d\xi\,d\eta\over(2\pi)^{N-1}} . }
\]

Everything in this formula is nonnegative. Therefore the exact normalized BT
flat-potential measure has a genuine positive joint lift by two real
commuting Gaussian fields. Averaging the displayed identity uniformly over
the root gives a convenient rooted lift. Once the Gaussian fields have been
integrated out, every root contributes the same
$1/(N\det{}'K)$. Consequently the root is uniform and independent of the
flat potential at that marginal level.

This is an exact finite-graph reformulation. It does not prove a Poincare
inequality, a Witten gap, or the interacting $H^{-1}$ bound.

## Ground-state transform and random walks

Suppose the original graph has edge weights $w_{xy}$. The null-vector
equation fixes the diagonal of $K$. Put

\[
 B=\operatorname{diag}(\Omega)K\operatorname{diag}(\Omega),
 \qquad c_{xy}=w_{xy}\Omega_x\Omega_y.
\]

Then $B$ is the weighted graph Laplacian with conductances $c_{xy}>0$.
Writing $z_x=\Omega_x\phi_x$, with $\phi_o=0$, yields

\[
 z^T Kz
 =\sum_{\{x,y\}}c_{xy}(\phi_x-\phi_y)^2.
\]

Thus the two auxiliary fields are precisely two independent pinned Gaussian
free fields in the conductance environment selected by the BT positive ground
state. Their covariances are killed-walk Green functions. This is the useful
new bridge: the determinant sector can be studied with positive
random-conductance and electrical-network tools, without rotating an
auxiliary contour.

The difficult part has not vanished. The conductances are themselves
correlated nonlinear functions of the BT field, and volume-uniform control of
their killed Green functions is not yet known.

## Exact four-cycle check

On the unweighted four-cycle take

\[
 \Omega=(1,2,1,1/2),\qquad \|\Omega\|_2^2={25\over4}.
\]

The root probabilities and principal minors are

\[
 q=\left({4\over25},{16\over25},{4\over25},{1\over25}\right),
 \qquad
 \det K^{(o)}=\left(5,20,5,{5\over4}\right).
\]

Their sum is $\det'K=125/4$, and root by root

\[
 {q_o\over\det K^{(o)}}={4\over125}={1\over\det'K}.
\]

The transformed cyclic conductances are

\[
 (2,2,1/2,1/2).
\]

The four spanning-tree products are $1/2,1/2,2,2$, whose sum is $5$.
This independently checks both the cofactor identity and the weighted
matrix-tree interpretation using exact rationals.

## Why the hyperbolic localization theorem does not transfer directly

The structural similarity to reinforced random walks is real, but the
probability laws are different. In the VRJP mixing density, the spanning-tree
polynomial $D(W,u)$ occurs as

\[
 \sqrt{D(W,u)},
\]

and the field energy is a nearest-neighbor hyperbolic-cosine energy. See
Sabot, Tarres, and Zeng, arXiv:1507.04660, Eq. `density_u`, and Sabot and
Tarres, arXiv:1111.3991, Theorem 2(i). The latter identifies the conditional
walk conductances as $W_{xy}e^{u_x+u_y}$.

The BT flat-potential density instead contains

\[
 {1\over\det{}'K(u)}
 \exp\!\left[-{\|u\|_2^2+N\ell_0(u)^2\over2\lambda^2}\right].
\]

Therefore the determinant exponents are $+1/2$ and $-1$, differing by
$3/2$, and the energies live on different variables and have different
forms. Root choice and scale gauge cannot repair either mismatch. Applying
the published supersymmetric normalization or localization theorem directly
would replace the BT measure by another measure.

In field-theory language, the distinction is statistics: the BT reciprocal
determinant is represented by two commuting real bosons, whereas the positive
square-root determinant in the hyperbolic model is part of a supersymmetric
determinant balance. This statement is only about the finite Euclidean
measure; it is not a Born, Krein, or Lorentzian interpretation.

Primary sources audited on 2026-08-15:

- <https://arxiv.org/abs/1507.04660>
- <https://arxiv.org/abs/1111.3991>

The certificate records SHA-256 hashes of the audited arXiv source archives.
They are literature comparators, not executable inputs to the exact proof.

## What is now worth trying

The next calculation should use the rooted lift, rather than importing the
hyperbolic theorem. After the ground-state transform, express the
connection-corrected Witten quadratic form through killed-walk Green
functions for $c_{xy}=w_{xy}\Omega_x\Omega_y$. There are two honest outcomes:

1. prove a volume-uniform annealed form bound in the lowest cyclic sector; or
2. construct a normalized low-Rayleigh sequence with nonzero lowest-mode
   overlap.

Only the first, followed by all dyadic shells, could yield the actual
interacting $H^{-1}$ estimate. The present result does not decide that
moment and is not a stopping certificate for the continuum-reconstruction
work item.
