# Two-phase counterflow secular clock: orbital-stability disposition

## Result

The unrestricted homogeneous relative phase/charge block is an exact
action--angle system,

\[
  \Omega_{\rm rel}=dQ_{\rm rel}\wedge d\psi,
  \qquad
  H_{\rm rel}=\frac{Q_{\rm rel}^2}{2I}+E_{\rm geometry},
  \qquad
  I=\frac{12\pi^2\sqrt{10}}5.
\]

Its exact flow is

\[
  \Phi_t(\psi,Q)=(\psi+tQ/I,Q),
\]

with the phase taken modulo \(2\pi\) for the compact clock.  Every constant
charge trajectory is a relative equilibrium under the physical global
\(R_{\rm rel}\) action, with frequency \(\nu(Q)=Q/I\).  At the certified
background,

\[
  Q_0=\frac{9\pi^2\sqrt{10}}5,
  \qquad \nu(Q_0)=\frac34.
\]

Differentiating the exact family

\[
  z_{\psi_*+\epsilon\psi_1,Q_0+\epsilon q_1}(t)
\]

at \(\epsilon=0\) gives exactly

\[
  \delta Q(t)=q_1,
  \qquad
  \delta\psi(t)=\psi_1+\frac{tq_1}{I}.
\]

Thus the size-two zero Jordan block is an integrable family tangent.  It is
not a negative-energy mode and has no exponential root.

## Four stability notions

These verdicts are different and must not be conflated.

1. **Bounded stability on a real phase lift fails.**  A nonzero charge
   perturbation produces unbounded linear shear \(t\,\delta Q/I\).
2. **Absolute Lyapunov stability of the compact \(S^1\) clock fails.**  An
   arbitrarily small frequency difference eventually produces angular
   separation \(\pi\).
3. **Fixed-charge orbital stability passes.**  The \(Q=Q_0\) level is one
   physical \(R_{\rm rel}\) orbit, and equal-charge trajectories retain a
   constant phase separation.  This comparison does not declare
   \(R_{\rm rel}\) gauge and does not resurrect a clock after fixed-charge
   symplectic reduction.
4. **Shifted-frequency modulated stability passes.**  Applying the explicitly
   physical modulation
   \(\alpha(t)=-(\nu(Q)-\nu(Q_0))t\) leaves constant phase and charge
   separation.

The unrestricted trajectories are also orbitally stable under the physical
global \(R_{\rm rel}\) action: their distance to the reference group orbit is
the constant charge separation.  This is a stability comparison, not a gauge
quotient.

The energy--momentum augmented Hamiltonian is

\[
  H_{\rm rel}-\nu(Q_0)Q_{\rm rel}
  =\frac{(Q_{\rm rel}-Q_0)^2}{2I}+\mathrm{constant}.
\]

Its Hessian has inertia \((1,0,1)\) in the order
(positive, negative, zero).  The zero direction is the physical group orbit;
the transverse charge curvature is positive.  The fixed-momentum symplectic
slice is zero-dimensional.

## Reduced family versus complete coupled backgrounds

The reduced relative-phase family is not a nearby family of complete
fixed-action Berger solutions.  At the selected geometry \(q=9/40,x=1\),
all three complete stationary rows collapse to

\[
  -\frac{16C-9}{32},
  \qquad C=(Q_{\rm rel}/I)^2,
\]

or equivalently

\[
  -\frac{5Q_{\rm rel}^2-162\pi^4}{576\pi^4}.
\]

The only charge roots are \(Q_{\rm rel}=\pm Q_0\), and the derivative at the
positive-frequency root is nonzero.  Hence the positive-frequency coupled
component is locally isolated and the full linearized lapse/metric constraint
requires \(\delta Q_{\rm rel}=0\).  The action--angle shear is exact on the
unrestricted reduced subsystem, but it does not silently manufacture a
nearby causal parent or full coupled background.

## Mutations and next gate

Charge reversal reverses the clock orientation without changing the positive
energy curvature.  Reversing the inertia sign preserves the algebraic shear
but changes the augmented Hessian to one negative direction.  At zero inertia
the Legendre transform is undefined.  These mutations distinguish the
certified positive shear from an energetic ghost.

The next admissible gate is
`classical-two-phase-counterflow-unrestricted-all-hodge-health`: compute the
complete scalar, vector, tensor, exceptional and global physical blocks on
the 70-row unrestricted carrier, retaining charged \(D\) and
\(R_{\rm rel}\), and certify pairing inertia, characteristic/Jordan data,
gradient signs, causal cones and radicals.  The homogeneous normal form is
not an all-Hodge theorem.

This is exact `LOCAL-ALGEBRAIC`/`REDUCED-MODE` evidence with the selected
`LORENTZIAN-CAUSAL` unary parent imported by hash.  It establishes no
observer, Hadamard, QME, particle, scattering, positivity or unitarity claim.

CLOSE-OUT: DONE — the complete stop condition is met
EVIDENCE: TWO_PHASE_COUNTERFLOW_SECULAR_CLOCK_ORBITAL_STABILITY_V1_TIER_RECEIPT
