# C2i: cyclic minimal-model bridge for pure Weyl BV

## Purpose

C2g determines the complete centered cohomology of the **minimal residual
free complex**:

\[
H^4_{\rm residual,min}
=\operatorname{span}\{[W_+^2],[W_-^2]\},
\qquad G=I_2.
\]

C2h proves that Cartan localization survives any compact-degree-equivariant
strong deformation retract.  C2i is the missing instantiation: derive that
retract and the residual charge from the full gauge-fixed pure-Weyl BV/BFV
complex on `R x S3`.

This is a free/classical bridge.  Quantum Diff `x` Weyl anomaly cancellation
is a later and independent requirement.

## Starting complex

Expand the master action around the conformally flat cylinder,

\[
S_{\rm BV}=S_2+S_3+S_4+\cdots,
\qquad q=(S_2,\cdot).
\]

The local field complex must include the metric fluctuation, diffeomorphism
and Weyl ghosts, antifields, the chosen gauge-fixing auxiliaries, antighosts,
and nonminimal doublets.  Split the local gauge ghosts into

\[
\text{fifteen conformal-Killing zero modes}
\oplus
\text{their nonzero-mode complement}.
\]

The finite residual ghosts belong only to the first summand; they must not be
counted again in the local quartet complex.

## Target local cohomology theorem

After the zero-mode split, prove in the relevant free window

\[
H(q)
\cong
\mathcal F(\mathcal W_+\oplus\mathcal W_-),
\]

where each chiral on-shell Weyl module has the exact resolution

\[
0\longrightarrow
\mathcal V(5;\tfrac12,\tfrac12)
\longrightarrow
\mathcal V(4;1,1)
\longrightarrow
\mathcal V(2;2,0)
\longrightarrow
\mathcal W_+
\longrightarrow0,
\]

with the parity-conjugate sequence for `W_-`.  In particular, there must be
no additional local-ghost or nonminimal harmonic classes at physical ghost
number and total compact degree zero.

## Compact-degree-equivariant retract

Choose a stationary, `SO(4)`-invariant auxiliary positive product on each
cylinder-harmonic block.  It is only a Hodge-theoretic tool and is not the
physical Krein pairing.  Define

\[
\Delta_q=qq^\dagger+q^\dagger q,
\qquad
s=q^\dagger\Delta_q^{-1}
\quad\text{on }(\ker\Delta_q)^\perp.
\]

With `p` the harmonic projector and `j` its inclusion,

\[
q s+s q=I-\jmath p,
\qquad p\jmath=I.
\]

Stationarity must give

\[
[D,p]=[D,\jmath]=[D,s]=0.
\]

This makes the contraction a strong deformation retract in the category of
compact-energy-graded complexes.  Consequently the transferred Cartan
identity is the ordinary residual one,

\[
[Q_H,\iota_D^H]_+={\cal L}_D^H,
\]

and every nonzero total compact degree remains contractible.

## Cyclicity obligation

The auxiliary Hodge product does not establish descent of the physical
pairing.  The retract must also be compatible with the BV/Krein bilinear form
in the cyclic-homological-perturbation sense.  At minimum, the transferred
pairing must be well defined and the transferred differential must obey the
required graded adjointness.  This is the input that promotes the residual
class Gram `I2` from a coefficient calculation to the induced free physical
pairing.

Failure of cyclicity would not invalidate the cohomology computation, but it
would invalidate its probability interpretation.

## Transferred residual charge

The leading minimal BFV charge should be

\[
\Omega_{\min}
=c^A\mu_A
-\frac12 f^A{}_{BC}c^Bc^Cb_A
+O(c\,\Phi^3,c^2\Phi,\ldots).
\]

The two displayed terms have already been certified separately:

- the second is the universal `so(4,2)` Chevalley--Eilenberg differential;
- the first is the quadratic Taub moment map acting on the Weyl module.

C2i must derive their coexistence from the same transferred master action and
fix the one-ghost/two-matter normalization to

\[
M_{\rm Taub}=-\frac{\sqrt2}{4\pi}J K^-.
\]

The transferred master equation must reproduce

\[
\{\mu_A,\mu_B\}=f_{AB}{}^C\mu_C
\]

and moment-map equivariance.  Because the Weyl module is multiplicity-free,
the all-level generator theorem and the two direct curvature seeds should
fix this arity uniquely up to the already chosen overall normalization.

## Spectral-sequence criterion

After the stabilizer modes are separated, filter the total complex by local
ghost number.  Its first pages are schematically

\[
E_1=H(q),
\qquad
E_2=H(Q_{\rm residual},H(q)).
\]

If local cohomology is concentrated in the physical row and the transferred
charge at the relevant arity is the strict residual charge above, no higher
differential can enter or leave the two centered classes.  Then

\[
H^4_{\rm free}
=\operatorname{span}\{[W_+^2],[W_-^2]\},
\qquad G=I_2,
\]

up to a possible local/topological identification of the parity-odd
Pontryagin combination.

## Acceptance criteria

C2i is closed only when all of the following are available.

1. An explicit pure-Weyl local BV/BFV field and ghost complex in a stationary
   cylinder gauge.
2. A non-overlapping split of the fifteen conformal-Killing zero modes.
3. The harmonic-kernel calculation giving exactly the `W_+ + W_-` module and
   no relevant extra cohomology.
4. Exact or theorem-level verification of the graded strong deformation
   retract and its `D` equivariance.
5. Cyclic compatibility with the BV/Krein pairing.
6. Derivation of the residual ghost differential and Taub coupling from the
   transferred master action, including the `-4` ghost-vacuum shift.
7. A spectral-sequence argument excluding higher differentials in the
   centered physical row.

Only after these free/classical items close should the programme test quantum
nilpotency.  The finite conformal algebra has no nontrivial ordinary central
two-cocycle, but that does not remove the local Weyl anomaly.

## Physical boundary of the conclusion

If C2i closes, the compact theory has no one-particle global physical states
in this polarization and no higher-weight absolute tower.  Its surviving
free candidates are action-density-like conformal composites.  This is not
an ordinary ghost-free graviton Fock space.

The conclusion also depends on treating cylinder `D` as residual gauge.  In
noncompact scattering or with boundaries, `D` can carry a surface charge and
need not be BRST exact; the Cartan contraction then does not remove its
charged sectors.
