# C2f-N: action-normalized cylinder oscillator pairing

## Result

The free pairing needed to convert the C2a Taub kernels into Hamiltonian
vector fields is now fixed in the **same coefficient coordinates used by the
curvature scripts**.

Those scripts insert the positive-frequency cylinder waves with the
Hamada--Horata oscillator coefficients

\[
N_E(J)={1\over4\sqrt{J(2J+1)}},\qquad
N_A(J)={1\over2\sqrt{(2J-1)(2J+1)(2J+3)}},
\]

\[
N_L(J)={1\over4\sqrt{(J+1)(2J+1)}}.
\]

For unit-normalized `S^3` harmonics, direct evaluation of the quadratic
Ostrogradsky/covariant symplectic form gives, in the conventional
Hamada--Horata Weyl-action normalization,

\[
\langle E,E\rangle_\Omega=+1,\qquad
\langle A,A\rangle_\Omega=-1,\qquad
\langle L,L\rangle_\Omega=-1.
\]

The magnitudes are exactly one, not merely conventional signs.  The result
reproduces their canonical commutators (3.28)--(3.30) from the reduced
quadratic action rather than assuming them.

## Exact 36-mode matrix

Use the C2b/C2c ordering

\[
z=(E_+,E_-,A_+,A_-,L_+,L_-),
\]

whose irrep dimensions are

\[
(5,5,8,8,5,5).
\]

Write the real covariant symplectic form as

\[
\Omega=i\,d\bar z\wedge G_\Omega\,dz,
\]

and define the Hermitian mode pairing by

\[
(u,v)_\Omega=-i\Omega(\bar u,v).
\]

For

\[
S_{\rm HH}=-\int C^2,
\]

the exact matrix is

\[
G_\Omega^{\rm HH}
=\operatorname{diag}
\left(I_5,I_5,-I_8,-I_8,-I_5,-I_5\right).
\]

There are no hidden mode-dependent phases: all entries are real, and the
symplectic phase is the displayed overall factor `i`.

## The C2a action convention

C2a deliberately uses the action-normalized density

\[
S_{\rm red}=\int\sqrt{-g}
\left(R_{\mu\nu}R^{\mu\nu}-{1\over3}R^2\right).
\]

In four dimensions,

\[
R_{\mu\nu}R^{\mu\nu}-{1\over3}R^2
={1\over2}(C^2-E_4).
\]

The Euler term changes the covariant symplectic current by a spatial exact
form, whose integral over the closed `S^3` slice vanishes.  Consequently,

\[
\Omega_{\rm red}=-{1\over2}\Omega_{\rm HH}.
\]

Keeping the **unchanged external-wave coordinates used in C2a**, one has

\[
\boxed{
G_\Omega^{\rm red}
=-{1\over2}G_\Omega^{\rm HH}
=\operatorname{diag}
\left(-{1\over2}I_5,-{1\over2}I_5,
+{1\over2}I_8,+{1\over2}I_8,
+{1\over2}I_5,+{1\over2}I_5\right).}
\]

The corresponding coefficient-space Poisson/commutator matrix is its
inverse,

\[
\boxed{
J_{\rm comm}^{\rm red}
=(G_\Omega^{\rm red})^{-1}
=-2G_\Omega^{\rm HH}
=\operatorname{diag}
\left(-2I_5,-2I_5,+2I_8,+2I_8,+2I_5,+2I_5\right).}
\]

Thus a statement such as `J=diag(+,-,-)` silently uses the conventional
`-C^2` action and canonically rescaled oscillator coordinates.  It is not the
literal matrix in the action and wave normalization of the C2a kernels.

For the physical convention

\[
S_W=-\alpha_g\int C^2,\qquad \alpha_g>0,
\]

the general formulas are instead

\[
G_\Omega=\alpha_gG_\Omega^{\rm HH},\qquad
J_{\rm comm}=\alpha_g^{-1}G_\Omega^{\rm HH}.
\]

The overall action scaling cancels between a Taub kernel and the inverse
symplectic form when both are derived from the same action.

## Primary-source conformal-charge cross-check

