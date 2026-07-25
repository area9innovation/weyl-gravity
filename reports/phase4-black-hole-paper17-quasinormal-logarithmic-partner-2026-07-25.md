# Paper 17 quasinormal logarithmic partner

## Result

Paper 17 now identifies the generalized axial Schwarzschild QNM as the
asymptotically flat quasinormal analogue of the logarithmic spin-two
partner in critical gravity.

For the normalized massive QNM family

\[
\Psi_m(t,r)=e^{i\omega_n(m)t}y_\sigma(m,r),
\qquad
\nu_n=\omega_n'(0)=\frac{2i}{\omega_n}\kappa_n,
\]

the canonical tangent class modulo the ordinary Einstein QNM obeys

\[
\boxed{
\frac{\partial_m\Psi_m|_0}{\Psi_0}
=
i\nu_nt-\frac{\sigma i}{2\omega_n}r+O(1).
}
\]

In the Bach normalization \(c(\omega_n)=i\omega_n/2\),

\[
\boxed{
\frac{c(\omega_n)\partial_m\Psi_m|_0}{\Psi_0}
=
-i\kappa_nt+\frac{\sigma}{4}r+O(1).
}
\]

Analytic renormalization of the QNM family changes only the \(O(1)\)
representative.  The coefficients of \(t\) and \(r\) are invariant in the
tangent class.

## No radial logarithm

The massive infinity Jost exponent is

\[
\rho_\sigma(m)=
\sigma i\left(2k+\frac{m}{k}\right),
\qquad
k=(\omega^2-m)^{1/2}.
\]

The exact cancellation

\[
\rho_\sigma'(0)
=
\sigma i\left(-\frac1\omega+\frac1\omega\right)
=0
\]

shows that the normalized scalar Jost tangent has no first-order
\(\log r\) term.  The linear \(r\) term comes instead from differentiating
the moving massive phase \(e^{\sigma ikr}\).

The phrase *quasinormal logarithmic partner* therefore refers to the same
mass-derivative and Jordan-chain mechanism as critical-gravity log modes,
not to literal logarithmic Schwarzschild radial behavior.

## Jordan time law

For the normalized length-two root chain

\[
HV_0=\omega_nV_0,
\qquad
HV_1=\omega_nV_1+V_0,
\]

one has

\[
\boxed{
e^{iHt}V_1=e^{i\omega_nt}(V_1+itV_0).
}
\]

The physical mass tangent carries the same class with polynomial
coefficient \(i\nu_nt\).  The time-independent generalized component
\(V_1\) has nonzero carrier quotient, whereas the \(t\)-weighted spatial
profile is the ordinary Einstein QNM \(V_0\).

## Literature position

The comparison was checked against primary sources:

- Lü and Pope, *Critical Gravity in Four Dimensions*, establish
  logarithmic spin-two modes at the critical massive/massless
  degeneration.
- Bergshoeff, Hohm, Rosseel, and Townsend, *Modes of Log Gravity*, show
  that the log modes arise as limits of massive spin-two modes in the
  noncritical theory.
- Yang, Berti, and Franchini, and independently Cheng and collaborators,
  identify the linear-in-time contribution required at black-hole
  exceptional points.
- Martel and Poisson give the gauge-invariant Schwarzschild reconstruction
  framework needed for the outstanding null-infinity audit.
- De Amicis and collaborators provide a concrete Green-function method
  for a future plunging-source QNM excitation calculation.

The paper makes no absolute priority claim.

## Asymptotic reconstruction gate

The linear \(r\) coefficient is a theorem for the reduced scalar infinity
Jost tangent.  It does not establish the falloff of a reconstructed metric,
curvature scalar, Newman–Penrose quantity, or strain.

Two candidate global realizations are recorded:

1. enlarge the endpoint domain to include differentiated-Jost tangents;
2. keep the standard bulk domain and encode the tangent in an augmented
   boundary pencil.

The leading double-pole contribution is Einstein-shaped.  If a future
null-infinity reconstruction proves

\[
\mathcal O_{\mathscr I^+}(\omega_n)V_0\ne0,
\]

then the enhanced term has the ordinary outgoing spatial profile,
schematically

\[
\frac{t}{r}e^{i\omega_nt}.
\]

That overlap, cancellation of the scalar \(O(r)\) tangent in the
time-independent generalized component, and the global causal contour
theorem remain open.

## Independent verification

The exact verifier independently checks:

- the Bach-normalized spacetime tangent from
  \(\nu_n=2i\kappa_n/\omega_n\);
- the vanishing derivative of the Coulomb exponent;
- exponentiation of the square-zero Jordan generator;
- the exact declarations for the scalar tangent, Jordan law, and
  asymptotic reconstruction gate;
- all fail-closed publication boundaries.

Six new adversarial tests reject a radial-sign mutation, promotion to a
literal radial logarithm, a Jordan-sign mutation, promotion of generalized
metric falloff, promotion of the null-infinity overlap, and an absolute
priority claim.  The full Paper 17 suite passed 83 tests in 134.988
seconds.  The repository discovery suite passed 149 tests in 0.280
seconds (2.26 seconds wall time).

## Claim boundary

Established:

- exact reduced scalar spacetime mass-tangent class;
- exact linear \(t\) and \(r\) coefficients;
- exact absence of a first-order scalar radial logarithm;
- exact length-two Jordan time law;
- precise critical-gravity and black-hole-EP literature positioning;
- explicit asymptotic reconstruction gate.

Not established:

- a literal Schwarzschild radial log mode;
- standard asymptotic-flatness falloff of the generalized metric;
- cancellation of the scalar \(O(r)\) tangent in strain or a
  Newman–Penrose observable;
- nonzero null-infinity observable overlap;
- a physical plunging-source adjoint overlap;
- a global retarded contour theorem;
- absolute priority;
- any Lorentzian quantum statement.

CLOSE-OUT: DONE — the certified Weyl generalized QNM is now identified
precisely as a quasinormal logarithmic partner: a mass-derivative Jordan
state with polynomial \(t\)- and \(r\)-behavior, but no first-order radial
logarithm in the normalized scalar Jost frame.

EVIDENCE: `reports/PAPER17_QUASINORMAL_LOGARITHMIC_PARTNER_TIER_RECEIPT.json`
