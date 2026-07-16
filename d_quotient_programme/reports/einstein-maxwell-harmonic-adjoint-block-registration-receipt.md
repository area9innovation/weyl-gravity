# Einstein--Maxwell harmonic/adjoint block registration receipt

Date: 2026-07-16

The programme imports commit
`9a2952d5f03598b2c73a69f69d0648342da8b570` and certificate
`bridge/certificates/einstein_maxwell_harmonic_adjoint_blocks.json` with
SHA-256
`af2e8ec8924d9b27afe4b4e9d1e63b995064741475dfc09eedb389f019aeaf2b`.

The registered phase space is the declared homogeneous axial `H_x/a_x`
tower on the fixed compact `U(1)` bundle.  Its exact all-`(ell,m)` spectrum,
reduced Wronskian, exceptional global `ell=1` zero mode, universal stabilizer
projectors, and fail-closed block interface are certified.

The verdict `G1_AXIAL_N0_TOWER_AND_ADJOINT_PREFLIGHT` is not a complete axial
gauge-quotient theorem.  Nonzero `S1` momentum, polar blocks, covariant
symplectic matching, possible extra fourth-order adjoint classes, and all new
quadratic coefficients remain open.

Verification:

```text
python3 d_quotient_programme/verify_programme_status.py --check --guards
```

The command passed in `0.23 s`, including exact regeneration, evidence hashes,
and mutation guards.  This is the affected Tier-2 registration chain; Tier 3
criteria are not met.