The pairing normalization is independently checked against the explicit
proper-conformal oscillator charge of Hamada--Horata.  Their Eqs. (4.42),
(4.60), and (4.62)--(4.63) give

\[
\gamma(J)=1,
\]

\[
A(J)=\sqrt2\sqrt{2J\over(2J-1)(2J+3)},\qquad
B(J)=\sqrt2\sqrt{2J+2\over(2J-1)(2J+3)}.
\]

For the exact magnetic representatives used by the C2a seeds, the relevant
normalized `H` coefficient contributes another `sqrt(2)`.  At `J=1` the
published canonical **charge kernel** therefore has seed magnitudes

\[
|Q_M:A_1\to E_1|={2\sqrt{10}\over5},
\qquad
|Q_M:L_1\to A_1|={4\sqrt5\over5}.
\]

The repo harmonic convention differs by the tower phases

\[
p_E=-1,\qquad p_A=p_L=+1,
\]

and the combined action, harmonic, component, and polarization conventions
give the common raw-kernel factor

\[
s_{\rm CK}={1\over2\sqrt2\pi}.
\]

These data reproduce both independent curvature coefficients:

\[
p_Ep_A s_{\rm CK}{2\sqrt{10}\over5}
=-\frac{\sqrt5}{5\pi},
\]

\[
p_Ap_L s_{\rm CK}{4\sqrt5\over5}
=\frac{\sqrt{10}}{5\pi}.
\]

This is not a one-coefficient fit: one common raw-kernel normalization and
the independently fixed tower phases match both adjacent branch families.

The complex phase is also fixed.  For the seeded component

\[
q=(\tfrac12,-\tfrac12),
\]

the Hamada--Horata label is `M=-q`, and scalar-harmonic reality gives
`Y_M^*=-Y_q` because `epsilon_M=(-1)^(m-m')=-1`.  Their Eq. (4.8)
normalizes the lowering conformal Killing field as

\[
(\xi^0,\xi^i)_{\rm HH}
=\left({\sqrt{\operatorname{Vol}(S^3)}\over2},
-i{\sqrt{\operatorname{Vol}(S^3)}\over2}\nabla^i\right)
e^{it}Y^*,
\]

where `Vol(S^3)=2 pi^2`.  The repo's `s=-1` reducibility
`r_-=(-i,1,1)` is written with lower `xi_0`; after raising the time index,

\[
(\xi^0,\xi^i)_{\rm repo}
=(i,\nabla^i)e^{it}Y.
\]

Consequently, with both vectors expressed against `Y_q`,

\[
\boxed{
\xi_{\rm repo}=-{i\sqrt2\over\pi}\xi_{{\rm HH},-q}.}
\]

The spherical conjugation phase changes with `q`; for `q=(1/2,1/2)`, for
example, `epsilon=+1`.  Since `S_red=-S_HH/2` modulo Euler, the Noether
charges for the same geometrical parameter obey

\[
Q_{\rm red}(\xi_{\rm repo})
=\frac{i}{\sqrt2\pi}Q_{\rm HH}(\xi_{{\rm HH},-q}).
\]

Thus the raw real C2a Taub matrix is not directly the complex
Hamada--Horata Noether/stress-tensor kernel; the comparison must cross both
the polarization and symplectic maps.

C2a defines the mixed polarization `Q[h_1,h_2]`.  For a real mode

\[
h=z u+\bar z\bar u,
\]

the quadratic moment map contains the two orderings and hence has kernel

\[
2M_{\rm Taub}.
\]

Using the exact inverse pairing above and the repo convention
`d mu=i_X Omega`,

\[
X_z=i(G_\Omega^{\rm red})^{-1}(2M_{\rm Taub})z.
\]

The Hamada--Horata numbers above are kernels `M_HH`, not generator entries.
For annihilator coordinates,

\[
T_{\rm HH}=J_{\rm HH}M_{\rm HH}.
\]

Their `A -> E` generator entry is `+2 sqrt(10)/5`, while `L -> A` is
`-4 sqrt(5)/5`, because the target `A` oscillator has negative signature.
With the repo tower rephasing `S=diag(-E,+A,+L)`,

