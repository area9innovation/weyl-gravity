# Einstein--Maxwell Chevreton tangent registration receipt

The programme dossier imports `EINSTEIN_MAXWELL_CHEVRETON_TANGENT` from
commit `9518d0ea13f2683d6039a1d475f0a65ed145e768` by its committed SHA-256
digest.

This is a new `CERTIFIED` setting,
`compact_einstein_maxwell_product_on_shell_tangent`, on the separate phase
space `einstein_maxwell_product_on_shell_linear_tangents`. It neither replaces
the exact common-background row nor promotes the principal BV preflight into
an off-shell curved chain map.

The registered verdict
`FULL_ON_SHELL_LINEAR_TANGENT_INCLUSION_CHEVRETON` records that every complete
linearized Einstein--Maxwell solution at the parallel-flux product maps to a
complete linearized Weyl--Maxwell solution with the same fields, before the
residual quotient. Curvature and flux lower-order terms are included on
shell. Off-shell BV row maps, cyclic and presymplectic comparison, quotient
injectivity, nonlinear closure, causal dynamics, observables, scattering, and
quantum equivalence remain open.

## Verification

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0 | JSON parse on contribution, phase-space registry, and programme certificate | < 0.1 s | PASS |
| 0 | `git diff --check` on the scoped registration paths | < 0.1 s | PASS |
| 1 | `python3 d_quotient_programme/verify_programme_status.py --check --guards` | 0.18 s | PASS, including mutation guards |
| 1 | independent source-certificate verifier | 0.34 s | PASS |

Tier 2 was not run because the registration changes no mathematical source
operator or schema; it imports a content-addressed theorem certificate. Tier
3 criteria were not met.

The concurrent quantum-team gauge-fixed Berger import files are not part of
this registration commit.
