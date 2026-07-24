# Covariant Einstein--Maxwell carrier theorem

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

The exact certificate verifies the trace-adjusted carrier

\[
q_{ab}[h]=\delta R_{ab}[h]-\frac16g_{ab}\delta R[h]
\]

and the Ricci-flat factorization

\[
\delta B_{ab}[h]=-\delta G_{ab}[q[h]],\qquad
\nabla^a q_{ab}=\nabla_b q.
\]

The kernel of this carrier map is exactly the linearized Einstein kernel.
If the target Einstein solution is a target diffeomorphism
\(q=\mathcal L_\eta g\), its carrier constraint is
\(\nabla^aF_{ab}=0\), where \(F=2\nabla_{[a}\eta_{b]}\).  A source Weyl
transformation shifts \(\eta\) by a gradient and leaves \(F\) fixed.

An independent Lorentz-signature local-jet contraction verifies

\[
q_{ab}q^{ab}-q^2
=F_{ab}F^{ab}
+4\nabla_a(\eta_b\nabla^b\eta^a-\eta^a\nabla_b\eta^b)
\]

on a Ricci-flat background.  Thus the spin-one carrier action is
\(2\alpha\int F^2=-8\alpha S_{\rm Maxwell}\) modulo boundary terms.  This
explains the sign of the separately certified axial spin-one endpoint norm
without promoting it to a quantum ghost theorem.

The general-\(\ell\) Einstein/Einstein/Maxwell factor pattern is now a
covariant prediction.  The all-row image/lift and extension statement is not
certified beyond the existing axial \(\ell=2\) system.

CLOSE-OUT: DONE — the covariant carrier, Maxwell gauge-vector, source-Weyl
and opposite-sign quadratic-action identities are independently certified.
EVIDENCE: black_hole_programme/phase4/covariant_einstein_maxwell_carrier_v1/certificate.json
