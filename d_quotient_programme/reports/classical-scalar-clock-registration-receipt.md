# Classical scalar-clock registration receipt

## Registered claim

```text
team_id          = classical
setting_id       = compact_scalar_clock
generator_id     = D_compact
phase_space_id   = compact_scalar_clock
lifecycle_layer  = CLASSICAL_CHARGE
claim_status     = CERTIFIED
verdict          = SINGLE_SCALAR_CLOCK_BACKGROUND_OBSTRUCTED
```

The claim is keyed to the one-real-scalar candidate on the exact vacuum
cylinder. It is not a verdict on a backreacted, composite/two-field, or
reference-matter clock phase space.

## Pinned evidence

```text
path    = d_quotient_classical/certificates/SCALAR_CLOCK_VERTICAL_SLICE.json
commit  = 704787c06de9e3746c1230e130bb652cb787a825
sha256  = de30ec828943d8c20be7e36bb523deb4d31f74e817bce92cf6d9374e80ab2948
```

The certificate proves exact local oscillator-clock mechanics, a positive
improved scalar charge, and the background obstruction. It deliberately
leaves the scalar-clock setting open without a `D_GAUGE` or `D_CHARGED`
verdict because the proposed coupled phase space does not exist.

## Next gate

```text
BACKREACTED_OR_COMPOSITE_CLOCK_MODEL
```

Allowed replacements are a genuinely backreacted scalar--pure-Weyl
background, a Weyl-invariant composite/two-field clock, or separately
declared reference matter.
