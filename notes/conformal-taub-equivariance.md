# C2c-E: partial tensor/coadjoint covariance of the reconstructed Taub kernels

## Result and exact scope

The executable certificate is
`symbolic/verify_conformal_taub_equivariance.py`.  It takes the two
action-normalized curvature seeds and their C2b Wigner--Eckart completion and
proves that the resulting low-mode quadratic Taub kernels transform
equivariantly under

\[
 SU(2)_L\times SU(2)_R\times\mathbb R_D.
\]

Here `D` is compact cylinder energy.  This is a **partial tensor/coadjoint
covariance theorem**, not a representation of the full `SO(4,2)` algebra.
At the C2c-E stage the proper-conformal seed kernels were known, while the
seven Killing kernels, the remaining oscillator towers, and the normalized
symplectic/global-generator map were not.  C2f-N/A/M subsequently close
those items through source energy four; global BRST cohomology remains open.

## Kernels are not generators

Let the 36 low oscillator coordinates be collected into

\[
 z\in E_+\oplus E_-\oplus A_+\oplus A_-
       \oplus L_+\oplus L_-.
\]

The reconstructed matrices `M_q` define quadratic functions

\[
 \mu_q(z,\bar z)=\bar z M_qz.
\]

They are action-normalized bilinear **kernels**.  They must not be identified
with the matrices that generate proper conformal transformations of `z`.
To promote a quadratic Taub-charge component to a moment map and obtain its
Hamiltonian vector field, one must prove the symplectic identity

