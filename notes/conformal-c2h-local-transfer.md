# C2h: Cartan localization through the pure-Weyl BV transfer

## Residual theorem

Let `d` be the absolute residual `SO(4,2)` BRST differential and let
`i_D` denote contraction with the compact-time generator.  On the total
compact-degree decomposition

\[
C=\bigoplus_\delta C_\delta,
\qquad {\cal L}_D|_{C_\delta}=\delta I,
\]

Cartan's identity gives

\[
d\iota_D+\iota_Dd={\cal L}_D.
\]

Thus every nonzero-degree component is contractible, with

\[
h_\delta=\frac{\iota_D}{\delta},
\qquad dh_\delta+h_\delta d=I
\quad(\delta\ne0).
\]

Equivalently,

\[
H^\bullet(C,d)\simeq H^\bullet(C_{\delta=0},d).
\]

The matter-weight-six window built over the residual ghost vacuum has
`delta=6-4=2`, so it is contractible before any matrix-rank calculation.
Matter weight four is the unique resonance built on the selected `-4`
residual ghost vacuum; the complete centered inventory also includes lower
matter weights with other ghost dressings.

## Transfer lemma

The remaining issue is not the residual algebra.  It is whether this Cartan
localization survives elimination of the nonzero local Diff `x` Weyl BV
modes.

Let

\[
(H,0)\mathrel{\mathop{\rightleftarrows}^{\jmath}_{p}}(C,q),
\qquad
\jmath p=I-qs-sq,
\qquad p\jmath=I,
\]

be a contraction of the local BRST complex onto its local cohomology.  Let
`Delta` contain the residual zero-mode differential and all mixed terms, so
that

\[
Q=q+\Delta,
\qquad Q^2=0.
\]

When the homological-perturbation series exists, the transferred data are

\[
\begin{aligned}
I&=(I+s\Delta)^{-1}\jmath,\\
P&=p(I+\Delta s)^{-1},\\
Q_H&=p\Delta(I+s\Delta)^{-1}\jmath.
\end{aligned}
\]

Suppose the full complex carries a Cartan operation

\[
[Q,\iota_D]_+={\cal L}_D.
\]

Define the transferred operators

\[
\iota_D^H=P\iota_DI,
\qquad
{\cal L}_D^H=P{\cal L}_DI.
\]

Because `I` and `P` are chain maps,

\[
\begin{aligned}
[Q_H,\iota_D^H]_+
&=P[Q,\iota_D]_+I\\
&=P{\cal L}_DI\\
&={\cal L}_D^H.
\end{aligned}
\]

This identity is formal and does not depend on a choice of representatives.
To retain the *same compact-degree grading*, rather than merely some
transferred endomorphism, impose the stronger equivariance conditions

Writing `mathcal L_D^C` for the operator before reduction and
`mathcal L_D^H` for its action on local cohomology, the precise conditions
are the intertwining relations

\[
p\mathcal L_D^C=\mathcal L_D^H p,
\qquad
\mathcal L_D^C\jmath=\jmath\mathcal L_D^H,
\qquad
[\mathcal L_D^C,s]=0,
\]

together with

\[
[\mathcal L_D^C,q]=[\mathcal L_D^C,\Delta]=0.
\]

Then every homological-perturbation term preserves `delta`, and
`L_D^H` is the expected compact-degree operator on the transferred complex.
On every subspace where it is invertible,

\[
h_H=\iota_D^H({\cal L}_D^H)^{-1}
\]

is a contracting homotopy.  This is the precise C2h mechanism.

The plus signs in the perturbation inverses follow from the convention
`j p=I-q s-s q` used above. With the opposite homotopy convention one obtains
the familiar minus-sign formulas; mixing the two conventions produces maps
that fail the chain-map identities.

## Exact nontrivial transfer fixture

`symbolic/verify_conformal_cartan_transfer.py` tests the lemma without putting
the transferred answer into the initial inclusion. Its residual algebra is

\[
[D,K]=K.
\]

The local complex contains one surviving class `h` and a contractible pair

\[
a\mathop{\longrightarrow}^{q}u,
\]

with residual action `K h=u`. Thus `K` maps the retained representative into
an exact local state, and homological perturbation changes the inclusion by a
nonzero correction. On the resulting twelve-dimensional total complex, the
executable independently verifies:

- the local strong-deformation-retract identities;
- strict residual closure and covariance with the local differential;
- nilpotency and the unreduced Cartan identity;
- nontrivial correction of the HPL inclusion;
- the corrected chain-map and retraction identities;
- equality of the transfer with the strict residual CE differential;
- unchanged transfer of elementary `D`-ghost contraction; and
- the reduced Cartan identity with the expected compact grading.

