# Compact-cylinder linearization-stability audit (blocking P4 interpretation)

## Status

The `E`, `A`, and `L` tower states used by the conformal harmonic machinery
are exact one-particle oscillator representatives of the linearized equations.
They are **not yet certified as genuine full BRST-cohomology asymptotic
states on compact `S^3`** after global conformal/Taub constraints are imposed.
Accordingly, the energy-six `AA <-> EL` block is a provisional oscillator
block, not yet a physical transition block.

This distinction became unavoidable in the t-channel current calculation.
The scalar block has `ell=omega=1`, zero covariant Hessian, and the exact
conformal-Killing reducibilities

\[
G_+ (i,1,1)^T=0,\qquad G_-(-i,1,1)^T=0.
\]

Writing

\[
p_+=(3,i,1)^T,\qquad p_-=(3,-i,1)^T,
\]

for its transverse quotient representatives, their quotient classes are the
frequency derivatives of the reducible gauge transformations:

\[
\partial_\omega G_+\,r_+-2p_+
=B_+(-2i,1)^T,
\]

\[
\partial_\omega G_-\,r_--2p_-
=B_-(2i,1)^T.
\]

Thus this is a generalized conformal-Killing zero mode, not an ordinary
propagator channel.  The raw chiral cubic slice currents are nonzero.  The
action-normalized operator bridge is now exact: with
`k_s=2 n_(mu xi_(s)nu)=-i s partial_omega(G_s r_s)`, the third action
variation gives twice the mixed Euler/Bach charge, while both ordinary-gauge
probes vanish.  Hence `Q_s=-i s C_s`.  The selected mixed components are

\[
Q_{\xi_-}[E_+^\dagger,A_+]=-{\sqrt5\over5\pi},\qquad
Q_{\xi_+}[L_-^\dagger,A_-]={\sqrt{10}\over5\pi}.
\]

This closes the direct Taub interpretation for those two components.  C2b
then uses their multiplicity-one `(1/2,1/2)` representations to reconstruct
all four proper-conformal magnetic components in the adjacent `A -> E` and
`L -> A` blocks.  The exact reduced coefficients are

\[
{\cal R}_{AE}=-{\sqrt{10}\over5\pi},\qquad
{\cal R}_{LA}={\sqrt2\over2\pi}.
\]

The reconstructed kernels obey all abstract left/right ladder identities,
lower compact energy by one, and reproduce the direct curvature seed,
reverse, and parity-seed entries.  The reverse statement is an ordinary
coefficient-kernel dagger, not yet a physical-adjoint theorem on the unknown
globally reduced pairing.  They remain mixed entries: this does not
compute `Q[A_3,A_3]`, `Q[E,L]`, the other mode-tower reduced elements, or the
global charge of a complete parity-projected energy-six state.  See
`notes/conformal-taub-bridge.md`, `notes/conformal-taub-charge.md`, and
`notes/conformal-taub-multiplets.md`, with executable certificates
`symbolic/verify_conformal_taub_charge.py` and
`symbolic/verify_conformal_taub_multiplets.py`.

Independent parity-partner probes give the same nonzero current rather than
the opposite sign, so the conventional parity projection does not remove the
constraint.  Independently reversed external waves give the exact conjugate
current with the two frequency sides exchanged.  The result is therefore not
an orientation or adjoint-normalization artifact.

## Required audit

Before interpreting any P4 contact or exchange coefficient as a physical
effective Hamiltonian, establish all of the following.

1. Construct the complete gauge-fixed BRST complex on `R x S^3`, including
   zero modes, reducibility ghosts, auxiliary fields, and global conformal
   generators.
2. Extend the two now-complete proper-CK magnetic multiplets to every
   required mode tower and multiplicity sector, and construct the seven
   compact-energy-preserving Killing-charge kernels.
3. Determine whether individual `E`, `A`, and `L` oscillator excitations
   descend to BRST cohomology or require charge-neutral, dressed, or conformal
   singlet combinations.
4. Evaluate the global conformal charges of `AA`, `EA`, and `EL`, including
   their parity projections and all degenerate energy-six partners.
5. Decide how the nonzero selected Taub components act on the complete
   parity-projected states and whether they are:

   - excluded because the proposed external block violates a global charge;
   - cancelled by the required dressing/constraint sector;
   - absorbed into a larger degenerate conformal multiplet; or
   - a genuine obstruction after full cohomology reduction.

6. Only after this audit, construct the reduced pairing `J_6`, the complete
   shell projector, and the second-order effective Hamiltonian.

## Fail-closed interpretation

Until those items close, the exact contact, Hessian, cubic-current, and
selected Taub-charge data
are useful local/covariant certificates and regression rails.  They do not
establish a physical energy-six amplitude, pseudo-unitarity violation, or
metric-deformation obstruction.  In particular, `kappa_t=0` is never divided
through.  The t current seeds two exactly reconstructed proper-conformal
mixed Taub multiplets, but the remaining reduced blocks, seven Killing
charges, full quadratic moment map, and global-BRST physical-state kernel
remain open.
