# BH-4 stage 1: horizon-monodromy Hawking temperature, universal across branches

## Verdict

`BH4_HAWKING_MONODROMY_TEMPERATURE_UNIVERSAL_ACROSS_BRANCHES`
(certificate `black_hole_programme/certificates/BH4_HAWKING_MONODROMY.json`,
tags `LOCAL-ALGEBRAIC` + `REDUCED-MODE`, lifecycle `CLASSIFIED`).

This is the programme's first Hawking-process result, scoped strictly to
the mode level (REDUCED-MODE): **the Boltzmann ratio
|β/α|² = e^{−ω/T_H} of the Damour–Ruffini horizon continuation is
universal across the Einstein and extra branches in both parity sectors
of ℓ = 2** — the extra sector of pure-Weyl gravity is thermally weighted
at exactly the Hawking temperature.

## Exact results

1. **Temperature**: κ = B′(2m)/2 = 1/(4m), T_H = κ/2π = 1/(8πm);
   the certified normalized-frame first-law temperature of the static
   family at the Schwarzschild member equals u·T_H exactly (the
   geometric-clock Hawking temperature matches the certified first law).
2. **Spectra re-derived from scratch** (and matched against the
   hash-pinned certificates), ingoing convention:
   - axial extra carrier: {0, 0, −4imω, −2−4imω}
   - polar extra carrier (traceless slice): {0×3, 1−4imω, −1−4imω, −3−4imω}
   - axial Einstein/RW: {0, −1−4imω}
   - polar Einstein: {0, −4imω}
3. **Monodromy theorem**: under ρ → e^{2πi}ρ every exponent has
   continuation factor exactly 1 or e^{8πmω} = e^{ω/T_H} — the integer
   parts are monodromy-trivial and the universal −4imω part carries the
   thermal factor. Every family (both branches, both parities) contains
   thermal-monodromy exponents.
4. **Flux link**: combined with the certified nonzero extra-branch
   horizon flux norms (axial and polar cross-flux certificates), the
   mode-level Hawking process radiates into the extra sector with the
   same thermal factor as the Einstein sector.

## Quantum claim boundary (fail-closed)

This is a REDUCED-MODE statement. Per the workspace quantum boundary,
none of the following is claimed or implied, and none exists until an
explicit certificate says otherwise: a Lorentzian off-shell BV
propagator; a BRST-compatible Hadamard state; renormalized time-ordered
products or stress tensor; grey-body factors or luminosity;
back-reaction; a LORENTZIAN-CAUSAL Hawking theorem. All are recorded as
missing objects.

## Receipts

```bash
python3 black_hole_programme/bh4_hawking_monodromy.py            # producer (~10 min)
python3 black_hole_programme/verify_bh4_hawking_monodromy.py     # independent verifier (~10 min)
python3 -m pytest black_hole_programme/tests/test_bh4_hawking_monodromy.py -q  # fast rail (~1 s)
```

The verifier re-runs everything (including all four spectra) on the
VbGeo Schouten/Kulkarni–Nomizu pipeline. Inputs pinned by hash.
