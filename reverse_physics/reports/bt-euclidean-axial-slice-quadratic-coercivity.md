# BT axial-slice quadratic coercivity

Certificate:
REVERSE_PHYSICS_BT_EUCLIDEAN_AXIAL_SLICE_QUADRATIC_COERCIVITY_V1

Dependency tags:
LOCAL-ALGEBRAIC, EUCLIDEAN-SPECTRAL, REDUCED-MODE

## Result

The positive nonlinear BT action retains a quadratic free-scale lower bound
for every lowest axial Fourier coefficient, even in the presence of arbitrary
transverse fluctuations. On every periodic four-dimensional \(L^4\) lattice
with \(L\geq4\),

\[
 A(\psi)\geq {N\omega_L^2\over3}
       |\widehat\psi(e_\mu)|^2,
 \qquad
 \omega_L=4\sin^2(\pi/L),\qquad N=L^4.
\]

Here

\[
 \widehat\psi(e_\mu)=N^{-1}\sum_x
 \psi_xe^{-2\pi i x_\mu/L}.
\]

Equivalently, with \(\psi=\lambda\phi\),

\[
 S_\lambda(\phi)={A(\lambda\phi)\over\lambda^2}
 \geq {N\omega_L^2\over3}|\widehat\phi(e_\mu)|^2.
\]

The coefficient is uniform in volume, nonzero coupling, choice of axis, and
all orthogonal field components. This improves the earlier correct-scale
quartic lowest-mode action-sublevel estimate to a quadratic estimate. The
known global bilaplacian quadratic envelope loses an extra factor of \(N\) at
this mode; the slice argument restores the correct free
\(N\omega_L^2\) scaling.

This is not yet the normalized lowest-mode moment. A lower bound on the
action at each field does not, on its own, control how the volume of the
orthogonal cross-section varies with the selected Fourier coefficient.

## Slice Jensen inequality

Choose the first coordinate as the axial direction and write each site as
\(x=(t,z)\), with \(z\) in a three-dimensional slice of size \(M=L^3\).
Define

\[
 b_t={1\over M}\sum_z\psi_{t,z},\qquad
 \bar r_t={1\over M}\sum_zr_{t,z}.
\]

For each of the six directed spatial neighbours, periodicity and Jensen give

\[
 {1\over M}\sum_z e^{\psi_{t,z+e}-\psi_{t,z}}
 \geq
 \exp\left[{1\over M}\sum_z
       (\psi_{t,z+e}-\psi_{t,z})\right]=1.
\]

The two temporal directed averages similarly obey

\[
 {1\over M}\sum_z e^{\psi_{t\pm1,z}-\psi_{t,z}}
 \geq e^{b_{t\pm1}-b_t}.
\]

Since \(e^s\geq1+s\),

\[
 \bar r_t
 \geq e^{b_{t-1}-b_t}+e^{b_{t+1}-b_t}-2
 \geq b_{t-1}+b_{t+1}-2b_t
 =:(\Delta_1b)_t.
\]

If \((\Delta_1b)_t>0\), this also gives
\(\bar r_t^2\geq(\Delta_1b)_t^2\). Slice Cauchy--Schwarz
therefore proves the all-profile bound

\[
 \boxed{
 A(\psi)\geq{M\over2}
       \|(\Delta_1b)_+\|_2^2.}
\]

Only the positive part is asserted. Negative slice Laplacian values can be
cancelled by the nonnegative exponential remainder; discarding that fact
would give an invalid stronger inequality.

## Zero-sum positive-part Fourier lemma

Put \(a=\Delta_1b\), so \(\sum_ta_t=0\). If \(a\neq0\), let

\[
 P=\sum_t(a_t)_+=\sum_t(-a_t)_+,\qquad
 c_-={1\over P}\sum_t(-a_t)_+h_t,
\]

where \(h_t=\cos(2\pi t/L+\theta)\). Then

