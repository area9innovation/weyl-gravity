# C2g-Cartan: residual contraction and the fate of weight six

## Exact Cartan identity

Write the absolute residual Chevalley--Eilenberg differential as

\[
d=c^a\rho(G_a)-\frac12f^a{}_{bc}c^bc^c\iota_a.
\]

Let `D` be cylinder time translation/dilatation and let
`i_D=partial/partial c^D`. The standard Cartan calculation gives

\[
\boxed{d i_D+i_Dd=L_D.}
\]

If

\[
[D,G_a]=w_aG_a,
\]

then the dual ghost has weight `-w_a`, and

\[
L_D=\rho(D)-\sum_aw_ac^a\iota_a.
\]

Thus on a homogeneous cochain with matter energy `E` and ghost energy

\[
E_{\rm gh}=-\sum_aw_a
\]

the Lie derivative acts by the total compact degree

\[
\delta=E+E_{\rm gh}.
\]

For `delta != 0`, a closed cochain is exact:

\[
d\Psi=0
\quad\Longrightarrow\quad
\Psi=d\left(\frac1\delta i_D\Psi\right).
\]

Therefore

\[
\boxed{H^q_\delta=0\qquad(\delta\ne0).}
\]

`symbolic/verify_conformal_cartan_contraction.py` reconstructs the exact
residual `so(4,2)` structure constants and verifies the ghost Cartan identity
on the unit and all fifteen exterior generators. Both sides are degree-zero
derivations, so the equality extends to all `2^15=32768` exterior monomials.
It separately verifies the exact compact grades of all represented generators.

This is the finite-dimensional version of Hamada's operator identity

\[
\{Q_{\rm BRST},b\}=\mathcal H,
\]

