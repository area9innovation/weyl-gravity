# Theory passports: assumptions to observations

**Result:** `FOUNDATIONAL_END_TO_END_THEORY_PASSPORT_ATLAS_V1`. **Lifecycle:** `CLASSIFIED`.

Show how far each proposed physical framework travels along the same six-step route, where it first stops, and whether it has actually met data.

A passport is not a score for which theory is true. It is an evidence-pinned route map. A green empirical endpoint means only that a particular prediction passed a particular gate; a red endpoint means only that the declared bounded comparison failed.

## Overview

| Passport | Assumptions | State | Dynamics | Observable | Prediction | Data | First blocker or failure |
|---|---:|---:|---:|---:|---:|---:|---|
| Standard GR — Cassini | scoped | scoped | exact | exact | exact | pass | none |
| Newtonian baryons — NGC 3198 | scoped | scoped | scoped | scoped | numeric | fail | Empirical benchmark |
| GR + NFW halo — NGC 3198 | scoped | scoped | scoped | scoped | numeric | pass | none |
| Mannheim conformal gravity — NGC 3198 | scoped | scoped | scoped | scoped | numeric | fail | Empirical benchmark |
| Bateman–Turok — finite Euclidean lattice | scoped | exact | partial | partial | partial | open | Dynamics |
| Krein free-mode ground state | scoped | exact | exact | open | — | — | Observable |
| Constructive coded wave observable | exact | scoped | exact | exact | open | — | Prediction |
| Pure Weyl BV — causal quantum route | exact | partial | exact | open | — | — | State space |

## How to read the statuses

- **Established Exact:** An exact or formally checked result closes this stage in the stated scope.
- **Established Scoped:** A declared or literature-backed ingredient closes this stage only inside an explicit model boundary.
- **Established Numeric:** A reproducible numerical calculation closes this stage under its stated protocol.
- **Empirical Pass:** The prediction reaches data and passes the declared comparison gate; this is not validation of the complete theory.
- **Empirical Fail:** The prediction reaches data but fails the declared comparison gate; this is a scoped negative result, not a universal refutation.
- **Partial:** Useful stage-local evidence exists, but a required piece or bridge is still missing.
- **Open:** The stage is required for this journey and has not been established.
- **Not Reached:** The journey cannot yet make this claim because an earlier required stage is open.

## Passports

### Standard GR — Cassini

Static, spherical, asymptotically flat solar exterior and the published Cassini gamma estimate.

**Empirical disposition:** `SUPPORTED_IN_DECLARED_SCOPE`. **Ready through:** `EMPIRICAL_BENCHMARK`. **First blocker/failure:** `None`.

- **Foundational assumptions — `ESTABLISHED_SCOPED`:** Four-dimensional Lorentzian metric gravity with the vacuum Einstein equation outside the Sun. Boundary: This does not cover the solar interior, cosmology, or quantum gravity.
- **State space — `ESTABLISHED_SCOPED`:** Static spherical exterior metrics with asymptotic-flatness and Newtonian normalization. Boundary: This is a deliberately restricted classical sector, not the full solution space of GR.
- **Dynamics — `ESTABLISHED_EXACT`:** The reduced Einstein equations integrate exactly to the Schwarzschild exterior. Boundary: Exact only inside the declared ansatz and boundary normalization.
- **Observable — `ESTABLISHED_EXACT`:** Null propagation identifies the Cassini-sensitive delay coefficient as 1+gamma. Boundary: The operational map imports the experiment's fitted-parameter interpretation.
- **Prediction — `ESTABLISHED_EXACT`:** The model predicts gamma=1, hence gamma-1=0. Boundary: This is one weak-field prediction, not a test of every GR sector.
- **Empirical benchmark — `EMPIRICAL_PASS`:** The prediction lies inside the publisher's displayed Cassini uncertainty band. Boundary: The raw spacecraft data and likelihood were not reanalysed.

**Highest-value next step:** Add an independently reproduced second solar-system benchmark and a systematics-aware comparison.

### Newtonian baryons — NGC 3198

One fitted stellar scale, fixed gas, and a common analytic thin-disk geometry compared with 39 SPARC velocities.

**Empirical disposition:** `FAILED_DECLARED_GATE`. **Ready through:** `PREDICTION`. **First blocker/failure:** `EMPIRICAL_BENCHMARK`.

