# BT mixed-Hessian-square obstruction

**Dependency tags:** `LOCAL-ALGEBRAIC`, `REDUCED-MODE`
**Lifecycle:** `CLASSIFIED`

## Result

The background-uniform pointwise estimate suggested by the quotient-site
Poincare theorem cannot have the fourth-order low-momentum scaling needed by
the free BT covariance.

More precisely, let

\[
 A(\psi)=\frac12\sum_x r_x(\psi)^2,
 \qquad
 r_x=\sum_{y\sim x}e^{\psi_y-\psi_x}-8,
\]

on the four-dimensional periodic lattice. On every torus with \(L\geq8\)
and \(4\mid L\), repeat the positive axial profile

\[
 \Omega_x=e^{\psi_x}=(1,2,3,4)_{x_1\bmod4}
\]

and take the lowest axial sine \(k_L(x)=\sin(2\pi x_1/L)\). At the origin,
the exact mixed Hessian is

\[
 \operatorname{Hess}S[h_o,k_L]
 =19\sin p_L+\frac9{16}\sin(2p_L)
 =\frac{161}{8}p_L+O(p_L^3),
 \qquad p_L=\frac{2\pi}{L}.
\]

The same first-order term survives after taking the one-site conditional
square. Consequently that square is order \(p_L^2\), whereas the desired
bilaplacian square \(\omega(p_L)^2\) is order \(p_L^4\). There is therefore no
constant \(C\), uniform in volume and conditional background, for

\[
 \mathbb E_{q_\eta}
 \left[(\operatorname{Hess}S[h_o,k_L])^2\right]
 \leq C\,\omega(p_L)^2.
\]

This is a method obstruction. It says that applying the one-site Poincare
inequality and Cauchy--Schwarz before extracting signed spatial cancellation
loses one derivative. It does **not** say that the signed conditional
covariance, a block heat-bath argument, or the interacting \(H^{-1}\) estimate
fails.

The machine-readable certificate is
`REVERSE_PHYSICS_BT_EUCLIDEAN_MIXED_HESSIAN_SQUARE_OBSTRUCTION_V1`.

## Exact Hessian stencil

Write \(t_{xy}=\Omega_y/\Omega_x\). Direct differentiation of
\(A=\frac12\sum r_x^2\) gives the off-diagonal range-two row

\[
 H_{xy}=-(8+2r_x)t_{xy}-(8+2r_y)t_{yx},
 \qquad x\sim y,
\]

\[
 H_{x,x+2e}=t_{x+e,x}t_{x+e,x+2e},
\]

and, for signed unit vectors \(e,f\) in distinct axes,

\[
 H_{x,x+e+f}=
 t_{x+e,x}t_{x+e,x+e+f}
 +t_{x+f,x}t_{x+f,x+e+f}.
\]

Shift invariance fixes \(H_{xx}=-\sum_{y\ne x}H_{xy}\). This also means that
the quotient direction \(h_o=\delta_o-N^{-1}\mathbf1\) can be replaced by
\(\delta_o\) inside the Hessian.

The scaling used throughout the normalized BT measure introduces no extra
factor: for \(S(\phi)=A(\lambda\phi)/\lambda^2\),

\[
 \operatorname{Hess}_\phi S=\operatorname{Hess}_\psi A.
\]

## Exact periodic witness

For the displayed profile, the origin residual is \(r_o=4\). Summing the
origin Hessian row by axial displacement gives

| displacement \(z_1\) | \(-2\) | \(-1\) | \(1\) | \(2\) |
|---:|---:|---:|---:|---:|
| \(\sum_{z:z_1}H_{oz}\) | \(3/16\) | \(-40\) | \(-21\) | \(3/4\) |

The odd parts of the unit and double shells are therefore

\[
 (-21)-(-40)=19,
 \qquad
 \frac34-\frac3{16}=\frac9{16}.
\]

Their first axial moment is

\[
 19+2\frac9{16}=\frac{161}{8}\ne0.
\]

The producer obtains these numbers from the closed range-two stencil. The
independent verifier instead differentiates every residual on an \(8^4\)
torus and reconstructs the Hessian as

\[
 H_{ij}=\sum_x
 \left[(\partial_i r_x)(\partial_j r_x)
       +r_x\partial_i\partial_j r_x\right].
\]

Thus the verifier does not import the producer's Hessian formula.

## Why the conditional expectation remains positive

The mode is mean zero and \(k_L(o)=0\), so it lies in \(h_o^\perp\), as required
by the quotient-site conditional decomposition. Along that fiber, varying
the normalized coordinate \(s\) multiplies only \(\Omega_o\) by
\(e^{\lambda s}\). The mixed Hessian has the form

\[
 G_L(s)=A_1(s)\sin p_L+A_2(s)\sin(2p_L),
\]

where \(A_1,A_2\) are analytic Laurent-exponential functions. The normalized
one-site density is strictly positive, and its exponential-quartic tails
integrate every Laurent-exponential moment needed here. Dominated convergence
therefore gives

\[
 \lim_{\substack{L\to\infty\\4\mid L}}
 \frac{\mathbb E_q[G_L(s)^2]}{p_L^2}
 =\mathbb E_q[(A_1(s)+2A_2(s))^2].
\]

The right side is strictly positive for every nonzero coupling: its analytic
integrand is not identically zero because its value at the displayed fiber
point is \((161/8)^2=25921/64\), and the conditional density is positive.

By contrast,

\[
 \omega(p_L)=2(1-\cos p_L)=p_L^2+O(p_L^4).
\]

Hence

\[
 \frac{\mathbb E_q[G_L^2]}{\omega(p_L)^2}
\]

diverges like a positive multiple of \(p_L^{-2}\).

## Meaning for the research programme

The local theorem

\[
 |D_km_o|
 \leq\frac12
 \sqrt{\mathbb E_q[(\operatorname{Hess}S[h_o,k])^2]}
\]

is correct, but this witness proves that its right side is generally only
first-order in a long wavelength. The free heat-bath response is
fourth-order because signed entries cancel across the entire range-two row.
An arbitrary conditional background destroys that cancellation pointwise.

The next viable calculation must retain the sign in

\[
 D_km_o=-\operatorname{Cov}_q(s,D_kS)
\]

and average the response kernel before taking absolute values or squares.
The natural alternatives are a translation-averaged signed axial symbol or a
block conditional response large enough to average the short period-four
fluctuation. Either route must be tested for an \(\omega\) term and an
\(\omega^2\) term separately.

## Claim boundary

This certificate does not establish failure of every heat-bath or
local-to-global method. It does not establish failure of the signed
conditional covariance, a block estimate, a global Poincare or Witten theorem,
the interacting \(H^{-1}\) bound, or a continuum Euclidean measure. It says
nothing new about a physical dimension, the Born rule, Krein reconstruction,
or any `LORENTZIAN-CAUSAL` claim.

## Verification

```bash
ulimit -v 500000; python3 reverse_physics/bt_euclidean_mixed_hessian_square_obstruction.py --check
ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_mixed_hessian_square_obstruction.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_mixed_hessian_square_obstruction
```