\[
d\mu_X=\iota_{X^\#}\Omega.
\]

That requires the correctly normalized oscillator symplectic or Krein
structure.  Schematically the resulting map would look like

\[
 T_q\sim\Omega^{-1}M_q,
\]

with the appropriate real structure and index placement.  No such normalized
`Omega` is used inside this historical C2c certificate.  C2f-N later derives
it and C2f-M performs the conversion.  Thus, within C2c-E alone, neither the ordinary matrix
commutator of two `M` kernels nor their ordinary dagger relation is a test of
the proper-conformal generator algebra.

By contrast, the compact oscillator generators

\[
 D,\qquad J^a_L,\qquad J^a_R
\]

are independently fixed on the low oscillator sum by the mode energies and
their `SU(2)_L x SU(2)_R` representations.  C2c-E uses these known generators
to test how the kernels transform.

## Exact partial coadjoint identity

Let

\[
 M^-_{q_Lq_R},
 \qquad q_L,q_R\in\left\{\frac12,-\frac12\right\},
\]

be the four reconstructed energy-lowering kernels.  For the algebraic
Condon--Shortley completion used here, define the raising tensor by

\[
 M^+_{q_Lq_R}
 =(-1)^{1-q_L-q_R}
 \left(M^-_{-q_L,-q_R}\right)^\dagger.
\]

The phase is essential: a component-reversed dagger without the spherical
tensor phase does not transform in the same `(1/2,1/2)` basis.  This
constructed family has not been independently evaluated for every cylinder
conformal-Killing mode and is not yet a physical-adjoint statement.

The exact matrix identities are

\[
 [D,M^s_q]=sM^s_q,
 \qquad s=\pm1,
\]

\[
 [J^a_L,M^s_{q_Lq_R}]
 =\sum_{q'_L}
 \left(t^a_{1/2}\right)_{q'_Lq_L}
 M^s_{q'_Lq_R},
\]

\[
 [J^a_R,M^s_{q_Lq_R}]
 =\sum_{q'_R}
 \left(t^a_{1/2}\right)_{q'_Rq_R}
 M^s_{q_Lq'_R},
\]

for all `a=x,y,z`, both energy signs, and every magnetic component.

For an infinitesimal compact symmetry represented on oscillator coordinates
by

\[
 \delta_Xz=-iJ_Xz,
 \qquad
 \delta_X\bar z=+i\bar zJ_X,
\]

one has

\[
 \delta_X\mu_M
 =i\bar z[J_X,M]z.
\]

The preceding matrix identities therefore give

\[
 \boxed{
 \delta_X\mu^s_q
 =i\sum_{q'}(t_X)_{q'q}\mu^s_{q'} }
\]

and

\[
 \boxed{\delta_D\mu^s_q=is\mu^s_q.}
\]

This is the precise partial coadjoint-equivariance statement established by
the certificate.  It is stronger than checking a few seed entries: all four
magnetic components, their raising partners, both compact `SU(2)` factors,
and all three real axes are checked as exact 36-by-36 matrix identities.

## Canonical exact quadratic polynomials

For a transition from an irrep `S=(j_L,j_R)` to
`T=(j'_L,j'_R)`, define the Condon--Shortley polynomial

\[
\begin{aligned}
 {\cal C}_q[T\leftarrow S]
 ={}&\sum_{m_L,m_R,m'_L,m'_R}
 C^{j'_Lm'_L}_{j_Lm_L,\frac12q_L}
 C^{j'_Rm'_R}_{j_Rm_R,\frac12q_R}\\
 &\hspace{22mm}\times
 \bar z_{T,m'_L,m'_R}z_{S,m_L,m_R}.
\end{aligned}
\]

Then every known lowering polynomial is given canonically by

\[
\boxed{
\begin{aligned}
 \mu^-_q={}&-{\sqrt{10}\over5\pi}
 \left(
 {\cal C}_q[E_+\leftarrow A_+]
 +{\cal C}_q[E_-\leftarrow A_-]
 \right)\\
 &+{\sqrt2\over2\pi}
 \left(
 {\cal C}_q[A_+\leftarrow L_+]
 +{\cal C}_q[A_-\leftarrow L_-]
 \right).
\end{aligned}}
\]

Each of the four polynomials has exactly 16 nonzero monomials.  The script's
`--show-polynomials` mode prints all 64 terms with canonical magnetic labels
and exact radicals.  The original curvature component appears inside
`q=(1/2,-1/2)` as

\[
 \mu^-_{\frac12,-\frac12}\supset
 -{\sqrt5\over5\pi}\,
 \bar e_{+;(2,0)}a_{+;(\frac32,\frac12)}
 +{\sqrt{10}\over5\pi}\,
 \bar a_{-;(\frac12,\frac32)}\ell_{-;(0,2)}.
\]

The remaining terms are its exact left/right ladder and parity completion.
The variables `z` and `zb` are treated as independent polynomial variables;
imposing a physical real slice awaits the global adjoint and pairing.

## Why this is not full `SO(4,2)` equivariance

Full equivariance would additionally require the proper-conformal bracket

\[
 [K_A^+,K_B^-]=2R_{AB}+2i\delta_{AB}D
\]

at the level of the actual Hamiltonian vector-field generators or,
equivalently, the corresponding Poisson brackets of all fifteen moment-map
components.  That test cannot be formed from the present data because:

1. `M_q` has not been converted to a Hamiltonian generator using the
   symplectic/Poisson structure and its real-form normalization;
2. the time-translation and six rotation Taub kernels are absent;
3. diagonal, self-charge, anomalous, and higher-tower blocks are absent;
4. the local-plus-global BRST reduction is absent.

Computing an ordinary commutator of the truncated action kernels would not
repair these omissions and is deliberately not reported as a conformal
algebra test.

## Reproduction and fail-closed rails

Run

```bash
python3 symbolic/verify_conformal_taub_equivariance.py
python3 symbolic/verify_conformal_taub_equivariance.py --show-polynomials
```

Each missing completion has an explicit nonzero guard:

```bash
python3 symbolic/verify_conformal_taub_equivariance.py --require-full-so42
python3 symbolic/verify_conformal_taub_equivariance.py --require-all-towers
python3 symbolic/verify_conformal_taub_equivariance.py --require-seven-killing
python3 symbolic/verify_conformal_taub_equivariance.py --require-global-brst
```

These guards must continue to fail until the corresponding data and
operator-level maps have been supplied.
