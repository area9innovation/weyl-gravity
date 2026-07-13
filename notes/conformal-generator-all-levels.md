# C2g-A: cutoff-stable conformal oscillator generator

## Purpose

`symbolic/verify_conformal_generator_all_levels.py` extends the exact C2f-A
proper-conformal action beyond the energy-four buffer.  It is both an
executable certificate and a reusable matrix constructor for the next global
BRST kernel/image calculation.

The construction is deliberately a finite **buffer**, not a finite conformal
representation.  A cutoff at compact energy `N` contains every oscillator
block needed to verify the algebra on energies at most `N-1`.  Its top shell
does not contain the raising map into energy `N+1`; the executable verifies
that this boundary defect is nonzero and refuses any request for top-shell
closure.

## Physical towers

For either chirality the one-particle irreps are

\[
\begin{array}{c|c|c|c}
\text{tower}&n_{\min}&(j_L,j_R)_+&J_{\rm conf}\\ \hline
E_n&2&(n/2+1,n/2-1)&+1\\
A_n&3&(n/2,n/2-1)&-1\\
L_n&4&(n/2,n/2-2)&-1.
\end{array}
\]

Parity exchanges `j_L` and `j_R`.  A lowering proper-conformal generator has
compact degree `-1` and transforms as `(1/2,1/2)`.  Its six stable branch
families are

\[
E\to E,\quad A\to E,\quad A\to A,\quad
L\to E,\quad L\to A,\quad L\to L.
\]

Every allowed block has Wigner--Eckart multiplicity one.

## Exact all-level reduced coefficients

Let `n` be the source energy.  In the canonical C2f-A tower phases, the
lowering coefficients multiplying the normalized Condon--Shortley
intertwiners are

\[
\begin{aligned}
k_{EE}(n)&=\sqrt{\frac{2(n-1)(n+1)(n+3)}{n+2}}, &&n\ge3,\\
k_{AE}(n)&=\sqrt{\frac{8(n-1)}{(n-2)(n+2)}}, &&n\ge3,\\
k_{AA}(n)&=\sqrt{\frac{2(n-3)(n-1)(n+2)}{n-2}}, &&n\ge4,\\
k_{LE}(n)&=-\sqrt{\frac{2(n-3)}{n-2}}, &&n\ge4,\\
k_{LA}(n)&=\sqrt{\frac8{n-2}}, &&n\ge4,\\
k_{LL}(n)&=\sqrt{2(n-2)(n+1)}, &&n\ge5.
\end{aligned}
\]

These are the normalized-Wigner--Eckart form of the six Hamada--Horata
oscillator families governed by their `alpha`, `beta`, `gamma`, `A`, `B`,
and `C` coefficients; see
[Hamada--Horata, hep-th/0307008](https://arxiv.org/abs/hep-th/0307008) and
[Hamada, arXiv:0811.1647](https://arxiv.org/abs/0811.1647).  At energies
three and four they reproduce all seven
coefficients independently solved in C2f-A:

\[
\left(
4\sqrt{6/5},4/\sqrt5,\sqrt{35},\sqrt2,
3\sqrt2,-1,2
\right).
\]

The exact matrix algebra at every tested cutoff then checks the level
recursion rather than merely matching those seeds.

## Pairing and adjoint

The canonical form is

\[
J=+I_E\oplus(-I_A)\oplus(-I_L).
\]

Raising generators are constructed, not guessed, by

\[
K^+_M=J(K^-_M)^\dagger J.
\]

For every cutoff and both chiralities the executable verifies exactly:

\[
[D,K^-_M]=-K^-_M,
\qquad
[D,K^+_M]=K^+_M,
\]

the full compact `(1/2,1/2)` tensor covariance, and on the complete interior

\[
[K^-_M,K^+_N]=2\delta_{MN}D+2R_{MN}.
\]

It also checks `[K^-_M,K^-_N]=0` through the entire source buffer and
`[K^+_M,K^+_N]=0` wherever both raising steps remain inside it.  The compact
generators are `J`-self-adjoint.

## Why energy five is the first useful buffer

The global conformal generators have compact grades `0,+1,-1`; their ghosts
carry the opposite grades.  Therefore a complete action on a target matter
energy `Delta` needs one-particle oscillator data through `Delta+1`.
Consequently the energy-five buffer supplies every one-particle block needed
for the first energy-four global-BRST kernel/image calculation.  It contains
thirteen parity-reduced lowering blocks: the seven C2f-A blocks plus all six
new source-energy-five families.

As an independent inventory check, the energy-five and energy-six shells
have respectively `68` and `101` states per chirality.  The cumulative
energy-six dimension is therefore `235` per chirality, or `470` after parity;
this agrees with the separate Weyl-module character calculation.

This is a sufficiency statement about the one-particle generator input.  The
script does not yet second-quantize it, enumerate the energy-graded Fock and
ghost basis, combine it with local Diff `x` Weyl BRST, or compute physical
cohomology.

## Fail-closed boundary

The following claims are explicitly rejected:

1. closure on the top shell of a finite buffer;
2. certification of the unbounded all-level operator domain;
3. completion of the oscillator-plus-ghost BRST cohomology.

The corresponding command-line guards are

```bash
python3 symbolic/verify_conformal_generator_all_levels.py --require-top-shell-closure
python3 symbolic/verify_conformal_generator_all_levels.py --require-infinite-module
python3 symbolic/verify_conformal_generator_all_levels.py --require-fock-brst-cohomology
```
