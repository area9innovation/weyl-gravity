# C2d: finite geometry of the seeded conformal Taub zero locus

## Scope

`symbolic/verify_conformal_taub_cone.py` studies only the four reconstructed
proper-conformal quadratic functions supplied by C2b.  The coordinate space
is the 36-complex-dimensional sum

\[
E_+\oplus E_-\oplus A_+\oplus A_-\oplus L_+\oplus L_-.
\]

For each `q=(q_L,q_R)\in(\tfrac12,\tfrac12)`, C2b gives an exact lowering
kernel `M_q`, and C2d defines

\[
\mu_q(z,\bar z)=\bar z^T M_q z.
\]

Each reconstructed polynomial contains sixteen exact Clebsch--Gordan
monomials.  Their general form is

\[
\mu_q=
\sum_{\mathcal F}
\mathcal R_{\mathcal F}
C^{j'_{L}m'_{L}}_{j_Lm_L,\frac12q_L}
C^{j'_{R}m'_{R}}_{j_Rm_R,\frac12q_R}
\bar z_{\mathcal F',m'_L,m'_R}
z_{\mathcal F,m_L,m_R},
\]

where the sum contains only the four curvature-seeded families

\[
A_+\to E_+,\qquad A_-\to E_-,\qquad
L_+\to A_+,\qquad L_-\to A_-.
\]

This is not the full Taub constraint map.  Nor has the symplectic identity

\[
d\mu_X=\iota_{X^\#}\Omega
\]

been proved for these oscillator-coordinate kernels, so this note does not
yet promote them to components of a Hamiltonian moment map.  The seven
Killing functions, other proper-conformal blocks, diagonal/self-charge terms,
other oscillator towers, and global ghosts are absent.

## Four-mode cancellation

On the selected coordinates

\[
(e_+,a_+,a_-,\ell_-),
\]

only the component `q=(\tfrac12,-\tfrac12)` survives:

\[
\mu_{\frac12,-\frac12}
=-\frac{\sqrt5}{5\pi}\bar e_+a_+
+\frac{\sqrt{10}}{5\pi}\bar a_-\ell_-,
\]

while the other three reconstructed components vanish identically on this
coordinate slice.  Therefore

\[
e_+=a_+=a_-=1,
\qquad
\ell_-=\frac1{\sqrt2}
\]

is an exact zero.  It is not a common operator kernel: at least one
`M_qz` is nonzero.  The zero is a genuine cancellation between distinct
mixed blocks.

## Jacobian ranks and regularity

Because `\mu_q` depends on both `z` and `\bar z`, two ranks are recorded.

1. Treating `z` and `\bar z` as independent Wirtinger coordinates, the
   four-by-72 complex Jacobian has

   \[
   \boxed{\operatorname{rank}_{\mathbb C}D_{(z,\bar z)}\mu=4}.
   \]

2. On the ordinary oscillator coefficient slice
   `\bar z=\operatorname{conj}(z)`, write `z=x+iy` and separate the real and
   imaginary parts of all four functions.  The eight-by-72 real Jacobian has

   \[
   \boxed{\operatorname{rank}_{\mathbb R}D(\Re\mu,\Im\mu)=8}.
   \]

Both are maximal.  Hence the cancelling point is regular relative to this
**seeded** four-complex-component Taub-constraint map.  Its real zero locus
on that coefficient slice has tangent dimension

\[
72-8=64.
\]

On the four-complex-coordinate slice, the effective single complex equation
has Wirtinger rank one and real rank two.  It is therefore also a smooth
real-codimension-two hypersurface there.  If one retains the three target
components that vanish identically after restriction, the displayed
eight-row restricted Jacobian naturally has rank two; that is a property of
the coordinate restriction, not a singularity of the effective equation.

This coefficient real slice has not yet been identified with the physical
`J_conf` real structure after global BRST reduction.  None of these
statements determines whether the same point is regular or singular for the
missing fifteen-component constraint map.  New constraints can change both
the zero locus and its differential rank.

## Available orbit tangents

C2b supplies independent action matrices for compact energy `D` and the six
`SO(4)` rotations.  Their oscillator-space infinitesimal action is

\[
\delta z=-iGz.
\]

At the cancelling point, the seven real tangent vectors are independent:

\[
\boxed{\operatorname{rank}_{\mathbb R}T_{D\times SO(4)}=7}.
\]

The corresponding combined `(z,\bar z)` columns also have complex rank seven.
Every one is annihilated by the appropriate partial Jacobian, as required by
the exact energy and rotation covariance of `\mu_q`.  Thus the known compact
orbit is contained in the seeded zero-locus tangent.  Formally subtracting only
this available orbit gives

\[
64-7=57
\]

remaining real tangent directions.  This is only a tangent-space vector
quotient count, not the dimension of a quotient manifold or physical phase
space; missing constraints and missing orbit directions can change it.

Only `D`, `J_L^z`, and `J_R^z` remain tangent to the chosen four-mode
coordinate slice, where their rank is three.  The other rotations leave the
slice while remaining tangent to the full seeded zero locus.

The proper-conformal `M_q` in C2d are charge kernels, not Hamiltonian action
matrices.  C2d deliberately does not substitute `M_qz` for the then-missing
symplectic construction.  C2f-N/M subsequently supply that conversion
through source energy four.  They also show that this four-mode vector,
although still neutral under every proper-CK lowering component, has
`mu_D=-6` and `mu_Rz=-3`; it is therefore not on the full conformal zero
locus.  The C2d rank numbers remain valid only for the seeded map.

## Fail-closed conclusion

The exact conclusion is limited:

> The C2b four-mode cancellation is a regular point of the reconstructed
> proper-conformal Taub-constraint zero locus on the ordinary coefficient
> real slice.  The seven independently available compact symmetry tangents
> lie in its tangent space.  The complete constraint locus, its Hamiltonian
> moment-map interpretation, and its globally reduced geometry remain
> unknown.

The later C2f result narrows this historical conclusion: the Hamiltonian
moment-map jet is now explicit through source energy four and excludes the
test vector from the full zero locus.  The infinite energy-graded locus and
its global-BRST quotient remain unknown.

The executable exposes three guards, all of which fail:

```bash
python3 symbolic/verify_conformal_taub_cone.py --require-full-cone
python3 symbolic/verify_conformal_taub_cone.py --require-full-orbit
python3 symbolic/verify_conformal_taub_cone.py --require-global-brst
```
