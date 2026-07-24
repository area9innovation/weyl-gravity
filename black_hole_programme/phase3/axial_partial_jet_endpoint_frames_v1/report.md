# Endpoint partial-jet frame audit

Dependency boundary: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`. Lifecycle:
`CLASSIFIED`.

The certificate establishes exact endpoint factor compatibility at the
future horizon, incoming null infinity, and outgoing null infinity.  In the
common factor order \((R,S,E)\), it freezes exact scalar rescalings and the
permutation to jet order \((E,R,S)\).  The spin-one normalization is
\(\tau\)-independent.  Exact dual-number algebra verifies multiplication,
inversion, and the inverse entries

\[
-\frac{b}{a^2},\qquad -\frac{d}{af},\qquad
\frac{bd-ac}{a^2f}.
\]

The endpoint recurrence audit imports the complete horizon lift, both
infinity carrier recurrences, the metric reconstruction recurrences, and
the scalar Regge--Wheeler divisor ledger.  It also recomputes the outgoing
quotient amplitudes

\[
\pi_x(XI2)=2(16\omega^2-4i\omega-5),\qquad
\pi_x(XI3)=-2i\omega.
\]

The exact shortfall is narrower than the previous endpoint-open status but
remains decisive.  The imported data do not include a
\(\tau\)-differentiated endpoint recurrence with compatible analytic
normalizers.  Hence the actual upper-triangular shear entries in

\[
K_\star=\begin{pmatrix}k_{2,\star}&h_\star\\0&0\end{pmatrix}
\]

are not computed.  Only their admissible type and the covariant law

\[
\dot C=F_I^{-1}\dot\Phi F_H-K_I C+C K_H,\qquad
\widetilde b=b+a(k_{2,H}-k_{2,I})
\]

are certified.  The residue class \([b]\bmod(a)\) is therefore protected,
but this package does not construct \(T_+\), certify scattering, or repair
bounded transport.

The typing is explicit: the metric Einstein column is the
\(\varepsilon\)-copy of the carrier Regge--Wheeler base germ.  It is not a
computed derivative of a moving endpoint exponent.  In particular, no
\(\dot\lambda_H\), \(\dot\lambda_-\), or \(\dot\lambda_+\) is claimed here;
those require the missing analytic \(\tau\)-family.