This proves the formal algebraic mechanism under the hypotheses above. It
does not instantiate those hypotheses for the pure-Weyl local BV complex.

Two distinctions matter for that instantiation. First, the formal transfer is
always

\[
\iota_D^H=P\iota_DI.
\]

Identifying this with elementary differentiation by the residual `D` ghost
requires the zero-mode split and the local retract to be ghost-factorized,
or else requires a separate equality check. If it fails, localization may
still hold with a corrected contraction, but the C2g residual formulas cannot
be imported unchanged.

Second, compact-degree equivariance transfers the Cartan theorem but does not
by itself prove that `Q_H` is the strict residual CE differential. A residual
action closing only up to `q`-homotopy generally transfers to an `L_infinity`
module with higher-ghost terms. Identifying `Q_H` with the C2g charge requires
a strict residual-equivariant retract or an explicit proof that those higher
operations vanish in the relevant window.

## Modewise equivariant Hodge construction

The graded retract need not be assembled quartet by quartet.  After the
fifteen conformal-Killing zero modes have been split off, choose on each
cylinder-harmonic block an auxiliary positive-definite inner product that is
invariant under cylinder time translations and `SO(4)`.  This is a
computational Hodge product, not the physical Krein form.  If `q^dagger` is
the corresponding adjoint, set

\[
\Delta_q=qq^\dagger+q^\dagger q,
\qquad
G=\Delta_q^{-1}\quad\hbox{on }(\ker\Delta_q)^\perp,
\qquad
s=q^\dagger G.
\]

With `p` the harmonic projector and `j` its inclusion, Hodge decomposition
gives

\[
qs+sq=I-\jmath p.
\]

Stationarity gives

\[
[D,q]=[D,q^\dagger]=[D,\Delta_q]=[D,G]=[D,p]=[D,s]=0.
\]

Thus the desired local contraction is a strong deformation retract in the
category of compact-energy-graded complexes.  The nontrivial content is the
identification of `ker Delta_q`: it must be precisely the two-chirality
on-shell Weyl module plus the separated stabilizer-ghost sector, with no
additional local-ghost or nonminimal harmonic classes in the relevant
degrees.

The positive auxiliary product proves equivariance but is not itself the
physical BV/Krein adjoint.  Cyclicity nevertheless need not be a second
spectral calculation once the local kernel and its nondegenerate induced
form are known.  In every finite compact-degree block, a cyclic retract can
be constructed by a Witt decomposition of the exact/contractible sector;
`verify_conformal_cyclic_hpl.py` then proves that homological perturbation is
an exact isometry.  The raw cross-energy implementation now constructs the
needed `D x SO(4)`-graded cyclic form, checks all adjacent noncompact
contravariance relations, and verifies the dressed isometry.  Its
representative retract is homotopy-equivariant rather than strictly
equivariant, but the complete centered HPL correction test gives the strict
CE differential.  The remaining obligation is to identify this certified
algebraic construction with the complete chosen field-theory BV domain.

## Pure-Weyl obligations and implementation status

The algebraic certificate suite now constructs the following objects on
`R x S^3`; the same inventory still has to be justified as complete for the
chosen field-theory BV domain.

1. **Local BV differential.**  Include the metric, diffeomorphism ghost,
   Weyl ghost, antifields, gauge-fixing auxiliaries, antighosts, and the
   nonminimal doublets used by the selected cylinder gauge.
2. **Zero-mode split.**  Decompose the local diffeomorphism/Weyl ghost into
   the fifteen conformal-Killing reducibility modes plus an orthogonal
   nonzero-mode complement.  The finite ghosts must not be counted twice.
3. **Local contraction.**  Exhibit `p`, `j`, and `s` on the nonzero-mode
   quartet/contractible sectors.  Their kernels and domains must include the
   treatment of the compact zero modes.  Use the finite-block cyclic
   construction for the physical BV/Krein form, while preserving compact
   degree. Prove ghost factorization or compute the corrected transferred
   `iota_D^H`.
4. **Compact-degree equivariance.**  Verify the intertwining and commutator
   identities above.  A
   stationary harmonic gauge and spectral Green operator are natural, but
   equivariance must be checked rather than inferred.
5. **Transferred residual charge.**  Show that `Q_H` is the residual charge
   used in the C2g calculation, including its ghost normal-ordering shift
   `D_gh=-4` and any mixed terms required by the BV master equation. Exclude
   or explicitly retain higher transferred ghost operations.
