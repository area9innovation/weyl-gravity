# C2g-F: exact relative conformal Fock rail at weight four

## Construction

`symbolic/verify_conformal_fock_energy4.py` applies normalized bosonic second
quantization to the all-level C2g-A one-particle generators.  It is an
independent occupation-basis calculation rather than a hard-coded use of the
expected conformal primary states.

The complete pure-Weyl matter Fock space through total compact energy four is

\[
\mathcal F_{\le4}
=\mathbf1\oplus\mathcal H_2\oplus\mathcal H_3\oplus
\left(\mathcal H_4\oplus\operatorname{Sym}^2\mathcal H_2\right).
\]

Here `H_2=E_2^+ direct-sum E_2^-` has dimension ten.  Exact dimensions are

\[
\dim\mathcal F_0=1,
\qquad
\dim\mathcal F_2=10,
\qquad
\dim\mathcal F_3=40,
\qquad
\dim\mathcal F_4=82+55=137,
\]

so `dim F_<=4=188`.

For a normalized occupation state, the executable uses

\[
d\Gamma(K)=\sum_{ij}K_{ij}a_i^\dagger a_j,
\]

including the exact coefficient

\[
K_{ij}\sqrt{n_j(n_i+1)}
\]

when `i` and `j` differ.  This independently checks all Bose normalization
factors.

## Induced form and conformal action

The one-particle fundamental symmetry is `+1` on the `E` tower and `-1` on
the `A,L` towers.  Its bosonic lift is multiplicative:

\[
J_{\mathcal F}|i_1\cdots i_n\rangle
=\prod_r J_{i_r}|i_1\cdots i_n\rangle.
\]

The exact matrices verify

\[
(K^-_M)^\sharp=K^+_M,
\qquad
X^\sharp=X
\quad(X=D,L_a,R_a),
\]

and the compact grades `-1,0,+1`.  The full proper-conformal bracket

\[
[K^-_M,K^+_N]=2\delta_{MN}D+2R_{MN}
\]

holds on total matter energies at most three, the complete interior of the
energy-four Fock buffer.  The lowering algebra is complete through the top
shell because it never leaves the buffer.

## Relative weight-four kernel

The relative global conformal conditions are

\[
D|\Psi\rangle=4|\Psi\rangle,
\qquad
L_a|\Psi\rangle=R_a|\Psi\rangle=0,
\qquad
K^-_M|\Psi\rangle=0.
\]

The script first computes the exact kernel of the compact Casimir on the full
137-dimensional energy-four space.  Its dimension is two.  It then verifies
that all six compact generators vanish on this kernel and that all four
lowering generators annihilate it.

The two classes are exactly the normalized chiral `E_2` pair singlets.  In a
spin-two magnetic basis they are

\[
|S_\pm\rangle
=\frac1{\sqrt{10}}
\left(
2|2,-2\rangle_\pm
-2|1,-1\rangle_\pm
+\sqrt2|0,0\rangle_\pm
\right).
\]

They obey

\[
\langle S_r|J_{\mathcal F}|S_s\rangle=\delta_{rs}.
\]

Thus

\[
\boxed{\dim\ker(D-4,R,K^-)=2}
\]

on the complete pure-Weyl oscillator Fock space at this weight.  Parity
exchanges the two generators; a further parity projection is not imposed.

### Independent absolute-global cross-check

The separate C2g-N calculation in
`symbolic/verify_conformal_global_brst_window.py` constructs the absolute
**global-only** particle-number-two window.  Its incoming space is empty,

\[
C_3=0,
\]

while `dim C_4=55` and

\[
\operatorname{rank}d_4=53.
\]

Its absolute-global kernel is therefore exactly two dimensional and is
spanned by the same chiral Weyl-square states found here.  This is a strong
independent agreement between relative and absolute global rails.  It is not
yet a local-BV or combined local-plus-global physical-cohomology theorem.

## Data exposed for the absolute window

The function `residual_ghost_window_maps` returns:

- matter indices by compact energy;
- all degree-zero compact generators;
- all four degree-minus-one and degree-plus-one proper generators;
- the exact relative inclusion `C^2 -> F_<=4`;
- its induced `2 x 2` form; and
- the generator compact degrees.

These are inputs for an absolute residual-ghost computation.  They are not
that computation.  In particular this rail does not introduce the fifteen
global ghost zero modes, combine them with local Diff `x` Weyl BRST, or claim
absolute cohomology.

The optional function `absolute_weight_four_matter_window` adds the one
necessary buffer shell.  Since a ghost paired with a grade-`g` generator has
grade `-g`, a total-degree-four one-ghost calculation uses matter energies
three, four, and five.  The returned object contains the exact blocks

\[
K^-:\mathcal F_4\to\mathcal F_3,
\qquad
K^+:\mathcal F_4\to\mathcal F_5,
\qquad
(D,R):\mathcal F_4\to\mathcal F_4,
\]

and all reverse blocks.  The optional executable check verifies their exact
`J`-adjoint relations.  The corresponding dimensions are

\[
(\dim\mathcal F_3,\dim\mathcal F_4,\dim\mathcal F_5)
=(40,137,536).
\]

Run it with

```bash
python3 symbolic/verify_conformal_fock_energy4.py --verify-absolute-window-inputs
```

## Fail-closed scope

The executable rejects requests for:

1. absolute residual-ghost cohomology;
2. combined local/global BRST cohomology; and
3. conformal closure on the top of the finite Fock buffer.
