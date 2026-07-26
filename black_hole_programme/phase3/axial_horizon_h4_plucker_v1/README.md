# Axial q00 Plücker preflight

This disjoint successor transports the future-horizon-regular complex
three-plane as a projective element of
\(\Lambda^3(\mathbb C^6)\), rather than through repeated Grassmann graph
solves.  It retains the shared q00 frequency generator and the complete
degree-four interval/Taylor enclosure.

The deliberately bounded target is the end of shell 3, segment 0.  This is
the first quarter-shell boundary not certified by the historical graph
representation.

The certified run establishes:

- exact induced exterior-cube transport of 20 complex Plücker coordinates;
- exact dyadic projective scaling after every panel;
- all 45 standard quadratic relation residuals contain zero at every
  quarter-shell boundary;
- a Plücker coordinate component excludes zero throughout every reported
  boundary, providing a rank-three witness;
- q00 reaches shell 3, segment 0 without an interval overflow, chart solve,
  or relation refusal.

The relation audit is a consistency check on the enclosure.  Decomposability
comes from the exact initial wedge and the generated \(\mathfrak{gl}_6\)
exterior-action identity, not from treating every point of the interval box
as decomposable.

This does not establish the remaining 22 shells, canonical endpoint
amplitudes, or a horizon-to-infinity scattering theorem.

From the standalone `weyl-gravity` repository root:

```bash
PYTHONPATH=. python3 -m \
  black_hole_programme.phase3.axial_horizon_h4_plucker_v1.produce

FORGE_LIB=/home/alstrup/area9/tango/forge/lib \
  /home/alstrup/area9/tango/forge/forge \
  -o /tmp/axial-h4-plucker-q00-v1 \
  black_hole_programme/phase3/axial_horizon_h4_plucker_v1/plucker_q00_preflight.forge

PYTHONPATH=. python3 -m unittest -v \
  black_hole_programme.phase3.axial_horizon_h4_plucker_v1.test_plucker

PYTHONPATH=. python3 -m \
  black_hole_programme.phase3.axial_horizon_h4_plucker_v1.verify
```
