# Two-phase counterflow causal BV parent V2

## Result

`TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V2` reissues the selected Berger
counterflow parent as an honest integer-graded cyclic BV complex.  The V1
artifacts remain immutable historical evidence; every V2 consumer must import
the new hashes explicitly.

The repaired 70 rows have degree ranks

\[
(6,29,29,6),
\]

and all 317 nonzero q70 operator blocks have compact-degree shift \(+1\).

## Action and cotangent derivation

The diagonal-U1 coordinate BRST rows are

\[
Q\chi=c,
\qquad
QA=dc,
\qquad
Q\bar c=b.
\]

In the invariant variables

\[
B=A-d\chi,
\qquad
H=\chi^*+\delta A^*,
\]

the action density and Noether identity are

\[
-2\langle B,B\rangle,
\qquad
E_A=-4B,
\qquad
E_\chi=4\delta B,
\qquad
E_\chi+\delta E_A=0.
\]

The q54 matrix is the linear BV chain acting on column generators, hence it
is contragredient to the coordinate-vector-field presentation.  Applying the
same cotangent convention to the U1 rows gives

```text
c_U1       -> chi
B_mu       -> -4 A_star_mu
H          -> c_U1_star
b           -> bar_c
bar_c_star  -> -b_star
```

These arrows are the transpose of the V1 multiplet table.  No coefficient or
sign was fitted to the previously observed degree defects.

## Explicit repaired block

The component order is

```text
chi, c_U1,
A_star_0..3, B_0..3,
c_U1_star, H,
bar_c, b, b_star, bar_c_star.
```

The repaired q16 and S16 obey

\[
q_{16}^2=0,
\qquad
q_{16}S_{16}+S_{16}q_{16}=1_{16}.
\]

The explicit canonical odd pairing has partners

```text
chi -- H
c_U1 -- c_U1_star
B_mu -- A_star_mu
bar_c -- bar_c_star
b -- b_star
```

with the relative c/c-star sign fixed by cyclicity.  Its matrix has rank 16,
and both q16 and S16 pass their exact cyclic identities.  All coefficients
are rational and real.

## Full direct sum

The package serializes the full PBW matrices

\[
q_{70}=q_{54}\oplus q_{16},
\qquad
S_{70}=S_{54}\oplus S_{16},
\]

together with the 70-row pairing and the 70-to-26 contraction.  The U1 rows
are killed by the projection and absent from the retained inclusion.  Thus

\[
\pi_{26}\iota_{70}=1_{26},
\qquad
q_{70}S_{70}+S_{70}q_{70}
=1_{70}-\iota_{70}\pi_{26},
\]

with the inherited side conditions.

For both causal orientations,

\[
\Lambda_{70}^{\pm}
=\Lambda_{54}^{\pm}\oplus S_{16}.
\]

The first summand has the pinned q54 same-sided causal and cyclic-adjoint
theorem.  The algebraic S16 kernel is supported on the diagonal and is
admissible in both directions.  No spatial inverse is introduced and all
zero modes remain present.

The corrected U1 block commutes with the imported helical action and

\[
K=D-\Omega R_{\rm rel},
\qquad
\Omega=\frac34.
\]

Unrestricted D remains charged and is not quotiented.

## Independent replay and mutations

The independent verifier does not import the producer.  It reconstructs q16
from the original action/BRST/Noether rows, expands the full component basis,
and checks the stored q/S/pairing matrices and content hashes.  It rejects:

- the old transposed-back orientation by its degree \(-1\) shifts;
- deleting any one arrow through the contraction identity;
- a canonical-pairing sign mutation through cyclicity;
- a row-degree mutation through homogeneity;
- a \(-1/4\to-1/5\) homotopy mutation through contraction.

It also evaluates the exact `two_j=1` q54 Wigner block and the repaired q16
tensor identity, independently confirming nilpotency in the finite harmonic
representation.

## Receiver policy

`TWO_PHASE_COUNTERFLOW_CAUSAL_BV_RECEIVER_CONTRACT_V2` binds Observer,
Nonlinear, Bridge and Quantum consumers to the V2 parent content hash.
V1 parent, receiver and q2 hashes are historical and are rejected for V2
claims.  In particular, nonlinear q2 must be rederived or independently
replayed against the repaired unary hash.

## Boundary

This closes the graded cyclic unary-parent repair.  It does not compute the
physical q70 quotient, mode signs, characteristics, q2, observers, Hadamard
data, anomaly coefficients, a QME, particles, positivity or unitarity.

CLOSE-OUT: DONE — the complete stop condition is met

EVIDENCE: `TWO_PHASE_COUNTERFLOW_CAUSAL_BV_PARENT_V2.json`, its payload and receiver, explicit operator hashes, strict schemas, independent action/cotangent verifier, scoped tests, tier receipt, and fail-closed atlas fragment.