\[
 \langle a,h\rangle
 =\sum_t(a_t)_+(h_t-c_-).
\]

For the lowest mode at every \(L\geq4\),

\[
 \sum_th_t=0,\qquad \sum_th_t^2={L\over2},\qquad |c_-|\leq1.
\]

Cauchy--Schwarz consequently yields

\[
 |\langle a,h\rangle|^2
 \leq\|(a)_+\|_2^2
       \sum_t(h_t-c_-)^2
 \leq{3L\over2}\|(a)_+\|_2^2.
\]

Choose the phase \(\theta\) so that the real pairing equals the modulus of
the complex Fourier pairing. Since

\[
 \sum_ta_te^{-2\pi it/L}
 =-L\omega_L\widehat\psi(e_1),
\]

we obtain

\[
 \|(\Delta_1b)_+\|_2^2
 \geq {2L\over3}\omega_L^2
       |\widehat\psi(e_1)|^2.
\]

Combining this with the slice inequality and \(ML=N\) proves the theorem.
Axis permutation proves the other three cases.

## Exact nonseparable fixture

On the \(4^4\) torus, take

\[
 \Omega_{txyz}=2^{k_{tx}},\qquad
 k_{tx}=b_t+c_ts_x,
\]

with

\[
 b=(0,1,0,-1),\qquad
 s=(1,-1,0,0),\qquad
 c=(1,0,0,0).
\]

This field is genuinely nonconstant within the \(t=0\) spatial slice. Exact
rational enumeration of all 256 sites gives

\[
 \bar r=\left({13\over8},-{15\over16},{1\over2},{9\over4}\right),
 \qquad
 A={1361\over2}.
\]

The slice exponent means are \(b\), and their Laplacian coefficients are
\((0,-2,0,2)\). The slice Cauchy lower bound is exactly

\[
 {64\over2}\sum_t\bar r_t^2={2261\over8},
\]

leaving the positive gap \(3183/8\). Moreover,

\[
 |\widehat\psi(e_1)|^2={\log^2 2\over4},\qquad \omega_4=2.
\]

Using the rational bound \(\log2<7/10\), the new right-hand side satisfies

\[
 {256\over3}\log^2 2<{3136\over75}<{1361\over2}.
\]

The independent verifier enumerates the full four-dimensional field and
reconstructs every residual and slice average without importing the
producer's fixture helper.

## Meaning for the reconstruction programme

This eliminates low-action escape of the selected coefficient itself: an
arbitrarily large lowest axial coefficient necessarily pays the correct
quadratic action cost, even if the transverse field is optimized
adversarially.

It does not eliminate entropy escape. The normalized marginal integrates
over \(N-2\) orthogonal directions, and their available weighted volume may
change with the coefficient. The exact fixed-volume runaway conditional
centers demonstrate why this distinction matters, even though those fields
also pay a large absolute action cost.

The next calculation should combine this origin-centered quadratic cost with
the certified all-background strong convexity of each lowest-mode fiber.
Parameterizing fibers by their unique centers isolates one remaining object:
the Jacobian and Gibbs weight of the center hypersurface. A volume-uniform
bound on that normalized object would prove the one-mode theorem; an actual
weighted countersequence would obstruct it.

## Boundary

This certificate does not establish a normalized marginal comparison,
lowest-mode second moment, interacting \(H^{-1}\) estimate, tightness, or a
continuum measure. It does not alter the finite-volume ordinary-OS
obstruction and has no Born, Krein, or LORENTZIAN-CAUSAL consequence. No
literature-priority claim is made.

## Verification

Run sequentially under the 500 MB cap:

    ulimit -v 500000; python3 reverse_physics/bt_euclidean_axial_slice_quadratic_coercivity.py --check
    ulimit -v 500000; python3 reverse_physics/verify_bt_euclidean_axial_slice_quadratic_coercivity.py
    ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_euclidean_axial_slice_quadratic_coercivity
