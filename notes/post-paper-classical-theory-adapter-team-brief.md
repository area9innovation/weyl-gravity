# Post-paper classical team brief: critical-gravity Taub atlas

## Scheduling status

`DEFERRED_UNTIL_CURRENT_PAPER_IMPROVEMENT_SPRINT_IS_COMPLETE`

Do not interrupt the current Weyl/clock, causal, or paper-hardening work for
this programme.  Begin only from immutable certified inputs after the current
paper claims and open gates have stabilized.

## Shared question

Construct the strongest exact counterexample to the claim that the present
Taub/BV conclusions are peculiar to pure Weyl gravity:

\[
\boxed{\text{How do charge, linearization stability, and physical pairing
change across Einstein--Weyl and critical gravity?}}
\]

The target family is

\[
S[g]=\int\!\sqrt{-g}\left[
\frac{1}{2\kappa}(R-2\Lambda)+\alpha C^2
\right],
\]

including generic Einstein--Weyl, critical, and pure-Weyl limits.  Treat each
coupling locus as a distinct theory/phase-space entry, not as an informal
continuation.

## Primary objective

Produce `CRITICAL_GRAVITY_TAUB_AND_PAIRING_ATLAS_V1` on one exact Einstein
background, preferably a background already supported by the Einstein and
boundary packages.

### A. Freeze a reusable theory adapter

Export, without duplicating the authoritative classical BV implementation:

- fields, ghosts, antifields, degrees, and cyclic pairing;
- action normalization and exact coupling domain;
- background and boundary identifiers;
- minimal `q1`, the required `q2`/Taub rows, and reducibility generators;
- the selected Hamiltonian generator and its normalized charge;
- immutable input hashes and exact coefficient conventions.

The adapter must distinguish `LOCAL-ALGEBRAIC`, `REDUCED-MODE`, and
`LORENTZIAN-CAUSAL` results.

### B. Compute the linear spectral and pairing atlas

At generic, critical, and pure-Weyl couplings, determine exactly:

- factorization and characteristic roots of the metric operator;
- ordinary and generalized/Jordan solution classes;
- symplectic norms and cross-pairings;
- which roots are Einstein, massive, logarithmic, null, or extra Weyl;
- whether the critical limit is regular or singular in the transported
  pairing and contraction.

Do not infer the critical answer by taking a floating-point limit of a
noncritical diagonalization.

### C. Compute the Taub/linearization-stability map

For every background reducibility/Killing generator, derive the quadratic
Taub map from the action-derived `q2`.  Determine:

- the common zero fibre;
- which linear modes are nonintegrable;
- whether log/generalized modes satisfy the quadratic constraints;
- whether zero energy coincides with gauge, null pairing, or neither;
- dependence on compact versus boundary-supported phase spaces.

### D. Return a binary comparison

The atlas must end in one of these exact outcomes for each coupling locus:

- `LINEARIZATION_STABLE_WITH_DECLARED_BOUNDARY_DATA`;
- `TAUB_ZERO_RESTRICTION_REQUIRED`;
- `NONINTEGRABLE_MODE_WITH_DUAL_WITNESS`;
- `INPUT_OR_ANALYTIC_GATE_BLOCKED`.

## Definition of done

- Exact generator and independent verifier agree.
- At least one nontrivial critical/log-mode Taub component is calculated
  directly rather than inferred by symmetry alone.
- Pairing and Taub kernels share a declared normalization.
- The output contains a machine-readable atlas, mutation guards, hashes, and
  a human-readable comparison theorem.
- Every no-go includes an explicit mode or adjoint-cokernel witness.

## Claim boundary

This programme does not establish quantum unitarity, a Mannheim/PT inner
product, nonlinear closure beyond the computed Taub order, or a Lorentzian
boundary theorem unless separately certified.

## Handoff

Send the frozen adapter, `q1/q2`, pairing, and Taub atlas to:

- the nonlinear team for interacting branch-closure tests;
- the Einstein team for boundary charges and Lorentzian branch selection;
- the quantum team only after the classical import gate passes independently.
