# Compact-Cauchy adjoint-kernel classification closeout

## Outcome

The global formal adjoint kernel of the action-derived, right-elliptic
Weyl--Maxwell constraint map on the compactified magnetically supported
Plebański--Hacyan slice is exactly

\[
\ker (D\mathcal C_{\bar z})^*
=\operatorname{span}_{\mathbb R}\{H,P_x,J_1,J_2,J_3\}.
\]

Its real dimension is five.  This closes the `exactly five?` field left open
by `EINSTEIN_MAXWELL_WEYL_COMPACT_CAUCHY_CONSTRAINT_FREDHOLM_GATE_V1`.

## Proof architecture

For the canonical constraint generator \(\mathcal C[\eta]\), with
\(\eta=(N,X,\rho,\sigma,\chi)\), the exact Hamiltonian transpose identity is

\[
 \langle D\mathcal C_{\bar z}\,\delta z,\eta\rangle_\Sigma
 =\Omega_{\bar z}(\delta z,X_{\mathcal C[\eta]}(\bar z)).
\]

The canonical form is nondegenerate before reduction.  Hence the adjoint
kernel consists precisely of gauge parameters whose Hamiltonian vector field
vanishes at the background.  These are the complete canonical KID equations.
Restriction and unique gauge-parameter development on the static analytic
product identify them with the already certified spacetime stabilizers.

The global classification is not inferred from a sample.  The nonzero Weyl
endomorphism forces preservation of the Lorentzian/spherical splitting.  A
compact-sphere divergence integral kills the common homothety and both Weyl
initial jets.  Circle periodicity removes the flat-cylinder boost.  The sphere
Killing operator leaves exactly the coexact \(\ell=1\) triplet.  Each rotation
has the unique based bundle lift

\[
 \iota_J\bar F+d\chi_J=0,\qquad \chi_J=-P n_J.
\]

The harmonic ledger covers every allowed circle momentum and all scalar,
exact-vector and coexact-vector spherical strata.  Its only surviving blocks
are:

| stratum | real dimension | basis |
|---|---:|---|
| \(k=0,\ell=0\) product scalar | 2 | \(H,P_x\) |
| \(k=0,\ell=1\) coexact sphere vector | 3 | \(J_1,J_2,J_3\) |
| all other strata | 0 | none |

The exact obstruction factors are \(k\), \(\lambda/r^2\), and
\((\lambda-2)/r^2\).  Their zero sets prove completeness for all harmonics
and show that no dimension jump occurs at any finite positive sphere radius.
Changing the nonzero magnetic amplitude only changes the compensating
Maxwell parameter.  The conformally flat and decompactified degenerations are
different background/boundary problems and remain fail-closed.

## Constant Maxwell reducibility

The declared Gauss codomain and Maxwell gauge algebra are mean-zero.  A
constant \(U(1)\) parameter is therefore absent.  Restoring it would produce
one formal reducibility with identically zero Hamiltonian vector field, not a
sixth nontrivial Taub charge.  The independent verifier tests this mutation
separately from deleting a true stabilizer.

## Evidence

- Certificate: `bridge/certificates/EINSTEIN_MAXWELL_WEYL_COMPACT_CAUCHY_ADJOINT_KERNEL_CLASSIFICATION_V1.json`
- Producer: `bridge/einstein_sector/einstein_maxwell_weyl_compact_cauchy_adjoint_kernel_classification.py`
- Independent verifier: `bridge/einstein_sector/verify_einstein_maxwell_weyl_compact_cauchy_adjoint_kernel_classification.py`
- Strict schema: `bridge/einstein_sector/schema/einstein-maxwell-weyl-compact-cauchy-adjoint-kernel-classification-v1.schema.json`
- Atlas fragment: `residual_atlas/einstein-weyl-compact-cauchy-adjoint-kernel-fragment-v1.json`
- Tier receipt: `bridge/einstein_sector/receipts/EINSTEIN_MAXWELL_WEYL_COMPACT_CAUCHY_ADJOINT_KERNEL_CLASSIFICATION_V1_TIER_RECEIPT.json`

The method-distinct verifier reconstructs the harmonic zero set and bundle
lift without importing the producer.  Ten unit tests, the strict JSON schema,
and the residual-atlas validator pass.

## Boundary of the result

This result preserves the earlier right-semi-Fredholm conclusion.  It does
not make the rank-30 to rank-14 constraint-plus-gauge map two-sided Fredholm
and does not remove any of its sixteen physical principal-symbol directions.
It does not yet prove the nonlinear Sobolev slice, the AMM momentum-map normal
form, bounded spacetime resonance sufficiency, retarded evolution, scattering,
or a quantum statement.

The activated next gate is the compact-Cauchy AMM semi-Fredholm slice.
