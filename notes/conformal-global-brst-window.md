# C2g-N: first cutoff-complete global-BRST kernel/image window

## Scope

The executable certificate is
`symbolic/verify_conformal_global_brst_window.py`.  It combines the universal
residual `SO(4,2)` ghost algebra of C2e with the exact one-particle generator
jet of C2f-A/M.  It answers a narrowly defined question:

> Is there any ghost-number/compact-degree sector whose incoming and outgoing
> global-BRST maps can be computed exactly from the source-energy-four jet,
> despite the fact that the jet is not a finite conformal representation?

The answer is yes.  The first such sector is the absolute exterior-ghost
window at total compact degree zero and ghost number four.  The certificate
solves it both on the one-particle module and on the complete lowest
particle-number-two block.

This is a **global-only free-module** calculation.  It is not the combined
local Diff `x` Weyl plus residual BRST cohomology or, by itself, a physical
ghost pairing.  The later C2g-N6 and Cartan rails complete the energy-six
inventory and prove that its nonzero total-degree absolute complex is
contractible.

## Residual ghost polarization

Hamada's cylinder BRST construction uses a residual ghost Fock vacuum
containing the four ghosts dual to the four raising conformal generators.
That ghost factor has compact energy `-4`.  In an absolute exterior-ghost
grading it lies at ghost number four.  Its relative representatives obey

\[
(D-4)|\psi\rangle=0,
\qquad R|\psi\rangle=0,
\qquad K^-|\psi\rangle=0.
\]

This is why the physically relevant absolute sector begins at

\[
(\delta,g)=(0,4),
\]

