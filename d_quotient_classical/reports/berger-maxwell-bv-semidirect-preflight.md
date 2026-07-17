# Berger Maxwell BV semidirect and apparatus preflight

## Outcome

The minimal Maxwell BV sector is now fixed as ten component rows:
`c_M` (one), `A_mu` (four), `A_plus_mu` (four), and `c_M_plus` (one).
Appending it to the certified 54-row Berger gravity-clock complex gives an
explicit 64-row consumer layout.  This imports the gravity operator by hash;
it does not reconstruct it.

On arbitrary smooth four-dimensional local component functions, exact
symbolic reduction proves

\[
[(\xi,\lambda),(\eta,\mu)]
=([\xi,\eta],\mathcal L_\xi\mu-\mathcal L_\eta\lambda),
\qquad
\delta_{(\xi,\lambda)}A=\mathcal L_\xi A+d\lambda .
\]

The Jacobi residual, action-commutator residual, `d^2` residual, Maxwell
gauge residual of `F`, and covariance residual
`delta F-L_xi F` all vanish coefficientwise.  In four dimensions the Hodge
star on two-forms has Weyl exponent `4-2*2=0`, so `A`, `c_M`, and `F` are
Weyl inert.  This certifies the gauge semidirect sector, not the dynamical
gravity-Maxwell Taylor coupling.

## Exact remaining mixed block

The authoritative `BERGER_SUPPORT_LOCAL_Q2` payload contains the pure
Weyl-plus-clock 54-row operator and no Maxwell rows.  The first actual
gravity-Maxwell dressing therefore still requires three linked exports:

- `q2(h_hat,A)->A_plus`, the metric variation of the Maxwell equation;
- `q2(A,A)->h_hat_plus`, the Maxwell stress source;
- their antifield partners required by BV cyclicity.

Once supplied, the prepared consumer evaluates
`ell2_res(x,y)=pi_cl q2(iota x,iota y)` and retains the homotopy leg needed
at the next arity.  Until then the scientific status is `INPUT_BLOCKED`.

## Relational localization contract

A homogeneous Berger slice has no preferred point.  Local endpoints must
therefore carry explicit reference data.  The contract uses the existing
clock `Theta` plus three local rod scalars `R^I` near compact emitter and
receiver worldtubes, with
`dTheta wedge dR1 wedge dR2 wedge dR3 != 0` on each tube.  It requires a
compact conserved emitter current, a retarded Maxwell Green operator, a
detector window, and a unique no-wrap causal intersection.  None of these
inputs is replaced by the old spatial average.

No new physical mode is introduced by this gauge-sector extension, so it
introduces no negative physical direction.  The sign of the unexported full
mixed dynamical block remains unevaluated.

Machine-readable result:
`d_quotient_classical/certificates/BERGER_MAXWELL_BV_SEMIDIRECT_PREFLIGHT.json`.

## Claim boundary

This is a `LOCAL-ALGEBRAIC` preflight.  It is not a localized or retarded
redshift theorem, not a backreaction result, not the first transferred
gravity-Maxwell interaction, and not a Lorentzian quantum claim.
