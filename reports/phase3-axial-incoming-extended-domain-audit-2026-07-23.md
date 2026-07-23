# Phase 3 extended axial incoming-connection audit

Date: 23 July 2026

## Summary

Four proposed upgrades were audited.  Three pass exactly:

1. the pilot-interval determinant has a uniform nonzero margin;
2. \(T_-\) invertibility and incoming Gram inertia extend to all real
   \(\omega>0\);
3. the incoming Gram has an exact factor-adapted anatomy.

The proposed upper-half-plane Evans no-zero theorem does **not** pass in the
repository phase convention.  The correct positive-potential theorem
excludes lower-half-plane growing modes.  Upper-half-plane frequencies are
temporally damped here, and their outgoing radial factors do not lie in the
\(L^2\) domain used by the energy proof.

## Uniform determinant margin

The analytic incoming theorem gives

\[
\det T_-=
C(\omega)A_{{\rm in},2}^2A_{{\rm in},1},
\qquad
|A_{{\rm in},s}|\ge1,
\]

with

\[
|C(\omega)|^2=
\frac{(4\omega^2+1)(16\omega^2+1)^2}
{16(\omega^2+1)}.
\]

Set \(x=\omega^2\).  Then

\[
\frac{d|C|^2}{dx}
=
\frac{(16x+1)(128x^2+208x+35)}
{16(x+1)^2}>0
\]

for \(x\ge0\).  Therefore the minimum on
\(\omega\in[1/2,3/4]\) occurs at \(\omega=1/2\), where

\[
|C|^2=\frac52.
\]

Hence

\[
\boxed{
|\det T_-(\omega)|\ge\sqrt{\frac52}.
}
\]

## Extension to every positive real frequency

Every exact map used by the factorization and endpoint assignment is regular
for \(r>2\) and real \(\omega>0\):

* the carrier cyclic determinant is
  \(-4\omega^2/[r^2(r-2)^2]\);
* the carrier triangular gauge has determinant
  \(-r^2(r-2)^2/(4\omega^2)\);
* the Einstein master map has determinant
  \[
  -\frac{i\omega^2(r-2)}
  {2r(\omega r-2i)};
  \]
* the factor-frame denominators
  \(\omega,\omega-i,2\omega-i,4\omega-i\) do not vanish;
* the horizon recurrence factors
  \(n+4i\omega\) and \(n+2+4i\omega\) do not vanish for positive integer
  \(n\);
* the infinity rates \(0,-2i\omega\) remain distinct;
* \(\omega r-2i\ne0\) on the real exterior.

The real short-range Wronskian argument applies at every real nonzero
frequency.  Consequently

\[
\boxed{
T_-(\omega)\in GL(3,\mathbb C)
\quad\text{for every real }\omega>0.
}
\]

The zero-frequency problem remains separate: cyclic coordinates and
endpoint rates degenerate there.

## Incoming Gram in the factor basis

Use the Hermitian convention

\[
G(u,v)=\overline u^{\,T}Gv,
\]

so the first slot is conjugate-linear.  Define

\[
RI=XI0-\frac{i}{\omega}XI1,\qquad
NI=-\omega^2XI0-2i\omega XI1+EI0,
\]

\[
SI=NI+\frac13EI0,\qquad EI=EI0.
\]

After the past-boundary Stokes sign, the exact dimensionless Gram in
\((RI,SI,EI)\) is

\[
G_-^{\rm factor}
=
\begin{pmatrix}
\frac{624}{5\omega}&0&\frac{576\omega}{5}\\
0&-\frac{384\omega^3}{5}&0\\
\frac{576\omega}{5}&0&0
\end{pmatrix}.
\]

Its leading principal minors are

\[
\frac{624}{5\omega},
\qquad
-\frac{239616\omega^2}{25},
\qquad
\frac{127401984\omega^5}{125}.
\]

Thus for \(\alpha_{\rm W}>0\) and every \(\omega>0\),

\[
\operatorname{inertia}G_-^{\rm factor}=(1,2,0).
\]

The exact quotient projection obeys

\[
\pi_x(XI0)=2,\qquad
\pi_x(XI1)=-2i\omega,\qquad
\pi_x(EI0)=0.
\]

Thus \(\pi_x(RI)=0\), whereas
\(\pi_x(NI)=\pi_x(SI)=-6\omega^2\).  The spin-two Regge--Wheeler
extension is therefore

