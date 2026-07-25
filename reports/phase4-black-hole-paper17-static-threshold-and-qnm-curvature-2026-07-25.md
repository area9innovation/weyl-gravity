# Paper 17 static threshold and massive-QNM curvature

## Result

Paper 17 now proves that the static mass-direction class is nontrivial for
every radiative multipole:

\[
[f]\ne0
\quad\text{in}\quad
\mathbb C(r)/\mathcal K_{\ell,0}\mathbb C(r),
\qquad
f=1-\frac2r,\quad \ell\ge2.
\]

The proof is exhaustive over \(\mathbb C(r)\).  It verifies:

- the zero indicial polynomial
  \[
  -8(k-6)(k-2)(k+2);
  \]
- the infinity degree polynomial
  \[
  (k-1)(k-2\ell-2)(k+2\ell);
  \]
- the exceptional \(r^{-2}\) compatibility
  \[
  \frac{\Lambda^2(\Lambda-2)^2}{9}a_{-2}=0;
  \]
- the static Regge--Wheeler polynomial recurrence and homogeneous
  symmetric square \(y_\ell^2\);
- the terminal cubic obstruction
  \[
  \Lambda^2+2\Lambda+12=0.
  \]

The dipole is an exact control:

\[
q_1=\frac{r^2}{6}+\frac{r^3}{15}+\frac{r^4}{36},
\qquad
\mathcal K_{1,0}q_1=f.
\]

This establishes the mass-direction theorem for all \(\ell\ge2\), not
all-\(\ell\) Bach nonsplitting.  The latter still requires the reduction

\[
[\mathcal I_{{\rm Bach},\ell}]
=c_\ell(\omega)[f]
\]

with \(c_\ell(\omega)\ne0\).

## Exact threshold valuation

For the explicitly reduced axial \(\ell=2\) Bach cocycle,

\[
[\mathcal I_{\rm Bach}]
=\frac{i\omega}{2}[f].
\]

The all-multipole static theorem removes the previous conditional
cokernel wording and proves

\[
\operatorname{ord}_{\omega=0}[\mathcal I_{\rm Bach}]=1,
\qquad
\left.\frac{[\mathcal I_{\rm Bach}]}{\omega}\right|_{\omega=0}
=\frac{i}{2}[f]\ne0.
\]

The original \(1/\omega\) term is statically exact.  The surviving
order-\(\omega\) class cannot be removed by a rational gauge holomorphic
at threshold.  No threshold-uniform Jost estimate for \(b/a^2\) is
promoted.

## Second-order QNM curvature

For the fixed-domain augmented pencil

\[
L_m(\omega)=L(\omega)+mA(\omega),
\qquad
\omega_n(m)=\omega_n+\nu_nm+\frac12\xi_nm^2+O(m^3),
\]

Paper 17 now proves

\[
\xi_n=
\frac{
2\langle\widetilde u_n,B_nH_nB_nu_n\rangle
-\nu_n^2\langle\widetilde u_n,L_n''u_n\rangle
-2\nu_n\langle\widetilde u_n,A_n'u_n\rangle
}{\alpha_n},
\qquad
B_n=A_n+\nu_nL_n'.
\]

The normalization-dependent component of \(\dot u_n\) cancels by the
first-order solvability identity
\(\langle\widetilde u_n,B_nu_n\rangle=0\).

The refined gap and local divided-exponential expansions are

\[
\delta_m=\nu_nm+\frac12\xi_nm^2+O(m^3),
\qquad
\frac1{\delta_m}
=\frac1{\nu_nm}-\frac{\xi_n}{2\nu_n^2}+O(m),
\]

and

\[
\frac{e^{i\omega_n(m)t}-e^{i\omega_nt}}{m}
=e^{i\omega_nt}\left[
i\nu_nt
+m\left(\frac{i\xi_nt}{2}-\frac{\nu_n^2t^2}{2}\right)
+O(m^2)
\right].
\]

## Claim boundary

Established:

- exact all-\(\ell\ge2\) static mass-direction nontriviality;
- exact \(\ell=1\) rational preimage control;
- exact axial \(\ell=2\) Bach threshold valuation one;
- exclusion of holomorphic improvement to \(O(\omega^2)\);
- exact fixed-domain augmented QNM-curvature formula;
- exact next-order gap and isolated-contour expansions.

Not established:

- the general-\(\ell\) Bach coefficient \(c_\ell(\omega)\);
- all-\(\ell\) Bach nonsplitting;
- a threshold-uniform physical Jost estimate;
- a numerical value or validated enclosure for \(\xi_n\);
- a global retarded contour deformation, stability theorem, or quantum
  statement.

CLOSE-OUT: DONE — the static mass direction is classified for every
radiative multipole, the axial Bach threshold valuation is exact, and the
massive-QNM curvature is reduced to ordinary augmented Regge--Wheeler data.
EVIDENCE: reports/PAPER17_STATIC_THRESHOLD_QNM_CURVATURE_TIER_RECEIPT.json
