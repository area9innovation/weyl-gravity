# C2a: exact conformal-Killing reducibility rail

## Scope

`symbolic/verify_conformal_c2a_reducibilities.py` constructs the complete
Diff x Weyl reducibility space of the unit Einstein cylinder in the same
Euler-angle and Fourier conventions as the conformal perturbiner.  It closes
the **kinematic** part of C2a:

* all 15 reducibility pairs are explicit;
* their conformal-Killing and Weyl-compensator equations hold exactly;
* their complexified algebra closes and satisfies Jacobi;
* the special `ell=|omega|=1` P4 t block is one of these reducibilities; and
* its transverse quotient is the signed-frequency derivative of the
  reducibility modulo ordinary gauge.

This kinematic rail does **not** compute the nonlinear Bach source, the full
15 Taub-charge matrices, or the global BRST cohomology.  The companion
`symbolic/verify_conformal_taub_charge.py` separately identifies two selected
mixed proper-CK current components with action-normalized Taub charges.  The
present verifier's `--require-taub-matrix` option still fails closed because
the complete fifteen-component matrix is absent.

## Cylinder conventions

The background is

\[
 ds^2=-d\tau^2+d\Omega_3^2,
\]

with Euler angles `(alpha,beta,gamma)` and

\[
 d\Omega_3^2={1\over4}
 \left(d\alpha^2+d\beta^2+d\gamma^2
       +2\cos\beta\,d\alpha\,d\gamma\right).
\]

The ambient coordinates used by the perturbiner are

\[
\begin{aligned}
X_0&=\cos{\beta\over2}\cos{\alpha+\gamma\over2},\\
X_1&=\sin{\beta\over2}\sin{\alpha-\gamma\over2},\\
X_2&=-\sin{\beta\over2}\cos{\alpha-\gamma\over2},\\
X_3&=-\cos{\beta\over2}\sin{\alpha+\gamma\over2}.
\end{aligned}
\]

The certificate checks directly that

\[
 X_AX_A=1,
 \qquad
 D_iX_A D^iX_B=\delta_{AB}-X_AX_B,
 \qquad
 D_iD_jX_A=-\gamma_{ij}X_A.
\]

These identities are sufficient to prove every conformal-Killing equation
below without a coordinate sample or floating-point evaluation.

## The 15 Diff x Weyl pairs

The reducibility equation uses precisely the perturbiner sign convention,

\[
 \mathcal L_\xi\bar g_{\mu\nu}
 +2\sigma\bar g_{\mu\nu}=0,
 \qquad
 \sigma=-{1\over4}\bar\nabla_\mu\xi^\mu.
\]

One generator is time translation,

\[
 T:\qquad \xi=\partial_\tau,qquad \sigma=0.
\]

Six are the spatial `SO(4)` rotations,

\[
 R_{AB}:\qquad
 \xi^0=0,
 \qquad
 \xi^i=X_A D^iX_B-X_BD^iX_A,
 \qquad
 \sigma=0,
 \quad A<B.
\]

The remaining eight real generators are most compactly written in a complex
frequency basis.  For `s=+/-1`,

\[
 K_A^s:\qquad
 \xi^\mu=e^{-is\tau}\bigl(-isX_A,D^iX_A\bigr),
 \qquad
 \sigma=e^{-is\tau}X_A.
\]

Complex conjugation exchanges `K_A^+` and `K_A^-`; hence these are eight
real generators, not sixteen.  An explicit real basis is

\[
 C_A={K_A^++K_A^-\over2},
 \qquad
 S_A={K_A^+-K_A^-\over2i},
 \qquad A=0,1,2,3.
\]

Thus the representation and compact-energy count is

\[
 15=1+(3+3)+4_{+1}+4_{-1}.
\]

The checked complex brackets include

\[
 [T,K_A^s]=-isK_A^s,
\]

\[
 [R_{AB},K_C^s]
 =\delta_{BC}K_A^s-\delta_{AC}K_B^s,
\]

\[
 [K_A^s,K_B^s]=0,
 \qquad
 [K_A^+,K_B^-]=2R_{AB}+2i\delta_{AB}T,
\]

together with the ordinary `so(4)` rotation bracket.  The verifier checks all
Jacobi identities across the complete 15-generator basis.

## Exact identification of the P4 t block

The highest scalar harmonic used by the t-channel rail is

\[
 Y_{++}^{(1/2)}
 ={e^{-i(\alpha+\gamma)/2}\cos(\beta/2)\over\pi}
 ={X_0+iX_3\over\pi}.
\]

Consequently its positive-frequency reducibility is the normalized
combination `(K_0^+ + i K_3^+)/pi`.  In the scalar metric-component basis

\[
 h_{00}=x_0Y,
 \qquad
 h_{0i}=x_1D_iY,
 \qquad
 h_{ij}=x_2\gamma_{ij}Y,
\]

the Diff x Weyl parameters are ordered as

\[
 (\xi_0,\xi_L,\sigma).
\]

For signed frequency `s Omega`, the exact gauge generator is

\[
 G_s(\Omega)=
 \begin{pmatrix}
 -2is\Omega&0&-2\\
 1&-is\Omega&0\\
 0&-2&2
 \end{pmatrix}.
\]

At `Omega=1`,

\[
 r_s=(is,1,1)^T,
 \qquad
 G_s(1)r_s=0.
\]

This is the precise finite-component form of the conformal-Killing
reducibility.  The conformal de-Donder/Weyl transverse representative is

\[
 p_s=(3,is,1)^T.
\]

Writing `B_s` for the first two columns of `G_s(1)`, the verifier proves

\[
 \boxed{
 \left.\partial_\Omega G_s(\Omega)\right|_{\Omega=1}r_s
 -2p_s
 =B_s(-2is,1)^T .}
\]

Therefore the quotient class of `p_s` is the frequency derivative of the
reducible gauge transformation.  This is an exact generalized-mode operator
identity.  It identifies the kinematic zero mode but, by itself, does not say
whether a particular nonlinear current equals a Taub charge; the selected
current-to-charge normalization is the logically separate companion rail.

## Reproduction

Run

```bash
python3 symbolic/verify_conformal_c2a_reducibilities.py
python3 symbolic/verify_conformal_c2a_reducibilities.py --show-formulas
```

The missing **full** nonlinear rail is intentionally visible:

```bash
python3 symbolic/verify_conformal_c2a_reducibilities.py --require-taub-matrix
```

The last command must exit nonzero until the full 15-component Bach/Taub
matrix and the corresponding global BRST reduction have been supplied.
