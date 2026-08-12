# BT scalar dressed-source free normal form

Certificate:
`REVERSE_PHYSICS_BT_SCALAR_DRESSED_SOURCE_FREE_NORMAL_FORM_V1`.

Dependencies: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`. Lifecycle:
`COEFFICIENT_COMPUTED`.

## Result

The formally affiliated positive scalar source has an explicit leading
normal form on the compact finite-mode covariant detector core.  It is a
state in the scalar Jordan oscillators, including the pulled squeezed vacuum;
it is not merely the symbol \(R_t^\dagger u_0\).

For a nonzero mode of energy \(E\), the covariant leading Appendix-C map and
its adjoint give

\[
 d_\Upsilon^\dagger
 =\frac{Z^{-1}a_1^\dagger}{\sqrt{2E}},
\]

\[
 d_\Omega^\dagger
 =\frac{Z}{4E^2\sqrt{2E}}
 \left(a_2^\dagger-2iEt\,a_1^\dagger
       +e^{-2iEt}a_1(-p)\right).
\]

Here \(d_X^\dagger=R_t^\dagger c_X^\dagger R_t\), where \(c_X\) denotes the
normalized BT cross oscillator.  The scalar vacuum is not bare:

\[
 |0_{\phi;t}\rangle
 =R_t^\dagger|0_{\rm BT}\rangle
 =e^{-\alpha_t(Q_{\rm cov})}|0_\phi\rangle.
\]

It is annihilated by both pulled annihilators.  The last term in
\(d_\Omega^\dagger\) therefore drops only when the creator acts on this
dressed vacuum:

\[
 d_\Omega^\dagger|0_{\phi;t}\rangle
 =\frac{Z(a_2^\dagger-2iEt\,a_1^\dagger)}
 {4E^2\sqrt{2E}}|0_{\phi;t}\rangle.
\]

For the three distinct incoming detector modes, the explicit leading source
is

\[
\begin{split}
 \psi_{\phi,+}^{(0)}=\frac1{\sqrt2}\bigg[&
 Z^{-3}\prod_{j=0}^2\frac{a_{1j}^\dagger}{\sqrt{2E_j}}\\
 &+Z^3\prod_{j=0}^2
 \frac{a_{2j}^\dagger-2iE_jt\,a_{1j}^\dagger}
 {4E_j^2\sqrt{2E_j}}
 \bigg]|0_{\phi;t}\rangle.
\end{split}
\]

This makes the two scalar vacuum-orbit branches explicit rather than hiding
them in an inverse symbol.

## Exact normalization

The repaired scalar Jordan commutator is

\[
 [a_1,a_2^\dagger]=(2E)^3.
\]

The one-mode pulled cross commutator is therefore

\[
 \frac{(2E)^3}
 {\sqrt{2E}\,4E^2\sqrt{2E}}=1.
\]

For three distinct modes, each pure-species branch is Krein-null while both
cross pairings equal the product \(1^3=1\).  Consequently

\[
 \langle\psi_{\phi,+}^{(0)},
          \psi_{\phi,+}^{(0)}\rangle_K
 =\frac12(1+1)=1.
\]

The pulled ghost parity exchanges the two branches, so their symmetric sum
is even.  The state has Laurent support \(\{Z^{-3},Z^3\}\), and its projector
has support \(\{Z^{-6},1,Z^6\}\), agreeing with the preceding abstract
affiliation theorem.

## Why the free normal form is enough at this order

Write the exact dressed source and six-point transition as

\[
 \psi_\phi=\psi_0+\lambda\psi_1+O(\lambda^2),
 \qquad
 A=\lambda^4A_4+\lambda^5A_5+O(\lambda^6).
\]

Then

\[
 A\psi_\phi
 =\lambda^4A_4\psi_0+O(\lambda^5),
\]

and hence

\[
 \operatorname{Prob}(A\psi_\phi)
 =\lambda^8\langle A_4\psi_0,A_4\psi_0\rangle_K
 +O(\lambda^9).
\]

Unknown \(O(\lambda)\) terms in the nonlinear source first enter the
probability at order \(\lambda^9\).  They cannot change the already certified
leading rate

\[
 \Gamma_{\phi,+,\Xi}
 =\frac{\lambda^8}
 {2048\pi^4\kappa^4L_xL_y^2L_z^2}.
\]

Thus the leading physical-scalar probability jet no longer depends on an
unexpanded source symbol.

## Carrier boundary

This source exists on the finite Laurent-polynomial Gaussian image core used
by the declared finite-volume detector.  It does not extend as a vector in
the ordinary massless Fock--Krein thermodynamic topology: the Appendix-C
squeezed vacuum has a certified infrared positive-norm divergence there.
That obstruction is retained, not bypassed by calling the finite core a
global Fock space.

The next constructive question is whether the three point modes can be
replaced by compact wave packets supported away from \(p=0\), with all
creator integrals closable on the same Gaussian image core and the pulled
effect continuous in the packet topology.  Removal of the infrared cutoff
would still require the inequivalent weighted representation or a local
algebraic state.

This result does not construct the standard shift-invariant
\(P_\chi^{(\phi)}\), general Eq. (19), a convergent nonlinear \(R_t\), global
shell gluing, all-time scattering, loops, gravity/BRST transfer, or anything
`LORENTZIAN-CAUSAL`.

## Verification receipt

All scientific commands run sequentially under `ulimit -v 500000`.

- The exact producer passes 23/23 checks with peak resident memory 65,124 KB.
- The independent fraction/polynomial verifier passes 19/19 checks using
  three unrelated exact energy fixtures, below 24 MB peak resident memory.
- Eight tests include six decisive mutations covering the dressed vacuum,
  orbit branches, annihilator domain, perturbative order, ordinary-Fock
  boundary, and general Eq. (19).
- The affected eight-producer chain passes 16/16, 19/19, 27/27, 26/26,
  31/31, 32/32, 38/38 and 23/23 checks.  Its independent verifiers pass
  14/14, 21/21, 26/26, 23/23, 24/24, 24/24, 29/29 and 19/19 checks.  The
  combined 60-test chain passes in 1.13 seconds with peak resident memory
  78,296 KB.
- Papers 5 and 6 rebuild twice with no new box warning.  Tier 3 is not needed
  because no shared core, freeze, release, QME state or Lorentzian claim
  changes.

Commands:

```text
ulimit -v 500000; python3 reverse_physics/bt_scalar_dressed_source_free_normal_form.py --write --check
ulimit -v 500000; python3 reverse_physics/verify_bt_scalar_dressed_source_free_normal_form.py
ulimit -v 500000; python3 -m unittest -v reverse_physics.tests.test_bt_scalar_dressed_source_free_normal_form
```

CLOSE-OUT: DONE -- the leading dressed scalar source is explicit and
normalized on the finite covariant detector core, and its unknown nonlinear
corrections cannot affect the \(\lambda^8\) rate; the continuum ordinary-Fock
source and general Eq. (19) remain open.

EVIDENCE:
`reverse_physics/certificates/REVERSE_PHYSICS_BT_SCALAR_DRESSED_SOURCE_FREE_NORMAL_FORM_V1.json`
