# Axial local commutant and spectral \(C\) — close-out

Date: 2026-07-24  
Dependency tags: `LOCAL-ALGEBRAIC`, `REDUCED-MODE`

## Established

The certified nonsplit axial spin-two extension has

\[
\operatorname{End}(E)\simeq
\mathbb C[\varepsilon]/(\varepsilon^2)
\]

for every real \(\omega>0\).  Consequently its only idempotents are \(0,I\),
its only involutions are \(\pm I\), every diagonalizable local endomorphism is
scalar, and every finite-order local automorphism is scalar.  The only
non-scalar local commutant direction is the nilpotent extension shear.

This strengthens the local-\(C\) obstruction: there is no nontrivial local
semisimple branch observable on the nonsplit spin-two block.

The local obstruction does not exclude a global spectral fundamental
symmetry.  For each positive real frequency,

\[
C_-=\operatorname{sgn}(G_-)
\]

is a Krein-self-adjoint involution and \(G_-C_-=|G_-|>0\).  Pullback through
the globally invertible incoming map \(T_-\) gives a positive fundamental
symmetry on the horizon-regular solution fiber.  On compact positive-frequency
bands it is bounded and produces a norm uniformly equivalent to the
coefficient norm.

In the exact incoming second-null Witt basis, the positive majorant is

\[
\frac{384}{5}\operatorname{diag}(\omega,\omega,\omega^3).
\]

The all-frequency completion is therefore naturally weighted; it is not
uniformly equivalent to unweighted \(L^2\) at threshold.

Finally, under the conserved Krein identity and the genuine
fundamental-symmetry axioms, the positive-metric scattering identity is
equivalent to

\[
(C_+\oplus C_H)\mathsf S=\mathsf S C_-.
\]

The reverse implication follows by expanding the positive norm of the
intertwining defect.  This corrects an earlier overly cautious reading: no
surjectivity of \(\mathsf S\) is needed.

## Not established

The spectral \(C\) is not shown to be canonical, covariant, causal,
complex-frequency holomorphic, endpoint-block-diagonal, or BRST compatible.
The complete six-state commutant is not classified because nonsplitting of
the mixed Maxwell extension remains open.

## Reproducibility

Primary record:

`black_hole_programme/phase4/axial_local_commutant_spectral_c_v1/certificate.json`

Commands:

```bash
python3 -m black_hole_programme.phase4.axial_local_commutant_spectral_c_v1.produce
python3 -m black_hole_programme.phase4.axial_local_commutant_spectral_c_v1.verify
python3 -m unittest -v black_hole_programme.phase4.axial_local_commutant_spectral_c_v1.test_commutant_spectral_c
```

Tier 0: Python parsing and scoped `git diff --check`.  
Tier 1: producer, independently written verifier, and mutation tests.  
Tier 2 was not required because imported operators and certificates were
content-addressed and unchanged.  Tier 3 was not required because no release
or cross-programme freeze was promoted.

EVIDENCE: black_hole_programme/phase4/axial_local_commutant_spectral_c_v1/certificate.json
CLOSE-OUT: DONE — objective met; exact certificate and independent verifier are recorded in the package above.
