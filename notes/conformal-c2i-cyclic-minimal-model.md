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

`notes/conformal-local-detour.md` now separates the exact smooth global BGG
bridge from the still-open BV/BFV zero-mode transfer.  The
Branson--Gover/Gover--Peterson/Čap deformation identities, the cylinder
topology, and the action-normalized factorization

\[
B_{\rm lin}=C_1^\sharp C_1
\]

are fixed.  They prove the smooth metric-to-geometric-curvature quotient.
They do not yet prove its restriction to the algebraic positive-energy
`E/A/L` module or the existence of finite-mode metric potentials.  Beyond
that algebraic-cylinder problem, the remaining statements are the placement
and normalization of the canonical degree-three global BGG sector, removal
of local/nonminimal rows, and the strict cyclic zero-mode transfer.

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

## Cyclicity collapses to a compatible choice

The auxiliary Hodge product does not establish descent of the physical
pairing.  Once the local kernel and its nondegenerate induced form are
identified, cyclicity is not an independent spectrum or norm calculation
inside one finite harmonic block: a cyclic retract exists there
algebraically.  It must nevertheless be chosen simultaneously
compact-degree equivariant, compatible with the conformal-Killing zero-mode
split, and equivariant under the noncompact generators `K^+` and `K^-`.
The last condition does not follow by averaging because the conformal
modules are nonunitary and need not be semisimple.  Those compatibility and
domain conditions—not a term-by-term recomputation of the dressed Gram—are
the remaining field-theory obligation that promotes the residual class Gram
`I2` to the induced pairing on local-plus-global cohomology.  Even after that
bridge closes, C2j-D identifies these as ghost-dressed
vertex/deformation classes rather than a propagating graviton Hilbert space.

### Even-pairing convention and cyclic isometry

The executable certificate uses the suspended even-pairing convention. For
an operator `A:V -> W` with nondegenerate Hermitian forms `G_V,G_W`, define

\[
A^\sharp=G_V^{-1}A^\dagger G_W.
\]

Use a normalized cyclic contraction

\[
p\jmath=I,
\qquad
\jmath p=I-qs-sq,
\qquad
s^2=s\jmath=ps=0,
\]

with

\[
q^\sharp=-q,
\qquad
s^\sharp=-s,
\qquad
\jmath^\sharp=p.
\]

Let `Q=q+Delta` be nilpotent and cyclic,

\[
\Delta^\sharp=-\Delta.
\]

For the displayed contraction convention, the Basic Perturbation Lemma uses
the **plus-sign** formulas

\[
I=(\mathbf1+s\Delta)^{-1}\jmath,
\qquad
P=p(\mathbf1+\Delta s)^{-1}.
\]

The cyclic identities then give

\[
(s\Delta)^\sharp=\Delta s
\]

and hence

\[
\boxed{
I^\sharp
=\jmath^\sharp(\mathbf1+\Delta s)^{-1}
=P.
}
\]

The normalized perturbation lemma supplies

\[
PI=\mathbf1_H,
\]

so

\[
\boxed{I^\sharp I=\mathbf1_H.}
\]

Thus the dressed inclusion is an exact isometry of the reduced form, even
though it need not equal the original choice of representatives. Writing the
transferred differential as

\[
Q_H=P Q I,
\]

one obtains

\[
Q_H^\sharp
=I^\sharp Q^\sharp P^\sharp
=-P Q I
=-Q_H.
\]

This proves preservation of the indefinite pairing. It does not turn an
indefinite form into a positive one; positivity of the centered two-class
sector remains the separate residual result `G=I2`.

### Exact finite cyclic fixture

`symbolic/verify_conformal_cyclic_hpl.py` constructs an exact
eight-dimensional Krein complex and a four-dimensional reduced complex. A
rational `G`-unitary rotation mixes the reduced and contractible blocks, so
the perturbation changes the inclusion nontrivially and produces a nonzero
transferred differential. The certificate verifies:

- `j^sharp=p`, `q^sharp=-q`, and `s^sharp=-s`;
- the normalized SDR identities and side conditions;
- `Delta^sharp=-Delta` and `(s Delta)^sharp=Delta s`;
- exact invertibility of the plus-sign BPL factors;
- both dressed chain-map identities;
- `I^sharp=P`, `P^sharp=I`, and `P I=1_H`;
- `I^sharp I=1_H` and direct equality of the pulled-back Gram matrix;
- nilpotency and skew-adjointness of the nonzero transferred differential;
  and
