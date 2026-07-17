# Retained-36 branch-projector obstruction import

The quantum-side consumer pins classical commit
`2f3d1b9af20abaf01d27a6172fb2d7f43657d22b` and independently accepts
`BERGER_RETAINED_36_RESIDUAL_BRANCH_LOCAL_PROJECTOR_OBSTRUCTION_V1`.
It validates the strict classical schema, hashes every pinned source artifact,
recomputes the polynomial division, and obtains the normalized value one from

```text
(80/71) coefficient_of(p1^2)
```

on the nonzero remainder

```text
(71*p1**2 + 71*p2**2 + 9*p3**2)/80.
```

The result closes the former request for a canonical, finite-order,
support-local, same-bundle Einstein-like/extra-Weyl projector on the retained
36-row carrier. It does not invalidate the independently accepted retained
full-BV `ell3` cyclicity result. Consequently, no 36-row branch-space `ell3`
mixing table is authorized.

The exact lower bound is four additional BV rows. The smallest natural
support-local candidate identified by the classical certificate adds a
spatial STF2 prolongation variable and its cyclic dual, ten rows in total,
for a retained rank of 46. This is a construction target, not a certified
projector. A filtered/mapping-cylinder carrier remains allowed. A nonlocal
spectral decomposition remains allowed only with the `REDUCED-MODE` tag.

## Claim boundary

This is `LOCAL-ALGEBRAIC` import evidence. It does not compute residual branch
mixing, restore the QME, identify a particle branch, or establish a quantum or
Lorentzian theorem.

## Verification

```bash
PYTHONPATH=quantum-weyl python3 -m transfer.berger_retained_36_branch_projector_obstruction_import --check
PYTHONPATH=quantum-weyl python3 -m transfer.verify_berger_retained_36_branch_projector_obstruction_import
PYTHONPATH=quantum-weyl python3 -m unittest quantum-weyl/transfer/tests/test_berger_retained_36_branch_projector_obstruction_import.py -v
npx --yes ajv-cli@5 validate --spec=draft2020 --strict=true -s quantum-weyl/transfer/schema/berger-retained-36-branch-projector-obstruction-import-v1.schema.json -d quantum-weyl/transfer/certificates/BERGER_RETAINED_36_BRANCH_PROJECTOR_OBSTRUCTION_IMPORT.json
```

Tier-1 elapsed times were respectively 0.67 s, 0.62 s, 0.85 s, and
1.21 s. Tier 2 was not repeated because the pinned classical chain already
passed at its source commit and this consumer independently checks its hashes
and normalized witness. Tier 3 was not run because no lifecycle, theorem
freeze, release, shared algebra, or quantum claim is promoted.
