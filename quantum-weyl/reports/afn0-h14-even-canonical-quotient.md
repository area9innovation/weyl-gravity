# Even AFN0 `H14` canonical candidate quotient

Date: 2026-07-15

Dependency tag: `LOCAL-ALGEBRAIC`

Result state: `COMPLETE_AFN0_EVEN_CANDIDATE_QUOTIENT`

## Outcome

The two pending mixed signatures in `H14_AFN0_EVEN` have been reduced
orbit-first. The computation materializes their 30 pairings only; it does
not expand any of the 2,860,932,903 raw ambient graphs.

| Signature | Raw pairings | Signed-symmetry orbits | Bianchi rank | Canonical dimension |
|---|---:|---:|---:|---:|
| `Riemann * nabla^2 omega` | 15 | 2 | 0 | 2 |
| `nabla Riemann * nabla omega` | 15 | 2 | 1 | 1 |

The differential Bianchi relation reduces the contracted Ricci-divergence
carrier to `-1/2` times the canonical `nabla R . nabla omega` carrier in the
project's Riemann convention. Five-index four-dimensional
antisymmetrization has no carrier here: these sectors contain only three
contraction pairs, and the exhaustive Schouten selector is empty.

## Exact relative matrices

In the ordered mixed coordinates

```text
(omega BoxR, R Boxomega, Ricci Hessomega, gradR gradomega)
```

the three generated divergences are

```text
div(R grad omega)       = (0, 1, 0,   1)
div(Ricci grad omega)   = (0, 0, 1, 1/2)
div(omega grad R)       = (1, 0, 0,   1)
```

and the only incoming Weyl row needed is

```text
Q(R^2) = -12 R Box(omega).
```

The combined incoming boundary matrix has rank four. It spans
`omega BoxR` and all three mixed carriers, so neither formerly pending
signature adds a class.

The seven-coordinate top basis also contains `omega R^2`. Its consistency
image is reduced against the sole ghost-two current:

```text
d_h(omega R d omega)
  = omega R Box(omega) + omega dR . d omega.
```

The term with two identically contracted `d omega` factors vanishes by the
Grassmann sign. The resulting one-dimensional `d_h` quotient carries a
nonzero coefficient `-12`, excluding `omega R^2` from the closure kernel.

Therefore

```text
top dimension             = 7
projected closure rank    = 6
relative boundary rank   = 4
candidate quotient dim   = 2
```

with complete normalized dual witnesses for

```text
ANOM_OMEGA_C2
ANOM_OMEGA_E4
```

and the explicit exact representative

```text
ANOM_OMEGA_BOX_R
  = Q(-R^2/12) + d_h(current).
```

## Claim boundary

This is a complete even Weyl-ghost, antifield-zero, dimension-four
**candidate quotient**. Universal Diff completion is factored through the
already-certified horizontal towers. This result does not classify the
antifield sector, compute an anomaly coefficient, establish a `D`-anomaly,
restore the QME, transfer a residual quantum differential, or establish a
Lorentzian construction.

## Artifacts

- `quantum-weyl/local_bv/h14_even_canonical_quotient.py`;
- `quantum-weyl/local_bv/certificates/AFN0_H14_EVEN_CANONICAL_QUOTIENT.json`;
- `quantum-weyl/local_bv/schema/afn0_h14_even_canonical_quotient.schema.json`;
- `quantum-weyl/local_bv/tests/test_h14_even_canonical_quotient.py`.

## Verification

| Rail | Result |
|---|---:|
| focused canonical-quotient tests | 6 pass in 0.02 s |
| complete local-BV suite | 210 pass in 48.92 s |
| canonical quotient, basis-gap, AFN0, and Cartan reproduction checks | pass |
| changed Python compile, strict schema, all quantum JSON parse, scoped diff check | pass |

The full repository suite is not required: this changes no classical datum,
shared freeze, quantum lifecycle state, spectral claim, causal claim, or
paper theorem.
