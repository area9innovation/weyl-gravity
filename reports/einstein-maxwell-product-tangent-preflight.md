# Einstein--Maxwell product tangent-preflight receipt

Date: 2026-07-15

## Result

The `LOCAL-ALGEBRAIC` certificate
`EINSTEIN_MAXWELL_PRODUCT_TANGENT_PREFLIGHT` freezes the two minimal BV
layouts at the certified common background and proves the complete
principal-symbol chain map

```text
Einstein--Maxwell:  5 -> 14 -> 14 -> 5
Weyl--Maxwell:      6 -> 14 -> 14 -> 6.
```

The Einstein ghost sector contains four diffeomorphism ghosts and one Maxwell
ghost. The Weyl complex adds the Weyl ghost and trace identity. The field map
is the identity, while the equation map is

```text
diag(alpha_B*kappa Q_p, identity_Maxwell),
```

where `Q_p` is the universal principal Bach-from-Einstein operator. All three
chain squares and both pairs of gauge/Noether nilpotency identities pass
exactly.

Both principal complexes are exact at the noncharacteristic rational fixture
`p=(1,2,3,5)`. At `p=(1,0,0,1)`, the Einstein field-symbol cohomology has two
metric plus two photon classes. It injects into the Weyl--Maxwell simple
null-symbol cohomology, which has four metric plus two photon classes. The
induced cokernel therefore has dimension two.

This does not count generalized fourth-order/Jordan solutions. That requires
the prolonged characteristic complex.

## Claim boundary

The lifecycle remains `CLASSIFIED`. Curvature-dependent lower-order Bach
terms, background-flux Hessian mixing, the `i_xi Fbar` gauge term, formal
adjoints, cyclicity, magnetic-bundle patching, presymplectic comparison, and
product-space helicity assignment remain open. No causal, observable,
scattering, or quantum claim is promoted.

## Verification

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0 | `python3 -m py_compile` on the generator, independent verifier, and scoped test | 0.03 s | PASS |
| 0 | `python3 -m json.tool` on the schema and certificate | < 0.1 s each | PASS |
| 1 | generator exact-regeneration check | 0.70 s | PASS |
| 1 | independent tensor-symbol consumer | 0.69 s | PASS |
| 1 | scoped unit suite | 0.96 s | PASS (7 tests) |

Tier 2 was not run because this is a new isolated principal preflight and does
not change a shared operator or an input consumed by an existing certificate
chain. Tier 3 criteria were not met.

## Pre-existing shared-tree changes

The session began with active quantum Berger-import and nonlinear-transfer
edits. None is included in this certificate package.