- **Foundational assumptions — `ESTABLISHED_SCOPED`:** Classical Newtonian gravity for the declared stellar and gas disk model. Boundary: The common analytic disk is a comparison control, not the full SPARC mass model.
- **State space — `ESTABLISHED_SCOPED`:** Circular tracers respond to a thin exponential stellar disk plus a fixed gas disk. Boundary: Distance, inclination and baryonic systematics are not marginalized.
- **Dynamics — `ESTABLISHED_SCOPED`:** The circular-speed law contains only the Newtonian stellar and gas contributions. Boundary: One stellar mass scale is fitted to this same galaxy.
- **Observable — `ESTABLISHED_SCOPED`:** The observable is the rotation speed at the common set of 39 galactic radii. Boundary: Only tabulated random velocity errors enter the objective.
- **Prediction — `ESTABLISHED_NUMERIC`:** A deterministic fit produces a complete 39-point baryons-only rotation curve. Boundary: This is an in-sample fit, not a held-out prediction.
- **Empirical benchmark — `EMPIRICAL_FAIL`:** The reduced chi-squared is about 128.72 and fails the declared <=2 random-error gate. Boundary: This rejects this bounded baryons-only control, not Newtonian gravity in every setting.

**Highest-value next step:** Use the failure as a calibrated baseline when testing added halo or modified-gravity structure.

### GR + NFW halo — NGC 3198

Newtonian weak-field baryons plus an NFW halo, with three fitted parameters under the common 39-point protocol.

**Empirical disposition:** `SUPPORTED_IN_DECLARED_SCOPE`. **Ready through:** `EMPIRICAL_BENCHMARK`. **First blocker/failure:** `None`.

- **Foundational assumptions — `ESTABLISHED_SCOPED`:** Weak-field general relativity represented by Newtonian baryons plus an NFW dark-matter halo. Boundary: No cosmological halo prior or posterior is included.
- **State space — `ESTABLISHED_SCOPED`:** The model combines the common stellar/gas disks with a spherical NFW halo. Boundary: The halo is a phenomenological fitted component for one galaxy.
- **Dynamics — `ESTABLISHED_SCOPED`:** Circular speed is the baryonic contribution plus the NFW circular-speed formula. Boundary: The fit has q_star, V200 and concentration as free parameters.
- **Observable — `ESTABLISHED_SCOPED`:** The observable is the rotation speed at the same 39 radii used for both competing curves. Boundary: The comparison uses random errors only.
- **Prediction — `ESTABLISHED_NUMERIC`:** Independent optimizers agree on a fitted 39-point NFW rotation curve. Boundary: The curve is fitted in-sample and has two more parameters than the one-parameter alternatives.
- **Empirical benchmark — `EMPIRICAL_PASS`:** Reduced chi-squared about 0.965 passes the declared <=2 gate and has the lowest AICc here. Boundary: One galaxy without systematic-error marginalization does not select a complete theory.

**Highest-value next step:** Repeat the common protocol across a preregistered galaxy sample with nuisance parameters and held-out tests.

### Mannheim conformal gravity — NGC 3198

The pure-metric conformal-gravity rotation law, common analytic disk geometry, and the same 39 SPARC velocities.

**Empirical disposition:** `FAILED_DECLARED_GATE`. **Ready through:** `PREDICTION`. **First blocker/failure:** `EMPIRICAL_BENCHMARK`.

- **Foundational assumptions — `ESTABLISHED_SCOPED`:** Four-dimensional pure-metric conformal gravity in the Mannheim–Kazanas phenomenological branch. Boundary: The matter-sector interpretation is an explicit unresolved assumption.
- **State space — `ESTABLISHED_SCOPED`:** Static weak-field metrics and thin stellar/gas disks describe massive circular tracers. Boundary: This assumes the displayed metric governs massive tracers; no galactic interior matter solution is supplied.
- **Dynamics — `ESTABLISHED_SCOPED`:** Certified exterior and orbit-law predecessors feed the published thin-disk and universal-term formula. Boundary: The disk integration is literature-transcribed and does not resolve the matter coupling.
- **Observable — `ESTABLISHED_SCOPED`:** The operational quantity is the circular rotation speed across NGC 3198. Boundary: The later SPARC data are not identical to the original fitting dataset.
- **Prediction — `ESTABLISHED_NUMERIC`:** A one-parameter common-protocol fit produces the complete Mannheim curve. Boundary: This differs from reproducing the original Mannheim likelihood.
- **Empirical benchmark — `EMPIRICAL_FAIL`:** Reduced chi-squared about 3.20 fails the declared <=2 random-error gate despite a low unweighted RMS. Boundary: This is a bounded one-galaxy result, not a universal refutation of conformal gravity.

**Highest-value next step:** Resolve or parameterize the massive-matter coupling, then test a preregistered multi-galaxy sample with systematics.

### Bateman–Turok — finite Euclidean lattice

