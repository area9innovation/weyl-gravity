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
strong deformation retract.  C2i now has a nontrivial algebraic
instantiation: the raw polynomial metric BV rows admit an exact rational
retract, its noncompact defects are explicitly homotopic, the induced
residual action is strict, and the centered metric-to-CE pipeline reproduces
the residual answer.  The cross-energy cyclic form, complete centered HPL
correction test, canonical residual CE pairing, explicit closed-`S3` BFV
choice, and all-energy Taub normalization are now also certified.  The one
remaining classical identification is whether this algebraic polynomial
complex is the complete chosen gauge-fixed field-theory BV domain, with no
additional rows or domain effects.

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
The symbolic all-energy cylinder preimages now prove its restriction to the
algebraic positive-energy `E/A/L` module.  The raw polynomial BV
implementation also includes the minimal ghost/antifield detour rows and
separate contractible nonminimal certificates.  Its cross-energy cyclic form
and residual BFV zero-mode choice are now explicit.  The remaining statement
is the field-theoretic identification of this algebraic model and its cyclic
form.

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
algebraically.  The raw calculation shows that demanding a strictly
equivariant representative choice is unnecessarily strong: its natural
`p,j,s` has nonzero `K^+/-` defects, but they are exactly `q`-homotopic, the
induced cohomology action is strict, and the physical-row HPL corrections
vanish.  The exact cross-energy recursion now supplies the raw cyclic
pairing, and the complete ordered-generator test proves the absence of
higher centered HPL terms.  What remains is to identify this certified
algebraic split and pairing with the complete field-theory BV domain.  That
domain condition—not a term-by-term recomputation of the dressed Gram—is
the remaining obligation that promotes the algebraic `I2` to the complete
field-theoretic local-plus-global cohomology.  Even after that
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

In the certified free algebraic cylinder model, the leading minimal BFV
charge is

\[
\Omega_{\min}
=c^A\mu_A
-\frac12 f^A{}_{BC}c^Bc^Cb_A
+O(c\,\Phi^3,c^2\Phi,\ldots).
\]

The two displayed terms are now tied together by exact certificates:

- the second is the universal `so(4,2)` Chevalley--Eilenberg differential;
- the first is the quadratic oscillator moment map, whose `D` component is
  derived from the quadratic Noether Hamiltonian and whose proper-conformal
  normalization is fixed by two independent direct `B^(2)` curvature seeds.

The complete centered HPL calculation gives the strict CE action with no
higher correction in this window, and the one-ghost/two-matter normalization
is

\[
M_{\rm Taub}=-\frac{\sqrt2}{4\pi}J K^-.
\]

The exact kernels reproduce

\[
\{\mu_A,\mu_B\}=f_{AB}{}^C\mu_C
\]

and moment-map equivariance.  Because the Weyl module is multiplicity-free,
the all-level generator theorem and the two direct curvature seeds fix this
arity uniquely up to the displayed normalization.  What remains conditional
is its identification with the charge obtained from the complete chosen
field-theory BV domain, not the algebraic all-energy comparison itself.

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

## Acceptance status

The five executable sprints in `bridge/README.md` are complete in the finite
algebraic cylinder category.  They provide the all-energy curvature
intertwiner, raw ghost/metric/antifield rows and zero-mode projector,
noncompact homotopies, cross-energy cyclic form, exact dressed isometry,
complete centered HPL test, residual CE pairing, explicit closed-universe
BFV choice, all-energy Taub normalization, and end-to-end `I2` integration
test.

C2i closes as a statement about the complete field-theory BV complex only
after one remaining identification: the chosen gauge-fixed pure-Weyl field
domain must be shown to have precisely the certified raw polynomial rows and
no additional cohomology, locality obstruction, or analytic domain effect.
Quantum nilpotency remains later still.  The finite conformal algebra has no
nontrivial ordinary central two-cocycle, but that does not remove the local
Weyl anomaly.

## Physical boundary of the conclusion

If C2i closes, the compact theory has no one-particle global physical states
in this polarization and no higher-weight absolute tower.  Its surviving
free candidates are action-density-like conformal composites.  This is not
an ordinary ghost-free graviton Fock space.

The conclusion also depends on treating cylinder `D` as residual gauge.  In
noncompact scattering or with boundaries, `D` can carry a surface charge and
need not be BRST exact; the Cartan contraction then does not remove its
charged sectors.
