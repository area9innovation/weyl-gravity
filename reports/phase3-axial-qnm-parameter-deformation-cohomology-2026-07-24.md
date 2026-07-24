# Phase 3 axial QNM parameter-deformation cohomology

## Result

The proposed geometric-parameter shortcut does not supply a new rational
deformation class for the certified repeated-spin-two extension.

Starting from the consistently dimensionful Schwarzschild \(\ell=2\)
ingoing-Eddington--Finkelstein Regge--Wheeler companion, the exact trace
residues of

\[
E_{\rm RW}
-q_\omega\partial_\omega A_{\rm RW}
-q_M\partial_M A_{\rm RW}
\]

at \(r=2\) and \(r=\infty\) force

\[
q_\omega+\omega q_M=0.
\]

The surviving combination is itself an exact rational connection
coboundary:

\[
\partial_M A_{\rm RW}
-\omega\partial_\omega A_{\rm RW}
=D_A B_{\rm scale},
\qquad
B_{\rm scale}=-rA_{\rm RW}-\operatorname{diag}(0,1),
\]

at \(M=1\).  Equivalently, in \(x=r/M\) and
\(\Omega=M\omega\), the scalar operator has no remaining mass dependence.

Therefore

\[
E_{\rm RW}\in
\operatorname{span}_{\mathbb Q(i,\omega)}
\{[\partial_\omega A_{\rm RW}],[\partial_M A_{\rm RW}]\}
\]

holds only if \([E_{\rm RW}]=0\) already.  Mass variation does not explain
the extension by a nontrivial geometric deformation.

## Exact residue ledger

For the candidate difference, the trace residues are:

| Point | Residue |
|---|---:|
| \(r=0\) | \(0\) |
| \(r=2\) | \(4i(q_\omega+\omega q_M)\) |
| \(r=2i/\omega\) | \(0\) |
| \(r=\infty\) | \(-4i(q_\omega+\omega q_M)\) |

The horizon and infinity conditions are the same constraint with opposite
orientation.

## Scope refusals

- No \(\partial_\Lambda A\) is defined by the frozen Schwarzschild input.
  Varying cosmological \(\Lambda\) requires a separately certified
  Schwarzschild--(A)dS family and a different endpoint problem.
- \(\ell=2\) is a discrete harmonic label.  An auxiliary analytic
  continuation in \(\ell(\ell+1)\) is not a physical parameter derivative
  and is outside this audit.

## Claim boundary

This result does **not** decide whether \(E_{\rm RW}\) is a pure rational
\(D_A\)-coboundary.  It does not compute \(\beta_n\), select a QNM Smith
type, or establish any resolvent-pole or generalized-ringdown claim.

## Verification

```bash
python3 -m \
  black_hole_programme.phase3.axial_qnm_parameter_deformation_cohomology_v1.produce
python3 -m \
  black_hole_programme.phase3.axial_qnm_parameter_deformation_cohomology_v1.verify
python3 -m unittest -v \
  black_hole_programme.phase3.axial_qnm_parameter_deformation_cohomology_v1.tests.test_cohomology
```

CLOSE-OUT: DONE — Exact residues and the scale-covariant gauge identity prove that Schwarzschild mass adds no independent rational deformation class.
EVIDENCE: black_hole_programme/phase3/axial_qnm_parameter_deformation_cohomology_v1/certificate.json
