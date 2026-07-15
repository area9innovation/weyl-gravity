# E-D1a generator-dictionary receipt

Date: 2026-07-15

## Established

The exact real Penrose-coordinate calculation separates real Einstein-static
universe time, real Minkowski dilation, and the radial-quantization compact
grading.  Real cylinder time pushes to

```text
(1+u^2)/2 d_u+r(u+r)d_r
```

and crosses a fixed `I_plus`.  Real Minkowski dilation is

```text
u d_u+r d_r,
```

is tangent to `I_plus`, and restricts there to `u d_u`.  It is not flat time
translation `P_0=d_u`; exactly `[D_M,P_0]=-P_0`.

The certificate also derives the finite action of flat dilation plus its
background-stabilizing Weyl compensator on reduced Bondi shear/news.  The
candidate strong radiative core is preserved kinematically, but the full
Bach phase space and charge remain open.

Finally, for the reduced Einstein-defect system it checks the formal
triangular Green matrix

```text
[[G,G^2],[0,G]]
```

for the operator `[[Box,-1],[0,Box]]`.  This is an operator identity only,
not a null-infinity Green theorem.

Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`.

## Claim boundary

No `LORENTZIAN-CAUSAL` result is asserted.  The certificate keeps false:

- closure of the full asymptotically flat phase space;
- a BMSW embedding;
- a pure-Weyl `D` charge or gauge verdict;
- the Lorentzian BV--BFV and null-infinity Green complexes;
- causal Einstein selection, helicity scattering, or Einstein scattering
  equivalence.

The issued verdicts are `PHASE_SPACE_NOT_CLOSED` and `EINSTEIN_OPEN`.

## Provenance

Input base commit: `69b2b240d9a06a5473d275a16ed41d6df12687f8`.

| Artifact | SHA-256 |
|---|---|
| `d_quotient_asymptotic_seed.py` | `69a9a43827b2dbd901e69cb1b32a96cf7d153ab390b0a3c99e0cc696a4bdcb52` |
| `d_quotient_asymptotic_seed.schema.json` | `a1feac2bbd71d557cec16504c039863c8630a3d59df1a8004726e579878f3de6` |
| `d_quotient_asymptotic_seed.json` | `e39cff26bc6b6037eb6d0063899d6612e0c293b6c154aca42ce70881ef009796` |
| `test_d_quotient_asymptotic_seed.py` | `397b24f9fa5c786da72b0d3276fe068d9ecd9ca9568ac74f8ebe454cea7664c3` |
| `conformal-d-quotient-asymptotic-seed.md` | `3bbe13fbd6d4f0060f3850c267ec3fdeb75592cbb81651373abb852695787b0b` |

## Verification

| Tier | Command | Elapsed | Result |
|---|---|---:|---|
| 0 | `python3 -m py_compile` on the generator and test | 0.03 s | PASS |
| 0 | `python3 -m json.tool` on the schema and certificate | 0.07 s | PASS |
| 1 | `python3 -m bridge.einstein_sector.d_quotient_asymptotic_seed --verify bridge/certificates/d_quotient_asymptotic_seed.json` | 0.59 s | PASS |
| 2 | `python3 -m unittest discover -s bridge/einstein_sector/tests -p 'test_*.py'` | 8.65 s | PASS (39 tests) |

The tests cover the exact Penrose generator map, metric Lie derivatives,
`I_plus` tangency/transversality, the `D_M`/`P_0` bracket, shear/news action,
triangular inverse, input hashes, and rejection of forged charge, gauge,
causal, and scattering promotions.

The certificate hash was refreshed after bootstrap schema v2 imported the
flat Einstein symplectic-restriction no-go.  No D-generator identity or
verdict changed.

It was refreshed again after the fail-closed Einstein-sector theorem imported
the independently verified compensated nonzero-characteristic snapshot.  The
new input certifies local `(0,2,2,0)` null-symbol cohomology and leaves every
asymptotic phase-space, charge, causal, and scattering flag unchanged.

The present hash additionally imports the universal compensated external-source
Ward/defect chain-map theorem.  It changes no asymptotic generator, phase-space,
charge, causal, or scattering verdict.

Tier 2 was limited to the directly affected Einstein-sector certificate
chain.  Tier 3 is not required because this work changes no shared core
algebra, freeze, release, or paper theorem and promotes no
`LORENTZIAN-CAUSAL` claim.

## Concurrent work

Unrelated quantum transfer, medical, and backgammon changes were present in
the shared tree.  They were neither modified nor staged by this work.
