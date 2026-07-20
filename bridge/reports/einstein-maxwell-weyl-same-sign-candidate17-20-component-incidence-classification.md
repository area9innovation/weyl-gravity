# Candidate-17/20 component-incidence classification

## Result

The remaining component question has a complete candidate-specific answer.
At every fixed positive active occupation, each strict opposite-sign
admissible quotient has exactly one path component:

| Candidate scope | Sign chamber | Components | Incidence |
|---|---|---:|---|
| candidate 17 | `delta<0<alpha` | 1 | the unique component meets `G=0`, `x=-delta/a` |
| candidate 20, negative-delta side | `delta<0<alpha` | 1 | the unique component meets `G=0`, `x=-delta/a` |
| candidate 20, positive-delta side | `alpha<0<delta` | 1 | the unique component meets `F=0`, `y=delta/b` |

There are no nonincident components. Candidate 17 and candidate 20 remain
different atlas scopes; only their invariant proof template is shared.

## Exact stratum ledger

For nonnegative node occupations `x=||F||_W^2` and `y=||G||_W^2`, the
compact carrier is the disjoint union of four occupation strata:

1. `x>0,y>0`;
2. `x=0,y>0`;
3. `x>0,y=0`;
4. `x=y=0`.

The zero-node strata are part of the carrier. At `F=0`, the stabilizer
contains `U(1)_F`; at `G=0`, it contains `U(1)_G`; and at the origin the
whole kernel-pair action fixes the pair. Each occupation stratum is further
partitioned by every realized compact orbit type `(H)`. No freeness,
constant-stabilizer or smooth-principal-stratum assumption is used. The
compact-group slice theorem supplies path lifting across orbit-type
frontiers.

## Why there is only one component

The preceding incidence theorem proved that a strict-sign component reaches
the connected hub if and only if it meets

```text
I={c=0=M_K}.
```

The complete-contraction theorem then supplied a path from every admissible
point to the appropriate one-zero-node incidence:

- for `delta<0<alpha`, delete `G`, damp the moment of `F` by time reversal,
  cross at `x=-delta/a`, and scale to the hub;
- for `alpha<0<delta`, delete `F`, damp the moment of `G`, cross at
  `y=delta/b`, and scale to the hub.

Thus every point, including every boundary and nonfree orbit type, lies in
the same candidate-specific hub component.

## Boundary

This is a fixed-positive-active-occupation finite-carrier classification.
It does not glue distinct total-occupation fibres, construct a global
Hausdorff quotient outside this carrier, perform final residual descent,
solve every mixed cone or evolution problem, or establish causal,
observational or quantum claims.

CLOSE-OUT: DONE — every candidate-specific component and stratum has an exact incidence disposition
EVIDENCE: bridge/certificates/einstein_maxwell_weyl_same_sign_candidate17_20_component_incidence_classification.json