The positive finite-volume Euclidean lattice slice, not the proposed full Lorentzian Krein theory.

**Empirical disposition:** `NOT_TESTED`. **Ready through:** `STATE_SPACE`. **First blocker/failure:** `DYNAMICS`.

- **Foundational assumptions — `ESTABLISHED_SCOPED`:** A finite periodic graph, ordinary real integration, and a positive Euclidean weight. Boundary: Finite graph does not mean a finite field-value space.
- **State space — `ESTABLISHED_EXACT`:** Mean-zero real lattice fields with positive Omega have a finite partition function and normalized Gibbs state. Boundary: This is a Euclidean statistical state, not a Lorentzian physical state.
- **Dynamics — `PARTIAL`:** A nonlinear Euclidean action and Gibbs weighting are explicit, but no Lorentzian time evolution or continuation is established. Boundary: Euclidean weighting cannot silently stand in for causal dynamics.
- **Observable — `PARTIAL`:** Finite-volume lattice observables can be sampled under the positive Gibbs measure. Boundary: No Born rule, scattering observable, or laboratory event rate is connected.
- **Prediction — `PARTIAL`:** Two samplers coarsely reproduce declared L=4 and L=6 finite-volume quantities. Boundary: No controlled continuum or regulator-independent prediction follows.
- **Empirical benchmark — `OPEN`:** No empirical benchmark has been connected to this Euclidean construction. Boundary: Numerical reproducibility of the regulator is not empirical validation.

**Highest-value next step:** Construct a controlled continuum and Euclidean-to-Lorentzian bridge before defining a physical observable.

### Krein free-mode ground state

The explicit free reduced-mode bosonic Krein–Fock carrier and its ground-state dynamics.

**Empirical disposition:** `NOT_TESTED`. **Ready through:** `DYNAMICS`. **First blocker/failure:** `OBSERVABLE`.

- **Foundational assumptions — `ESTABLISHED_SCOPED`:** Ordinary local algebra on a reduced Krein–Fock carrier with an explicit companion positive form. Boundary: This is a reduced free system, not a full field theory.
- **State space — `ESTABLISHED_EXACT`:** The energy selects a unique normalized vector ground state and unique normal zero-energy density state. Boundary: Selection is conditional on the free ground-state criterion.
- **Dynamics — `ESTABLISHED_EXACT`:** The same total-energy operator generates a dynamics that fixes the vacuum. Boundary: Stationarity alone would not make the state unique.
- **Observable — `OPEN`:** No generalized Born rule or operational field observable is joined to this state and dynamics. Boundary: A valid free state is not yet a measurement theory.
- **Prediction — `NOT_REACHED`:** No experimental number or curve follows without an observable and probability rule. Boundary: Reduced-mode energy identities are not phenomenological predictions.
- **Empirical benchmark — `NOT_REACHED`:** No dataset is in scope for the certified free-mode interface. Boundary: No empirical agreement is implied.

**Highest-value next step:** Define a physical observable and probability rule on the same carrier, then compute a bounded prediction.

### Constructive coded wave observable

Rationally coded one-dimensional chiral-wave data and one bounded smeared observable over a weak base theory.

**Empirical disposition:** `NOT_TESTED`. **Ready through:** `OBSERVABLE`. **First blocker/failure:** `PREDICTION`.

- **Foundational assumptions — `ESTABLISHED_EXACT`:** Finite rational codes use primitive-recursive arithmetic; RCA_0 supplies coded completion and uniform limits. Boundary: RCA_0 is proved sufficient, not necessary or weakest.
- **State space — `ESTABLISHED_SCOPED`:** Mean-zero rational step-pair initial data represent two chiral wave components. Boundary: The full wave state is not reconstructed from the one observable.
- **Dynamics — `ESTABLISHED_EXACT`:** Explicit translations evolve the two chiral components, with a uniform bounded-time reconstruction theorem. Boundary: This does not establish curved-spacetime or variable-coefficient dynamics.
- **Observable — `ESTABLISHED_EXACT`:** A declared polygonal detector produces a bounded smeared amplitude with explicit rational approximants. Boundary: It is one detector profile, not a point field or probability rule.
- **Prediction — `OPEN`:** The observable has no empirical calibration, source model, or measured target. Boundary: Computing an amplitude is not yet predicting an experiment.
- **Empirical benchmark — `NOT_REACHED`:** No empirical dataset can be compared until the detector profile and initial data are operationally calibrated. Boundary: No observational support is claimed.

**Highest-value next step:** Calibrate a coded source and detector against one bounded wave experiment without strengthening the logical base silently.

