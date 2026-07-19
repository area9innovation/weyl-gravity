# Berger recoil exact mode-kernel payload

Dependency tags: `LOCAL-ALGEBRAIC`, `LORENTZIAN-CAUSAL`.

The finite Berger Green theorem now has a machine-readable algebraic carrier.
For every `two_j=0,...,4`, the certificate exports sparse exact matrices for
the Maxwell degree-0/1 and massive-two-form degree-1/2 wave operators, followed
by the first six sine-kernel matrix coefficients in factored form `c_n A^n`
at powers `tau^1,tau^3,...,tau^11`.  All twenty blocks satisfy the exact series
recurrence through order four, and a flipped series sign is detected.

The massive payload retains a single symbolic positive `mu_squared`; it does
not invent a mass range.  Consequently this is not yet a rational interval
kernel enclosure or a physical convolution input.  Switch multiplication,
detector/profile contraction, truncation remainders and the channel values
`I_abc` remain open.
