# C2b: proper-conformal Taub multiplets from the mixed curvature seeds

## Result and scope

The executable certificate is
`symbolic/verify_conformal_taub_multiplets.py`.  It takes the two direct,
action-normalized C2a curvature values

\[
\langle E_+|Q_-|A_+\rangle=-{\sqrt5\over5\pi},\qquad
\langle A_-|Q_-|L_-\rangle={\sqrt{10}\over5\pi}
\]

and reconstructs their complete proper-conformal magnetic multiplets by
Wigner--Eckart.  This closes all four \((q_L,q_R)=(\pm\tfrac12,
\pm\tfrac12)\) components in these two low-energy mixed blocks, including
parity and reverse-kernel partners.

It does **not** compute the full Taub moment map.  In particular, it does not
determine `Q[A,A]`, `Q[E,L]`, the seven compact-energy-preserving Killing
charges, other oscillator towers, anomalous real-field bilinears, the
quadratic zero locus, or global BRST cohomology.  The result reconstructs two
mixed reduced matrix elements; it does not exclude an `A`, `AA`, `EL`, or
any other complete state.

## Representation data

The modes touched by the curvature calculation carry

\[
\begin{array}{c|c|c}
\text{mode}&\Delta&(j_L,j_R)\\ \hline
E_+&2&(2,0)\\
A_+&3&(\tfrac32,\tfrac12)\\
A_-&3&(\tfrac12,\tfrac32)\\
L_-&4&(0,2).
\end{array}
\]

The signed-frequency-minus proper conformal charge transforms as
\((\tfrac12,\tfrac12)\) and lowers compact energy by one.  The two seeded
blocks are therefore

\[
(\tfrac32,\tfrac12)\otimes(\tfrac12,\tfrac12)
\supset(2,0),
\]

and

\[
(0,2)\otimes(\tfrac12,\tfrac12)
\supset(\tfrac12,\tfrac32).
\]

Each target occurs with multiplicity one.  Spatial representation theory
therefore fixes every magnetic entry once one reduced coefficient is known.

In the exact Clebsch--Gordan convention used by the cylinder scripts,

\[
\begin{split}
&\langle j'_Lm'_L,j'_Rm'_R|Q_{q_Lq_R}|
j_Lm_L,j_Rm_R\rangle\\
&\qquad={\cal R}\,
C^{j'_Lm'_L}_{j_Lm_L,\frac12q_L}
C^{j'_Rm'_R}_{j_Rm_R,\frac12q_R}.
\end{split}
\]

Both direct curvature seeds belong to

\[
(q_L,q_R)=(\tfrac12,-\tfrac12).
\]

For `A+ -> E+`, the seed Clebsch product is \(1/\sqrt2\), so

\[
\boxed{{\cal R}_{AE}=-{\sqrt{10}\over5\pi}}.
\]

For `L- -> A-`, it is \(2/\sqrt5\), so

\[
\boxed{{\cal R}_{LA}={\sqrt2\over2\pi}}.
\]

Parity exchanges left and right and supplies the `A- -> E-` and `L+ -> A+`
seed entries with the same reduced coefficients in the fixed intrinsic-phase
convention.  The remaining magnetic entries follow from Wigner--Eckart, not
from additional curvature runs.  The reverse curvature seeds agree with the
ordinary coefficient-kernel daggers.  This is not yet a physical-adjoint
statement: the globally reduced pairing is one of the missing C2b outputs.

## Exact matrix checks

On the low one-particle sum

\[
E_+\oplus E_-\oplus A_+\oplus A_-\oplus L_+\oplus L_-,
\]

of dimension 36, every reconstructed component has rank 16 and satisfies

\[
[D,Q_{q_Lq_R}]=-Q_{q_Lq_R}.
\]

The script checks every left and right ladder identity,

\[
[J_L^z,Q_{q_Lq_R}]=q_LQ_{q_Lq_R},
\]

\[
[J_L^+,Q_{q_Lq_R}]
=\sqrt{(\tfrac12-q_L)(\tfrac32+q_L)}
Q_{q_L+1,q_R},
\]

