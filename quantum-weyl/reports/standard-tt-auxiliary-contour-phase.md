# Standard TT auxiliary contour and phase

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

For one eigenmode \(Ah=\lambda h\), the standard auxiliary action is

\[
S_\lambda=\lambda h^2+\lambda hf-\frac12f^2.
\]

The real \(f\) contour diverges in \(e^{-S_\lambda}\). Choose instead the
oriented positive-imaginary thimble

\[
f=iy,\qquad y\in\mathbb R,
\]

with measure \(df/(i\sqrt{2\pi})=dy/\sqrt{2\pi}\). Then

\[
S_\lambda(h,iy)
=\frac12(y+i\lambda h)^2
\frac12\lambda(\lambda+2)h^2.
\]

The integrand is entire, so the Gaussian contour may be translated within the
same Stokes wedge. With

\[
\int_{\mathbb R}\frac{dy}{\sqrt{2\pi}}e^{-y^2/2}=1,
\]

the algebraic auxiliary contributes phase \(+1\) per oriented real mode and
no background-dependent logarithmic coefficient. The convergence wedge is
\(\pi/4<\arg f<3\pi/4\) modulo \(\pi\); the real axis diverges and the wedge
boundaries are not absolutely convergent.

This fixes a standard-factor contour policy. It does not yet prove that the
repository TT auxiliary row has this normalization, choose the full
infinite-dimensional regulator, or settle the physical Hessian, Slavnov
breaking, or QME.