\[
T_{\rm repo}=-{i\sqrt2\over\pi}S T_{\rm HH}S^{-1}.
\]

Both independent curvature seeds reproduce this exactly:

\[
(T_{\rm repo})_{A\to E}={4i\sqrt5\over5\pi},
\qquad
(T_{\rm repo})_{L\to A}={4i\sqrt{10}\over5\pi}.
\]

The factor two is the bilinear-polarization factor, the target sign belongs
to `J_HH`, and the complex phase is fixed by the CK component and the
Hamiltonian `i`; none is a free normalization choice.

## Derivation

For a unit-normalized TT harmonic, the conventional quadratic action is the
PU oscillator

\[
L_{\rm TT}={\gamma\over2}
\left[\ddot q^2-(\omega_E^2+\omega_L^2)\dot q^2
+\omega_E^2\omega_L^2q^2\right],
\]

with

\[
\gamma=-1,\qquad \omega_E=2J,\qquad \omega_L=2J+2.
\]

Its Ostrogradsky symplectic pairing on a mode
`q=N exp(-i omega t)` is

\[
-i\Omega(\bar q,q)
=2\gamma\omega
\left(2\omega^2-\omega_E^2-\omega_L^2\right)|N|^2.
\]

Substituting `N_E` and `N_L` gives `+1` and `-1` exactly.

For a transverse vector harmonic the quadratic action reduces to

\[
L_A={\mu_A\over2}(\dot q^2-\omega_A^2q^2),
\]

where

\[
\omega_A=2J+1,\qquad
\mu_A=-2(2J-1)(2J+3).
\]

Therefore

\[
-i\Omega(\bar q,q)=2\mu_A\omega_A|N_A|^2=-1.
\]

At the low level used by C2a (`J=1`) the wave coefficients are

\[
N_E={1\over4\sqrt3},\qquad
N_A={1\over2\sqrt{15}},\qquad
N_L={1\over4\sqrt6},
\]

exactly those inserted by the existing cylinder curvature scripts.

## What this closes, and what it does not

This closes the previously missing **free oscillator normalization**.  In
particular, a C2a quadratic kernel `M_X` can now be contracted with the exact
inverse symplectic matrix rather than a signs-only surrogate.  On both
directly evaluated C2a seed families, the mixed-polarization factor and the
full complex generator normalization are also fixed by the independent
Hamada--Horata charge.

The all-block covariant theorem is still logically separate:

\[
d\mu_X=\iota_{X^\#}\Omega,
\qquad
\mu_X=\bar zM_Xz.
\]

For the two seeded blocks the answer is now exactly `2 M_Taub`, with the
orientation shown above.  Extending that statement to every unseeded block
still requires either the covariant phase-space identity or direct canonical
charge reconstruction.  The known seeded generator block is

\[
X^\#_z=i(G_\Omega^{\rm red})^{-1}(2M_X)z.
\]

The pairing certificate does **not** supply:

- the unseeded proper-conformal Taub blocks;
- the seven Killing-charge kernels;
- the full fifteen-component moment map;
- the local-plus-global BRST cohomology; or
- the reduced energy-six physical pairing.

The first three items are supplied subsequently, through source energy four,
by `verify_conformal_generator_ansatz.py` and
`verify_conformal_moment_map_energy4.py`.  They use the canonical charge
reconstruction and retain an explicit buffer-boundary guard.  The all-level
global-BRST and energy-six physical-pairing items remain open.

## Reproduction

```bash
python3 symbolic/verify_conformal_oscillator_pairing.py
```

The executable derives the TT and vector norms, constructs both exact
36-by-36 matrices, verifies that they are inverse in the stated sense, and
checks the general `-alpha_g C^2` convention.

Reference for the cylinder quadratic action, mode coefficients and canonical
commutators: Hamada--Horata,
[arXiv:hep-th/0307008](https://arxiv.org/abs/hep-th/0307008),
Eqs. (3.5), (3.26)--(3.30).
