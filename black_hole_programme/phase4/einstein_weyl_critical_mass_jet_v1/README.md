# Critical Einstein--Weyl mass jet

This package certifies the exact algebra that is already independent of a
Schwarzschild harmonic reduction:

- the rescaled Einstein--Weyl parent equations;
- the mass derivative modulo the Einstein kernel;
- the transverse-traceless critical propagator difference quotient;
- the singular finite-mass branch-sign involution and its nilpotent residue;
- the massive radial momentum and Schwarzschild Coulomb-phase derivatives.

The conventional finite-mass auxiliary field is singular in the pure-Weyl
limit.  The regular variable used here is the Schouten/Ricci carrier
`phi=q`; in the conventions of the cited Einstein--Weyl auxiliary action it
is proportional to `-mu^2 f_EW`.

The package deliberately does **not** identify the existing reduced radial
parameter `tau` with `-mu^2`.  That requires an exact axial reduction of the
finite-mass Fierz--Pauli system and comparison of projective cocycles:

```text
[I_mass] = [I_Bach] in C(r)/K_U C(r).
```

Until that gate passes, the Jost derivative and QNM-slope readings are
conditional.

Run:

```bash
python3 -m black_hole_programme.phase4.einstein_weyl_critical_mass_jet_v1.produce
python3 -m black_hole_programme.phase4.einstein_weyl_critical_mass_jet_v1.verify
python3 -m unittest -v black_hole_programme.phase4.einstein_weyl_critical_mass_jet_v1.test_mass_jet
```
