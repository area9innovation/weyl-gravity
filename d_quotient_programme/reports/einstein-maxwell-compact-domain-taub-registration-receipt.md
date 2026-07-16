# Einstein--Maxwell compact-domain/Taub registration receipt

Date: 2026-07-16

The programme imports commit
`191594d83209c462aeb5db3d03e79f3bbef86550` and certificate
`bridge/certificates/compact_harmonic_domain_taub_descent.json` with SHA-256
`4607543c23acdf5df0110aa6df4a01d7e397e6a73afd2d416f3bdd8482048e09`.

The registered phase space contains smooth periodic Einstein--Maxwell
tangents on one fixed compact `U(1)` bundle `P_N` with `N=2`, before the final
residual quotient.  Exact flux integration proves that its second-order
magnetic harmonic coefficient must vanish.  The earlier augmented magnetic
row is therefore registered separately as an enlarged continuous-flux theory,
not as a direction in this phase space.

The verdict `G1_FIXED_U1_DOMAIN_AND_RELATIVE_TAUB_DESCENT` also records the
formal action-Noether gauge descent, closed-slice conservation, and resulting
relative Taub interpretation.  It must not be promoted to a complete
`H^0_lin` computation, full adjoint-cokernel theorem, off-shell BV map, or
Lorentzian-causal result.

Verification:

```text
python3 d_quotient_programme/verify_programme_status.py --check --guards
```

The command passed in `0.26 s`, including exact regeneration, evidence hashes,
and mutation guards.  This is the affected Tier-2 chain.  Tier 3 is not required because no complete
harmonic freeze, shared core-algebra change, lifecycle promotion, or release
is made.
