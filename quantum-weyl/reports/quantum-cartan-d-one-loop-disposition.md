# First one-loop quantum D-Cartan disposition

Dependency tags: `LOCAL-ALGEBRAIC`, `EUCLIDEAN-SPECTRAL`.

This gate imports the completed local BV anomaly audit and asks the narrower
operator question

\[
A_D^{(1)}
 =[Q_0,\iota_{D,1}]
 +[Q_1,\iota_{D,0}]
 -\mathcal L_{D,1}.
\]

The target is

\[
H^0(\operatorname{Der}_{\rm adm}(\mathcal C),[Q_0,-]),
\]

not the local relative group \(H^{1,4}(s\mid d)\).  The sourced consistency
identity is

\[
[Q_0,A_D^{(1)}]
 =[[Q_0,Q_1],\iota_{D,0}]
  -\bigl([Q_0,\mathcal L_{D,1}]
         +[Q_1,\mathcal L_{D,0}]\bigr).
\]

## Coefficient-bearing bulk input

On the regular Bach locus the complete strict local BV quotient has the
one-loop vector

\[
\left(
 {199\over30},
 -{87\over20},
 0,
 0
\right)
\]

in the ordered basis
\(\omega C^2,\omega E_4,\omega C\widetilde C,\omega\Box R\).
The first two rows are nontrivial strict classes, the odd class has zero
coefficient, and the type-D row is exact with its stored primitive.

For the closed vacuum cylinder, \(\sigma_D=0\), so the direct local bulk
pullback is exactly zero.  For the Minkowski dilation cross-check,
\(\sigma_D=-1\), and the exact image is

\[
\left(-{199\over30},{87\over20}\right).
\]

Neither result is a quantum Cartan class: a local ghost-number-one density
does not acquire a canonical map to a degree-zero admissible derivation from
grading data alone.

## Theory-by-theory disposition

### Strict pure Weyl gravity

The one-loop local Euclidean QME source is nonzero in the complete
fixed-field-content quotient.  Consequently there is no nilpotent
renormalized \(Q_0+\hbar Q_1\) in the strict theory, and the first Cartan
defect is governed by the sourced identity rather than defining an unsourced
closed \(H^0\) class.  Its status is therefore
`UNDEFINED_ANALYTICALLY`, not `NONTRIVIAL_ANOMALY`.

The zero compact-cylinder pullback does not change that conclusion: it kills
only the displayed direct bulk term, not the unconstructed Ward insertion,
measure, boundary, or zero-mode contributions.

### Formal tau-adic compensator extension

The local one-loop Euclidean QME is restored in the declared formal extended
algebra, and the coefficient-bearing Wess--Zumino Hamiltonian piece is fixed.
However, the complete \(Q_1\) is not fixed.  The allowed
\(C(\widehat g)^2\) and \(R(\widehat g)^2\) finite counterterms give an exact
rank-two bulk ambiguity, while the finite/nonlocal remainder and the
renormalized BV-Laplacian or time-ordered-product contribution remain absent.
The repository also lacks \(\iota_{D,1}\), \(\mathcal L_{D,1}\), the
same-background compensator-extended classical contraction, and the
local-to-Cartan map.  The defect cannot yet be assembled, so its status is
again `UNDEFINED_ANALYTICALLY`.

### Positive Berger clock

The complete classical causal cyclic Cartan theorem through arity three uses

\[
K_{\rm Berger}=D-\Omega R.
\]

The raw cylinder \(D\) is affine about the rotating background and has a
nonzero arity-zero component.  It has no certified Cartan contraction.
Moreover, the Berger temporal clock variable is not the Wess--Zumino
compensator.  The pure-Weyl anomaly vector therefore cannot be placed on the
Berger \(K_{\rm Berger}\) carrier by matching the symbol `tau`, the background
name, or the word “Cartan.”  Both the \(K_{\rm Berger}\) and raw-\(D\) quantum
rows remain `UNDEFINED_ANALYTICALLY`.

## Exact missing-carrier theorem

No declared row currently supplies a closed, assembled,
coefficient-bearing \(A_D^{(1)}\).  The next required objects are:

1. a complete normalized renormalized \(\Gamma_1/Q_1\), including the
   renormalized-product contribution;
2. \(\iota_{D,1}\), \(\mathcal L_{D,1}\), an admissible observable complex,
   and the local-to-Cartan map;
3. a same-background tau-adic compensator-extended classical \(D\)
   contraction;
4. for Berger specifically, a coefficient-bearing quantum construction on
   that same clock carrier and an explicit bridge to \(K_{\rm Berger}\).

Two append-only Science Forge requests record the first three dependencies.
Until they land, `ZERO`, `EXACT_REMOVABLE`, and `NONTRIVIAL_ANOMALY` are all
forbidden promotions, and residual transfer remains forbidden.

## Reproduction

```bash
PYTHONPATH=quantum-weyl python3 -m cartan.quantum_cartan_d_one_loop_disposition_certificate --check
PYTHONPATH=quantum-weyl python3 -m cartan.verify_quantum_cartan_d_one_loop_disposition
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/cartan/tests/test_quantum_cartan_d_one_loop_disposition.py -v
```

This result is not a Lorentzian QME, Hadamard state, positivity, particle,
scattering, or unitarity theorem.

CLOSE-OUT: DONE — every currently evidence-supported bulk candidate and consistency relation is disposed across the strict, tau-adic, K_Berger, and affine raw-D rows; the missing operators are named by two typed requests and no Cartan class is over-promoted.
EVIDENCE: quantum-weyl/cartan/certificates/QUANTUM_CARTAN_D_ONE_LOOP_DISPOSITION.json