not at ordinary ghost number zero with invariance under all fifteen
generators.  The source is Hamada's broader Riegert--Weyl system,
[arXiv:1202.4538](https://arxiv.org/abs/1202.4538), especially Eqs.
(3.5)--(3.10) and (5.2)--(5.6).  The present certificate uses its residual
ghost polarization as an algebraic convention; it does not import the
Riegert sector or claim that the same vacuum has already been derived from
the pure-Weyl local BV complex.

## General finite-buffer rule

The complex basis contains

- four generators of compact degree `+1`;
- seven generators of degree zero; and
- four generators of degree `-1`.

The dual ghosts therefore have degrees `-1`, zero, and `+1`, respectively.
At ghost number `q`, the maximal absolute ghost degree is

\[
w(q)=\min(q,4,15-q).
\]

For total compact degree `delta`, the coefficient states in `C^q_delta`
have energies in

\[
\delta-w(q)\le E\le\delta+w(q),
\]

intersected with the true spectrum of the coefficient module.  Thus a safe
coefficient-energy buffer for the kernel/image problem

\[
C^{g-1}_\delta\longrightarrow C^g_\delta
\longrightarrow C^{g+1}_\delta
\]

ends at

\[
E_{\max}=\delta+max\{w(g-1),w(g),w(g+1)\}.
\]

This rule assumes a genuine lowest-weight boundary below, not an artificial
lower cutoff.  The C2f one-particle module begins at `E=2`, and every
lowering generator annihilates that block exactly.

For `(delta,g)=(0,4)`, the nominal upper edge is `E=4`.  The three cochain
spaces use

\[
\begin{array}{c|c}
q&\text{coefficient energies}\\ \hline
3&2,3\\
4&2,3,4\\
5&2,3,4.
\end{array}
\]

There is no hidden need for the unknown `E_4 -> E_5` raising blocks.  Every
`E=4` source in `C^4_0` already contains all four degree-`-1` raising ghosts.
Wedge multiplication by another raising ghost is therefore zero.  This is
the exterior-saturation mechanism that makes the window cutoff-complete.

For comparison, targeting ghost number four and total degree two, the degree
associated with a weight-six matter state on the same `-4` ghost vacuum,
requires a coefficient buffer through energy six.  The same saturation means
energy seven is unnecessary.  That complete buffer is now constructed by
`verify_conformal_global_brst_energy6.py`; Cartan's identity contracts it
without a large rank reduction.

## Exact one-particle complex

For one chirality, the exact dimensions are

\[
\boxed{
C^3_0(290)\xrightarrow{d_3}
C^4_0(1311)\xrightarrow{d_4}
C^5_0(3657).
}
\]

The script reconstructs an exact fifteen-generator basis from the C2f
matrices on the complete energy-two/three interior, verifies antisymmetry and
all Jacobi identities, constructs both sparse differentials, and proves

\[
d_4d_3=0
\]

entry by entry in characteristic zero.

The differential coefficients lie in

\[
\mathbb Q(i,\sqrt2,\sqrt3,\sqrt5).
\]

For a rank certificate, reduce this exact coefficient ring modulo `241`
using

\[
i\mapsto64,
\quad\sqrt2\mapsto22,
\quad\sqrt3\mapsto56,
\quad\sqrt5\mapsto103.
\]

Each image obeys its defining square relation.  Exact finite-field
elimination gives

\[
\operatorname{rank}_{\mathbb F_{241}}d_3=260,
\qquad
\operatorname{rank}_{\mathbb F_{241}}d_4=1051.
\]

A nonzero minor after good-prime reduction is a nonzero characteristic-zero
minor, so these are lower bounds on the exact ranks.  Exact nilpotency gives

\[
\operatorname{rank}d_3+\operatorname{rank}d_4
\le \dim C^4_0=1311.
\]

The modular lower bounds already sum to `1311`; hence both exact ranks are
fixed and

\[
\boxed{H^4_{\delta=0}(\mathfrak{so}(4,2),\mathcal M_{1,+})=0}
\]

for the positive-chirality one-particle jet.  Parity supplies the conjugate
chirality, so their direct sum also has zero middle cohomology.

## Exact particle-number-two complex

The residual free generators preserve oscillator particle number.  The
lowest two-particle matter sector has energy four and is

\[
\operatorname{Sym}^2(E_2^+\oplus E_2^-),
\qquad \dim=\binom{10+1}{2}=55.
\]

At `(delta,g)=(0,4)`, no ghost-number-three monomial has enough negative
compact degree to accompany an energy-four coefficient state.  Hence

\[
C^3_0=0.
\]

At ghost number four there is the unique product of all four raising ghosts,
while at ghost numbers five and six one may append one or two of the seven
compact ghosts.  Therefore the exact beginning of the complex is

\[
\boxed{
0\longrightarrow C^4_0(55)
\xrightarrow{d_4}C^5_0(385)
\xrightarrow{d_5}C^6_0(1155).
}
\]

Only the second-quantized compact action is needed.  Every lowering
generator annihilates both lowest-weight `E_2` factors, and every omitted
raising action is killed by the already saturated raising-ghost volume.
The script verifies exactly that

\[
d_5d_4=0.
\]

The two normalized chiral scalar vectors are

\[
|W^2_\pm\rangle
=\sqrt{\frac25}|2,-2\rangle_\pm
-\sqrt{\frac25}|1,-1\rangle_\pm
+\frac1{\sqrt5}|0,0\rangle_\pm.
\]

Both are exact `d_4` cocycles.  Good-prime reduction gives

\[
\operatorname{rank}_{\mathbb F_{241}}d_4=53.
\]

The two displayed independent kernel vectors give the characteristic-zero
upper bound `rank(d4)<=53`, while the modular minor gives the lower bound.
Thus the exact rank is `53`, the kernel is exactly their span, and the empty
incoming space means there are no global-only incoming exacts in this
particle-number sector:

\[
\boxed{
H^4_{\delta=0}
\left(\mathfrak{so}(4,2),
\operatorname{Sym}^2(E_2^+\oplus E_2^-)\right)
=\operatorname{span}\{|W^2_+\rangle,|W^2_-\rangle\}.
}
\]

This is the absolute-global counterpart of the two-dimensional relative
primary kernel found independently by C2g-R.

## Relation to the relative weight-four kernel

The one-particle vanishing does not contradict the separate C2g-R result.
C2g-R works
on the complete matter weight-four **Fock** space and finds two relative
primary scalars in `Sym^2(E_2)`.  C2g-N works only on the **one-particle**
module, where no such bilinear exists.

Nor does the positive matter Gram matrix on the C2g-R relative kernel yet
define the absolute physical pairing.  That step requires:

1. the incoming-exact subspace in the full Fock ghost complex;
2. the residual ghost adjoint and dual insertion;
3. orthogonality of exacts and identification of the radical;
4. the relative-to-absolute comparison; and
5. compatibility with the local Diff `x` Weyl BRST differential.

The natural ghost pairing need not preserve uncentered ghost number; with
fifteen absolute ghosts it pairs complementary degrees before the vacuum and
insertion conventions are centered.

## What is and is not closed

Closed exactly:

- the ghost-degree buffer theorem;
- the true lowest-energy boundary;
- exterior saturation at the top boundary;
- the first finite global-only absolute kernel/image pair;
- exact nilpotency; and
- vanishing one-particle middle cohomology;
- absence of incoming exacts in the lowest two-particle sector; and
- the exact two-dimensional absolute-global Weyl-square cohomology there.

Still open:

- derivation of the residual zero-mode split from pure-Weyl local BV data;
- the combined local-plus-global complex;
- the embedding or elimination of the two absolute-global Weyl-square classes
  in the combined local-plus-global complex;
- the induced ghost-plus-matter pairing on that combined cohomology; and
- the cyclic local-BV transfer and quantum-anomaly conditions needed to call
  the residual answer the full free pure-Weyl cohomology.

## Reproduction and fail-closed boundary

Run

```bash
python3 symbolic/verify_conformal_global_brst_window.py
```

All stronger requests must fail:

```bash
python3 symbolic/verify_conformal_global_brst_window.py --require-local-brst
python3 symbolic/verify_conformal_global_brst_window.py --require-energy-six-fock
python3 symbolic/verify_conformal_global_brst_window.py --require-physical-cohomology
```
