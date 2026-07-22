# Phase 2 Nariai sign mechanism V2

## Outcome

The unit-Nariai Bach factorization supplies an exact invariant mechanism for
the relative sign reversal between its fixed-Lambda Einstein and
complementary branches.  On the action-paired transverse carrier,

\[
G_H^{-1}B_{\rm action}
=\frac12 L_E L_C,
\qquad
L_E=\Box I_9+A,
\qquad
L_C=L_E-\frac23I_9.
\]

The valid Lorentzian sign structure used here is one Nariai static patch,
with (H=\partial_t) timelike only for (-1<r<1).  Both boundaries
(r=\pm1) are retained as Killing-horizon flux components.  No global
timelike Nariai generator and no reflecting or zero-flux boundary condition
is introduced.

The close-out is:

```text
DONE_SCOPED_MECHANISM_THEOREM
```

This is a theorem about opposite exact factor residues.  It is not a theorem
about the absolute sign or positivity of either second-order canonical
energy.

## Frozen imports

The producer imports and checks by SHA-256:

- the action-derived Bach endpoint;
- the cyclic four-row metric Bach BV complex;
- the exact Nariai metric biwave Green homotopy;
- the invariant Einstein-background biwave theorem identifying the Einstein
  and partially-massless factors;
- the repaired rank-310 causal transfer.

The machine-readable certificate contains the paths, result identifiers,
states, and exact hashes.  Drift in any imported byte fails closed.

## Einstein and complementary factors

The curvature-channel projectors in the certified nine-dimensional
trace-free symmetric-tensor fibre have ranks

\[
(4,1,4)
\]

for intrafactor trace-free, relative-trace, and mixed tensors.  The exact
zeroth-order part of the first factor is

\[
A=-2P_{\rm intraTF}+2P_{\rm relative}+0P_{\rm mixed}.
\]

This is the Nariai curvature action (2R_{\mu\alpha\nu\beta}).  Equivalently,
in the certified invariant Einstein-background normalization it is
(2W-\tfrac23I).  Thus (L_E=\Box I+A) is the gauge-fixed fixed-Lambda
linearized Einstein factor.  The second factor is its exact scalar shift by
(-2/3).

On the product-kernel solution carrier, the invariant differential
projectors are

\[
\Pi_E=-\frac32L_C,
\qquad
\Pi_C=\frac32L_E.
\]

Modulo (L_E L_C=0), they obey

\[
\Pi_E+\Pi_C=I,
\quad
\Pi_E^2=\Pi_E,
\quad
\Pi_C^2=\Pi_C,
\quad
\Pi_E\Pi_C=0.
\]

No frequency, mode basis, or representative lift enters these projectors.

## Lee--Wald residue identity

For a formally self-adjoint second-order operator (L), fix the Green
concomitant by

\[
\nabla_a j_L^a(u,v)=\langle u,Lv\rangle-\langle Lu,v\rangle.
\]

For the exact commuting Bach polynomial, one representative is

\[
j_B(u,v)=\frac12\left[
j_{L_E}(u,L_Cv)+j_{L_C}(L_Eu,v)
\right].
\]

Consequently,

\[
j_B\big|_{\ker L_E}=-\frac13j_{L_E},
\qquad
j_B\big|_{\ker L_C}=+\frac13j_{L_C}.
\]

The same multipliers apply to the static-patch slice term and to each of the
two horizon-flux terms in the finite-slab balance.  Their opposition is fixed
by the derivative/residue of the factor polynomial, not by attaching a sign
to an “Einstein” or “additional” label.

This is the requested invariant explanation at fixed Nariai: any later
absolute sign comparison must separately normalize and determine one of the
underlying second-order branch forms.  The present theorem does not assume
that either is positive.

## Claim boundary

Established:

- exact Einstein/complementary factor identification on the transverse
  action-paired carrier;
- exact invariant solution projectors modulo the product equation;
- exact opposite branch multipliers (-1/3) and (+1/3);
- a legitimate static-patch (H)-current comparison with both horizons kept
  in the balance.

Not established:

- absolute canonical-energy signs, inertia, or positivity;
- a globally timelike Nariai generator;
- conservation after throwing away horizon flux;
- a Hadamard state, CPT metric, particle interpretation, or unitarity;
- an open background-family theorem;
- identity with the Phase-1 compact Weyl--Maxwell family.

The exact result is tagged `LOCAL-ALGEBRAIC` and `LORENTZIAN-CAUSAL`.  The
Lorentzian tag refers to the already certified causal metric complex and the
declared static-patch current/flux structure; it does not promote any quantum
claim.

## Verification

The producer replays all imported hashes and exact matrix identities.  A
separate verifier does not import the producer and independently checks:

- factor matrices and their (2/3) gap;
- curvature-projector completeness, idempotence, orthogonality, ranks, and
  reconstruction of (A);
- the solution-projector identities in the polynomial quotient;
- both branch residues;
- the static-patch horizon ledger and all negative claim flags.

Mutation tests reject a changed gap, channel rank, residue sign, input hash,
global-timelike promotion, horizon omission, zero-flux assumption,
Weyl--Maxwell-family relabeling, real-symplectic inertia claim, and positive
energy promotion.

## Next gate

For an absolute sign theorem, choose an explicit horizon state or boundary
prescription and independently establish the sign and nondegeneracy of one
normalized second-order branch canonical form.  For family robustness,
construct and certify a separate open Nariai-type background family before
transporting this fixed-background residue conclusion.

