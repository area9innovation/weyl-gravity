# Local dimension-four curvature-candidate receipt

Date: 2026-07-15

Dependency tag: `LOCAL-ALGEBRAIC`

Result state: `CANDIDATES_GENERATED_NOT_COHOMOLOGY`

Classical snapshot: `UNFROZEN`

## Outcome

The first derivative-bounded one-loop curvature ansatz is now generated
directly at mass dimension four.  Exhausting all 105 pairings of two Riemann
tensors gives four intrinsic-symmetry monomials; two generated algebraic
Bianchi rows have rank one, leaving the exact three-dimensional span

```text
Riemann^2, Ricci^2, R^2.
```

The infinitesimal Weyl variation is represented before integration by parts
on `Ricci^{ab} nabla_a nabla_b omega` and `R Box omega`.  The contracted
Bianchi identity and integration by parts identify the first carrier with
one half of the second.  The resulting exact variation row is

```text
[-4, -4, -12],
```

whose kernel has dimension two.  The conventional vectors

```text
C^2 = (1, -2, 1/3),   E4 = (1, -4, 1)
```

are independently verified to span that computed kernel.  Thus they are
normalizations of a generated kernel, not a hard-coded kernel dimension.

## Target-native Weyl and parity sectors

The dimension-four Weyl targets are generated independently of the mapped
order-six Riemann quotient.  In both parity sectors, 105 pairings reduce to
two tracefree ambient monomials; two target-native Bianchi relations have
rank one, leaving one even and one odd class.

The odd calculation uses a compressed `DualWeyl` carrier.  The certificate
expands it as epsilon-over-two times Weyl and verifies equality for all four
choices of Weyl factor and antisymmetric index pair.  It also rechecks
`star^2=+1` in Euclidean signature and `star^2=-1` in Lorentzian signature.
This makes the odd enumeration exhaustive within the quadratic Weyl sector
without materializing the raw single-epsilon orbit.

Cotton remains present in the target differential identity.  A separate
complete-contraction enumeration proves that one derivative of tracefree
Cotton supplies no scalar at mass dimension four.  This does not compute the
unrestricted higher-derivative Weyl--Cotton quotient.

## Generated catalogues

The ghost-number-zero catalogue contains `CT_C2`, `CT_E4`,
`CT_C_DUAL_C`, and `CT_BOX_R`.  `Box R` carries the explicit divergence
primitive `nabla^a R`.  Multiplying the four densities by the exact odd
rank-zero Weyl ghost generates the ghost-number-one catalogue.  The type-D
candidate has the explicit integrated trivialization

```text
omega Box R = -(1/12) s(R^2) mod d.
```

The Euler candidate remains distinct from the strictly Weyl-invariant
densities.  Its first Chern--Weil transgression and both frozen-carrier
ordinary-bidegree connecting equations are now certified.  The independent
epsilon-contracted identification of the head with `omega E4` remains
pending.  Universal Diff completion and intrinsic Weyl descent are recorded
in separate fields.

## Claim boundary

This is a finite curvature-candidate theorem, not the complete
`H^{0,4}(s|d)` or `H^{1,4}(s|d)` theorem.  Still `NOT_COMPUTED` are:

- the epsilon-contracted Euler-head identification and mixed sectors;
- antifield/Koszul--Tate, equation-of-motion, and gauge-fixing sectors;
- nontriviality of the `C^2`, Euler, and parity-odd anomaly candidates;
- anomaly or counterterm coefficients and QME restoration;
- cylinder restriction and residual transfer.

Gate A remains fail-closed.  The classical team's causal-homotopy progress
is logically separate from the portable `Q0`, `iota_cl`, `pi_cl`, `S_cl`,
pairing, and adjacent-degree exports needed by the quantum import.

## Verification receipt

| Tier | Command/rail | Elapsed | Result |
|---|---|---:|---|
| 0 | compile changed Python, parse/validate new JSON, scoped diff check | under 3 s | pass |
| 1 | focused Weyl-target/candidate/certificate tests | under 2 s | 12 pass in 1.57 s |
| 1 | complete local-BV unit rail | 36.83 s wall | 124 pass in 36.06 s |
| 1 | new certificate under hash seeds `1,7,123`, parallel | 3.2 s wall | pass |
| 2 | two-pass paper build in isolated output directory | 2.3 s | pass; no unresolved references |

The complete local rail remains below the agreed 60-second escalation
threshold.  The exact target analyses use in-process caching and
content-hashed relation receipts; a persistent disk cache is not yet
justified.  Tier 3 was not triggered because this is an isolated
local-algebra candidate result, not a classical freeze, complete cohomology
theorem, lifecycle promotion beyond candidate classification, or release.

## Machine receipts

- `quantum-weyl/local_bv/certificates/LOCAL_DIMENSION_FOUR_CANDIDATE_CATALOGUE_CERTIFICATE.json`;
- `quantum-weyl/counterterms/ghost_number_0/COUNTERTERM_CANDIDATES.json`;
- `quantum-weyl/anomalies/ghost_number_1/ANOMALY_CANDIDATES.json`;
- `quantum-weyl/certificates/COUNTERTERM_CANDIDATES_DIMENSION_FOUR.json`;
- `quantum-weyl/certificates/ANOMALY_CANDIDATES_DIMENSION_FOUR.json`.

## Next local gate

Implement the longitudinal Diff--Weyl action on the generated density
carriers and solve the full antifield-independent descent.  The
Koszul--Tate/antifield completion remains queued behind the classical freeze.
