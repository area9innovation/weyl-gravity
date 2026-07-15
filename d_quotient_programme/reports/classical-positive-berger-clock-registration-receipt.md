# Classical positive Berger-clock registration receipt

## Registered claim

The classical team has certified an exact open family of smooth
non-conformally-flat Berger-cylinder backgrounds with two standard-sign
rotating conformal scalars. The coupled Bach--scalar equations, positive
target metric, bounded-below quartic, dominant-energy inequalities, timelike
phase, and full raw Diff \(\times\) Weyl incidence are exact.

The registered verdict is deliberately

```text
POSITIVE_BERGER_CLOCK_BACKGROUND_EXISTS
```

and not `D_GAUGE`. The perturbative covariant charge, support-local all-row BV
contraction, causal propagation, and stability have not been proved.

## Claim key

```text
generator_id: D_compact
phase_space_id: positive_rotating_scalar_berger_background
lifecycle_layer: CLASSICAL_CHARGE
status: PARTIAL
```

## Evidence

- Certificate: `d_quotient_classical/certificates/POSITIVE_BERGER_CLOCK_BACKGROUND.json`
- Producer: `d_quotient_classical/backreacted_clock/positive_berger_clock.py`
- Evidence commit: `77c4108b6a7e8d4aedb6ef6ddaaa5772c4636851`
- SHA-256: `fd7419b3a5985d83593de83824263c320b8fe44e47c69c473e7db5e30040b192`

## Next gate

```text
FULL_BERGER_CLOCK_CHARGE_AND_BV_AUDIT
```

This gate must compute the normalized covariant \(D\) charge on perturbations
and construct the complete support-local clock/BV reduction before a physical
clock verdict is assigned.
