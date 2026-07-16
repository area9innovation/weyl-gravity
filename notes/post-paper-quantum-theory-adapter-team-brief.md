# Post-paper quantum team brief: Riegert--Wess--Zumino completion

## Scheduling status

`DEFERRED_UNTIL_CURRENT_PAPER_IMPROVEMENT_SPRINT_IS_COMPLETE`

Finish and freeze the current anomaly-coefficient and paper-improvement work
before opening this programme.  Do not add a compensator merely because a
candidate cohomology class exists; consume the computed coefficients.

## Shared question

The even antifield-zero candidate quotient contains the two classes

\[
[\omega C^2],\qquad [\omega E_4],
\]

while `[omega Box R]` is exact.  Determine whether a Riegert/Wess--Zumino
extension removes the actual quantum obstruction:

\[
\boxed{\text{Does the extended BV theory restore the QME and the quantum
Cartan identity for }D?}
\]

## Primary objective

Produce `RIEGERT_WZ_QME_AND_D_CARTAN_AUDIT_V1` for the first matter content
with fully certified anomaly coefficients.

### A. Freeze the coefficient input

Record separately:

- coefficients of `omega C^2` and `omega E4`;
- trivial/scheme-dependent `omega Box R` terms;
- measure and zero-mode contributions;
- dependency tag and regularization scheme;
- whether the result is pure Weyl, Weyl plus matter, or compensator-extended.

No Wess--Zumino conclusion may be inferred from a candidate-basis result
without coefficients.

### B. Import an authoritative classical compensator extension

Require a classical snapshot containing the extra field, gauge transformations,
BV pairing, `q1`, and relevant nonlinear rows.  Pass the classical import gate
before constructing quantum corrections.  Do not build a second classical
model inside `quantum-weyl/`.

### C. Solve the extended local cohomology problem

Determine whether the coefficient-weighted anomaly is:

- zero;
- exact in the original complex;
- nontrivial originally but exact after Riegert/WZ extension;
- still nontrivial in the extended admissible complex.

Retain explicit primitives or normalized dual witnesses.  Track the Euler
and Weyl-square components separately.

### D. Restore the QME before residual transfer

Construct the allowed counterterm/WZ functional and verify

\[
\frac12(S,S)-i\hbar\Delta S=0
\]

to the declared order.  Only after `QME_RESTORED` may the team compute the
quantum Cartan defect and ask whether

\[
[Q_\hbar,\iota_{D,\hbar}]=\mathcal L_D
\]

holds in the extended theory.

### E. Matter-selection comparison

If the defect depends on matter content, solve the exact coefficient
cancellation equations for declared combinations of scalars, fermions, and
Yang--Mills fields.  Distinguish coefficient cancellation from compensator
trivialization.

## Definition of done

- Exact coefficient-bearing anomaly representative.
- Original-versus-extended cohomology comparison.
- Explicit WZ primitive/counterterm or obstruction witness.
- Lifecycle state reported honestly as `CLASSIFIED`,
  `COEFFICIENT_COMPUTED`, `QME_RESTORED`, or later—never skipped.
- No residual quantum pairing or (D)-quotient claim before QME restoration.
- Machine certificate, independent verifier, hashes, assumptions, and
  scheme ledger.

## Secondary comparison

After the QME audit, test whether the Mannheim/PT metric defines a
BRST-compatible quantum adjoint on the same physical complex.  Keep that
question separate from Wess--Zumino anomaly cancellation.

## Claim boundary

`LOCAL-ALGEBRAIC` anomaly cancellation is not a Lorentzian quantum theory.
No `LORENTZIAN-CERTIFIED` claim exists without renormalized Lorentzian
time-ordered products, a compatible state, and causal Ward identities.
