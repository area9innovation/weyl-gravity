# Homogeneous `a,b,d` crossed with the complete `ell=2` extra primary

Status: `CLASSIFIED` under `LOCAL-ALGEBRAIC` and `REDUCED-MODE`.

The direct four-dimensional Weyl--Maxwell expansion now covers the three
dynamical homogeneous metric directions `a,b,d` crossed with both extra
representatives in both output parities.  The `a` and `b` fixtures retain the
complete polynomial-in-time source rather than evaluating it at one time.
The existing certified `d` columns are imported by content hash.

After projection onto the two-dimensional extra-shell adjoint cokernel, each
parity and extra polarization gives three linearly independent polynomials,
one for each of `a,b,d`.  Their coefficients are therefore explicit
compatibility functionals for bounded or finite-quasiperiodic corrections.
The generated certificate records the full action rows, adjoint bases,
projected polynomials, scopes, provenance and fail-closed lifecycle flags.

This is deliberately a source-matrix theorem rather than a nonlinear no-go.
Twist position and velocity can enter the same `ell=2` output channel and have
not yet been appended.  Smooth secular and causal/retarded correction classes
also remain open until their respective complete operators are certified.

Evidence:

- `bridge/certificates/einstein_maxwell_weyl_abd_ell2_extra_resonance_matrix.json`
- `bridge/einstein_sector/einstein_maxwell_weyl_abd_ell2_extra_resonance_matrix.py`
- `bridge/einstein_sector/verify_einstein_maxwell_weyl_abd_ell2_extra_resonance_matrix.py`

Receipt: the successful Tier-2 four-worker direct tensor replay took 150.01
seconds.  The fast exact verifier took 0.74 seconds and the two scoped unit
tests took less than 0.01 seconds.  Tier 3 was not run because the twist
columns and the complete tangent-cone gate remain open.

The next gate is the twist-position/twist-velocity cross matrix followed by
the simultaneous stabilizer and complete bounded-resonance zero locus.
