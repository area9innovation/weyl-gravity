# Local Weyl--Schouten--Cotton foundation receipt

Date: 2026-07-15

Dependency tag: `LOCAL-ALGEBRAIC`

Result state: `WEYL_DECOMPOSITION_INFRASTRUCTURE_VERIFIED`

Classical snapshot: `UNFROZEN`

## Outcome

The local tensor layer now represents the metric, Schouten tensor, and Cotton
tensor explicitly.  The fixed conventions are

```text
P_ab = (R_ab - R g_ab/(2(n-1)))/(n-2)
A_abc = nabla_b P_ca - nabla_c P_ba
R_abcd = C_abcd + g_ac P_bd - g_ad P_bc
                    - g_bc P_ad + g_bd P_ac
```

The Ricci decomposition has six exact canonical terms.  Its differentiated
version also has six terms because metric compatibility removes `nabla g`.
The Cotton tensor is antisymmetric in its last pair, cyclic, and tracefree in
the irreducible quotient.

## Differential sign audit

The cyclic Weyl identity is stored with three `nabla C` terms and six
metric--Cotton terms.  It is not accepted from a typed formula alone.  The
certificate expands every Cotton tensor into its two Schouten-derivative
terms, independently cyclically differentiates the exact Ricci decomposition,
removes the differential Riemann Bianchi row, and compares the resulting
15-term expressions.  Their canonical hashes agree exactly.

The conventions were cross-checked against Boulanger's
[Weyl-covariant tensor calculus](https://arxiv.org/abs/hep-th/0412314) and
Garcia, Hehl, Heinicke, and Macias's
[Cotton tensor analysis](https://arxiv.org/abs/gr-qc/0309008).  These sources
fix notation and provide an independent check; the machine equality is
generated from the repository's declared Ricci decomposition.

## Removed unsafe shortcut

The pre-existing `replace_riemann_by_weyl` primitive remains available for
algebraic curvature tensors.  It now rejects a Riemann factor carrying any
covariant derivative.  A direct differentiated replacement would erase the
Schouten/Cotton completion and could create false relations in the derivative
sectors.  Callers must now use the explicit decomposition.

## Full-Weyl Hodge witness

The tensor engine can dualize either antisymmetric pair of an actual Weyl
factor by inserting `epsilon/2`.  This moves an even monomial into the odd
parity block.  Reducing the two epsilons in `(*^2 C).C` gives exactly

```text
EUCLIDEAN    + C.C
LORENTZIAN   - C.C
```

No floating-point or sampled-component computation enters these identities.

## Claim boundary

This hardens the substrate for the next calculation; it does not perform that
calculation.  The following remain `NOT_COMPUTED`:

- the tracefree-Weyl image and kernel of the eight-dimensional 4D Riemann
  quotient;
- the parity-odd single-epsilon invariant basis;
- Weyl-BRST closure and exactness;
- antifield/Koszul--Tate completion and relative descent;
- anomaly coefficients, QME restoration, or residual transfer.

Gate A remains fail-closed while the classical team continues the portable
classical export and contraction certificate.

## Verification receipt

| Tier | Command/rail | Elapsed | Result |
|---|---|---:|---|
| 0 | compile local package, parse certificate JSON, validate common result schema | 0.80 s | pass |
| 1 | focused specialization and Weyl-decomposition tests | 0.16 s | 13 pass |
| 1 | complete local-BV unit rail, quiet mode | 22.91 s wall | 103 pass in 22.48 s |
| 2 | affected certificate reproduction, parallel by independent receipt | 12.83 s wall | 8 pass |
| 2 | two-pass `07-08-conformal-residual-cohomology-archive.tex` build | 1.21 s | pass; no unresolved references on final pass |

The full local rail remains well below the agreed 60-second escalation
threshold.  No test subdivision is needed yet.  Independent certificate
emission and checking were parallelized, reducing the affected-chain wall
time to about 13 seconds without sharing output files.  Tier 3 was not
triggered: this is a hardening certificate, not a classical freeze, local
BRST-cohomology theorem, QME result, lifecycle promotion, or release.  The
full repository suite was not run and is not represented as passing.

Commands:

```bash
PYTHONPATH=quantum-weyl python3 -m unittest \
  quantum-weyl/local_bv/tests/test_specialization.py \
  quantum-weyl/local_bv/tests/test_weyl_decomposition.py -v
PYTHONPATH=quantum-weyl python3 -m unittest discover \
  -s quantum-weyl/local_bv/tests -q
PYTHONPATH=quantum-weyl python3 \
  -m local_bv.weyl_decomposition_certificate --check
python3 quantum-weyl/schema/validate_result.py \
  quantum-weyl/certificates/LOCAL_WEYL_DECOMPOSITION_FOUNDATIONS.json
```

## Machine receipts

- `quantum-weyl/local_bv/certificates/LOCAL_WEYL_DECOMPOSITION_FOUNDATIONS_CERTIFICATE.json`;
- `quantum-weyl/certificates/LOCAL_WEYL_DECOMPOSITION_FOUNDATIONS.json`.

## Next local gate

Build the exact tracefree-Weyl image map from the certified eight-dimensional
four-dimensional Riemann quotient, then enumerate the odd single-epsilon
sector against the same canonical basis.
