# Coupled cyclicity-defect atlas

The complete retained obstruction is now exported as 953 exact normalized
coefficients. Every defect contains exactly two Maxwell legs:

- 800 are physical metric--potential--potential (`hAA`) coefficients;
- 138 are diffeomorphism-ghost/potential-antifield completion coefficients;
- 15 are Maxwell ghost-density completion coefficients.

The obstruction is not an integration-by-parts artifact: 60 coefficients
already occur at jet order zero. The smallest physical fixture has

```text
q2(A1,A1) -> h*00       40/9
q2(h00,A1) -> A+1       20/9
q2(A1,h00) -> A+1       20/9
```

and cyclic defect `-20/9`. This exposes a factor-two seam between gravity-
and Maxwell-output components.

A uniform factor two on every Maxwell-output `q2` component preserves the
retained `q1/q2` identity and removes 938 defects, including the entire
physical `hAA` sector. It leaves precisely 15 ghost-density defects. A tested
additional sign scaling removes those 15 only by creating 108 `q1/q2`
defects, so it is not an admissible repair. Natural Maxwell pairing-sign
flips leave all 953 defects unchanged.

The next repair target is therefore small and explicit: correct the 15-term
Maxwell ghost-density completion while retaining the uniform factor-two
physical normalization and exact `q1/q2`. This report does not certify that
correction or authorize mixed `q3`.