### Pure Weyl BV — causal quantum route

The immutable 386-row classical BV carrier through nonlinear causal compatibility and a BRST Hadamard pseudo-state.

**Empirical disposition:** `NOT_TESTED`. **Ready through:** `FOUNDATIONAL_ASSUMPTIONS`. **First blocker/failure:** `STATE_SPACE`.

- **Foundational assumptions — `ESTABLISHED_EXACT`:** The content-pinned classical pure-Weyl BV snapshot passes its import gate. Boundary: The classical complex is authoritative; this does not certify the quantum theory.
- **State space — `PARTIAL`:** A full-row BRST Hadamard pseudo-state exists, but positivity on physical cohomology is not certified. Boundary: Hadamard regularity and Ward identities do not turn an indefinite covariance into a physical state.
- **Dynamics — `ESTABLISHED_EXACT`:** The same carrier has typed q2/q3 nonlinear compatibility with retarded and advanced Green homotopies. Boundary: This is a causal perturbative envelope, not an all-order convergent interacting theory.
- **Observable — `OPEN`:** No positive physical-state quotient has yet been joined to an operational observable. Boundary: The residual Weyl-square classes are deformation classes, not one-particle graviton states.
- **Prediction — `NOT_REACHED`:** Renormalized Lorentzian products and a restored QME are still absent, so no quantum prediction is promoted. Boundary: Reduced-mode or Euclidean calculations cannot fill this Lorentzian gap.
- **Empirical benchmark — `NOT_REACHED`:** No observational benchmark is connected to the certified quantum route. Boundary: Classical phenomenology from another assembly cannot be transferred without a typed interface.

**Highest-value next step:** Decide physical-cohomology positivity on the same 386-row Hadamard carrier; then construct Lorentzian products and restore or obstruct the QME.

## Evidence and audit boundary

- `GR_CASSINI` → `foundations/results/FOUNDATIONAL_GR_CASSINI_MODEL_ASSEMBLY_V1.json` (`f87aa0453de1af594175d1c23c39b48d644064a8582a56785bd9ea4ce279a902`)
- `NGC3198_COMMON` → `foundations/results/FOUNDATIONAL_NGC3198_COMMON_FIT_COMPARISON_V1.json` (`e9c9ecd8e6778a98cf15754970ac2e8fa6c117edca630f3a89b30aea1a03eaeb`)
- `MANNHEIM_NGC3198` → `foundations/results/FOUNDATIONAL_MANNHEIM_NGC3198_MODEL_ASSEMBLY_V1.json` (`d4e7b8774f6593136b512453108a2d39396cd91969fdfc73681ee14d936e0154`)
- `BT_EUCLIDEAN` → `foundations/results/FOUNDATIONAL_BT_EUCLIDEAN_LATTICE_IMPORT_V1.json` (`f8791f9209682cd01b29a5868ea8f353b958f9fb8ce24d77d9b8af6bc92b7f94`)
- `KREIN_FREE` → `foundations/results/FOUNDATIONAL_KREIN_FOCK_GROUND_STATE_DYNAMICS_INTERFACE_V1.json` (`36444854eaed27ebd0a82cb7b26f2c3ad1c1e211f08fc0326882fd325676af06`)
- `CODED_WAVE` → `foundations/results/FOUNDATIONAL_CODED_WAVE_OBSERVABLE_RECONSTRUCTION_V1.json` (`cf90e90abb824e19a2a0e7caf2d32c4772f408a70107e4c9ea6013edc0e8e215`)
- `PURE_WEYL` → `foundations/results/FOUNDATIONAL_LORENTZIAN_WEYL_BV_COMPLETION_ATLAS_V49.json` (`5dd450b6186f41508407829f7f00983c604b809e0b51f5af161883fa1e5519ce`)

Every stage carries JSON-pointer assertions into these content-pinned sources. Generation refuses source drift; the independent checker recomputes pins, assertions, joins, and summary counts.

This atlas does not establish:

- that the six stage functions have identical mathematical meaning in classical, quantum, Euclidean, constructive, and indefinite-metric theories.
- that a stage-local theorem composes with later evidence unless the passport join is closed.
- that passing one bounded empirical gate validates a complete theory.
- that failing one bounded empirical gate universally refutes a research programme.
- population-level or held-out observational performance for any galactic model.
- a new Lorentzian, quantum, continuum, positivity, or QME result.
- any promotion of a completion-matrix cell.

## Reproduce

```bash
python3 foundations/build_theory_passport_atlas.py --write
python3 foundations/check_theory_passport_atlas.py
python3 foundations/verify_theory_passport_atlas.py
```
