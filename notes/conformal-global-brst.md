# C2e: algebra-only global conformal BRST rail

## Scope

The executable certificate is
`symbolic/verify_conformal_global_brst.py`.  It takes the exact
15-generator complex cylinder basis and brackets already verified by
`symbolic/verify_conformal_c2a_reducibilities.py` and constructs their
universal minimal Chevalley--Eilenberg/BRST complex.

This is a finite-Lie-algebra result.  It does **not** provide matrices for the
fifteen charges on the pure-Weyl oscillator or Fock space, combine the global
ghosts with the local Diff `x` Weyl BRST complex, impose the Taub-constraint
zero locus, compute physical cohomology, or determine the induced physical
pairing.

## Algebra and compact grading

Use the complex cylinder basis

\[
T,\qquad R_{AB}\ (A<B),\qquad K_A^+,K_A^-\quad(A=0,1,2,3).
\]

The nontrivial brackets include

\[
[T,K_A^s]=-isK_A^s,
\]

\[
[R_{AB},K_C^s]
=\delta_{BC}K_A^s-\delta_{AC}K_B^s,
\]

\[
[K_A^+,K_B^-]=2R_{AB}+2i\delta_{AB}T,
\]

together with the ordinary `so(4)` rotation algebra.  Write

\[
[G_a,G_b]=f_{ab}{}^cG_c.
\]

The script rechecks antisymmetry and every Jacobi identity directly from the
imported exact structure constants.

For compact cylinder energy define

\[
D=iT,
\qquad
\deg_D K_A^+=+1,
\quad
\deg_D K_A^-=-1,
\quad
\deg_D T=\deg_D R_{AB}=0.
\]

Every nonzero structure constant is homogeneous:

\[
f_{ab}{}^c\ne0
\quad\Longrightarrow\quad
\deg_DG_c=\deg_DG_a+\deg_DG_b.
\]

## Minimal ghost complex

Introduce one odd ghost `c^a` for each complex-basis generator.  The real
`so(4,2)` form is recovered by the corresponding reality condition, or
equivalently by changing from `K^+`,`K^-` to the real cosine/sine basis.
Assign

\[
\operatorname{gh}(c^a)=1,
\qquad
\deg_D(c^a)=-\deg_D(G_a).
\]

The Chevalley--Eilenberg differential is

\[
s c^a=-{1\over2}f_{bc}{}^a c^b\wedge c^c.
\]

The executable uses an exact sparse exterior algebra, checks `s^2 c^a=0`
for all fifteen ghosts, and performs a regression sweep over every exterior
monomial through degree three.  Nilpotency on the generators, together with
the checked odd derivation law, proves nilpotency on the full finite exterior
algebra.  It also verifies

\[
[N_{\rm gh},s]=s,
\qquad
[D,s]=0.
\]

There is a second exact check with coefficients in the formal adjoint module:

\[
sG_a=c^b[G_b,G_a].
\]

Again `s^2G_a=0` is precisely Jacobi.  Here `G_a` are abstract formal
constraints, not operators on a Weyl-gravity state space.

## Formal minimal BRST charge

With canonical odd ghost momenta `b_a`, of ghost number `-1`, the universal
minimal expression is

\[
\Omega_{\rm min}
=c^aG_a-{1\over2}f_{bc}{}^a c^b c^c b_a.
\]

Assigning

\[
\deg_D b_a=\deg_DG_a
\]

makes every term of `Omega_min` have ghost number `+1` and compact degree
zero.  The CE and adjoint-module checks prove nilpotency on the ghost and
formal-constraint sectors.  The executable also uses the standard canonical
BFV rule

\[
s b_a=G_a+c^b f_{ba}{}^c b_c
\]

and verifies `s^2 b_a=0` for all fifteen ghost momenta.  Nilpotency is thus
checked on every generator of the universal minimal algebra; the odd
derivation law extends it to the whole algebra.

This is not a representation-level BRST theorem.  Such a theorem also
requires exact charge operators satisfying the algebra without an anomaly or
central extension, as well as the local gauge complex and its compatibility
with the global sector.

## Relation to Hamada

Hamada's cylinder construction is useful as an algebraic template for
organizing compact-energy, rotation, proper-conformal, and global-ghost
terms.  No physical-state or pure-Weyl cohomology statement is imported from
that broader conformal-gravity/Riegert system:
[arXiv:1202.4538](https://arxiv.org/abs/1202.4538).

## What remains open

Before the global reduction can act on the provisional P4 oscillator block,
the programme still needs:

1. extension of the exact fifteen-component one-particle moment-map jet
   beyond the energy-four buffer and its second quantization on the relevant
   oscillator, auxiliary, and contractible sectors;
2. verification that the resulting full operator algebra has no anomaly or
   central term;
3. the combined local Diff `x` Weyl plus global conformal BRST operator;
4. its ghost-number-zero cohomology and induced pairing; and
5. the disposition of the Hessian-null `t` block after that reduction.

Consequently C2e does not define a `t`-channel inverse, physical quartic
amplitude, or metric-deformation obstruction.

## Reproduction and fail-closed boundary

Run

```bash
python3 symbolic/verify_conformal_global_brst.py
```

Both stronger requests must fail:

```bash
python3 symbolic/verify_conformal_global_brst.py --require-oscillator-action
python3 symbolic/verify_conformal_global_brst.py --require-physical-cohomology
```
