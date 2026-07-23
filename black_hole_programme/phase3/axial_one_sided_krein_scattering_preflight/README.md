# Axial one-sided Krein scattering preflight

This package proves the finite-dimensional one-sided Krein theorem that
would follow from a typed global Stokes handoff, and audits its exact
normalization against the committed incoming and future-horizon Grams.

The physical result is deliberately fail closed.  The global channel gate
does not contain the typed \(T_+\) entries or an independently verified
current-conservation defect.  Consequently the package does not activate a
physical \(J\)-isometry, reflection defect, or scattering matrix.

The separate local horizon scope audit does extend the exact Gram and factor
formula to every real positive frequency: the symbolic Frobenius recurrence,
compatible resonance residuals, denominator factors, and omitted-head power
count are collision-free there.  This does not widen the global scattering
claim beyond the pilot band.

Run:

```bash
python3 -m black_hole_programme.phase3.axial_one_sided_krein_scattering_preflight.produce
python3 -m black_hole_programme.phase3.axial_one_sided_krein_scattering_preflight.verify
python3 -m unittest -v black_hole_programme.phase3.axial_one_sided_krein_scattering_preflight.tests.test_preflight
```
