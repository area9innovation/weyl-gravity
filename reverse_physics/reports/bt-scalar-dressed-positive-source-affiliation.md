# BT scalar dressed positive-source affiliation

Certificate:
`REVERSE_PHYSICS_BT_SCALAR_DRESSED_POSITIVE_SOURCE_AFFILIATION_V1`.

Dependencies: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`. Lifecycle:
`COEFFICIENT_COMPUTED`.

## Result

The positive BT source constructed for the six-point detector has a genuine
perfect-square scalar preimage on the finite covariant detector ideal.  It is
not the standard shift-invariant characteristic projector.  It is an
explicitly \(R_t\)-dressed, shift-breaking scalar projector.

Let

\[
 u_0=\frac{|\Upsilon\Upsilon\Upsilon\rangle
              +|\Omega\Omega\Omega\rangle}{\sqrt2},
 \qquad P_u=|u_0\rangle\langle u_0|_K.
\]

The certified perturbative coisometry theorem gives, coefficientwise in the
formal coupling,

\[
 R_t^\dagger R_t=R_tR_t^\dagger=1.
\]

Therefore

\[
 \psi_{\phi,+}=R_t^\dagger u_0,
 \qquad P_{\phi,+}=R_t^\dagger P_uR_t
\]

obey

\[
 \langle\psi_{\phi,+},\psi_{\phi,+}\rangle_K=1,
 \qquad P_{\phi,+}^2=P_{\phi,+}=P_{\phi,+}^\dagger,
\]

and the source-affiliation square closes exactly:

\[
 \boxed{R_tP_{\phi,+}R_t^\dagger=P_u.}
\]

This is not an arbitrary-isometry construction.  The theorem uses the public
formal \(R_t\) whose two-sidedness was derived from its pulled oscillator CCR.
The rational Krein-unitary matrix in the producer is only a nontrivial replay
of the universal algebraic identities and is explicitly not identified with
\(R_t\).

## Why the source must break shift charge

On a three-particle species string \(x\in\{0,\ldots,7\}\), the boost charge is

\[
 q(x)=2\operatorname{popcount}(x)-3.
\]

The spectrum is

\[
 -3,-1,-1,+1,-1,+1,+1,+3.
\]

There is no zero-charge three-particle state.  Moreover, the cross-Krein
metric sends \(|x\rangle\) to \(|7-x\rangle\), whose charge is \(-q(x)\).
Consequently the metric restricted to every fixed-charge space vanishes:

\[
 \eta|_{V_q\times V_q}=0.
\]

If a nonzero subspace is charge invariant, it contains a nonzero charge
eigenvector.  That vector is null.  Hence

\[
 \boxed{\text{no nonzero charge-invariant three-particle range is positive}.}
\]

This is the exact reason the positive-source route cannot secretly be the
standard shift-invariant Eq. (18) projector.  A positive odd-particle source
must break the boost/shift charge.

For the declared source, the state has charge support \(\{-3,+3\}\).  Its
Krein projector has operator-charge support

\[
 \operatorname{supp}_q(P_u)=\{-6,0,+6\}.
\]

The exact Eq. (16) charge intertwiner therefore gives the scalar source
Laurent orbit support

\[
 \operatorname{supp}_Z(P_{\phi,+})=\{Z^{-6},1,Z^6\},
 \qquad Z=e^{\lambda\phi_0}.
\]

Both orbit branches are compulsory.  This construction remains regular on
the covariant Laurent--Fock ideal: it does not invert
\(F=\Box\phi+\lambda(\partial\phi)^2\), adjoin \(\log F\), or assert a
same-chart local hidden-parity automorphism.  It evades that obstruction by
preparing a charged superposition, not by contradicting it.

## Transfer of the detector effect

Let \(U_+\) be the positive four-frame and let

\[
 G=R_+^TR_+
\]

be the certified fixed-shell effect.  On the full target carrier define

\[
 E_{\rm click}^{\rm BT}
 =\zeta U_+GU_+^\sharp,
 \qquad
 E_{\rm no}^{\rm BT}
 =P_+-E_{\rm click}^{\rm BT}.
\]

Pull them to the scalar detector ideal:

\[
 E_{\rm click}^{\phi}
 =R_t^\dagger E_{\rm click}^{\rm BT}R_t,
 \qquad
 E_{\rm no}^{\phi}
 =R_t^\dagger E_{\rm no}^{\rm BT}R_t.
\]

They are complete relative to the pulled positive plane,

\[
 E_{\rm click}^{\phi}+E_{\rm no}^{\phi}
 =R_t^\dagger P_+R_t.
\]

On the finite detector ideal, cyclicity of the trace and two-sidedness of
\(R_t\) give

\[
 \operatorname{tr}(P_{\phi,+}E_a^\phi)
 =\operatorname{tr}(P_uE_a^{\rm BT}),
 \qquad a\in\{\mathrm{click},\mathrm{no}\}.
\]

Thus the scalar probabilities are inherited without fitting:

\[
 q_{\rm click}=\frac\zeta{16},
 \qquad q_{\rm no}=1-\frac\zeta{16},
\]

where

\[
 0\leq\zeta\leq16-8\sqrt3.
\]

The leading scalar click rate is therefore

\[
 \boxed{\Gamma_{\phi,+,\Xi}
 =\frac{\lambda^8}
 {2048\pi^4\kappa^4L_xL_y^2L_z^2}}.
\]

The BT cut supplies the transition coefficient, pseudo-unitarity supplies its
leading complement, and the formal quantum embedding transfers both effects
to the scalar projector.  On the declared periodic finite-volume cell the
spatial boundary term in the public Hamiltonian relation integrates away.

## What has and has not been proved

This is a physical-scalar result in the following scoped sense:

- the source is an idempotent, Krein-self-adjoint scalar projector with a
  positive normalized range;
- it is affiliated with the public BT source by the certified formal
  two-sided \(R_t\), not by a fitted isometry;
- the interaction coefficient and detector normalization are inherited from
  the complete six-point tree and finite-time Hamiltonian cut; and
- the finite-rank generalized-Born trace is positive and normalized on the
  declared interval.

It is a coupling-dressed, finite-time, vacuum-orbit-sensitive source.  It is
not the shift-invariant \(P_\chi^{(\phi)}\) of Eq. (18).  Therefore it does not
repair the known ghost-parity failure of the public pushforward of that
projector and does not prove general Eq. (19).

It also does not establish convergence of \(R_t\), a global dense domain,
point-cell-independent wave-packet preparation, ten-shell gluing, an all-time
Møller/LSZ/\(S\) operator, loops, gravity/BRST transfer, or anything
`LORENTZIAN-CAUSAL`.

## Verification receipt

All scientific commands run sequentially under `ulimit -v 500000` with
Python 3.12.13.

- The exact producer passes 38/38 checks with peak resident memory below
  70 MB.
- The independent fraction-only verifier passes 29/29 checks and reconstructs
  the charge theorem, rational Krein pullback, effect and trace without
  importing the producer; peak resident memory is below 24 MB.
- Nine tests include seven decisive claim mutations: charge support, loss of
  one Laurent branch, rate, standard-projector promotion, general-Eq.-(19)
  promotion, all-time promotion, and misuse of the rational fixture as the
  public \(R_t\).
- The affected seven-producer chain passes 16/16, 19/19, 27/27, 26/26,
  31/31, 32/32 and 38/38 checks.  Its independent verifiers pass 14/14,
  21/21, 26/26, 23/23, 24/24, 24/24 and 29/29 checks.  The combined 52-test
  chain passes in 2.31 seconds with peak resident memory 78,476 KB.
- Papers 5 and 6 are rebuilt twice before commit.
- Tier 3 is unnecessary because there is no shared-core change, freeze,
  release, QME lifecycle promotion, or Lorentzian claim.

Commands:

```text
ulimit -v 500000; python3 reverse_physics/bt_scalar_dressed_positive_source_affiliation.py --write --check
ulimit -v 500000; python3 reverse_physics/verify_bt_scalar_dressed_positive_source_affiliation.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_scalar_dressed_positive_source_affiliation
```

CLOSE-OUT: DONE -- a positive normalized BT source and its click/no-click
effect have an exact formal pullback to a dressed perfect-square scalar
projector; the standard shift-invariant projector and general Eq. (19) remain
open.

EVIDENCE:
`reverse_physics/certificates/REVERSE_PHYSICS_BT_SCALAR_DRESSED_POSITIVE_SOURCE_AFFILIATION_V1.json`
