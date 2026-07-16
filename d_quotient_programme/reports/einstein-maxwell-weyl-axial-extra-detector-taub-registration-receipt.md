# Axial extra detector and Taub registration receipt

The programme imports
`bridge/certificates/einstein_maxwell_weyl_axial_extra_ell2_taub.json` at
commit `3d8003c5e4e87bafaf0585c744d77ae998178bd2`, SHA-256
`6a326de926f0d59d5300794665d0058af43841ee261dff92c6a2b9a68c3edf12`.
That certificate imports the exact generic axial detector, whose provenance in
turn imports the reduced action-Hessian reconstruction and direct Lee--Wald
completion.

The registered `LOCAL-ALGEBRAIC` / `REDUCED-MODE` result has two layers. The
linear detector reconstructs both extra coordinates and vanishes on the
certified generic axial Einstein image. On the real `ell=2,k=0` fixed-charge
extra span, the constant-lapse Taub matrix is

```text
diag(-1728/5,-832/45),
```

so it is negative definite and obstructs every nonzero real combination at
second order.

This does not register generic harmonic or momentum obstruction, final
residual descent, a causal or asymptotic observable, a particle, or a quantum
ghost theorem.

Verification:

```text
python3 d_quotient_programme/verify_programme_status.py --check --guards
PASS; mutation guards PASS; elapsed 0.33 s

python3 -m unittest \
  bridge.einstein_sector.tests.test_einstein_maxwell_weyl_axial_reduced_action_hessian \
  bridge.einstein_sector.tests.test_einstein_maxwell_weyl_axial_extra_detector \
  bridge.einstein_sector.tests.test_einstein_maxwell_weyl_axial_extra_ell2_taub
PASS; 10 tests; elapsed 1.275 s
```

The source receipt and exhaustive 137.31-second tensor replay are recorded in
`notes/einstein-maxwell-weyl-axial-extra-taub-report.md` at the evidence
commit. Tier 3 is not required because this registration does not alter shared
core algebra, freeze a release, or promote a causal or quantum lifecycle.
