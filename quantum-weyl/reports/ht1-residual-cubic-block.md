# HT1 residual cubic charge block

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

Result state: `PARTIAL_CUBIC_BLOCK_COMPUTED`

## Result

The first genuine nonlinear-transfer block is now imported from the
classical bridge.  Composing the endpoint Bach/Taub obstruction map, the
selected closed-cylinder BV--BFV suspension, the action-normalized all-energy
moment map, and the strict centered HPL transfer gives

```text
Omega_3 = c^A mu_A(Phi,Phi) - f^A_BC c^B c^C b_A/2,
M_A = -(1/2) J K_A.
```

This determines `ell_2(residual ghost, physical matter)` and the universal
`ell_2(residual ghost, residual ghost)` for all fifteen conformal generators.
The finite exact regression buffer has dimension 132 through energy four;
the source certificate supplies the symbolic all-energy coefficients.

All moment-map kernels are chirality block diagonal.  There are zero
off-diagonal entries between the `W_+` and `W_-` one-particle modules.  The
moment-map normalization is fixed by the direct `D` Hamiltonian and two
independent `B^(2)` curvature integrations, then extended by exact conformal
equivariance.  Together with the ghost bracket it transfers as the strict CE
differential in the centered physical window.

Consequently, the centered one-particle `H4=0` statement persists under this
specific cubic residual charge block, while the two-particle centered space
remains two-dimensional.

## Claim boundary

This is not yet the gravitational self-interaction bracket.  The missing
block is

```text
ell_2(physical matter, physical matter),
```

obtained from the quadratic nonlinear Bach source together with its complete
antifield/BV rows and projected through `pi_cl`.  Until that block is
exported, the result does not establish closure of the dynamical Weyl-square
direction, centrality of the Pontryagin direction, or absence of sector
re-entry at higher arity.

The result is not a quantum correction and carries no `LORENTZIAN-CAUSAL`
claim.

## Next exact target

HT1b should serialize the bilinear Bach source
`B^(2)(h_1,h_2)`, its ghost/antifield completions required by the classical
master equation, and the compatible endpoint projection.  The acceptance
test is the exact tensor

```text
ell_2^matter = pi_cl q2(iota_cl(-), iota_cl(-))
```

in the chiral basis, followed by the `(e,o)` change of basis.  No expected
closure or centrality matrix will be hard-coded.

## Verification receipt

| Command | Elapsed seconds | Status | Tier |
|---|---:|---|---:|
| `python3 quantum-weyl/transfer/residual_cubic_certificate.py --emit` | 5.51 | PASS | 1 |
| `python3 quantum-weyl/transfer/nonlinear_transfer_certificate.py --emit` | 0.03 | PASS | 1 |
| `python3 -m unittest discover -s quantum-weyl/transfer/tests -v` | 5.61 | PASS (12 tests) | 1 |
| `python3 -m py_compile quantum-weyl/transfer/*.py quantum-weyl/transfer/tests/*.py` | 0.02 | PASS | 0 |
| JSON parse of both generated transfer certificates | 0.04 | PASS | 0 |

Tiers 2 and 3 were not run.  No upstream classical artifact was changed and
no full matter self-interaction, lifecycle, paper, quantum, or Lorentzian
claim was promoted.  The upstream inputs are bound by content hashes and the
new certificate independently regenerates the exact finite moment-map
matrices.
