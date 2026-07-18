# Generic ghost n=3 five-carrier projection

## Result

The generic nonexceptional-momentum three-Ricci Endo ghost triangle is now
projected exactly onto the parity-even scalar-flat CPT carrier quotient.
The raw effective module has eleven labelled orientations:

```text
I10: 1
I24: 3
I25: 3
I28: 3
I29: 1
```

The exact TT evaluation matrix has shape `125 x 11` and rank ten.  Appending
the section condition

```text
Gamma_I28_123 + Gamma_I28_132 + Gamma_I28_231 = 0
```

fixes the unique four-dimensional CPT-IV null direction and gives an
invertible eleven-row solve.  This is a choice of quotient representative,
not an additional physical identity.

Every channel is stored in the exact form

\[
 \Gamma_i(\alpha;x)=
 \frac{N_i(\alpha_1,\alpha_2;x_1,x_2,x_3)}{\Delta^4},
 \qquad
 \Delta=\alpha_0\alpha_1x_1+
 \alpha_1\alpha_2x_2+
 \alpha_2\alpha_0x_3,
\]

with rational coefficients.  For a carrier with `d` explicit derivatives,
the numerator is homogeneous of box degree `3-d/2`.  The maximum alpha
degree is nine.  The `W=-2 Ric` and third-order trace-log multiplier `-8/3`
is already included; the common loop prefactor `(4*pi)^-2` is not.

## Exact reconstruction

The producer avoids raw tensor-graph expansion.  It:

1. evaluates the eleven carriers on all 125 products of exact TT
   polarizations;
2. solves the rank-ten carrier quotient with the declared `I28` section;
3. retains symbolic Feynman parameters throughout;
4. reconstructs the homogeneous box coefficients from ten unisolvent
   momentum fixtures; and
5. verifies zero interpolation residual and the `I28` section coefficient by
   coefficient.

The resulting certificate contains 11 rows and 837 nonzero exact rational
terms.  Its formula digest is
`2b3c0de4147aa45b7b4f783495dfaa4097903f4db1f1cc84aa665a0ae467a245`.

## Independent replay

The fast verifier does not rerun interpolation.  It evaluates the stored
formula at two unseen momentum fixtures and two unseen rational simplex
points, reconstructs all 125 TT tensor amplitudes, and compares them exactly
with the interpolation-independent Endo triangle kernel.  Both residuals and
the symmetric `I28` coordinate vanish exactly.  A coefficient mutation is
rejected even when the attacker recomputes the formula digest.

The exhaustive producer/check takes about 163 seconds and belongs to the
scientific or release tier.  The five focused tests, including both holdout
replays and mutation rejection, take about 4.4 seconds and belong to the
default changed-package tier.

## Claim boundary

This is an `EUCLIDEAN-SPECTRAL` computation of the parametric `n=3` ghost
contribution.  It does not yet compute:

- the curved-Endo one- or two-insertion traces;
- the complete generic ghost determinant;
- the generic physical fourth-order Hessian kernel;
- the integrated five repository third-curvature functions or their full
  coefficients;
- the parity-odd derivative sector;
- finite normalizations, complete `Gamma1`, or complete `Q1`;
- residual transfer or any Lorentzian QME, Hadamard, particle, positivity,
  scattering, or unitarity theorem.

## Reproduction

Fast exact replay:

```bash
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.verify_generic_background_ghost_n3_five_carrier_projection
PYTHONPATH=quantum-weyl python3 -m unittest \
  spectral.euclidean.tests.test_generic_background_ghost_n3_five_carrier_projection
```

Scientific full regeneration:

```bash
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.generic_background_ghost_n3_five_carrier_projection --check
```
