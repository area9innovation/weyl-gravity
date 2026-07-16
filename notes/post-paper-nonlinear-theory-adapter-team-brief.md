# Post-paper nonlinear team brief: Mannheim-metric interaction audit

## Scheduling status

`DEFERRED_UNTIL_CURRENT_PAPER_IMPROVEMENT_SPRINT_IS_COMPLETE`

Do not replace the current support-local Berger `q2/D` and paper-improvement
work with this programme.  Begin after the current nonlinear claim boundary
is frozen and the relevant classical inputs are immutable.

## Shared question

Test the strongest field-theoretic version of the Bender--Mannheim proposal:

\[
\boxed{\text{Can the positive PT/CPT metric descend through BRST/Taub
reduction and remain compatible with interactions?}}
\]

The oscillator metric is an input hypothesis, not the answer.  The target is
the gauge-reduced gravitational complex.

## Primary objective

Produce `MANNHEIM_METRIC_BRST_Q2_COMPATIBILITY_V1` for one exact fourth-order
gravity setting already represented in the repository.

### A. Import the metric without reconstructing a competing copy

Consume the certified modewise Bender--Mannheim metric/operator and record:

- its real form and domain;
- equal-frequency/Jordan behavior;
- locality or mode dependence;
- adjoint convention and relation to the existing BV/symplectic pairing;
- content hashes and source normalization.

Reject any implicit identification of the oscillator Hilbert space with
physical BRST cohomology.

### B. Test unary descent

Determine exactly whether the metric is compatible with:

- the local BRST differential `q1`;
- the homological projection and contraction;
- the Taub-zero/derived quotient;
- the residual conformal action and selected time generator.

The required identities must be written in the declared graded-adjoint
convention.  If descent fails, retain the first nonzero row and a normalized
dual witness.

### C. Test interacting cyclicity

Using an action-derived `q2`, calculate whether the candidate metric makes
the cubic vector field cyclic/pseudo-Hermitian on the admitted complex.
Separate:

- failure before the local gauge quotient;
- failure introduced by the Taub restriction;
- failure only in nonzero-weight or infinite all-weight sectors;
- failure caused by a singular equal-frequency limit.

The already-certified finite nonzero-weight Berger closure no-go forbids
using a finite cyclic mode block as a substitute for the infinite/local
test.

### D. Return a binary verdict

The result must be one of:

- `METRIC_DESCENDS_AND_Q2_IS_CYCLIC_ON_DECLARED_SECTOR`;
- `UNARY_BRST_DESCENT_OBSTRUCTED`;
- `INTERACTING_CYCLICITY_OBSTRUCTED`;
- `INFINITE_OR_SUPPORT_LOCAL_COMPLETION_REQUIRED`.

An obstruction should be preferred over an ever-larger formal ansatz when a
finite exact witness exists.

## Secondary objective

After the Mannheim audit, consume the classical critical-gravity adapter and
test whether the Einstein, massive, and logarithmic branches are closed under
the first nontrivial transferred bracket.  Produce an explicit correction or
obstruction; do not argue from the free spectrum alone.

## Definition of done

- Exact metric import and independent hash/identity verification.
- A complete unary descent ledger.
- At least one nonzero action-derived cubic compatibility calculation.
- Exact primitive or normalized obstruction witness.
- Separate verdicts for unreduced, Taub-zero, and physical/cohomological
  sectors.
- No promotion from `REDUCED-MODE` to `LORENTZIAN-CAUSAL`.

## Claim boundary

Compatibility of isolated Pais--Uhlenbeck modes does not prove a positive
interacting gravitational Hilbert space.  Conversely, failure in one
declared real form does not refute every possible antilinear completion.
