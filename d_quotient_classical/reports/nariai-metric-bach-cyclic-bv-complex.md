# Nariai metric Bach cyclic BV complex

The action-derived endpoint closes as the four-row complex

\[
H_0\xrightarrow{K}H_1\xrightarrow{B_{\rm action}}H_1^*
\xrightarrow{K^\sharp}H_0^*.
\]

The field/equation pairing is the evaluation matrix (I_9): the tensor Gram
has already converted the Bach tensor into endpoint covector coordinates and
must not be applied a second time.  The ghost/identity pairing is the
Lorentzian matrix \(\operatorname{diag}(-1,1,1,1)\).

The exact coefficient identities give

\[
B_{\rm action}K=0,
\qquad
K^\sharp B_{\rm action}=0.
\]

Together with Hessian symmetry of the Weyl-squared action, these prove the
four-row differential is nilpotent and odd cyclic.  The generic
post-normal-order PBW adjoint is deliberately not used as authority.

## Formal-adjoint proof

Let (S[g]) be the Weyl-squared action in the normalization recorded by the
endpoint certificate.  Its first variation is the evaluation pairing of the
Bach tensor with a metric variation, modulo a boundary term.  Unit Nariai is
Bach-flat.  Therefore, for compactly supported trace-free variations (u,v),
commutation of the two ordinary variation parameters gives

\[
0=(\delta_u\delta_v-\delta_v\delta_u)S[\bar g]
  =\langle u,B_{\rm action}v\rangle
   -\langle B_{\rm action}u,v\rangle .
\]

The boundary term vanishes by compact support.  This proves the required
formal self-adjointness in the action pairing independently of any chosen PBW
normal-order implementation.

## Boundary

This certificate derives the endpoint field/equation and ghost/identity pairings from the action-coordinate types, derives Ksharp from K, and verifies the exact four-row metric Bach BV complex on unit Nariai: B K=0, Ksharp B=0, Q squared zero modulo those coefficient identities, and odd cyclicity. Formal self-adjointness of B is the second-variation theorem for the Weyl-squared action at the Bach-flat background; the known generic post-normal-order PBW adjoint path is not used as authority. This does not yet construct a chain equivalence to the parent curvature-incidence cylinder, the relative equation/identity-row cone or SDR, any Green homotopy, an open background class, nonlinear interactions, or a quantum claim.