6. **Local cohomology concentration.**  Prove, in the relevant free window,
   that the local cohomology is represented by the gauge-reduced `E/A/L`
   oscillator Fock module and has no extra nonminimal or local-ghost classes
   capable of contributing at total degree zero.
7. **Quantum condition.**  Separate the classical transfer theorem from the
   anomaly question.  Quantum nilpotency requires cancellation or control of
   the Diff `x` Weyl anomaly and normal-ordering shifts.

The first six items are now instantiated in the finite algebraic cylinder
model, including the explicit closed-`S3` residual BFV choice and all-energy
Taub normalization.  Their promotion to the complete field-theoretic BV
domain is the remaining classical identification.  The last item is a
genuinely quantum consistency condition.

## Finite centered inventory

In the minimal residual exterior algebra there are only four ghosts of
degree `-1`.  At the physical centered ghost number four, the most negative
ghost degree is therefore `-4`.  Total degree zero implies

\[
D_{\rm matter}\le4.
\]

The free pure-Weyl matter spectrum begins at weight two, so only the vacuum,
one-particle, and two-particle sectors through matter weight four can occur.
The residual calculations give

\[
H^4_{\delta=0,N=1}=0,
\qquad
H^4_{\delta=0,N=2}
=\operatorname{span}\{[W_+^2],[W_-^2]\}.
\]

For the vacuum coefficient module, standard semisimple Lie-algebra
cohomology gives

\[
H^\bullet(\mathfrak{so}(4,2);\mathbb C)
\simeq\Lambda(u_3,u_5,u_7),
\qquad H^4(\mathfrak{so}(4,2);\mathbb C)=0.
\]

The complete minimal free residual result is therefore

\[
H^4_{\delta=0}
=\operatorname{span}\{[W_+^2],[W_-^2]\},
\qquad G=I_2.
\]

Any extra local/nonminimal fields must either be removed by the equivariant
local contraction or explicitly included in this centered inventory.

## C2i: cyclic minimal-model bridge

Expanding the pure-Weyl master action around the conformally flat cylinder,

\[
S_{\rm BV}=S_2+S_3+S_4+\cdots,
\qquad q=(S_2,\cdot),
\]

the C2h contraction transfers the BV/BFV structure to `H(q)`.  The expected
leading residual charge is

\[
\Omega_{\min}
=c^A\mu_A-\frac12 f^A{}_{BC}c^Bc^Cb_A+\cdots.
\]

Here the first term is the transferred one-ghost/two-matter Taub moment map,
and the second is the universal residual ghost differential already used in
the absolute complex.  The master equation then contains the moment-map
equivariance and conformal Jacobi identities already certified on the
residual side.

The implementation has established the following three facts in the finite
algebraic cylinder category rather than by computing another matter shell:

1. `H(q)` is the Fock space on the two chiral on-shell Weyl modules after the
   fifteen stabilizer modes are separated, with no additional relevant
   local or nonminimal cohomology.
2. A retract can be chosen simultaneously compact-degree equivariant and
   cyclic.  Cyclic existence and HPL isometry are now algebraic consequences
   blockwise; locality, zero modes, and domains remain part of this
   simultaneous construction.
3. Through one residual ghost and two matter legs, the transferred charge is
   the already normalized moment-map action,
   `M_Taub = -sqrt(2)/(4*pi) J K^-`, with no unaccounted higher operation in
   that arity.

The resulting centered algebraic spectral sequence collapses at the
residual-cohomology page, so the two positive Weyl-square classes are the
complete answer in that model.  The remaining field-theory conjecture is
that no additional BV row or domain effect changes this model.  Quantum
nilpotency remains a distinct local Diff `x` Weyl anomaly problem; the
absence of a finite-dimensional central extension does not settle it.

## Physical meaning and boundary dependence

If C2h closes, the compact theory is not a positive-energy graviton Fock
space.  The one-particle oscillators are local-cohomology building blocks,
while the global physical candidates are weight-four conformal composites.
The provisional matter-weight-six quartic block then has no physical
absolute state on which to act.

This conclusion is specific to treating all conformal-Killing
transformations as residual gauge transformations on a closed `S^3` slice.
It does not automatically extend to noncompact Minkowski scattering, where
the same transformations can carry asymptotic surface charges and need not
be quotiented as gauge.  That distinction reconciles Cartan localization on
the cylinder with the split-phase scattering calculation of Paper VI.
