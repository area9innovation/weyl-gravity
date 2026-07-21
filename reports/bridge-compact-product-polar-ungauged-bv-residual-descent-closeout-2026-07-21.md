# Polar ungauged BV residual-descent obstruction

Date: 2026-07-21
Team: Einstein/nonlinear bridge
Science Forge item: `bridge-compact-product-polar-ungauged-bv-residual-descent`

## Outcome

The ungauged equation/Noether lift exists, but the requested strict cyclic BV
lift with the fixed identity Einstein field inclusion does not. On generic
polar solution cohomology,

```text
D = R-I = [[0, -3 lambda], [-3/2, 0]],
D^2 = (9/2) lambda I,
det D = -(9/2) lambda.
```

Thus `D` has rank two on every physical `lambda=ell(ell+1)>=6`. A strict
cyclic chain map would induce a symplectic map on solution cohomology, but the
nonzero nonradical defect contradicts that necessary condition. This is the
first exact obstruction in the work item; no gauge-fixed primary module has
been relabelled as an ungauged BV map.

The precursor remains useful: source and target nilpotency, all local
ghost/field/equation/identity squares, the natural support-local all-row chain
map, and the noncyclic mapping cofiber are certified. What fails is standard
pairing cyclicity for the identity inclusion. Corrected nonidentity maps and
cyclic chain homotopies remain open.

## Exceptional and global ledger

- `ell=1`, `k=0` and `k!=0` have independent off-shell chain maps and
  standard relative operator `4I`; they are not inferred from generic `ell`.
- Polar `ell=0`, `k!=0` has an empty physical solution quotient.
- The homogeneous `ell=0,k=0` block has `R=I+N`, `N^2=0`, `rank N=2`;
  `Q_e` and `W_x` are retained.
- Each axial twist position/velocity pair has `R=-2I` and remains a physical
  holonomy tangent before any separately declared finite moduli quotient.
- Large `U(1)` winding makes the finite Wilson-line coordinate periodic; it
  does not delete the tangent or its electric conjugate.
- No asymptotic/exterior boundary carrier is imported.

## Why no final residual dimensions are exported

The actual connected background stabilizer is the five-generator
`R_t x U(1)_x x SO(3)`, not vacuum `SO(4,2)`. Its action preserves the direct
Lee--Wald form but is not universally null: `H`, nonzero-`k` `P_x`, and
nonzero-`m` rotations have explicit nonzero moment-map matrix elements on the
positive extra block. Therefore an absolute gauge quotient by these global
symmetries is not authorized. The missing carrier is a declared common
moment-map/Taub-zero derived sector with its induced quotient complex and
pairing. Until it exists, final residual cohomology dimensions and descended
radical are `NO_CERTIFIED_MAP`.

## Scope

This `LOCAL-ALGEBRAIC/REDUCED-MODE` obstruction does not rule out a corrected
field identification or cyclic map up to homotopy. It establishes no causal,
observational, particle, positivity, unitarity or quantum result.

EVIDENCE: bridge/certificates/EINSTEIN_MAXWELL_WEYL_POLAR_UNGAUGED_BV_RESIDUAL_DESCENT_OBSTRUCTION_V1.json
CLOSE-OUT: OBSTRUCTED — fixed-identity cyclic BV compatibility fails before final residual descent.
