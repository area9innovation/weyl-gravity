# C2g-N6: the cutoff-complete degree-two absolute window

`symbolic/verify_conformal_global_brst_energy6.py` constructs the complete
free matter/ghost inventory needed at

\[
(\delta,g)=(2,4)
\]

for the absolute residual-global \(SO(4,2)\) Chevalley--Eilenberg complex.
It is a global-only free-module certificate.  It does not include the local
Diff\(\times\)Weyl BV complex and therefore is not, by itself, a calculation
of the physical interacting pure-Weyl BRST cohomology.

## Complete matter inventory

The all-level two-chirality oscillator module has one-particle dimensions

\[
\dim \mathcal H_E^{(1)}=(10,40,82,136,202),\qquad E=2,3,4,5,6.
\]

Bosonic second quantization through total energy six gives

\[
\begin{array}{c|rrrrrr}
E&0&2&3&4&5&6\\ \hline
\dim\mathcal F_E&1&10&40&137&536&2062.
\end{array}
\]

The nontrivial particle-number refinement is

\[
\begin{array}{c|rrr}
E&N=1&N=2&N=3\\ \hline
2&10&0&0\\
3&40&0&0\\
4&82&55&0\\
5&136&400&0\\
6&202&1640&220.
\end{array}
\]

At energy six the two-particle contribution is
\(\mathcal H_2\otimes\mathcal H_4\oplus
\operatorname{Sym}^2\mathcal H_3\), of dimension \(820+820=1640\), and the
three-particle contribution is \(\operatorname{Sym}^3\mathcal H_2\), of
dimension \(220\).  Since the lowest oscillator energy is two, no state with
four particles can occur through energy six.

## Absolute cochain inventory

There are four generator ghosts of compact degree \(-1\), seven of degree
zero and four of degree \(+1\), with ghost degree opposite to generator
degree.  Tensoring their exterior powers with the matter inventory gives

\[
\begin{array}{c|rrrr|r}
 &N=0&N=1&N=2&N=3&\text{total}\\ \hline
C^3_2&42&9778&3910&0&13730\\
C^4_2&142&32044&20650&220&53056\\
C^5_2&322&74836&64390&1540&141088\\
C^6_2&552&129424&132000&4620&266596.
\end{array}
\]

The executable prints the finer inventory by ghost number, matter energy and
particle number.  In particular, \(C^3_2\) stops at matter energy five,
whereas \(C^4_2,C^5_2,C^6_2\) reach energy six.

## Why energy six is a complete cutoff

For an absolute window centered at ghost number four, the ghost-width rule is

\[
E_{\max}=\delta+max\{w(3),w(4),w(5)\}=2+4=6.
\]

At matter energy six the required ghost energy is \(-4\).  Every such ghost
monomial contains all four ghosts dual to the raising generators.  Hence an
otherwise omitted raising action from energy six to seven is killed first by
exterior saturation:

\[
c^{K^+_M}\wedge c^{K^+_{++}}c^{K^+_{+-}}c^{K^+_{-+}}c^{K^+_{--}}=0.
\]

There is no energy-six source in \(C^3_2\).  The energy-five raising action
lands in the included energy-six shell.  At the lower boundary, the vacuum
is annihilated by second-quantized generators and the one-particle energy-two
states are conformal lowest weights.  Thus no missing matter action is used
by \(d_3,d_4,d_5\).

## Exact Cartan contraction

Let \(D\) be the compact cylinder-energy generator and \(i_D\) contraction
with its ghost.  In the conventions of the executable,

\[
[D,G_a]=r_aG_a,
\qquad
\{i_D,c^a\wedge\}=\delta_D{}^a.
\]

The ghost part of the CE differential obeys

\[
\{d_{\rm gh},i_D\}=-\sum_{a\in m}r_a
\]

on a ghost monomial \(m\), while the coefficient-module part obeys

\[
\left\{c^a\rho(G_a),i_D\right\}=\rho(D).
\]

On a cochain of matter energy \(E\), their sum is therefore

\[
\{d,i_D\}=E-\sum_{a\in m}r_a=\delta.
\]

The script checks the graded Lie brackets exactly, exhausts the ghost Cartan
and wedge/contraction identities over all monomials in \(C^3\) through
\(C^6\), and checks the exact compact grade of every all-level matter
generator entry.  Since \(\delta=2\),

\[
h=\frac12 i_D,
\qquad
dh+hd=1.
\]

Both \(d\) and \(h\) preserve matter particle number.  Consequently

\[
\boxed{H^4_{\rm global}(\delta=2,N)=0,
\qquad N=0,1,2,3.}
\]

This is stronger than a finite-field rank computation: it contracts the
entire degree-two absolute complex and identifies why every possible class
is exact.  A lazy exact differential builder is retained and verifies the
sign conventions, nilpotency and Cartan identity on a representative of
every energy/particle sector without materializing matrices as large as
\(266596\times141088\).

## Reproduction and fail-closed boundary

Run

```bash
python3 symbolic/verify_conformal_global_brst_energy6.py
```

The switches `--require-local-brst`, `--require-physical-cohomology` and
`--require-materialized-ranks` fail closed.  The last switch records that the
large rank reduction is deliberately unnecessary: the exact homotopy proves
the cohomology statement directly.
