# Nonlinear source/transfer dictionary and tangent-cone naturality

With factorial Taylor operations,

\[
E(\bar\Phi+\varphi)=q_1\varphi+\frac12q_2(\varphi,\varphi)
+\frac1{3!}q_3(\varphi,\varphi,\varphi)+\cdots,
\]

so `D^2E(u,u)=q2(u,u)`.  For
`Phi=barPhi+epsilon*u+epsilon^2*v`, the second-order equation is

\[
q_1v=-\frac12q_2(u,u).
\]

On a contraction, `ell2=pi_cl q2(iota,iota)` and
`I2=-S q2(iota,iota)`.  The ternary operation is

\[
\ell_3=\pi_{cl}q_3(\iota^3)
+\sum_{\mathrm{Sh}(2,1)}\epsilon\,\pi_{cl}q_2(I_2,\iota).
\]

Thus `ell2`, not `ell3`, is the quadratic tangent-cone source.  `ell3`
controls the next Taylor order and the quartic action/deformation problem.

For an admissible field change with linear tangent map `T`, equation-bundle
map `U`, and quadratic coordinate term `F2`, the Hessian source changes by

\[
S'(u,u)=U\bigl(S(Tu,Tu)+q_1F_2(u,u)\bigr).
\]

The `q1 F2` term vanishes after projection to the adjoint cokernel.  Hence the
obstruction map transforms by the induced invertible cokernel map and
`Z_2^C` is carried to `T^{-1} Z_2^C`, provided the field change preserves the
declared harmonic input space and correction category `C`.  Changing `C` is
a change of theorem, not a field redefinition.

This naturality statement imports the general finite-harmonic tangent-cone
theorem.  It does not supply a Berger harmonic branch crosswalk or turn the
mixed `ell3` obstruction into a second-order Taub obstruction.
