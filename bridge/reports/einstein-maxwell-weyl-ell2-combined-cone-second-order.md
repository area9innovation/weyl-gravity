# Complete combined ell=2,k=0 second-order cone

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

Let `u=u_A+u_P` contain arbitrary finite axial and polar `ell=2,k=0`
Einstein-plus, Einstein-minus, and both extra-primary amplitudes, with all
`m`.  The stabilizer moment maps have no axial-polar cross terms by parity.

The pure axial and pure polar zero-frequency sources share the same scalar
row direction, and their physical `L=1` pairings are the rotation moment
maps.  Consequently their obstruction projections add to the total
`H,J_1,J_2,J_3` values, including cancellations between parities.

Every axial-polar cross source has odd total parity and lands in an invertible
polar `L=1,3` or axial `L=2,4` quotient block.  No cross coefficient can add a
new constraint.

Therefore the complete generic `ell=2,k=0`, all-`m`, both-parity common-zero
cone admits a second-order correction.  At this fixture the second-order
tangent cone is exactly as large as the stabilizer moment-map test permits.
General `ell`, opposite momentum, exceptional/global modes, and all-orders
integration remain open.

## Verification receipt

Date: 2026-07-17.

* Tier 0: scoped `py_compile`, `0.03 s`, passed.
* Tier 1/2: six deterministic certificate replays, `2.32 s`, passed.
* Tier 1/2: six independent verifiers and 18 scoped tests, `2.17 s`, passed.
* Tier 3: complete `bridge/einstein_sector/tests` discovery,
  446 tests in `304.151 s` (`305.24 s` wall), passed.