- as a negative control, failure of both chain-map identities when the
  opposite BPL signs are inserted while retaining
  `j p=I-q s-s q`.

The fixture proves the algebraic statement in this explicit even-pairing
convention. Raw BV odd symplectic conventions require the corresponding
Koszul signs or an explicit suspension; no broader graded-sign formula is
claimed by this certificate.

### Existence theorem and its boundary

There is a finite-dimensional algebraic existence result. Let `(C,G,q)` have
a nondegenerate Hermitian form, `q^2=0`, and `q^sharp=-q`. Then

\[
(\operatorname{im}q)^\perp=\ker q,
\qquad
(\ker q)^\perp=\operatorname{im}q.
\]

Consequently the induced cohomology form is nondegenerate. Choose a
nondegenerate representative space `H` inside `ker q`, let `p` be its
`G`-orthogonal projection, and choose an isotropic complement `L` with

\[
H^\perp=\operatorname{im}q\oplus L.
\]

Then `q:L -> im q` is an isomorphism. Its inverse on `im q`, extended by
zero, gives a normalized homotopy satisfying `s^sharp=-s`. Thus a cyclic SDR
exists algebraically in finite dimension.

If, in addition, `D` is diagonalizable, `[D,q]=0`, and the pairing makes its
compact-degree blocks orthogonal (equivalently `D^sharp=D` in the suspended
Hermitian convention), the same Witt construction can be performed inside
each eigenspace.  The resulting cyclic SDR is automatically `D`-equivariant.
Thus at any finite cylinder cutoff, compact-degree equivariance and cyclicity
collapse to one compatible blockwise choice once the local kernel and its
form have been identified.

This theorem does **not** yet close C2i. It does not guarantee that the same
choice is simultaneously:

- compact-degree equivariant before the required `D`-adjointness and
  diagonalizability hypotheses are verified;
- local or covariant as a field-theory Green operator;
- compatible with the conformal-Killing zero-mode split;
- equivariant under the full noncompact `SO(4,2)` action rather than only
  blockwise `D x SO(4)`;
- continuous on an infinite-dimensional completed state space;
- cyclic for the physical BV/Krein form rather than merely for the auxiliary
  positive Hodge product; or
- compatible with the interacting perturbation and quantum measure.

In particular, the adjoint used in the positive auxiliary Hodge Laplacian
cannot simply be identified with the even cyclic `sharp` above. On a
positive-definite space, a skew-adjoint operator is normal, so a nilpotent
skew-adjoint operator must vanish. A nontrivial BRST differential can obey
`q^sharp=-q` only for an indefinite form or after the appropriate BV degree
shift. The auxiliary positive product may construct `p,j,s`; their cyclic
relations must then be checked separately against the physical BV/Krein
pairing.

In infinite dimension, nonclosed images, zero modes, domains of unbounded
operators, and boundary conditions can obstruct the orthogonal splitting.
Moreover, convergence or filtration-local nilpotence of the BPL inverses is a
separate hypothesis. C2i must therefore construct the cyclic,
compact-degree-equivariant retract for the actual pure-Weyl BV complex rather
than infer it solely from the finite-dimensional existence argument.

## Transferred residual charge

The leading minimal BFV charge should be

\[
\Omega_{\min}
=c^A\mu_A
-\frac12 f^A{}_{BC}c^Bc^Cb_A
+O(c\,\Phi^3,c^2\Phi,\ldots).
\]

The two displayed terms have strong separate evidence:

- the second is the universal `so(4,2)` Chevalley--Eilenberg differential;
- the first is the quadratic oscillator moment map, matched to selected Taub
  kernels in the finite cylinder certificate.

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

The executable work packages and sprint order are maintained in
`bridge/README.md`; that file is the canonical programmer handoff for these
criteria.

1. An explicit pure-Weyl local BV/BFV field and ghost complex in a stationary
   cylinder gauge.
2. A non-overlapping split of the fifteen conformal-Killing zero modes.
3. An all-level curvature intertwiner from the explicit `E/A/L` modes into
   the geometric chiral kernel, together with a `D`- and `SO(4)`-finite
   metric-potential construction.
4. The full local BV harmonic-kernel calculation giving exactly the
   `W_+ + W_-` module and no relevant extra ghost or antifield cohomology.
5. Verification that the local form and compact-degree operator meet the
   hypotheses above, followed by construction of the resulting
   full `SO(4,2)`-equivariant cyclic retract and its exact HPL isometry.
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
