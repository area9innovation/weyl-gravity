# Polar Weyl–Maxwell Lee–Wald completion registration receipt

The programme imports
`bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json` at commit
`cb7295275a2ff3eeb0729dcc9d6246a93bfb6e71`, SHA-256
`8175f454ab4ff0f95a047aa7fb13b7ed1f7ed40acb2ee76b3b943426330d3ce6`.

The registered G2 result equips the complete physical polar target module
with its direct four-dimensional Lee–Wald current.  The extra `p`-primary
block is nonradical with positive-frequency inertia `(2,0)`, is orthogonal to
the Einstein `q`-primary image, and gives complete pre-residual polar inertia
`(3,1)`.  The associated coefficient extractors remain stationary spectral
functionals rather than residual or Peierls observables.

The evidence certificate records the exact sparse direct-current timings:

```text
ell=2  131.77334666252136 seconds  PASS
ell=3  104.59966182708740 seconds  PASS
ell=4  172.30356574058533 seconds  PASS
total  408.67657423019410 seconds  PASS
```

Verification:

```text
python3 -m bridge.einstein_sector.einstein_maxwell_weyl_polar_lee_wald_gate --verify bridge/certificates/einstein_maxwell_weyl_polar_lee_wald_gate.json
python3 bridge/einstein_sector/verify_einstein_maxwell_weyl_polar_lee_wald_gate.py
python3 -m unittest bridge.einstein_sector.tests.test_einstein_maxwell_weyl_polar_lee_wald_gate
python3 d_quotient_programme/verify_programme_status.py --check --guards
```

The three fast polar producer/verifier/test commands completed in `4.12`
seconds with status `PASS`.  Programme regeneration and mutation guards
completed in `0.83` seconds with status `PASS`.

Tier 3 was not run because this registration changes no shared core algebra,
causal or quantum lifecycle state, paper theorem freeze, release, or final
residual claim.