\[
\ker\pi_x=\operatorname{span}\{EI,RI\}.
\]

Its Gram in the basis \((EI,RI)\) is

\[
\begin{pmatrix}
0&576\omega/5\\
576\omega/5&624/(5\omega)
\end{pmatrix},
\]

so its inertia is \((1,1,0)\).  The attribution is not inferred from
endpoint exponents: \(E\perp N\) and, with the displayed Hermitian slot
convention,

\[
G(E,RI)=\frac32G(E,XI0)=\frac{576\omega}{5}.
\]

Moreover \(G(RI,NI)=-192\omega/5\), so the coefficient \(1/3\) in
\(SI=NI+EI/3\) gives \(G(RI,SI)=0\).  It also leaves

\[
G(SI,SI)=G(NI,NI)=-\frac{384\omega^3}{5}.
\]

Hence the exact factor/pairing anatomy is

\[
\boxed{
\ker\pi_x\ (1,1,0)
\ \widehat\oplus\
\operatorname{span}\{SI\}\ (0,1,0).
}
\]

For a canonical Witt display set
\(RI_0=RI-13EI/(24\omega^2)\).  In the basis \((EI,RI_0,SI)\),

\[
G_-=
\begin{pmatrix}
0&576\omega/5&0\\
576\omega/5&0&0\\
0&0&-384\omega^3/5
\end{pmatrix}.
\]

This corrects the tempting but wrong identification
\(\operatorname{span}\{RI,XI1\}\) as the differential-factor split.  Since
\(\pi_x(XI0)=2\), the earlier endpoint Witt basis is not factor aligned.

## Evans convention correction

The repository uses

\[
e^{+i\omega v},
\qquad\text{hence}\qquad e^{+i\omega t}.
\]

Exponential time growth therefore occurs for

\[
\operatorname{Im}\omega<0,
\]

not for \(\operatorname{Im}\omega>0\).

For an incoming-coefficient zero, the horizon radial factor is
\(e^{+i\omega r_*}\) and the outgoing infinity factor is
\(e^{-i\omega r_*}\).  When \(\operatorname{Im}\omega<0\), both decay on a
constant-\(t\) slice.  The mode is in the energy domain of

\[
H_s=-D_{r_*}^2+V_s,
\qquad
H_s\psi=\omega^2\psi,
\]

with \(V_1,V_2\ge0\).  Therefore

\[
\langle\psi,H_s\psi\rangle
=\int\left(|\psi'|^2+V_s|\psi|^2\right)dr_*
\ge0.
\]

If \(\operatorname{Re}\omega\ne0\), then \(\omega^2\) is nonreal and cannot
be an eigenvalue of the self-adjoint operator.  If
\(\operatorname{Re}\omega=0\), then \(\omega^2<0\), contradicting
nonnegativity.  Hence the two reduced Evans factors have no
lower-half-plane growing zeros.

For \(\operatorname{Im}\omega>0\), the same radial factors grow on a
constant-\(t\) slice.  The \(L^2\) identity does not apply.  These frequencies
are temporally damped in this convention, so a no-UHP-zero claim would be a
quasinormal-mode exclusion and is not implied by potential positivity.

## The points \(i/4,i/2,i\)

All three points are exact singularities of the chosen endpoint or
reconstruction frames:

* \(\omega=i/4\): \(4\omega-i=0\), the Einstein horizon exponents collide,
  and \(\omega r-2i=0\) at \(r=8\);
* \(\omega=i/2\): \(2\omega-i=0\), two carrier horizon exponents collide,
  and the reconstruction wall is at \(r=4\);
* \(\omega=i\): \(\omega-i=0\), the spin-one Frobenius recurrence reaches
  its fourth-order integer resonance, and the reconstruction wall reaches
  the horizon \(r=2\).

Thus each is classified as a
**Frobenius/reconstruction-frame singularity**.  Because all lie in the
upper half-plane, the positive-energy theorem does not decide whether a
regularized reduced Evans function also vanishes there.  Their genuine
Evans status remains open.

## Scope

This audit does not classify \(\omega=0\), \(T_+\), reflection
nonvanishing, damped quasinormal frequencies, total energy, CPT positivity,
particles, ghosts or unitarity.  It strengthens the incoming theorem and
proves absence of reduced exponentially growing modes for the three
diagonal scalar factors; it is not yet a full stability theorem for the
coupled Bach system.
