# Mannheim--Kazanas to NGC 3198 model assembly v1

**Result:** `FOUNDATIONAL_MANNHEIM_NGC3198_MODEL_ASSEMBLY_V1`

**Lifecycle:** `NUMERICAL_REPRODUCTION_WITH_MIXED_EMPIRICAL_COMPARISON`

## Outcome

This is the first model-scoped Mannheim conformal-gravity prediction assembly in the foundations atlas. It keeps the Weyl/Bach model, Mannheim--Kazanas exterior, circular-orbit law, published thin-disk formula, published NGC 3198 parameters, endpoint calculation, and independent SPARC comparison on one typed chain.

It is deliberately **partial**. The endpoint is coarsely reproduced, but the independent SPARC comparison fails the declared random-error reduced-chi-squared gate. The result therefore does not certify empirical support or a complete assembly.

## Seven-stage chain

| Stage | State | Establishes |
|---|---|---|
| Weyl action and Bach equation | `DECLARED_MODEL_INPUT` | The classical model is four-dimensional pure metric conformal gravity with Bach equation B_mu_nu=0 in the exterior. |
| Mannheim--Kazanas vacuum family | `CERTIFIED_LOCAL_PREDECESSOR` | The local BH0B certificate derives the complete static spherical Bach-flat family in the declared conformal gauge. |
| Weak-field circular-orbit law | `CERTIFIED_LOCAL_PREDECESSOR` | The local BH0C certificate derives the leading weak-field beta/r + gamma r/2 - k r^2 circular-speed law and records its exact-family correction. |
| Luminous exponential-disk prediction | `PUBLISHED_MODEL_TRANSCRIPTION` | Mannheim--O'Brien Eqs. (5) and (20) integrate the Newtonian and linear kernels over thin stellar and gas disks and add universal linear and quadratic terms. |
| Published NGC 3198 parameters | `CONTENT_PINNED_TRANSCRIPTION` | The model uses the paper's distance, scale length, stellar and HI masses, fitted M/L, endpoint radius, and fixed universal constants without refitting. |
| Published endpoint reproduction | `COARSE_NUMERICAL_REPRODUCTION` | Independent evaluation of the displayed equations predicts the endpoint velocity within the declared five-percent coarse gate of the velocity reconstructed from the paper's endpoint acceleration. |
| Independent SPARC curve comparison | `MIXED_RANDOM_ERROR_GATE_FAILED` | Without refitting, the curve passes the declared five km/s RMS shape gate but fails the reduced-chi-squared gate based on SPARC random errors alone. |

## Published endpoint reproduction

At the published last radius `38.6 kpc`, the paper's tabulated endpoint acceleration reconstructs an observed velocity of `149.576 km/s`. Independent evaluation of the paper's disk formula and tabulated parameters gives `153.904 km/s`.

The residual is `4.328 km/s`, or `2.893%`. This passes the declared five-percent **coarse reproduction** gate. The endpoint has no tabulated pointwise uncertainty, so this is not a significance test or a full-curve reproduction.

## Independent SPARC cross-dataset check

The content-pinned SPARC extract contains `43` measurements; `39` remain after rescaling radii from 13.8 to 14.1 Mpc and applying the paper's 38.6 kpc endpoint. No parameter is refitted.

- Unweighted RMS residual: `4.538 km/s` — coarse 5 km/s shape gate **passes**.
- Maximum absolute residual: `8.166 km/s`.
- Reduced chi-squared from SPARC random errors only: `5.592` — declared gate `<=2` **fails**.

The pass and failure are not averaged. SPARC is a later 3.6-micron reduction rather than the heterogeneous blue-band input of the original fit, and its quoted errors omit inclination and other systematics. This rail is a useful stress test, not an exact replay of the publisher's likelihood.

## Disposition

`BOUNDED_ASSEMBLY_PARTIAL_MIXED_COMPARISON`: endpoint reproduction is `True`, the coarse SPARC shape gate is `True`, the SPARC random-error gate is `False`, and bounded completion is `False`.

## Boundaries

- This does not establish that the macroscopic scalar conformal frame is irrelevant to massive-particle trajectories or that Mannheim's matter-sector response is correct.
- This does not establish an interior galactic solution of the Bach equation with baryonic matter.
- This does not establish identity of the 2012 heterogeneous blue-band fit data with the 2016 SPARC 3.6-micron reduction.
- This does not establish reproduction of the original pointwise curve, fitting algorithm, likelihood, covariance model, distance uncertainty, or systematic-error budget.
- This does not establish that the fitted stellar mass-to-light ratio is independently preferred; it is imported without refitting.
- This does not establish empirical support under the SPARC random-error gate, which fails.
- This does not establish the published 111- or 141-galaxy population claims, lensing, cosmology, or another observational sector.
- This does not establish ghost freedom, quantum unitarity, a Mannheim C operator, or any quantum lifecycle promotion.
- This does not establish a complete observationally validated conformal-gravity theory.

## Verification

```bash
python3 foundations/build_mannheim_ngc3198_assembly.py --check
python3 foundations/check_mannheim_ngc3198_assembly.py
python3 foundations/verify_mannheim_ngc3198_assembly.py
python3 -m unittest foundations.tests.test_mannheim_ngc3198_assembly
```
