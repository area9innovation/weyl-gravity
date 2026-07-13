# C2f-A: proper-conformal generator ansatz through source energy four

## Scope and convention

`symbolic/verify_conformal_generator_ansatz.py` constructs an actual
one-particle conformal-generator ansatz.  It does not commute the C2b Taub
kernels as though they were generators.

Through source energy four, representation theory permits seven
parity-reduced lowering blocks:

\[
\begin{array}{c|c}
\text{coefficient}&\text{block}\\ \hline
a&E_3\to E_2\\
b&A_3\to E_2\\
c&E_4\to E_3\\
d&A_4\to E_3\\
e&A_4\to A_3\\
f&L_4\to E_3\\
g&L_4\to A_3.
\end{array}
\]

Each block is the unique Condon--Shortley `(1/2,1/2)` tensor allowed by
`SU(2)_L\times SU(2)_R`; parity supplies the opposite chirality with the same
reduced coefficient.

The executable uses the cylinder convention

\[
[K^-_M,K^+_N]=2\delta_{MN}D+2R_{MN}.
\]

This is the convention used in Hamada's explicit cylinder construction,
[arXiv:0811.1647](https://arxiv.org/abs/0811.1647).  If the anti-Hermitian
time generator is `T=-iD`, the scalar term is `2i\delta_{MN}T`; reversing the
commutator order reverses the right-hand side.  Thus it is equivalent to the
alternative `[K^+,K^-]` notation after the declared convention change.

Hamada--Horata's earlier canonical construction already gives the all-level
traceless-mode oscillator charge and its six branch families; see
[arXiv:hep-th/0307008](https://arxiv.org/abs/hep-th/0307008), Eqs. (4.42),
(4.60), and (4.62)--(4.63).  C2f-A is an independent finite-matrix
reconstruction in the repository's representation conventions.  Its new
role is to audit the low-energy restriction and connect that known generator
to the independently computed Taub kernels; no priority claim is made for
the conformal oscillator algebra itself.

The commutator is imposed on energy-two and energy-three states.  This is the
largest complete domain at this cutoff: on an energy-four state, the
`K^-K^+` ordering passes through energy five and needs the missing
source-energy-five lowering blocks.

## Exact algebraic solution

Introduce independent raising coefficients

\[
(A,B,C,D,E,F,G)
\]

for the reverses of `(a,b,c,d,e,f,g)`.  Exact solution of all matrix entries
of the sixteen proper-conformal brackets gives

\[
b={\sqrt6\,a d\over2e},
\qquad
g=-{2ef\over3d},
\]

and

\[
\begin{aligned}
A&={96\over5a},&
B&=-{16\sqrt6\,e\over15ad},&
C&={35\over c},\\
D&=-{2\over d},&
E&={18\over e},&
F&=-{1\over f},&
G&=-{6d\over ef}.
\end{aligned}
\]

Thus five lowering quantities `(a,c,d,e,f)` remain free.  They are exactly
the five independent relative rescalings of the six one-particle irreps at
energies two through four; one common scale is irrelevant.

The basis-invariant lowering--raising products are

\[
\boxed{
(aA,bB,cC,dD,eE,fF,gG)
=\left({96\over5},-{16\over5},35,-2,18,-1,4\right).}
\]

The same exact matrices verify:

- `[D,K^-]=-K^-` and `[D,K^+]=K^+`;
- the complete `(1/2,1/2)` tensor action under both compact `SU(2)` factors;
- the proper-conformal bracket on energies two and three for both chiralities;
- `[K^-_M,K^-_N]=0` through source energy four.

## General diagonal form

Let the nondegenerate diagonal form on an irrep `X` be `\eta_X`, and impose

\[
K^+=J^{-1}(K^-)^\dagger J.
\]

For a block `S\to T`, its raising coefficient is

\[
k^+_{T\to S}=k^-_{S\to T}{\eta_T\over\eta_S}.
\]

The invariant products therefore give the seven exact Gram equations

\[
\begin{aligned}
a^2{\eta_{E2}\over\eta_{E3}}&={96\over5},&
b^2{\eta_{E2}\over\eta_{A3}}&=-{16\over5},\\
c^2{\eta_{E3}\over\eta_{E4}}&=35,&
d^2{\eta_{E3}\over\eta_{A4}}&=-2,\\
e^2{\eta_{A3}\over\eta_{A4}}&=18,&
f^2{\eta_{E3}\over\eta_{L4}}&=-1,\\
g^2{\eta_{A3}\over\eta_{L4}}&=4.&&
\end{aligned}
\]

For real nonzero coefficients their signs force, up to one overall reversal,

\[
\eta_E>0,
\qquad
\eta_A<0,
\qquad
\eta_L<0.
\]

The algebra fixes this signature pattern and the invariant products, not the
five arbitrary basis magnitudes.

## Canonical oscillator normalization

With

\[
\eta_E=+1,
\qquad
\eta_A=\eta_L=-1,
\]

one consistent phase choice is

\[
\boxed{
(a,b,c,d,e,f,g)
=\left(
4\sqrt{\frac65},
\frac4{\sqrt5},
\sqrt{35},
\sqrt2,
3\sqrt2,
-1,
2
\right).}
\]

The corresponding raising tuple is

\[
(A,B,C,D,E,F,G)
=\left(
a,-b,c,-d,e,1,g
\right).
\]

Other sign choices related by rephasing individual mode towers are
equivalent.

## Relation to the Taub kernels

Only now introduce the separate kernel-to-generator ansatz

\[
M^-_{\rm Taub}=\lambda J K^-.
\]

The two independently computed action-normalized reduced kernels are

\[
m_b=-{\sqrt{10}\over5\pi},
\qquad
m_g={\sqrt2\over2\pi}.
\]

In the canonical form they independently give

\[
{m_b\over \eta_{E2}b}
=
{m_g\over \eta_{A3}g}
=\boxed{-{\sqrt2\over4\pi}}.
\]

The executable also freezes the Clebsch--Gordan factors rather than comparing
only reduced matrix elements.  For the selected highest-weight entries,

\[
C_b={1\over\sqrt2},\qquad C_g={2\over\sqrt5},
\]

so the canonical generator entries are

\[
bC_b={2\sqrt{10}\over5},\qquad
gC_g={4\sqrt5\over5}.
\]

The map `M=\lambda J K` then reproduces the two independently calculated
curvature-kernel entries

\[
M_b=-{\sqrt5\over5\pi},\qquad
M_g={\sqrt{10}\over5\pi}.
\]

Equivalently, one can use a positive scale
`1/(2\sqrt2\pi)` and attach phases `E=-1`, `A=L=+1`; this is the same
convention as `\lambda=-1/(2\sqrt2\pi)` with
`J=(+1,-1,-1)`.

Thus one nonzero curvature seed fixes the overall `\lambda` after the free
oscillator normalization and mode phases are fixed; the second is an exact
independent consistency check.  Before canonical Gram magnitudes are chosen,
their ratio fixes only

\[
\boxed{{\eta_{E2}\over\eta_{L4}}=-1},
\]

while other magnitude ratios remain basis choices.

This agreement is evidence for the map `M=\lambda JK` on the two seeded
blocks.  It is not yet a derivation of that map from the reduced symplectic
form for every tower.

## Fail-closed boundary

The certificate does not establish:

1. the energy-four commutator, which requires source-energy-five blocks;
2. the all-level recursion or domain of the unbounded generators;
3. the symplectic derivation of `M=\lambda JK` beyond the two seeds;
4. the seven nonlinear Killing Taub kernels;
5. the global BRST complex or physical quotient.

Its three scope guards reject energy-four closure, all-level closure, and
direct kernel--generator identification.
