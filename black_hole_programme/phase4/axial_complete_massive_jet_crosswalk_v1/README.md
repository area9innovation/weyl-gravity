# Complete massive axial first-jet crosswalk

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

This package imports the complete coupled axial massive-spin-two equations
of Brito--Cardoso--Pani and the equivalent Schwarzschild auxiliary-field
system of Antoniou--Gualtieri--Pani. It transforms their first
mass-squared jet into the massless Maxwell/Regge--Wheeler factor basis and
compares the tensor-led tangent with the certified Bach self-extension.

Run:

```text
python3 black_hole_programme/phase4/axial_complete_massive_jet_crosswalk_v1/produce.py
python3 black_hole_programme/phase4/axial_complete_massive_jet_crosswalk_v1/verify.py
python3 -m unittest -v black_hole_programme.phase4.axial_complete_massive_jet_crosswalk_v1.test_crosswalk
```

The exact result is

```text
[I_phys] = (1/3)[f],
[I_Bach] = (3 i omega/2)[I_phys].
```

Thus the previously used isolated shifted-RW target has the right
cohomological direction but the wrong normalization for the complete
massive tensor branch. The fixed-frequency tangent relation is
`m=(3 i omega/2) tau`, modulo rational gauge.

The verifier reconstructs the imported \(Q,Z\) flow, the Berndtson state
map, the conjugated mass tangent, both scalarizations, and the two
projective normal forms instead of accepting producer-recorded zero
residuals. Mutation tests alter an imported flow coefficient, the
factor-three normalization, and the physical-promotion flags.

The package does not certify an all-order differentiated Jost map, a
physical massive-QNM velocity, a common global Fredholm domain, or a causal
ringdown theorem.
