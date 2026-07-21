# Repaired q70 low-j and stabilizer health

## Result

The exceptional Peter--Weyl sector of the repaired 70-row Berger carrier is
now complete.  The exact spatial gauge-rank census has only two exceptional
representations:

\[
j=0,\qquad j=1.
\]

The fixed-\(m\) nullity is one in each exceptional representation.  Including
the \(m\)-degeneracy gives

\[
1\cdot 1+3\cdot 1=4,
\]

which exhausts the Berger spatial Killing algebra
\(\mathfrak{su}(2)_L\oplus\mathfrak u(1)_R\).  Direct ranks through
\(2j=6\), together with the exact isometry-algebra decomposition, show that
there are no further stabilizer representations.

The calculation uses invariant-coframe tensor components with scalar
Peter--Weyl coefficients.  It therefore retains all ten field-component rows
at \(j=0\) and all thirty all-\(k\) rows at \(j=1\).  It does not delete rows
by importing the low-\(j\) availability rules of a different irreducible
TT/vector tensor-harmonic basis.  Relations and absent physical directions
are decided by the exact gauge rank and quotient instead.

## Zero-frequency stabilizers

At both \(j=0\) and \(j=1\), the full \(z=0\) complex has

\[
\dim(H^{-1},H^0,H^1,H^2)=(1,1,1,1)
\]

per fixed \(m\).  The descended graded BV pairing has rank four and zero
radical.  This is a stabilizer torsion quartet, not a propagating particle.
Ordinary positive/negative inertia is not defined for this graded pairing;
the certificate records that distinction explicitly rather than assigning a
spurious symmetric-form signature.

At \(j=1\), all internal weights \(k=-1,0,+1\) are retained.  The exact
raising/lowering matrices reject an isolated \(k=0\) carrier.

## Nonzero-frequency physical quotients

The \(j=0\) quotient is a 7-by-7 exact physical Hessian.  Its characteristic
divisor contains

\[
3200z^6+12600z^4+7605z^2-7812.
\]

As a polynomial in \(y=z^2\), it has two negative roots and one positive
root.  The positive root gives a genuine real exponential pair.  Its
factor-field nullity is one, its characteristic pairing has zero radical,
and the sixth-order action representative has inertia \((3,3,0)\).

The \(j=1\) quotient is a 21-by-21 exact physical Hessian per fixed \(m\).
Two sectors contain complex-frequency roots.  The first is

\[
3240z^4+113013z^2+986578,
\]

whose \(y\)-discriminant is \(-14112711\).  The second is the multiplicity-two
degree-ten factor

\[
\begin{aligned}
&7558272000z^{10}+268203182400z^8+3648301495200z^6\\
&\quad+23672119906305z^4+73066019605029z^2+85345353120218.
\end{aligned}
\]

It has three negative real \(y\)-roots and two nonreal \(y\)-roots.  The two
real action sectors have exact two-copy inertias \((4,4,0)\) and
\((8,12,0)\).  For every nonzero factor at \(j=0,1\), the exact factor-field
nullity equals the determinant exponent.  Hence the elementary divisors are
simple and there is no polynomial-time Jordan partner.  The inherited cyclic
pairing descends without a radical.

## Charges and contractible directions

The spatial stabilizers are local Diff reducibilities.  They are not the
global charged \(R_{\rm rel}\) action-angle carrier.  On the stabilizer rows,

\[
D=z=0,\qquad R_{\rm rel}=0,\qquad
K=D-\frac34R_{\rm rel}=D.
\]

The repaired diagonal-\(U(1)\) block is checked separately.  Its 16 rows per
Peter--Weyl weight satisfy the exact contraction

\[
q_{16}S_{16}+S_{16}q_{16}=1,
\]

with nondegenerate cyclic pairing and zero local Gauss charge.  It contributes
no physical cohomology.  Fixing \(Q_{\rm rel}\) removes the separate global
action-angle pair, but it does not remove the nonzero-frequency \(j=0\)
exponential or \(j=1\) Hamiltonian-Hopf modes.

## Verification architecture

The producer specializes and hashes the complete all-\(k\) unary, constructs
the full zero-frequency quotient and nonzero-frequency physical Hessians, and
computes the exact factor and root ledgers.  The independent verifier does not
import the producer.  It reconstructs the Wigner generators and PBW matrices,
materializes the full 70-row contraction and cross-\(m\) cyclic pairing at
both exceptional representations, recomputes the zero-mode pairing and
physical determinants, and checks every factor-field rank.

The independent verifier is process-isolated by scientific stage.  Its fast
rails are each below twelve seconds; the full determinant and contraction
stages are run for the affected certificate chain without turning an
exhaustive replay into the per-edit loop.

## Boundary

This is an exact same-background linear classification of the repaired q70
exceptional representations.  It completes the low-\(j\) input required by
the repaired-q70 health assembly.  It does not establish nonlinear
instability or finite-time blow-up, nor any observer, Hadamard, anomaly, QME,
particle, positivity or unitarity claim.

CLOSE-OUT: DONE — every repaired-q70 low-j/stabilizer exception is classified and glued to the generic representation family

EVIDENCE: `TWO_PHASE_COUNTERFLOW_REPAIRED_Q70_LOW_J_STABILIZER_HEALTH_V1.json`; payload; exact producer; process-isolated independent direct-matrix verifier; strict schemas; mutation and scoped tests; tier receipt; four-row fail-closed atlas fragment.
