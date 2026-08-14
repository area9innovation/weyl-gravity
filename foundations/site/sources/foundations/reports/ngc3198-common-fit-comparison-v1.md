# NGC 3198 common-protocol fit comparison v1

**Dependency:** `LOCAL-ALGEBRAIC`. **Result kind:** bounded numerical single-galaxy comparison.

All families use the same 39 SPARC velocities, random-error-only diagonal objective, distance rescaling, and analytic thin exponential stellar/gas geometry. The stellar mass scale `q*` is fitted for every family; gas is fixed. NFW additionally fits `V200` and `c200`.

| Family | fitted parameters | RMS (km/s) | reduced chi-squared | AICc | gate <= 2 |
|---|---:|---:|---:|---:|---:|
| NEWTONIAN_BARYONS_ONLY | q*=1.632122 | 23.896 | 128.722 | 4893.557 | FAIL |
| GR_NFW_DARK_HALO | q*=0.825390, V200=116.3160 km/s, c200=6.80220 | 5.148 | 0.965 | 41.435 | PASS |
| MANNHEIM_CONFORMAL_GRAVITY | q*=1.064543 | 4.694 | 3.202 | 123.776 | FAIL |

## Scoped result

GR_NFW_DARK_HALO has the lowest AICc and is the only family that passes the declared random-error gate within this common analytic, single-galaxy protocol.

This is a useful control: baryons alone fail strongly, the one-parameter Mannheim curve improves substantially but still fails the declared random-error gate, and the three-parameter GR+NFW curve passes. AICc and BIC penalize the two extra NFW parameters and retain that ordering.

## Boundaries

- Does not establish a likelihood with distance, inclination, beam-smearing, stellar-population, gas-profile, or other systematic uncertainties.
- Does not establish identity of the analytic baryonic geometry with the SPARC numerical mass components or the original Mannheim fitting data.
- Does not establish a cosmological concentration--mass prior or a posterior probability for an NFW halo.
- Does not establish population-level performance, held-out prediction, or model selection beyond NGC 3198.
- Does not establish that the best score in this bounded protocol validates a complete theory or refutes another theory.

The shared analytic baryonic model is used for comparability. It is neither a full SPARC mass-model likelihood nor an identity claim between the later SPARC photometry and the dataset used in the original Mannheim fit.

## Reproduction

```bash
python3 foundations/build_ngc3198_common_fit_comparison.py --write
python3 foundations/check_ngc3198_common_fit_comparison.py
python3 foundations/verify_ngc3198_common_fit_comparison.py
```
