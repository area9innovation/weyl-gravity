# Neutral conformal clock-pair theorem

## Result

The one-scalar obstruction has a minimal exact-cylinder repair at the
classical homogeneous level.  Take two real conformal scalars with internal
metric \(\eta_{AB}=\operatorname{diag}(+1,-1)\):

\[
S_{\rm pair}=-\frac12\int\sqrt{-g}\,\eta_{AB}
\left(\nabla T^A\!\cdot\!\nabla T^B+\frac{R}{6}T^AT^B\right).
\]

Their homogeneous variables \(\chi_A=aT_A\) are unit oscillators.  Define

\[
H_D=\frac12(\chi_1^2+\pi_1^2-\chi_2^2-\pi_2^2),\qquad
W=\chi_1\pi_2-\chi_2\pi_1.
\]

Both \(H_D\) and \(W\) are conserved.  On the open sector

\[
H_D=0,\qquad W\ne0,
\]

the total improved stress tensor vanishes componentwise.  Since the cylinder
is Bach-flat, this is an exact nonzero solution sector of the coupled scalar
and metric equations, rather than a test-field background.

A representative is

\[
(\chi_1,\pi_1,\chi_2,\pi_2)
=r(\cos t,-\sin t,\sin t,\cos t).
\]

## Clock and gauge incidence

The projective field

\[
z=\frac{\chi_1+i\chi_2}{\sqrt{\chi_1^2+\chi_2^2}}\in U(1)
\]

is Weyl invariant.  Its local angle obeys

\[
\dot\theta=\frac{W}{\chi_1^2+\chi_2^2},
\]

so it has no turning point on either connected component \(W>0\) or
\(W<0\).  It is a global group-valued clock for the effective compact
\(D\)-orbit.  A real clock on the universal cover additionally requires a
winding lift and an initial reference.

In raw scalar coordinates, compact time translation and Weyl rescaling act by

\[
\delta T_A=\epsilon_D\dot T_A-\sigma_WT_A.
\]

In the fixed cylinder frame \(a=1\), these raw fields agree numerically with
\(\chi_A\), and the two-field incidence determinant is exactly \(W\).  It
therefore has full rank throughout the regular clock sector.  The distinction
is conceptual: \(\chi_A=aT_A\) is individually Weyl invariant and is used for
oscillator dynamics, whereas the raw radius
\(u=\tfrac12\log(T_1^2+T_2^2)\) fixes Weyl.  The projective angle fixes \(D\)
independently.

## Scoped symplectic conclusion

With

\[
\Omega=d\chi_1\wedge d\pi_1-d\chi_2\wedge d\pi_2,
\]

the Hamiltonian of the \(D\)-flow is \(H_D\).  The zero level is regular for
nonzero amplitude, and the \(D\)-flow is a kernel direction of the pullback
of \(\Omega\).  Therefore

```text
D_compact = D_GAUGE
```

on the declared phase space
`compact_neutral_clock_pair_homogeneous`.

## Essential limitation

The cancellation uses an opposite-sign reference scalar.  The unrestricted
matter theory is not positive-energy, and this certificate does not show
that the negative direction is removed in the full inhomogeneous BV theory.
It proves a working classical clock and exact-cylinder background, not a
healthy standalone matter model.

The next gate is `FULL_NEUTRAL_CLOCK_PAIR_BV_COMPLETION`: construct the local
inhomogeneous complex, determine whether its reference sector is entirely
gauge/contractible, and test nonlinear stability and quantum admissibility.