where `b` is the antighost of the residual time ghost and
`mathcal H=H+H^gh`; see
[Hamada, arXiv:1202.4538](https://arxiv.org/abs/1202.4538), Secs. 3 and 5.

## Why it removes the matter-weight-six residual sector

Hamada's standard residual ghost vacuum contains the four ghosts dual to the
four raising generators. Their total compact ghost energy is `-4`. Hence the
usual ghost-vacuum representative built on matter weight `E` has

\[
\delta=E-4.
\]

In particular, matter weight six means `delta=2`, not `delta=6`. More
strongly, the complete fifteen-ghost exterior algebra has ghost energies only
in

\[
-4,-3,\ldots,3,4.
\]

No alternative residual ghost dressing can put an `E=6` coefficient at
`delta=0`; all such cochains have

\[
2\le\delta\le10.
\]

Consequently the **entire matter-weight-six coefficient sector is acyclic in
the absolute residual global CE complex**. The four relative-primary states
found by C2g-E6 are valid relative matter kernels, but they do not survive as
absolute residual cohomology classes under these assumptions. In particular,
the provisional energy-six quartic channel is not a physical absolute-global
block unless the residual time translation is deliberately retained as a
global symmetry rather than gauged.

## Completing the delta-zero free Fock window

At `delta=0`, the ghost-energy floor limits matter coefficients to `E<=4`.
Since the pure-Weyl one-particle spectrum starts at energy two, only particle
numbers zero, one, and two can occur.

C2g-N already proves

\[
H^4_{\delta=0,N=1}=0,
\qquad
H^4_{\delta=0,N=2}
=\operatorname{span}\{|W_+^2\rangle,|W_-^2\rangle\}.
\]

The remaining matter-vacuum sector needs no matrix calculation. With trivial
coefficients it is the ordinary Chevalley--Eilenberg cohomology of
`so(4,2)`. After complexification,

\[
\mathfrak{so}(4,2)_\mathbb C
\simeq\mathfrak{so}(6,\mathbb C)
\simeq\mathfrak{sl}(4,\mathbb C).
\]

The invariant-polynomial degrees of type `A3` are `2,3,4`, so the primitive
cohomology degrees are `3,5,7`. The standard semisimple Lie-cohomology
theorem gives

\[
H^\bullet(\mathfrak{so}(4,2);\mathbb C)
\simeq\Lambda(u_3,u_5,u_7),
\qquad H^4(\mathfrak{so}(4,2);\mathbb C)=0.
\]

The field-extension/unitary-trick form of the semisimple theorem is in
[Chevalley--Eilenberg, *Cohomology Theory of Lie Groups and Lie Algebras*
(1948)](https://www.ams.org/tran/1948-063-01/S0002-9947-1948-0024908-8/).

The certificate checks this degree consequence explicitly; it does not use a
large finite rank calculation as the proof of the general theorem. Particle
number is preserved by the free residual generators. Therefore the complete
minimal free-Fock answer in this global-only complex is

\[
\boxed{
H^4_{\delta=0,\,\mathcal F_{\rm free}}
=\operatorname{span}\{|W_+^2\rangle,|W_-^2\rangle\}.
}
\]

Together with C2g-G, this sector has the exact residual class Gram `I_2`.
This is the complete centered cohomology of the minimal free residual
complex, not merely the first shell. The remaining qualification concerns
its transfer from the local pure-Weyl BV theory.

## Exact local-to-residual transfer lemma

The remaining C2h bridge is not supplied by an ungraded quasi-isomorphism.
The relevant statement is the following.

Let `(K,s)` be the gauge-fixed local Diff `x` Weyl BV/BRST coefficient
complex, carrying a strict residual action `rho` of `g=so(4,2)`, and form

\[
\mathcal C=\Lambda(\mathfrak g^*)\otimes K,
\qquad
Q=s+c^a\rho(G_a)-\frac12f^a{}_{bc}c^bc^c\iota_a.
\]

Assume:

1. `[s,rho(G_a)]=0` and the residual matrices obey the strict conformal Lie
   algebra, with no central or boundary term;
2. the local reduction is a strong deformation retract

   \[
   (H,0)\mathop{\rightleftarrows}^{\,i}_{\,p}(K,s),
   \qquad
   pi=1,
   \qquad
   ip=1-sh-hs;
   \]
3. the retract is residual-equivariant,

   \[
   p\rho_a=\bar\rho_ap,
   \qquad
   \rho_ai=i\bar\rho_a,
   \qquad
   [h,\rho_a]=0;
   \]
4. `p`, `i`, and `h` act trivially on the residual exterior ghosts, so they
   commute in the graded sense with `i_D=partial/partial c^D`;
5. the maps preserve the complete `D` grading, including the quantum
   normal-ordering/intercept contribution that gives the residual vacuum
   energy `-4`.

Then extension by the identity on `Lambda(g*)` transfers `Q` to the strict
residual differential

\[
\bar Q=c^a\bar\rho(G_a)
-\frac12f^a{}_{bc}c^bc^c\iota_a,
\]

and transfers the Cartan relation without correction:

\[
\boxed{
\bar Q i_D+i_D\bar Q=\bar L_D.
}
\]

The proof does not assume the conclusion. On the unreduced complex,
`[Q,i_D]_+=L_D` follows directly from the displayed strict differential.
Equivariance makes the extended `p` and `i` chain maps and gives

\[
[\bar Q,i_D]_+
=p[Q,i_D]_+i
=pL_Di
=\bar L_D.
\]

Because the retract intertwines `L_D`, its eigenspaces and the `-4` shift are
unchanged. Hence the contracting homotopy `i_D/delta` is valid after transfer
on every nonzero eigenspace.

There is a slightly more general chain-map statement. For any strong
deformation retract between total complexes, define

\[
\bar i_D=p i_D i,
\qquad
\bar L_D=pL_Di.
\]

Then `[\bar Q,\bar i_D]_+=\bar L_D`. However, without the equivariance and
ghost-factorization hypotheses, `\bar i_D` need not be the elementary
residual antighost contraction and `\bar L_D` need not be the intended
cylinder grading. That weaker identity is therefore insufficient to remove
the advertised weight-six sector.

If the local residual algebra closes only up to BRST homotopy, homological
perturbation generally transfers an `L_infinity` action with higher-ghost
terms. In that case one must construct the corrected effective contraction
and verify its Cartan relation explicitly; the strict residual-CE result
cannot simply be imported.

## Scope and failure modes

The contraction theorem is exact, but its physical use is conditional.

1. **Residual gauge versus fixed-cylinder symmetry.** In Hamada's generally
   covariant construction, `D` belongs to the residual gauge algebra and
   `b` supplies its contraction. In a QFT formulated on a fixed cylinder,
   `D` is normally the physical Hamiltonian/global conformal generator. One
   must then not quotient nonzero-energy states by `i_D/delta`.
2. **Local-BV zero-mode split.** The repository has not derived the residual
   conformal-Killing ghost complex, its vacuum, or its `-4` shift from the
   full pure-Weyl Diff `x` Weyl BV complex. The result is global-only until
   that relative-to-absolute bridge and the treatment of contractible local
   modes are proved. In particular, the local contraction data must be
   `D`-equivariant and must preserve the residual ghost polarization; an
   ordinary quasi-isomorphism does not suffice.
3. **Quantum anomalies.** The argument needs a nilpotent quantum BRST charge
   and the unmodified identity `{Q,b}=mathcal H`. Anomalies or normal-ordering
   changes must be excluded in the pure-Weyl theory rather than imported from
   Hamada's broader Riegert-Wess-Zumino model.
4. **Boundaries and large gauge transformations.** On compact `S^3` there is
   no spatial boundary term in the residual algebra. With asymptotic or
   timelike boundaries, `D` may carry a nonzero surface charge and cease to
   be BRST-exact. Then the Cartan contraction does not remove its charged
   sectors.
5. **Interactions.** The free conformal action preserves particle number;
   the interacting local BRST differential need not. The two-class result is
   therefore a free residual statement, not an interacting cohomology
   theorem.

## Reproduction

```bash
python3 symbolic/verify_conformal_cartan_contraction.py
```