and the analogous right and lowering relations.  It also constructs the
exact parity permutation and verifies

\[
P Q_{q_Lq_R}P=Q_{q_Rq_L}.
\]

Projecting the reconstructed component back to the original ordered basis

```text
(E_+, A_+, A_-, L_-)
```

reproduces both independently assembled C2a matrices, including the ordinary
kernel relation \(M_+=M_-^\dagger\).  The identification of an operator
adjoint requires the reduced form; for a provisional nondegenerate oscillator
form it would act on \(T=J^{-1}M\), not on `M` alone.

The uncomputed magnetic entries use the standard Condon--Shortley
Clebsch--Gordan convention and the intrinsic parity phase fixed by the direct
seed rails.  The ladder checks certify the resulting abstract
`SU(2)_L x SU(2)_R` tensor.  A coordinate-level match of every generated
entry to the cylinder harmonic and conformal-Killing ladder conventions is
still a hardening task, not an additional independent curvature result.

## Why this is a quadratic constraint, not state deletion

On the four seed coordinates, the known part of the lowering moment map is

\[
\mu_-^{\rm known}
=-{\sqrt5\over5\pi}\,\bar e_+a_+
+{\sqrt{10}\over5\pi}\,\bar a_-\ell_-.
\]

Consequently a mixed `E/A` superposition has a nonzero charge, but distinct
mixed blocks can cancel.  The exact test vector

\[
e_+=a_+=a_-=1,\qquad \ell_-={1\over\sqrt2}
\]

makes every reconstructed quadratic value
\(v^\dagger M_qv\) and \(v^\dagger M_q^\dagger v\) vanish.  It is not a
common operator kernel: generally \(M_qv\ne0\).  This is only a point on the
**partial** quadratic cone; unknown charge blocks may still act on it.  Its
purpose is to certify the logical distinction: nonzero mixed entries do not
imply that either basis mode is individually excluded.

## Energy grading and global BRST

The proper conformal generators do not act inside one fixed compact-energy
shell.  Their lowering and raising pieces connect neighboring energies,
whereas time translation and the six rotations preserve energy.  The global
constraint problem must therefore be formulated as an energy-graded complex,
not as fifteen unrelated matrices restricted to the provisional energy-six
oscillator block.

Hamada's cylinder BRST construction makes this algebraic structure explicit:
its global charge contains compact-energy, rotation, proper-conformal, and
global-ghost terms, with the proper generators appearing together with their
adjoints.  It is a useful template, not a result imported here, because that
paper treats a broader conformal-gravity/Riegert system rather than this
pure-Weyl reduced complex:
[arXiv:1202.4538](https://arxiv.org/abs/1202.4538).

The linearization-stability interpretation of the quadratic moment map on a
compact Cauchy slice is consistent with the higher-curvature analysis of
Altas and Tekin:
[arXiv:1705.10234](https://arxiv.org/abs/1705.10234).

## Next obligations

The two layers must remain separate.

### C2b-classical

1. Reconstruct the remaining reduced Taub elements for all relevant mode
   towers and multiplicity sectors.
2. Add the seven compact-energy-preserving Killing-charge kernels and any
   real-field anomalous bilinears.
3. Assemble the fifteen quadratic functions \(\mu_A(z,\bar z)\).
4. Classify \(\mu^{-1}(0)\) modulo the global conformal action.

### C2b-quantum

1. Construct the pure-Weyl global ghost system and nilpotent global BRST
   operator with its compact-energy grading.
2. Combine it consistently with the local Diff x Weyl BRST complex.
3. Determine the ghost-number-zero cohomology and the induced pairing.
4. Only then decide whether the provisional `AA`, `EA`, and `EL` oscillator
   representatives survive, require dressing, or disappear.

Until both layers are supplied, no t-channel inverse, quartic physical
amplitude, or metric-deformation obstruction is defined.

## Reproduction

Run

```bash
python3 symbolic/verify_conformal_taub_multiplets.py
```

The two scope guards must fail:

```bash
python3 symbolic/verify_conformal_taub_multiplets.py --require-full-moment-map
python3 symbolic/verify_conformal_taub_multiplets.py --require-global-brst
```
