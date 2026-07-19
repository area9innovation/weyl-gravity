# Generic-background physical-Hessian n=3 integration obstruction

## Result

The isolated bosonic three-linear term

\[
\frac16\operatorname{Tr}\bigl[(\mathcal H_0^{-1}\mathcal H_1)^3\bigr]
\]

does not define a finite simplex integral by itself.  At the exact symmetric
fixture \(x_1=x_2=x_3=1\), the \(S_3\)-averaged five-carrier numerator contains

\[
M_{14}=\frac{e_3}{e_2^4},\qquad
e_2=\alpha_0\alpha_1+\alpha_1\alpha_2+\alpha_2\alpha_0,
\quad e_3=\alpha_0\alpha_1\alpha_2.
\]

The declared pole-four relative-IBP-plus-master span has exact rank 49.
Adjoining \(M_{14}\) raises it to 50.  A normalized dual functional is stored
which annihilates all 49 boundary/master directions and evaluates to one on
\(M_{14}\).  Thus the rank jump is independently checkable without replaying
the elimination.

Near each simplex corner, with one dominant parameter \(1-\epsilon\) and the
other two split as \(\epsilon t\) and \(\epsilon(1-t)\), the measure-weighted
carrier is

\[
\frac{t(1-t)}{\epsilon}\,d\epsilon\,dt+O(1).
\]

The angular coefficient is \(1/6\) per corner and \(1/2\) in total.  Hence
\(M_{14}\) is logarithmically corner divergent.

## Raw carrier ledger

The nonzero \(M_{14}\) and total logarithmic coefficients are:

| Raw channel | \(M_{14}\) coefficient | \(\log(1/\epsilon)\) coefficient |
| --- | ---: | ---: |
| `I10_123` | \(15/2\) | \(15/4\) |
| each `I24` orientation | \(17/18\) | \(17/36\) |
| each `I25` orientation | \(-121/9\) | \(-121/18\) |
| each `I28` orientation | \(0\) | \(0\) |
| `I29_123` | \(176/3\) | \(88/3\) |

Exactly eight raw orientations are nonzero: `I10_123`, the three `I24`
orientations, the three `I25` orientations, and `I29_123`.  The zero
\(M_{14}\) coordinate for `I28` is not promoted to a claim that every
remaining `I28` integral is absolutely convergent.

## Consequence and boundary

This is a `LOCAL-ALGEBRAIC` plus `EUCLIDEAN-SPECTRAL` obstruction to treating
the isolated \(\mathcal H_1^3\) trace as a finite physical form factor.  The
minimal next input is either:

1. the curvature-squared \(\mathcal H_2\) and mixed \(\mathcal H_1\mathcal H_2\)
   rows, followed by an exact test of the same corner class; or
2. an explicitly fixed renormalized subtraction prescription.

The certificate does **not** assert that \(\mathcal H_2\) cancels the class.
It does not integrate the physical triangle, assemble the complete five
repository functions, supply \(\Gamma_1\) or \(Q_1\), authorize residual
transfer, or prove a Lorentzian/Hadamard/particle statement.

## Receipts

```text
PYTHONPATH=quantum-weyl python3 -m \
  spectral.euclidean.generic_background_physical_hessian_n3_integration_obstruction --check
PYTHONPATH=quantum-weyl python3 \
  quantum-weyl/spectral/euclidean/verify_generic_background_physical_hessian_n3_integration_obstruction.py
PYTHONPATH=quantum-weyl python3 -m unittest \
  quantum-weyl/spectral/euclidean/tests/test_generic_background_physical_hessian_n3_integration_obstruction.py
```

The machine-readable receipt is
`quantum-weyl/spectral/euclidean/certificates/GENERIC_BACKGROUND_PHYSICAL_HESSIAN_N3_INTEGRATION_OBSTRUCTION.json`.
