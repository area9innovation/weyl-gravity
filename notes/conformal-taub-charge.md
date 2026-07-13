# C2a: first exact conformal Taub-charge components

## Scope

`symbolic/verify_conformal_taub_charge.py` converts the exact Hessian-null
`t`-channel current data into the corresponding action-normalized conformal
Taub functional.  It closes the local operator normalization for the selected
proper-conformal components.  It does **not** yet construct the full global
BRST complex or the complete fifteen-component charge matrix.

The action convention is

\[
S_{\rm red}[g]=\int d^4x\sqrt{-g}
\left(R_{\mu\nu}R^{\mu\nu}-\frac13R^2\right),
\]

and its lower-metric Euler derivative is denoted by
`\mathcal E^{\mu\nu}`.  With the standard Bach convention this is
`B^{\mu\nu}`; keeping the action-normalized symbol avoids hiding an overall
sign convention.  The mixed quadratic coefficient is defined explicitly by

\[
\mathcal E(\bar g+a h_1+b h_2)
=ab\,\mathcal E^{(2)}[h_1,h_2]+O(a^2,b^2).
\]

For a conformal-Killing reducibility parameter `\xi_s` of signed cylinder
frequency `s=\pm1`, the charge is

\[
Q_s[h_1,h_2]
=\int_{S^3}\!\sqrt\gamma\,d^3x\,
n_\mu\xi_{s\nu}\mathcal E^{(2)\mu\nu}[h_1,h_2],
\qquad n_\mu=(-1,0,0,0).
\]

## Fifteen reducibility parameters

Under the cylinder `SO(4)` subgroup, the conformal Killing parameters split
as

| signed frequency | doubled `(2j_L,2j_R)` | multiplicity | meaning |
|---:|---:|---:|---|
| `0` | `(0,0)` | 1 | time translation |
| `0` | `(2,0)` | 3 | left rotations |
| `0` | `(0,2)` | 3 | right rotations |
| `+1` | `(1,1)` | 4 | proper conformal |
| `-1` | `(1,1)` | 4 | proper conformal |

The count is `1+3+3+4+4=15`.  C2a constructs the two proper-conformal
frequency sectors algebraically, but evaluates only the magnetic component
selected by the P4 chiral seed and its independently checked parity partner.

## Exact current-to-charge identity

In the scalar component basis `(h_{00},h_{0i},h_{ij}^{\rm tr})`, write

\[
r_s=(is,1,1)^T,
\qquad
G_s r_s=0,
\]

for the Diff `\times` Weyl reducibility.  Let `p_s` denote the transverse
quotient representative and `B_s` the reduced ordinary-gauge generator.  The
exact component identities are

\[
\partial_\omega(G_s r_s)
=2p_s+B_s(-2is,1)^T,
\]

and

\[
k_s\equiv2n_{(\mu}\xi_{s\nu)}
=-is\,\partial_\omega(G_s r_s).
\]

The third action variation against `k_s` is `2Q_s`.  Since the direct cubic
probes against both columns of `B_s` integrate to zero, while the slice probe
has coefficient `C_s`, one obtains the exact normalization

\[
\boxed{Q_s=-is\,C_s.}
\]

This is stronger than observing `\kappa_t=0`: it identifies the nonzero slice
current with the normal projection of the mixed quadratic Euler/Bach source,
up to a convention that is now fixed by the action itself.

## Exact low-energy components

For the forward raw chiral seeds, the charge densities reconstructed from the
independently evaluated slice and gauge probes are

\[
\mathcal D_{Q_-}(t)
=-\frac{\sqrt5\,t(11t^2+1)}
{240\pi^3(1+t^2)^2},
\]

\[
\mathcal D_{Q_+}(t)
=\frac{\sqrt{10}\,t(35t^2-11)}
{480\pi^3(1+t^2)^2}.
\]

With the stereographic measure

\[
\mathcal I_Q(t)=\frac{2}{1+t^2}\mathcal D_Q(t),
\qquad
Q=8\pi^2\int_0^\infty\mathcal I_Q(t)\,dt,
\]

the exact components are

\[
\boxed{Q_-=-\frac{\sqrt5}{5\pi}},
\qquad
\boxed{Q_+=\frac{\sqrt{10}}{5\pi}}.
\]

More explicitly, in the raw chiral routing used by P4 these are

\[
Q_-=Q_{\xi_-}[E_+^\dagger,A_+],
\qquad
Q_+=Q_{\xi_+}[L_-^\dagger,A_-].
\]

Thus the completed certificate identifies **mixed `EA` and `LA` bilinear
charges**, not a diagonal `Q[A_3,A_3]` component.  This is forced by the
actual `t`-channel routing.  Independent reverse curvature runs give the
ordinary coefficient-kernel dagger entries, and the parity runs reproduce a
second nonzero magnetic orbit rather than cancelling the first.

On the restricted ordered chiral basis

\[
(E_+,A_+,A_-,L_-),
\]

the filled entries are

\[
M_-^{\rm low}=
\frac1{5\pi}
\begin{pmatrix}
0&-\sqrt5&0&0\\
0&0&0&0\\
0&0&0&\sqrt{10}\\
0&0&0&0
\end{pmatrix},
\]

\[
M_+^{\rm low}=(M_-^{\rm low})^\dagger.
\]

This is not yet a physical-adjoint statement.  These kernels act on exact
**oscillator representatives**.  They are not yet
operators on the globally reduced physical Hilbert space.

The companion C2b certificate
`symbolic/verify_conformal_taub_multiplets.py` uses multiplicity-one
Wigner--Eckart reconstruction to generate all four proper-conformal magnetic
components in these two adjacent mixed blocks.  See
`notes/conformal-taub-multiplets.md`.  That reconstruction does not turn the
two seeds into self-charges or a full moment map.

## Interpretation and fail-closed boundary

The result proves that the Hessian-null `t` block is not an ordinary
propagator channel and that its nonzero current is precisely a selected
proper-conformal Taub component in the action normalization.  It does not yet
decide whether the external modes:

1. are excluded as nonintegrable isolated perturbations;
2. survive only in charge-neutral or dressed combinations;
3. require collective background coordinates; or
4. remain after a larger global BRST reduction.

The following remain mandatory before P4 can be interpreted physically:

1. extend the two reconstructed mixed proper-CK multiplets to the remaining
   mode towers and construct the seven Killing-charge kernels, diagonal
   blocks, and any real-field anomalous bilinears;
2. include local ghosts, reducibility ghosts and contractible sectors;
3. compute the global BRST cohomology and the reduced energy-six pairing;
4. decide the disposition of the `t` zero mode before forming any reduced
   inverse;
5. only then assemble the contact-plus-exchange effective Hamiltonian.

The script exposes `--require-full-15` and `--require-global-brst`; both fail
closed by design.
